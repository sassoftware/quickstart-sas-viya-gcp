""" Creates the network resources """

def GenerateConfig(context) :

    """ Retrieve the variable values from the context """
    deployment = context.env['deployment']
    region = context.properties['Region']
    admin_ingress_location = context.properties['AdminIngressAccess']
    web_ingress_location = context.properties['WebIngressAccess']
    # allows traffic from both the load balancer and the health checker
    health_check_range1 = "35.191.0.0/16"
    health_check_range2 = "130.211.0.0/22"


    """ Define the network resources """
    resources = [
        {
            'name' : "%s-vpc" % deployment,
            'type' : "gcp-types/compute-v1:networks",
            'properties' : {
                'autoCreateSubnetworks' : False
            }
        },
        {
            'name' : "%s-public-subnet" % deployment,
            'type' : "gcp-types/compute-v1:subnetworks",
            'properties' : {
                'region' : region,
                'ipCidrRange' : "10.0.128.0/20",
                'network' : "$(ref.%s-vpc.selfLink)" % deployment
            }
        },
        {
            'name' : "%s-private-subnet" % deployment,
            'type' : "gcp-types/compute-v1:subnetworks",
            'properties' : {
                'region' : region,
                'ipCidrRange' : "10.20.128.0/20",
                'network' : "$(ref.%s-vpc.selfLink)" % deployment
            }
        },
        {
            'name' : "%s-nat" % deployment,
            'type' : "gcp-types/compute-v1:routers",
            'properties' : {
                'region' : region,
                'network' : "$(ref.%s-vpc.selfLink)" % deployment,
                'nats' : [{
                    'name' : "%s-nat" % deployment,
                    'subnetworks' : [{
                        'name' : "$(ref.%s-private-subnet.selfLink)" % deployment,
                        'sourceIpRangesToNat' : [
                            "ALL_IP_RANGES"
                        ]
                    }],
                    'natIpAllocateOption' : "AUTO_ONLY",
                    'sourceSubnetworkIpRangesToNat' : "LIST_OF_SUBNETWORKS"
                }]
            }
        },
        {
            'name' : "%s-allow-ansible-external-access" % deployment,
            'type' : "gcp-types/compute-v1:firewalls",
            'properties' : {
                'network' : "$(ref.%s-vpc.selfLink)" % deployment,
                'sourceRanges' : [
                    admin_ingress_location
                ],
                'allowed' : [{
                    'IPProtocol' : "tcp",
                    'ports' : [
                        22
                    ]
                }]
            }
        },
        {
            'name' : "%s-allow-viya-ssh-from-ansible" % deployment,
            'type' : "gcp-types/compute-v1:firewalls",
            'properties' : {
                'network' : "$(ref.%s-vpc.selfLink)" % deployment,
                'sourceTags' : [
                    "sas-viya-ansible-controller"
                ],
                'allowed' : [{
                    'IPProtocol' : "tcp",
                    'ports' : [
                        22
                    ]
                }]
            }
        },
        {
            'name' : "%s-allow-viya-to-viya" % deployment,
            'type' : "gcp-types/compute-v1:firewalls",
            'properties' : {
                'network' : "$(ref.%s-vpc.selfLink)" % deployment,
                'sourceTags' : [
                    "sas-viya-vm"
                ],
                'allowed' : [{
                    'IPProtocol' : "tcp"
                }]
            }
        },
        {
            'name' : "%s-vpc-allow-http" % deployment,
            'type' : "gcp-types/compute-v1:firewalls",
            'properties' : {
                'description' : "Incoming http and https allowed.",
                'network' : "$(ref.%s-vpc.selfLink)" % deployment,
                'sourceRanges': [
                    web_ingress_location,
                    health_check_range1,
                    health_check_range2,
                ],
                'targetTags' : [
                    "sas-viya-vm"
                ],
                'allowed' : [{
                    'IPProtocol' : "tcp",
                    'ports' : [
                        80,
                        443
                    ]
                }]
            }
        }
    ]

    return { 'resources' : resources }
