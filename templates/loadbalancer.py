"""Load balancer resources"""


def GenerateConfig(context):
    """ Retrieve variable values from the context """
    deployment = context.env['deployment']
    project = context.env['project']
    region = context.properties['Region']
    zone = context.properties['Zone']

    """ Define the Load Balancer resources """
    resources = [
        {
            'name': "{}-loadbalancer-ip".format(deployment),
            'type': "gcp-types/compute-v1:addresses",
            'properties': {
                'networkTier': "STANDARD",
                'region': region
            }
        },
        {
            'name': "{}-instance-group".format(deployment),
            'type': "gcp-types/compute-v1:instanceGroups",
            'properties': {
                'managed': "no",
                'zone': zone,
                'network': "$(ref.{}-vpc.selfLink)".format(deployment),
                'namedPorts': [
                    {'name': "https", 'port': 443}
                ]
            }
        },
        {
            'name': "add-to-instance-group",
            'action': "gcp-types/compute-v1:compute.instanceGroups.addInstances",
            'properties': {
                'project': project,
                'zone': zone,
                'instanceGroup': "{}-instance-group".format(deployment),
                'instances': [
                    {
                        'instance': "$(ref.{}-services.selfLink)".format(deployment)
                    }
                ]
            }
        },
        {
            'name': "{}-https-healthcheck".format(deployment),
            'type': "gcp-types/compute-v1:httpsHealthChecks",
            'properties': {
                'requestPath': "/SASLogon/login",
                'port': 443
            }
        },
        {
            'name': "{}-backend".format(deployment),
            'type': "gcp-types/compute-v1:backendServices",
            'properties': {
                'port': 443,
                'portName': "https",
                'protocol': "HTTPS",
                'backends': [
                    {'group': "$(ref.{}-instance-group.selfLink)".format(deployment)}
                ],
                'healthChecks': [
                    "$(ref.{}-https-healthcheck.selfLink)".format(deployment)
                ]
            }
        },
        {
            'name': "{}-loadbalancer".format(deployment),
            'type': "gcp-types/compute-v1:urlMaps",
            'properties': {
                'defaultService': "$(ref.{}-backend.selfLink)".format(deployment)
            }
        },
        {
            'name': "{}-loadbalancer-target-proxy".format(deployment),
            'type': "gcp-types/compute-v1:targetHttpsProxies",
            'properties': {
                'protocol': "HTTPS",
                'sslCertificates': [
                    "global/sslCertificates/viya-sslcert"
                ],
                'urlMap': "$(ref.{}-loadbalancer.selfLink)".format(deployment)
            }
        },
        {
            'name': "{}-forwarding-rules".format(deployment),
            'type': "gcp-types/compute-v1:forwardingRules",
            'properties': {
                'IPAddress': "$(ref.{}-loadbalancer-ip.selfLink)".format(deployment),
                'IPProtocol': "TCP",
                'networkTier': "STANDARD",
                'portRange': 443,
                'region': region,
                'target': "$(ref.{}-loadbalancer-target-proxy.selfLink)".format(deployment)
            }
        }
    ]

    outputs = [
        {
            'name': 'SASDrive',
            'value': "https://$(ref.{}-loadbalancer-ip.address)/SASDrive".format(deployment)
        },
        {
            'name': 'SASStudio',
            'value': "https://$(ref.{}-loadbalancer-ip.address)/SASStudioV".format(deployment)
        }
    ]

    return {'resources': resources, 'outputs': outputs}
