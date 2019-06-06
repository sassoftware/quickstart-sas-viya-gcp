"""Creates Runtime Config resources to wait for startup to complete successfully"""


def GenerateConfig(context):
    """ Retrieve variables from the context """
    deployment = context.env['deployment']

    """ Define the resources for the Runtime Config """
    resources = [
        {
            'name': "%s-waiter-config" % deployment,
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs',
            'properties': {
                'config': '%s-runtime-config' % deployment
            }

        },
        # Triggers for the following waiters are in ansible_startup_script  contained in file vms.py
        {
            'name': "%s-startup-waiter1" % deployment,
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs.waiters',
            'metadata': {
                'dependsOn': [
                    "%s-ansible-controller" % deployment
                ]
            },
            'properties': {
                'parent': "$(ref.%s-waiter-config.name)" % deployment,
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
            'name': "%s-startup-waiter2" % deployment,
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs.waiters',
            'metadata': {
                'dependsOn': [
                    "%s-startup-waiter1" % deployment
                ]
            },
            'properties': {
                'parent': "$(ref.%s-waiter-config.name)" % deployment,
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
            'name': "%s-startup-waiter3" % deployment,
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs.waiters',
            'metadata': {
                'dependsOn': [
                    "%s-startup-waiter2" % deployment
                ]
            },
            'properties': {
                'parent': "$(ref.%s-waiter-config.name)" % deployment,
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
        }
    ]

    return {'resources': resources}
