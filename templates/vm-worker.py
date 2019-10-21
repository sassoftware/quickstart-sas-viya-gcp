"""Creates the cas worker nodes"""


""" Startup script for cas worker node """
worker_startup_script = '''#!/bin/bash
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
# yum -y update
'''


def GenerateConfig(context):
    """ Retrieve variable values from the context """
    worker_machinetype = context.properties['WorkerMachineType']
    if context.properties['CASInstanceCount'] is 10:
        cas_instance_count = context.properties['CASInstanceCount']
    else:
        cas_instance_count = "{:0>2}".format(context.properties['CASInstanceCount'])




    project = context.env['project']
    deployment = context.env['deployment']
    zone = context.properties['Zone']
    ssh_key = context.properties['SSHPublicKey']

    """ Define the resources for the VMs """
    resources = [
        {
            'name': "{}-worker{}".format(deployment, cas_instance_count),
            'type': "gcp-types/compute-v1:instances",
            'properties': {
                'zone': zone,
                'machineType': "zones/{}/machineTypes/{}".format(zone, worker_machinetype),
                'hostname': "worker{}.viya.sas".format(cas_instance_count),
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
                            # 'sourceImage': "https://www.googleapis.com/compute/v1/projects/rhel-cloud/global/images/family/rhel-7",
                            'sourceImage': "https://www.googleapis.com/compute/v1/projects/rhel-cloud/global/images/rhel-7-v20190729",
                            'diskSizeGb': 10
                        }
                    },
                    {
                        'deviceName': "sashome",
                        'type': "PERSISTENT",
                        'boot': False,
                        'autoDelete': True,
                        'initializeParams': {
                            'diskName': "{}-sashome-worker{}".format(deployment, cas_instance_count),
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
                            'diskName': "{}-userlib-worker{}".format(deployment, cas_instance_count),
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
                            'diskName': "{}-cascache-worker{}".format(deployment, cas_instance_count),
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
                        {'key': 'startup-script', 'value': worker_startup_script.format(deployment=deployment)}
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
