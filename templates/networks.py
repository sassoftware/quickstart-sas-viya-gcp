""" Creates the network resources """


def GenerateConfig(context):
    """ Retrieve the variable values from the context """
    deployment = context.env['deployment']
    region = context.properties['Region']
    admin_ingress_location = context.properties['AdminIngressLocation']
    web_ingress_location = context.properties['WebIngressLocation']
    # allows traffic from both the load balancer and the health checker
    health_check_range1 = "35.191.0.0/16"
    health_check_range2 = "130.211.0.0/22"

    """ Define the network resources """
    resources = [
        {
            'name': "{}-vpc".format(deployment),
            'type': "gcp-types/compute-v1:networks",
            'properties': {
                'autoCreateSubnetworks': False
            }
        },
        {
            'name': "{}-public-subnet".format(deployment),
            'type': "gcp-types/compute-v1:subnetworks",
            'properties': {
                'region': region,
                'ipCidrRange': "10.0.128.0/20",
                'network': "$(ref.{}-vpc.selfLink)".format(deployment)
            }
        },
        {
            'name': "{}-private-subnet".format(deployment),
            'type': "gcp-types/compute-v1:subnetworks",
            'properties': {
                'region': region,
                'ipCidrRange': "10.20.128.0/20",
                'network': "$(ref.{}-vpc.selfLink)".format(deployment)
            }
        },
        {
            'name': "{}-nat".format(deployment),
            'type': "gcp-types/compute-v1:routers",
            'properties': {
                'region': region,
                'network': "$(ref.{}-vpc.selfLink)".format(deployment),
                'nats': [{
                    'name': "{}-nat".format(deployment),
                    'subnetworks': [{
                        'name': "$(ref.{}-private-subnet.selfLink)".format(deployment),
                        'sourceIpRangesToNat': [
                            "ALL_IP_RANGES"
                        ]
                    }],
                    'natIpAllocateOption': "AUTO_ONLY",
                    'sourceSubnetworkIpRangesToNat': "LIST_OF_SUBNETWORKS",
                    'minPortsPerVm': 8000
                }]
            }
        },
        {
            'name': "{}-allow-ansible-external-access".format(deployment),
            'type': "gcp-types/compute-v1:firewalls",
            'properties': {
                'network': "$(ref.{}-vpc.selfLink)".format(deployment),
                'sourceRanges': [
                    admin_ingress_location
                ],
                'allowed': [{
                    'IPProtocol': "tcp",
                    'ports': [
                        22
                    ]
                }]
            }
        },
        {
            'name': "{}-allow-viya-ssh-from-ansible".format(deployment),
            'type': "gcp-types/compute-v1:firewalls",
            'properties': {
                'network': "$(ref.{}-vpc.selfLink)".format(deployment),
                'sourceTags': [
                    "sas-viya-ansible-controller"
                ],
                'allowed': [{
                    'IPProtocol': "tcp",
                    'ports': [
                        22, 8008
                    ]
                }]
            }
        },
        {
            'name': "{}-allow-viya-ping-from-ansible".format(deployment),
            'type': "gcp-types/compute-v1:firewalls",
            'properties': {
                'network': "$(ref.{}-vpc.selfLink)".format(deployment),
                'sourceTags': [
                    "sas-viya-ansible-controller"
                ],
                'allowed': [{
                    'IPProtocol': "icmp",
                }]
            }
        },
        {
            'name': "{}-allow-viya-to-viya".format(deployment),
            'type': "gcp-types/compute-v1:firewalls",
            'properties': {
                'network': "$(ref.{}-vpc.selfLink)".format(deployment),
                'sourceTags': [
                    "sas-viya-vm"
                ],
                'allowed': [{
                    'IPProtocol': "tcp"
                }]
            }
        },
        {
            'name': "{}-vpc-allow-healthcheck".format(deployment),
            'type': "gcp-types/compute-v1:firewalls",
            'properties': {
                'network': "$(ref.{}-vpc.selfLink)".format(deployment),
                'sourceRanges': [
                    health_check_range1,
                    health_check_range2,
                ],
                'targetTags': [
                    "sas-viya-vm"
                ],
                'allowed': [{
                    'IPProtocol': "tcp",
                    'ports': [
                        443
                    ]
                }]
            }
        },
        {
            'name': "{}-vpc-security-policy".format(deployment),
            'type': "gcp-types/compute-v1:securityPolicies",
            'properties': {
                'description': "Enabling IP allow list/deny list for HTTP(S) Load Balancing",
                'rules': [
                    {
                        'action': "deny(403)",
                        'description': "Default rule, higher priority overrides it",
                        'priority': 2147483647,
                        'match': {
                            'versionedExpr': "SRC_IPS_V1",
                            'config': {
                                'srcIpRanges': [
                                    "*"
                                ]
                            }
                        }
                    },
                    {
                        'action': "allow",
                        'description': "Open Ports to CIDR range",
                        'priority': 10,
                        'match': {
                            'versionedExpr': "SRC_IPS_V1",
                            'config': {
                                'srcIpRanges': [
                                    web_ingress_location
                                ]
                            }
                        }
                    }
                ]
            }
        },
    ]

    return {'resources': resources}
