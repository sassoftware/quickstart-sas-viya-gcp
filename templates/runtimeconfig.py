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
                'config': '{}-waiter-config'.format(deployment)
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
                        'path': 'startup/success'
                    }
                },
                'failure': {
                    'cardinality': {
                        'number': 1,
                        'path': 'startup/failure'
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
                        'number': 2,
                        'path': 'startup/success'
                    }
                },
                'failure': {
                    'cardinality': {
                        'number': 1,
                        'path': 'startup/failure'
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
                        'number': 3,
                        'path': 'startup/success'
                    }
                },
                'failure': {
                    'cardinality': {
                        'number': 1,
                        'path': 'startup/failure'
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
                        'number': 4,
                        'path': 'startup/success'
                    }
                },
                'failure': {
                    'cardinality': {
                        'number': 1,
                        'path': 'startup/failure'
                    }
                }
            }
        },
    ]

    return {'resources': resources}
