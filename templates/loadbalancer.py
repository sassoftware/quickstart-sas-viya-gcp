"""Load balancer resources"""

def GenerateConfig(context):

    """ Retrieve varable values from the context """
    deployment = context.env['deployment']
    project = context.env['project']
    region = context.properties['Region']
    zone = context.properties['Zone']

    """ Define the Load Balancer resources """
    resources = [
        {
            'name' : "%s-loadbalancer-ip" % deployment,
            'type' : "gcp-types/compute-v1:addresses",
            'properties' : {
                'networkTier' : "STANDARD",
                'region' : region
            }
        },
        {
            'name' : "%s-instance-group" % deployment,
            'type' : "gcp-types/compute-v1:instanceGroups",
            'properties' : {
                'managed' : "no",
                'zone' : zone,
                'network' : "$(ref.%s-vpc.selfLink)" % deployment,
                'namedPorts' : [
                    { 'name' : "http", 'port' : 80 },
                    { 'name' : "https", 'port' : 443}
                ]
            }
        },
        {
            'name' : "add-to-instance-group",
            'action' : "gcp-types/compute-v1:compute.instanceGroups.addInstances",
            'properties' : {
                'project' : project,
                'zone' : zone,
                'instanceGroup' : "%s-instance-group" % deployment,
                'instances' : [
                    {
                        'instance' : "$(ref.%s-services.selfLink)" % deployment
                    }
                ]
            }
        },
        {
            'name' : "%s-http-healthcheck" % deployment,
            'type' : "gcp-types/compute-v1:httpHealthChecks",
            'properties' : {
                'requestPath' : "/SASLogon/login",
                'port' : 80
            }
        },
        {
            'name' : "%s-https-healthcheck" % deployment,
            'type' : "gcp-types/compute-v1:httpsHealthChecks",
            'properties' : {
                'requestPath' : "/SASLogon/login",
                'port' : 443
            }
        },
        {
            'name' : "%s-backend" % deployment,
            'type' : "gcp-types/compute-v1:backendServices",
            'properties': {
                'port' : 80,
                'portName' : "http",
                'protcol' : "HTTP",
                'backends' : [
                    { 'group' : "$(ref.%s-instance-group.selfLink)" % deployment }
                ],
                'healthChecks' : [
                    "$(ref.%s-http-healthcheck.selfLink)" % deployment
                ]
            }
        },
        {
            'name' : "%s-loadbalancer" % deployment,
            'type' : "gcp-types/compute-v1:urlMaps",
            'properties' : {
                'defaultService' : "$(ref.%s-backend.selfLink)" % deployment
            }
        },
        {
            'name' : "%s-loadbalancer-target-proxy" % deployment,
            'type' : "gcp-types/compute-v1:targetHttpProxies",
            'properties' : {
                'protocol' : "HTTP",
                'urlMap' : "$(ref.%s-loadbalancer.selfLink)" % deployment
            }
        },
        {
            'name' : "%s-forwarding-rules" % deployment,
            'type' : "gcp-types/compute-v1:forwardingRules",
            'properties' : {
                'IPAddress' : "$(ref.%s-loadbalancer-ip.selfLink)" % deployment,
                'IPProtocol' : "TCP",
                'networkTier' : "STANDARD",
                'portRange' : 80,
                'region' : region,
                'target' : "$(ref.%s-loadbalancer-target-proxy.selfLink)" % deployment
            }
        }
    ]

    return { 'resources' : resources }
