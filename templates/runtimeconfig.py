"""Creates Runtime Config resources to wait for startup to complete successfully"""


def GenerateConfig(context):
    """ Retrieve variables from the context """
    deployment = context.env['deployment']

    """ Define the resources for the Runtime Config """
    resources = [
        {
            'name': "%s-startup-config" % deployment,
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs',
            'properties': {
                'config': '%s-runtime-config' % deployment
            }

        },
        {
            'name': "%s-startup-waiter" % deployment,
            'type': 'gcp-types/runtimeconfig-v1beta1:projects.configs.waiters',
            'metadata': {
                'dependsOn': [
                    "%s-ansible-controller" % deployment
                ]
            },
            'properties': {
                'parent': "$(ref.%s-startup-config.name)" % deployment,
                'waiter': 'viya-runtime-waiter',
                'timeout': "7200s",  # 2 hours
                'success': {
                    'cardinality': {
                        'number': 1,
                        'path': '/success'
                    }
                },
                'failure': {
                    'cardinality': {
                        'number': 1,
                        'path': '/failure'
                    }
                }
            }
        }
    ]

    return {'resources': resources}
