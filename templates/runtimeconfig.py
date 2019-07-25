"""Creates Runtime Config resources to wait for startup to complete successfully"""


def GenerateConfig(context):
    """ Retrieve variables from the context """
    deployment = context.env['deployment']

    """ Define the resources for the Runtime Config """
    resources = [
        {
            'name': "{}-deployment-waiter".format(deployment),
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs',
            'properties': {
                'config': '{}-deployment-waiter'.format(deployment)
            }

        },
        # Triggers for the following waiters are in ansible_startup_script  contained in file vms.py
        {
            'name': "{}-initialization-status".format(deployment),
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs.waiters',
            'metadata': {
                'dependsOn': [
                    "{}-ansible-controller".format(deployment)
                ]
            },
            'properties': {
                'parent': "$(ref.{}-deployment-waiter.name)".format(deployment),
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
            'name': "{}-deployment-status1".format(deployment),
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs.waiters',
            'metadata': {
                'dependsOn': [
                    "{}-initialization-status".format(deployment)
                ]
            },
            'properties': {
                'parent': "$(ref.{}-deployment-waiter.name)".format(deployment),
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
            'name': "{}-deployment-status2".format(deployment),
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs.waiters',
            'metadata': {
                'dependsOn': [
                    "{}-deployment-status1".format(deployment)
                ]
            },
            'properties': {
                'parent': "$(ref.{}-deployment-waiter.name)".format(deployment),
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
            'name': "{}-deployment-status3".format(deployment),
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs.waiters',
            'metadata': {
                'dependsOn': [
                    "{}-deployment-status2".format(deployment)
                ]
            },
            'properties': {
                'parent': "$(ref.{}-deployment-waiter.name)".format(deployment),
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
        {
            'name': "{}-services-status".format(deployment),
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs.waiters',
            'metadata': {
                'dependsOn': [
                    "{}-deployment-status3".format(deployment)
                ]
            },
            'properties': {
                'parent': "$(ref.{}-deployment-waiter.name)".format(deployment),
                'waiter': 'viya-runtime-waiter5',
                'timeout': "5000s",
                'success': {
                    'cardinality': {
                        'number': 5,
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
