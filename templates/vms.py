"""Creates three VMs: anisble controller, viya services and cas controller"""

""" Startup script for Ansible Controller """
ansible_startup_script = '''#!/bin/bash
# The VM needs a few seconds to come up before executing the startup scripts
sleep 10
###################################
# Setting up environment
###################################
export COMMON_CODE_TAG="%s"
export OLCROOTPW="%s"
export OLCUSERPW="%s"
export VIYA_VERSION="%s"
export DEPLOYMENT_DATA_LOCATION="%s"
export IAAS=gcp
export INSTALL_DIR=/sas/install
export LOG_DIR=/var/log/sas/install
/bin/su sasinstall -c "export > /home/sasinstall/SAS_VIYA_DEPLOYMENT_ENVIRONMENT"
###################################
# Installing dependencies
###################################
yum install -y java-1.8.0-openjdk
yum install -y epel-release
yum install -y python-pip
yum install -y git
# Getting quick start scripts from Github  # TODO: Remove '-b develop' before push to master
git clone https://github.com/sassoftware/quickstart-sas-viya-gcp $INSTALL_DIR -b develop
# Clean up GitHub identifier files
pushd $INSTALL_DIR
rm -rf .git*
popd
# Getting specific release of quick start common code from Github
git clone https://github.com/sassoftware/quickstart-sas-viya-common $INSTALL_DIR/common
pushd $INSTALL_DIR/common
git checkout tags/$COMMON_CODE_TAG -b $COMMON_CODE_TAG
# Clean up GitHub identifier files
rm -rf .git*
popd
# Updating ownership so that sasinstall user can read/write
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
   -e OLCROOTPW=$(echo -n "$OLCROOTPW" | base64) \
   -e OLCUSERPW=$(echo -n "$OLCUSERPW" | base64)"
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
   -e ADMINPASS=$(echo "$OLCROOTPW" | base64) \
   -e VIYA_VERSION=$VIYA_VERSION"
###################################
# Run VIRK
# The VIRK pre-install playbook covers most of the Viya Deployment Guide prereqs in one fell swoop.
###################################
export ANSIBLE_LOG_PATH=$LOG_DIR/virk.log
export ANSIBLE_INVENTORY=$INSTALL_DIR/ansible/sas_viya_playbook/inventory.ini
/bin/su sasinstall -c "ansible-playbook -v $INSTALL_DIR/ansible/sas_viya_playbook/virk/playbooks/pre-install-playbook/viya_pre_install_playbook.yml \
  -e "use_pause=false" \
  --skip-tags skipmemfail,skipcoresfail,skipstoragefail,skipnicssfail,bandwidth"
##################################
# Install Viya
##################################
export ANSIBLE_LOG_PATH=$LOG_DIR/viya_deployment.log
export ANSIBLE_CONFIG=$INSTALL_DIR/ansible/sas_viya_playbook
pushd /sas/install/ansible/sas_viya_playbook
/bin/su sasinstall -c "ansible-playbook -v site.yml"
##################################
# Post Deployment Steps
##################################
export ANSIBLE_LOG_PATH=$LOG_DIR/post_deployment.log
export ANSIBLE_CONFIG=$INSTALL_DIR/common/ansible/playbooks/ansible.cfg
/bin/su sasinstall -c "ansible-playbook -v $INSTALL_DIR/common/ansible/playbooks/post_deployment.yml"
##################################
# Final system update
##################################
yum -y update
/bin/su sasinstall -c "echo 'Check /var/log/sas/install for deployment logs.' > /home/sasinstall/SAS_VIYA_DEPLOYMENT_FINISHED"
'''

""" Startup script for viya services """
services_startup_script = '''#! /bin/bash
# Setting up environment
export NFS_SERVER=%s-ansible-controller
export HOST=`hostname`
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

""" Startup script for cas controller """
controller_startup_script = '''#!/bin/bash
# Setting up environment
export NFS_SERVER=%s-ansible-controller
export HOST=`hostname`
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
    common_code_tag = context.properties['COMMON_CODE_TAG']
    olc_root_pw = context.properties['OLCROOTPW']
    olc_user_pw = context.properties['OLCUSERPW']
    viya_version = context.properties['VIYA_VERSION'].replace('\\', '')
    deployment_data_location = context.properties['DEPLOYMENT_DATA_LOCATION']
    deployment = context.env['deployment']
    zone = context.properties['zone']
    ssh_key = context.properties['ssh-key']

    """ Define the resources for the VMs """
    resources = [
        {
            'name' : "%s-ansible-controller" % deployment,
            'type' : 'gcp-types/compute-v1:instances',
            'properties' : {
                'zone' : zone,
                'machineType' : "zones/%s/machineTypes/g1-small" % zone,
                'serviceAccounts' : [{
                    'email' : "$(ref.%s-ansible-svc-account.email)" % deployment,
                    'scopes' : [
                        "https://www.googleapis.com/auth/cloud-platform"
                    ]
                }],
                'disks' : [{
                    'deviceName' : 'boot',
                    'type' : 'PERSISTENT',
                    'boot' : True,
                    'autoDelete' : True,
                    'initializeParams': {
                        'sourceImage' : "https://www.googleapis.com/compute/v1/projects/rhel-cloud/global/images/family/rhel-7",
                        'diskSizeGb' : 10
                    }
                }],
                'networkInterfaces' : [{
                    'subnetwork' : "$(ref.%s-public-subnet.selfLink)" % deployment,
                    'accessConfigs' : [{
                        'name' : 'External NAT',
                        'type' : 'ONE_TO_ONE_NAT'
                    }],
                }],
                'tags' : {
                    'items' : [
                        'sas-viya-ansible-controller'
                    ]
                },
                'metadata' : {
                    'items' : [
                        { 'key' : 'ssh-keys', 'value' : "sasinstall:%s" % ssh_key },
                        { 'key' : 'block-project-ssh-keys', 'value' : "true" },
                        { 'key' : 'startup-script', 'value' : ansible_startup_script % (common_code_tag, olc_root_pw, olc_user_pw, viya_version, deployment_data_location) }
                    ]
                }
            }
        },
        {
            'name' : "%s-services" % deployment,
            'type' : "gcp-types/compute-v1:instances",
            'properties': {
                'zone' : zone,
                'machineType' : "zones/%s/machineTypes/n1-highmem-8" % zone,
                'hostname' : "services.viya.sas",
                'serviceAccounts' : [{
                    'email' : "$(ref.%s-ansible-svc-account.email)" % deployment,
                    'scopes' : [
                        "https://www.googleapis.com/auth/cloud-platform"
                    ]
                }],
                'disks' : [
                    {
                        'deviceName' : 'boot',
                        'type': "PERSISTENT",
                        'boot' : True,
                        'autoDelete' : True,
                        'initializeParams': {
                            'sourceImage' : "https://www.googleapis.com/compute/v1/projects/rhel-cloud/global/images/family/rhel-7",
                            'diskSizeGb' : 25
                        }
                    },
                    {
                        'deviceName' : 'sashome',
                        'type' : "PERSISTENT",
                        'boot' : False,
                        'autoDelete' : True,
                        'initializeParams' : {
                            'diskName' : "%s-sashome-services" % deployment,
                            'diskSizeGb' : 100,
                            'description' : "SAS_INSTALL_DISK"
                        }
                    }
                ],
                'networkInterfaces' : [{
                    'subnetwork' : "$(ref.%s-private-subnet.selfLink)" % deployment
                }],
                'metadata' : {
                    'items' : [
                        { 'key' : 'ssh-keys', 'value' : "sasinstall:%s" % ssh_key },
                        { 'key' : 'block-project-ssh-keys', 'value' : "true" },
                        { 'key' : 'startup-script', 'value' : services_startup_script % deployment }
                    ]
                },
                'tags' : {
                    'items' : [
                        'sas-viya-vm'
                    ]
                }
            }
        },
        {
            'name' : "%s-controller" % deployment,
            'type' : "gcp-types/compute-v1:instances",
            'properties': {
                'zone' : zone,
                'machineType' : "zones/%s/machineTypes/n1-standard-2" % zone,
                'hostname' : "controller.viya.sas",
                'serviceAccounts' : [{
                    'email' : "$(ref.%s-ansible-svc-account.email)" % deployment,
                    'scopes' : [
                        "https://www.googleapis.com/auth/cloud-platform"
                    ]
                }],
                'disks' : [
                    {
                        'deviceName' : "boot",
                        'type' : "PERSISTENT",
                        'boot' : True,
                        'autoDelete' : True,
                        'initializeParams' : {
                            'sourceImage' : "https://www.googleapis.com/compute/v1/projects/rhel-cloud/global/images/family/rhel-7",
                            'diskSizeGb' : 10
                        }
                    },
                    {
                        'deviceName' : "sashome",
                        'type' : "PERSISTENT",
                        'boot' : False,
                        'autoDelete' : True,
                        'initializeParams' : {
                            'diskName' : "%s-sashome-controller" % deployment,
                            'diskSizeGb' : 50,
                            'description' : "SAS_INSTALL_DISK"
                        }
                    },
                    {
                        'deviceName' : "userlib",
                        'type' : "PERSISTENT",
                        'boot' : False,
                        'autoDelete' : True,
                        'kind' : "compute",
                        'mode' : "READ_WRITE",
                        'initializeParams' : {
                            'diskName' : "%s-userlib" % deployment,
                            'diskType' : "projects/ace-dev/zones/%s/diskTypes/pd-standard" % zone,
                            'diskSizeGb' : 50,
                            'description' : "USERLIB_DISK"
                        }
                    },
                    {
                        'deviceName' : "cascache",
                        'type' : "PERSISTENT",
                        'boot' : False,
                        'autoDelete' : True,
                        'kind' : "compute",
                        'mode' : "READ_WRITE",
                        'initializeParams' : {
                            'diskName' : "%s-cascache" % deployment,
                            'diskType' : "projects/ace-dev/zones/%s/diskTypes/pd-standard" % zone,
                            'diskSizeGb' : 50,
                            'description' : "CASCACHE_DISK"
                        }
                    }
                ],
                'networkInterfaces' : [{
                    'subnetwork' : "$(ref.%s-private-subnet.selfLink)" % deployment
                }],
                'metadata' : {
                    'items' : [
                        { 'key' : "ssh-keys", 'value' : "sasinstall:%s" % ssh_key },
                        { 'key' : "block-project-ssh-keys", 'value' : "true" },
                        { 'key' : "startup-script", 'value': controller_startup_script % deployment }
                    ]
                },
                'tags' : {
                    'items' : [
                        "sas-viya-vm"
                    ]
                }
            }
        }
    ]

    return { 'resources' : resources }
