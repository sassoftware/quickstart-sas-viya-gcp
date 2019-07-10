"""Creates three VMs: anisble controller, viya services and cas controller"""

import base64

""" Startup script for Ansible Controller """
ansible_startup_script = '''#!/bin/bash
###################################
# Setting up environment
###################################
export COMMON_CODE_COMMIT="ba0f1d7ac7c2e9dd50640d9120780a678258d6a9"
export PROJECT="{project}"
export DEPLOYMENT="{deployment}"
export OLCROOTPW="{olc_root_pw}"
export OLCUSERPW="{olc_user_pw}"
export DEPLOYMENT_DATA_LOCATION="{deployment_data_location}"
export IAAS="gcp"
export INSTALL_DIR="/sas/install"
export LOG_DIR="/var/log/sas/install"
/bin/su sasinstall -c "export >> /home/sasinstall/SAS_VIYA_DEPLOYMENT_ENVIRONMENT"
###################################
# Installing dependencies
###################################
yum install -y java-1.8.0-openjdk
yum install -y epel-release
yum install -y python-pip
yum install -y git
###################################
# Getting quick start scripts from Github  # TODO: Remove '-b develop' before push to master
###################################
git clone https://github.com/sassoftware/quickstart-sas-viya-gcp $INSTALL_DIR -b develop
# Clean up GitHub identifier files
pushd $INSTALL_DIR
rm -rf .git*
popd
###################################
# Verify the license file exists. The startup script will exit if it does not exist.
###################################
set +e
LICENSE_STAT=$(gsutil stat $DEPLOYMENT_DATA_LOCATION 2>&1)
set -e
if [[ $LICENSE_STAT =~ "No URLs matched" ]]; then
   echo "*** ERROR: The specified license file '$DEPLOYMENT_DATA_LOCATION' does not exist."
   # failing waiter, which fails deployment.
   gcloud beta runtime-config configs variables set startup/failure/message "*** ERROR: The specified license file '$DEPLOYMENT_DATA_LOCATION' does not exist." --config-name $DEPLOYMENT-waiter-config
   exit 1
fi
###################################
#  Download license file and extract Viya version
###################################
gsutil cp $DEPLOYMENT_DATA_LOCATION /tmp/license.zip
export VIYA_VERSION=$(python $INSTALL_DIR/functions/getviyaversion.py)
/bin/su sasinstall -c "export >> /home/sasinstall/SAS_VIYA_DEPLOYMENT_ENVIRONMENT"
###################################
#  Generate Self Signed SSL Certificate
###################################
pip install pyOpenSSL
# Generating new SSL Cert and Key
LOADBALANCERIP=$(gcloud compute addresses list | grep $DEPLOYMENT-loadbalancer | awk '{{print $2}}')
python $INSTALL_DIR/functions/create-self-signed-cert.py $LOADBALANCERIP
ret="$?"
if [ "$ret" -ne "0" ]; then
    echo "*** ERROR: SSL Certificate generation failed"
    # Viya deployment failed, exiting
    gcloud beta runtime-config configs variables set startup/failure/message "*** ERROR: SSL Certificate generation failed" --config-name $DEPLOYMENT-waiter-config
    exit $ret
elif [[ -f /tmp/selfsigned.crt && -f /tmp/private.key  ]]; then
    echo "Assign new SSL Cert to target-https-proxy resource and clean up." 
    gcloud compute ssl-certificates create $DEPLOYMENT-sslcert-tmp --certificate /tmp/selfsigned.crt --private-key /tmp/private.key
    gcloud compute target-https-proxies update $DEPLOYMENT-loadbalancer-target-proxy --ssl-certificates=https://www.googleapis.com/compute/v1/projects/$PROJECT/global/sslCertificates/$DEPLOYMENT-sslcert-tmp
    gcloud compute ssl-certificates delete $DEPLOYMENT-sslcert --quiet
    gcloud compute ssl-certificates create $DEPLOYMENT-sslcert --certificate /tmp/selfsigned.crt --private-key /tmp/private.key
    gcloud compute target-https-proxies update $DEPLOYMENT-loadbalancer-target-proxy --ssl-certificates=https://www.googleapis.com/compute/v1/projects/$PROJECT/global/sslCertificates/$DEPLOYMENT-sslcert
    gcloud compute ssl-certificates delete $DEPLOYMENT-sslcert-tmp --quiet   
else
   echo "The specified ssl certs do not exist. Failing sslcert-waiter and startup-waiter then exit."
   gcloud beta runtime-config configs variables set startup/failure/message "*** ERROR: The specified ssl certs do not exist. Failing sslcert-waiter and startup-waiter then exit." --config-name $DEPLOYMENT-waiter-config
   exit 1
fi
###################################
# Getting specific release of quick start common code from Github
###################################
git clone https://github.com/sassoftware/quickstart-sas-viya-common $INSTALL_DIR/common
pushd $INSTALL_DIR/common
git checkout $COMMON_CODE_COMMIT -b $COMMON_CODE_COMMIT
# Clean up GitHub identifier files
rm -rf .git*
popd
# Updating ownership so that sasinstall user can read/write
mkdir "$INSTALL_DIR/ansible"
chown -R sasinstall:sasinstall $INSTALL_DIR
# Bootstrapping ansible controller machine
/bin/su sasinstall -c "$INSTALL_DIR/common/scripts/ansiblecontroller_prereqs.sh"
export ANSIBLE_CONFIG=$INSTALL_DIR/common/ansible/playbooks/ansible.cfg
###################################
# Ansible playbook does additional steps needed before installing SAS, including
# - host routing
# - volume attachments
# - setting up directories and users
###################################
export ANSIBLE_LOG_PATH=$LOG_DIR/prepare_nodes.log
/bin/su sasinstall -c "ansible-playbook -v $INSTALL_DIR/common/ansible/playbooks/prepare_nodes.yml \
   -e SAS_INSTALL_DISK=/dev/disk/by-id/google-sashome \
   -e USERLIB_DISK=/dev/disk/by-id/google-userlib \
   -e CASCACHE_DISK=/dev/disk/by-id/google-cascache"
###################################
# Ansible playbook sets up an OpenLDAP server that can be used as initial identity provider for SAS Viya.
###################################
export ANSIBLE_LOG_PATH=$LOG_DIR/openldapsetup.log
/bin/su sasinstall -c "ansible-playbook -v $INSTALL_DIR/common/ansible/playbooks/openldapsetup.yml \
   -e OLCROOTPW=$OLCROOTPW \
   -e OLCUSERPW=$OLCUSERPW"
###################################
# Ansible playbook does additional steps needed before installing SAS,  including
# - download sas-orchestration
# - set up access to deployment mirror (optional)
# - build playbook from SOE file
# - modify inventory.ini and vars.yml
###################################
export ANSIBLE_LOG_PATH=$LOG_DIR/prepare_deployment.log
/bin/su sasinstall -c "ansible-playbook -v $INSTALL_DIR/common/ansible/playbooks/prepare_deployment.yml \
   -e DEPLOYMENT_DATA_LOCATION=$DEPLOYMENT_DATA_LOCATION \
   -e ADMINPASS=$OLCROOTPW \
   -e VIYA_VERSION=$VIYA_VERSION"
###################################
# Run VIRK
# The VIRK pre-install playbook covers most of the Viya Deployment Guide prereqs in one fell swoop.
###################################
export ANSIBLE_LOG_PATH=$LOG_DIR/virk.log
export ANSIBLE_INVENTORY=$INSTALL_DIR/ansible/sas_viya_playbook/inventory.ini
/bin/su sasinstall -c "ansible-playbook -v $INSTALL_DIR/ansible/sas_viya_playbook/viya-ark/playbooks/pre-install-playbook/viya_pre_install_playbook.yml \
  -e "use_pause=false" \
  --skip-tags skipmemfail,skipcoresfail,skipstoragefail,skipnicssfail,bandwidth"
##################################
# Install Viya
##################################
export PID_FILE="$LOG_DIR/viya_deployment.pid"
export RETURN_FILE="$LOG_DIR/viya_deployment.rc"
export ANSIBLE_LOG_PATH="$LOG_DIR/viya_deployment.log"
export ANSIBLE_CONFIG="$INSTALL_DIR/ansible/sas_viya_playbook"
pushd $INSTALL_DIR/ansible/sas_viya_playbook
nohup /bin/su sasinstall -c "ansible-playbook -v site.yml" &
PID=$!
echo $PID > "$PID_FILE"
ret="$?"
echo "$ret" > "$RETURN_FILE"
if [ "$ret" -ne "0" ]; then
    echo "*** ERROR: Viya Deployment script did not start"
    # viya deployment failed, exiting
    gcloud beta runtime-config configs variables set startup/failure/message "*** ERROR: Viya Deployment script did not start" --config-name $DEPLOYMENT-waiter-config
    exit $ret
fi
echo Running Waiters
# Waiters 1-3, deploying Viya
for ((WAITER_COUNT=1 ; WAITER_COUNT<4 ; WAITER_COUNT++))
do
    # first time through only wait 30 minutes, then wait 60 minutes
    if [ $WAITER_COUNT -eq "1" ]; then
        TIME_TO_LIVE_IN_SECONDS=$((SECONDS+30*60)) # 30 minutes
    else
        TIME_TO_LIVE_IN_SECONDS=$((SECONDS+60*60)) # 60 minutes
    fi
    # wait for about an hour or until the child process finishes.
    while [ "$SECONDS" -lt "$TIME_TO_LIVE_IN_SECONDS" ] && kill -s 0 $PID; do
        echo "Viya deployment is still running."
        echo "Waiter: $WAITER_COUNT has $(($((TIME_TO_LIVE_IN_SECONDS-SECONDS))/60)) minutes left"
        sleep 60
    done
    # complete waiter
    gcloud beta runtime-config configs variables set startup/success/message$WAITER_COUNT success --config-name $DEPLOYMENT-waiter-config
done
##################################
# Post Deployment Steps
##################################
export ANSIBLE_LOG_PATH=$LOG_DIR/post_deployment.log
export ANSIBLE_CONFIG=$INSTALL_DIR/common/ansible/playbooks/ansible.cfg
/bin/su sasinstall -c "ansible-playbook -v $INSTALL_DIR/common/ansible/playbooks/post_deployment.yml"
/bin/su sasinstall -c "echo 'Check /var/log/sas/install for deployment logs.' > /home/sasinstall/SAS_VIYA_DEPLOYMENT_FINISHED"
# Final Waiter 4, checking on Viya services
# wait for 50 minutes or until the login service is available for three consecutive tests
TIME_TO_LIVE_IN_SECONDS=$((SECONDS+60*60)) # 60 minutes
uriCheck=0
while [[ "$SECONDS" -lt "$TIME_TO_LIVE_IN_SECONDS" && $uriCheck -lt 5 ]]; do
    if [ $(curl -sk -o /dev/null -w "%{{http_code}}" https://$LOADBALANCERIP/SASLogon/login) -eq 200 ]; then
        uriCheck=$((uriCheck+1))
        echo "Viya is open for business. Check: $uriCheck"
        echo "Waiter: 4 has $(($((TIME_TO_LIVE_IN_SECONDS-SECONDS))/60)) minutes left"
        sleep 60
    else
        uriCheck=0
        echo "Viya Logon service is still not available."
        echo "Waiter: 4 has $(($((TIME_TO_LIVE_IN_SECONDS-SECONDS))/60)) minutes left"
        sleep 60
    fi
done
if [[ $(curl -sk -o /dev/null -w "%{{http_code}}" https://$LOADBALANCERIP/SASLogon/login) -eq 200 && $uriCheck -eq 5 ]]; then
    echo "Viya deployment was successful."
    # complete final waiter
    gcloud beta runtime-config configs variables set startup/success/message4 success --config-name $DEPLOYMENT-waiter-config
else
    echo "Viya Services are not available and we're out of time.  Please check install logs on ansible-controller in /var/log/sas/install."
    # failing final waiter
    gcloud beta runtime-config configs variables set startup/failure/message "*** ERROR: Viya Services are not available and we're out of time.  Please check install logs on ansible-controller in /var/log/sas/install." --config-name $DEPLOYMENT-waiter-config
    exit 1
fi
##################################
# Final system update
##################################
yum -y update
'''

""" Startup script for Viya services """
services_startup_script = '''#! /bin/bash
# Setting up environment
export NFS_SERVER="{deployment}-ansible-controller"
export HOST=$(hostname)
# Installing dependencies
yum -y install git
# Getting quick start scripts
git clone https://github.com/sassoftware/quickstart-sas-viya-common /tmp/common
# Bootstrapping all SAS VM
/bin/su sasinstall -c '/tmp/common/scripts/sasnodes_prereqs.sh'
# VIRK requires GID 1001 to be free
groupmod -g 2001 sasinstall
# Final system update
yum -y update
# Moving yum cache to /opt/sas where there is more room to retrieve sas viya repo
while [[ ! -d /opt/sas ]];
do
  sleep 2
done
sed -i '/cachedir/s/var/opt\/sas/' /etc/yum.conf
'''

""" Startup script for cas controller """
controller_startup_script = '''#!/bin/bash
# Setting up environment
export NFS_SERVER="{deployment}-ansible-controller"
export HOST=$(hostname)
# Installing dependencies
yum -y install git
# Getting quick start scripts
git clone https://github.com/sassoftware/quickstart-sas-viya-common /tmp/common
# Bootstrapping all SAS VM
/bin/su sasinstall -c '/tmp/common/scripts/sasnodes_prereqs.sh'
# VIRK requires GID 1001 to be free
groupmod -g 2001 sasinstall
# Final system update
yum -y update
'''


def GenerateConfig(context):
    """ Retrieve variable values from the context """
    ansible_controller_machinetype = context.properties['AnsibleControllerMachineType']
    services_machinetype = context.properties['ServicesMachineType']
    controller_machinetype = context.properties['ControllerMachineType']
    olc_root_pw = base64.b64encode(context.properties['SASAdminPass'])
    olc_user_pw = base64.b64encode(context.properties['SASUserPass'])
    deployment_data_location = context.properties['DeploymentDataLocation']
    project = context.env['project']
    deployment = context.env['deployment']
    zone = context.properties['Zone']
    ssh_key = context.properties['SSHPublicKey']

    """ Define the resources for the VMs """
    resources = [
        {
            'name': "{}-ansible-controller".format(deployment),
            'type': 'gcp-types/compute-v1:instances',
            'properties': {
                'zone': zone,
                'machineType': "zones/{}/machineTypes/{}".format(zone, ansible_controller_machinetype),
                'serviceAccounts': [{
                    'email': "$(ref.{}-ansible-svc-account.email)".format(deployment),
                    'scopes': [
                        "https://www.googleapis.com/auth/cloud-platform"
                    ]
                }],
                'disks': [{
                    'deviceName': 'boot',
                    'type': 'PERSISTENT',
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': "https://www.googleapis.com/compute/v1/projects/rhel-cloud/global/images/family/rhel-7",
                        'diskSizeGb': 10
                    }
                }],
                'networkInterfaces': [{
                    'subnetwork': "$(ref.{}-public-subnet.selfLink)".format(deployment),
                    'accessConfigs': [{
                        'name': 'External NAT',
                        'type': 'ONE_TO_ONE_NAT'
                    }],
                }],
                'tags': {
                    'items': [
                        'sas-viya-ansible-controller'
                    ]
                },
                'metadata': {
                    'items': [
                        {'key': 'ssh-keys', 'value': "sasinstall:{}".format(ssh_key)},
                        {'key': 'block-project-ssh-keys', 'value': "true"},
                        {'key': 'startup-script',
                         'value': ansible_startup_script.format(project=project, deployment=deployment, olc_root_pw=olc_root_pw, olc_user_pw=olc_user_pw, deployment_data_location=deployment_data_location)}
                    ]
                }
            }
        },
        {
            'name': "{}-services".format(deployment),
            'type': "gcp-types/compute-v1:instances",
            'properties': {
                'zone': zone,
                'machineType': "zones/{}/machineTypes/{}".format(zone, services_machinetype),
                'hostname': "services.viya.sas",
                'serviceAccounts': [{
                    'email': "$(ref.{}-ansible-svc-account.email)".format(deployment),
                    'scopes': [
                        "https://www.googleapis.com/auth/cloud-platform"
                    ]
                }],
                'disks': [
                    {
                        'deviceName': 'boot',
                        'type': "PERSISTENT",
                        'boot': True,
                        'autoDelete': True,
                        'initializeParams': {
                            'sourceImage': "https://www.googleapis.com/compute/v1/projects/rhel-cloud/global/images/family/rhel-7",
                            'diskSizeGb': 10
                        }
                    },
                    {
                        'deviceName': 'sashome',
                        'type': "PERSISTENT",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskName': "{}-sashome-services".format(deployment),
                            'diskSizeGb': 100,
                            'description': "SAS_INSTALL_DISK"
                        }
                    }
                ],
                'networkInterfaces': [{
                    'subnetwork': "$(ref.{}-private-subnet.selfLink)".format(deployment)
                }],
                'metadata': {
                    'items': [
                        {'key': 'ssh-keys', 'value': "sasinstall:{}".format(ssh_key)},
                        {'key': 'block-project-ssh-keys', 'value': "true"},
                        {'key': 'startup-script', 'value': services_startup_script.format(deployment=deployment)}
                    ]
                },
                'tags': {
                    'items': [
                        'sas-viya-vm'
                    ]
                }
            }
        },
        {
            'name': "{}-controller".format(deployment),
            'type': "gcp-types/compute-v1:instances",
            'properties': {
                'zone': zone,
                'machineType': "zones/{}/machineTypes/{}".format(zone, controller_machinetype),
                'hostname': "controller.viya.sas",
                'serviceAccounts': [{
                    'email': "$(ref.{}-ansible-svc-account.email)".format(deployment),
                    'scopes': [
                        "https://www.googleapis.com/auth/cloud-platform"
                    ]
                }],
                'disks': [
                    {
                        'deviceName': "boot",
                        'type': "PERSISTENT",
                        'boot': True,
                        'autoDelete': True,
                        'initializeParams': {
                            'sourceImage': "https://www.googleapis.com/compute/v1/projects/rhel-cloud/global/images/family/rhel-7",
                            'diskSizeGb': 10
                        }
                    },
                    {
                        'deviceName': "sashome",
                        'type': "PERSISTENT",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskName': "{}-sashome-controller".format(deployment),
                            'diskSizeGb': 50,
                            'description': "SAS_INSTALL_DISK"
                        }
                    },
                    {
                        'deviceName': "userlib",
                        'type': "PERSISTENT",
                        'boot': False,
                        'autoDelete': True,
                        'kind': "compute",
                        'mode': "READ_WRITE",
                        'initializeParams': {
                            'diskName': "{}-userlib".format(deployment),
                            'diskType': "projects/{}/zones/{}/diskTypes/pd-standard".format(project, zone),
                            'diskSizeGb': 50,
                            'description': "USERLIB_DISK"
                        }
                    },
                    {
                        'deviceName': "cascache",
                        'type': "PERSISTENT",
                        'boot': False,
                        'autoDelete': True,
                        'kind': "compute",
                        'mode': "READ_WRITE",
                        'initializeParams': {
                            'diskName': "{}-cascache".format(deployment),
                            'diskType': "projects/{}/zones/{}/diskTypes/pd-standard".format(project, zone),
                            'diskSizeGb': 50,
                            'description': "CASCACHE_DISK"
                        }
                    }
                ],
                'networkInterfaces': [{
                    'subnetwork': "$(ref.{}-private-subnet.selfLink)".format(deployment)
                }],
                'metadata': {
                    'items': [
                        {'key': "ssh-keys", 'value': "sasinstall:{}".format(ssh_key)},
                        {'key': "block-project-ssh-keys", 'value': "true"},
                        {'key': 'startup-script', 'value': controller_startup_script.format(deployment=deployment)}
                    ]
                },
                'tags': {
                    'items': [
                        "sas-viya-vm"
                    ]
                }
            }
        }
    ]

    return {'resources': resources}
