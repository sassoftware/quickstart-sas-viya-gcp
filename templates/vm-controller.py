"""Creates the  cas controller VM"""

""" Startup script for cas controller """
controller_startup_script = '''#!/bin/bash
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
yum -y update
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
'''


def GenerateConfig(context):
    """ Retrieve variable values from the context """
    common_code_commit = context.properties['CommonCodeCommit']
    source_image = context.properties['SourceImage']
    controller_machinetype = context.properties['ControllerMachineType']
    project = context.env['project']
    deployment = context.env['deployment']
    zone = context.properties['Zone']
    ssh_key = context.properties['SSHPublicKey']
    boot_disk = context.properties['BootDisk']
    sashome_disk = context.properties['SASHomeDisk']
    userlib_disk = context.properties['UserLibDisk']
    cascache_disk = context.properties['CASCacheDisk']

    """ Define the resources for the VMs """
    resources = [
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
                            'sourceImage': "{}".format(source_image),
                            'diskSizeGb': "{}".format(boot_disk)
                        }
                    },
                    {
                        'deviceName': "sashome",
                        'type': "PERSISTENT",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskName': "{}-sashome-controller".format(deployment),
                            'diskSizeGb': "{}".format(sashome_disk),
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
                            'diskSizeGb': "{}".format(userlib_disk),
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
                            'diskSizeGb': "{}".format(cascache_disk),
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
                        {'key': 'startup-script',
                         'value': controller_startup_script.format(common_code_commit=common_code_commit,
                                                                   deployment=deployment)}
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
