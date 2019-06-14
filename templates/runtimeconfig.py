"""Creates Runtime Config resources to wait for startup to complete successfully"""


def GenerateConfig(context):
    """ Retrieve variables from the context """
    deployment = context.env['deployment']

    """ Define the resources for the Runtime Config """
    resources = [
        {
            'name': "{}-waiter-config".format(deployment),
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs',
            'properties': {
                'config': '{}-runtime-config'.format(deployment)
            }

        },
        # Triggers for the following waiters are in ansible_startup_script  contained in file vms.py
        {
            'name': "{}-startup-waiter1".format(deployment),
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs.waiters',
            'metadata': {
                'dependsOn': [
                    "{}-ansible-controller".format(deployment)
                ]
            },
            'properties': {
                'parent': "$(ref.{}-waiter-config.name)".format(deployment),
                'waiter': 'viya-runtime-waiter1',
                'timeout': "5000s",
                'success': {
                    'cardinality': {
                        'number': 1,
                        'path': '/success1'
                    }
                },
                'failure': {
                    'cardinality': {
                        'number': 1,
                        'path': '/failure1'
                    }
                }
            }
        },
        {
            'name': "{}-startup-waiter2".format(deployment),
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs.waiters',
            'metadata': {
                'dependsOn': [
                    "{}-startup-waiter1".format(deployment)
                ]
            },
            'properties': {
                'parent': "$(ref.{}-waiter-config.name)".format(deployment),
                'waiter': 'viya-runtime-waiter2',
                'timeout': "5000s",
                'success': {
                    'cardinality': {
                        'number': 1,
                        'path': '/success2'
                    }
                },
                'failure': {
                    'cardinality': {
                        'number': 1,
                        'path': '/failure2'
                    }
                }
            }
        },
        {
            'name': "{}-startup-waiter3".format(deployment),
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs.waiters',
            'metadata': {
                'dependsOn': [
                    "{}-startup-waiter2".format(deployment)
                ]
            },
            'properties': {
                'parent': "$(ref.{}-waiter-config.name)".format(deployment),
                'waiter': 'viya-runtime-waiter3',
                'timeout': "5000s",
                'success': {
                    'cardinality': {
                        'number': 1,
                        'path': '/success3'
                    }
                },
                'failure': {
                    'cardinality': {
                        'number': 1,
                        'path': '/failure3'
                    }
                }
            }
        },
        {
            'name': "{}-startup-waiter4".format(deployment),
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs.waiters',
            'metadata': {
                'dependsOn': [
                    "{}-startup-waiter3".format(deployment)
                ]
            },
            'properties': {
                'parent': "$(ref.{}-waiter-config.name)".format(deployment),
                'waiter': 'viya-runtime-waiter4',
                'timeout': "5000s",
                'success': {
                    'cardinality': {
                        'number': 1,
                        'path': '/success4'
                    }
                },
                'failure': {
                    'cardinality': {
                        'number': 1,
                        'path': '/failure4'
                    }
                }
            }
        }
    ]

    return {'resources': resources}
