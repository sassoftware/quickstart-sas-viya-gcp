""" Creates the viya services VM """

""" Startup script for Viya services """
services_startup_script = '''#!/bin/bash
# Setting up environment
export COMMON_CODE_COMMIT="{common_code_commit}"
export NFS_SERVER="{deployment}-ansible-controller"
export HOST=$(hostname)
# Set SELinux to Permissive on Viya nodes
# In Viya 3.5, Viya-ark now validates that SELinux is *not* enforced.
setenforce 0
sed -i.bak -e 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config
# Installing dependencies
yum -y install git
# Getting quick start scripts
git clone https://github.com/sassoftware/quickstart-sas-viya-common /tmp/common
pushd /tmp/common
git checkout $COMMON_CODE_COMMIT -b $COMMON_CODE_COMMIT
# Clean up GitHub identifier files
rm -rf .git*
popd
# Bootstrapping all SAS VM
/bin/su sasinstall -c '/tmp/common/scripts/sasnodes_prereqs.sh'
# VIRK requires GID 1001 to be free
groupmod -g 2001 sasinstall
# Moving yum cache to /opt/sas where there is more room to retrieve sas viya repo
while [[ ! -d /opt/sas ]];
do
  sleep 2
done
sed -i '/cachedir/s/var/opt\/sas/' /etc/yum.conf
# Final system update
echo "Sleeping 5 minutes before running system update"
sleep 5m
yum -y update
'''


def GenerateConfig(context):
    """ Retrieve variable values from the context """
    common_code_commit = context.properties['CommonCodeCommit']
    source_image = context.properties['SourceImage']
    services_machinetype = context.properties['ServicesMachineType']
    deployment = context.env['deployment']
    zone = context.properties['Zone']
    ssh_key = context.properties['SSHPublicKey']
    boot_disk = context.properties['BootDisk']
    sashome_disk = context.properties['SASHomeDisk']

    """ Define the resources for the VMs """
    resources = [
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
                            'sourceImage': "{}".format(source_image),
                            'diskSizeGb': "{}".format(boot_disk),
                        }
                    },
                    {
                        'deviceName': 'sashome',
                        'type': "PERSISTENT",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskName': "{}-sashome-services".format(deployment),
                            'diskSizeGb': "{}".format(sashome_disk),
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
                        {'key': 'startup-script', 'value': services_startup_script.format(common_code_commit=common_code_commit, deployment=deployment)}
                    ]
                },
                'tags': {
                    'items': [
                        'sas-viya-vm'
                    ]
                }
            }
        }
    ]

    return {'resources': resources}
