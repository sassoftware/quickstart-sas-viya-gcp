""" Creates the IAM resources """
import uuid

def GenerateConfig(context):

    """ Retrieve variable values from the context """
    deployment = context.env['deployment']
    project = context.env['project']
    accountId = uuid.uuid4()

    """ Define the IAM resources """
    resources = [
        {
            'type' : "gcp-types/iam-v1:projects.serviceAccounts",
            'name' : "%s-ansible-svc-account" % deployment,
            'properties' : {
                'accountId' : str(uuid.UUID(bytes=accountId.bytes))[:30],
                'displayName' : "%s-ansible-svc-account" % deployment
            }
        },
        {
            'name' : "get-iam-policy",
            'action' : "gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.getIamPolicy",
            'properties' : {
                'resource' : project
            }
        },
        {
            'name' : "patch-iam-policy",
            'action' : "gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.setIamPolicy",
            'properties' : {
                'resource' : project,
                'policy' : "$(ref.get-iam-policy)",
                'gcpIamPolicyPatch' : {
                    'add' : [{
                        'role' : "roles/storage.objectAdmin",
                        'members' : [
                            "serviceAccount:$(ref.%s-ansible-svc-account.email)" % deployment
                        ]
                    }]
                }
            }
        },
        {
            'name' : "test-account-key",
            'type' : "gcp-types/iam-v1:projects.serviceAccounts.keys",
            'properties' : {
                'parent' : "$(ref.%s-ansible-svc-account.name)" % deployment,
                'privateKeyType' : "TYPE_GOOGLE_CREDENTIALS_FILE"
            }
        }
    ]

    return { 'resources' : resources }
