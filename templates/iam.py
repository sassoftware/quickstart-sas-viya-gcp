""" Creates the IAM resources """

import uuid


# noinspection PyPep8Naming
def GenerateConfig(context):
    """ Retrieve variable values from the context """
    deployment = context.env['deployment']
    project = context.env['project']

    """ Define the IAM resources """
    resources = [
        {
            'type': "gcp-types/iam-v1:projects.serviceAccounts",
            'name': "{}-ansible-svc-account".format(deployment),
            'properties': {
                'accountId': ''.join("v" + str(uuid.uuid4())[:29]),
                'displayName': "{}-ansible-svc-account".format(deployment)
            }
        },
        {
            'name': "get-iam-policy",
            'action': "gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.getIamPolicy",
            'properties': {
                'resource': project
            }
        },
        {
            'name': "patch-iam-policy",
            'action': "gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.setIamPolicy",
            'properties': {
                'resource': project,
                'policy': "$(ref.get-iam-policy)",
                'gcpIamPolicyPatch': {
                    'add': [
                        {
                            'role': "roles/storage.objectViewer",
                            'members': ["serviceAccount:$(ref.{}-ansible-svc-account.email)".format(deployment)]
                        },
                        {
                            'role': "roles/logging.logWriter",
                            'members': ["serviceAccount:$(ref.{}-ansible-svc-account.email)".format(deployment)]
                        },
                        {
                            'role': "roles/compute.viewer",
                            'members': ["serviceAccount:$(ref.{}-ansible-svc-account.email)".format(deployment)]
                        },
                        {
                            'role': "roles/runtimeconfig.admin",
                            'members': ["serviceAccount:$(ref.{}-ansible-svc-account.email)".format(deployment)]
                        },
                        {
                            'role': "roles/compute.loadBalancerAdmin",
                            'members': ["serviceAccount:$(ref.{}-ansible-svc-account.email)".format(deployment)]
                        }
                    ]
                }
            }
        },
        {
            'name': "test-account-key",
            'type': "gcp-types/iam-v1:projects.serviceAccounts.keys",
            'properties': {
                'parent': "$(ref.{}-ansible-svc-account.name)".format(deployment),
                'privateKeyType': "TYPE_GOOGLE_CREDENTIALS_FILE"
            }
        }
    ]

    return {'resources': resources}
