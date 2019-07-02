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
            'name': "{}-sslcert".format(deployment),
            'type': "gcp-types/compute-v1:sslCertificates",
            'properties': {
                'certificate': '-----BEGIN CERTIFICATE-----\nMIIDATCCAemgAwIBAgIJAOg1L49MrFLrMA0GCSqGSIb3DQEBCwUAMBcxFTATBgNV\nBAMMDHNhc0luc3RhbGxDQTAeFw0xOTA0MTcxMjQ2MDlaFw0yOTA0MTQxMjQ2MDla\nMBcxFTATBgNVBAMMDHNhc0luc3RhbGxDQTCCASIwDQYJKoZIhvcNAQEBBQADggEP\nADCCAQoCggEBANPUy02Nym4yyoAamPoYE9LJ+f6LMnediVPLkFWTnW/kDieIST6d\nyUDaVnGJQxgubhyEk6L1ci96HhmRMtyOmxT6CNyQBiYUin549N4B5upLTKpOgtzH\ngNVXd+Nmgti3XNAenQ2Sl7HcPsrYvVTrUUWHyHBzcOC1Ta0BfnP2UMS87sgeMi3m\nDpebW1jQrpNLtfiD4OK+86SwJbzzpXawdY93hZkaNrXehOZY0q6Bj2/XcUY4jtmc\nSShanCcWDXvmyEYH7aGasAXigMbwG5zkour3wcI+bSQ7QU+m+edw3HJfoSJyUstK\nlh1ovZfF4gKBuiVBEaw277u9YzK9KOd1AEcCAwEAAaNQME4wHQYDVR0OBBYEFPZd\n5/5JRRswuKTSuWFsqjvzpbn3MB8GA1UdIwQYMBaAFPZd5/5JRRswuKTSuWFsqjvz\npbn3MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBADwqQoQ62X6GSBiB\nsG+H3Y3ZWJVUJ/vrpEDpbzdaDfL4uu79jF/jbSyhqZKihu8ltOQRTFhWGG+pruml\nMwuxPWipzCth4wLFAzOg+JDuXNOY8gJfcf+q/LKhzujBVmbJWD02AB1QY8GvbQt5\nG8kAkdlCg+Oj13tTfI93A4cEmm3GxiJsELLV0TUlERBFPEb3ghWC6gdleIdCUeYt\nkuDfBN+9HufTo3qPXi4LUVM/dWQbMgPVq2aGufwwOK0kr1gUg2Rn+WaVe76b62LB\npd9FXX4pZ1Bktj5dC6C++5enKR7PdgkFtJc3L+1h1BZ9BcXZNQ0XZ+eS8SAoibRU\nJ6rjZKI=\n-----END CERTIFICATE-----\n',
                'privateKey': '-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDT1MtNjcpuMsqA\nGpj6GBPSyfn+izJ3nYlTy5BVk51v5A4niEk+nclA2lZxiUMYLm4chJOi9XIveh4Z\nkTLcjpsU+gjckAYmFIp+ePTeAebqS0yqToLcx4DVV3fjZoLYt1zQHp0Nkpex3D7K\n2L1U61FFh8hwc3DgtU2tAX5z9lDEvO7IHjIt5g6Xm1tY0K6TS7X4g+DivvOksCW8\n86V2sHWPd4WZGja13oTmWNKugY9v13FGOI7ZnEkoWpwnFg175shGB+2hmrAF4oDG\n8Buc5KLq98HCPm0kO0FPpvnncNxyX6EiclLLSpYdaL2XxeICgbolQRGsNu+7vWMy\nvSjndQBHAgMBAAECggEATxBUlWy/yqPAe1HyGR6Vf46NdZlky8qL8C/Bfn9rOtEH\nC3BNzkY8UK1tqFDQLx1dUd2V8TPlW50b0PUl47aCYbD1T8Wd1ebCznO9CYPyOS7D\nvakyJM994aMVB1ZCrjq6NJ/IhMFbRzJqaXG+MQznt6j3gilET0q8ZD9zgDrGaLdi\nD3dNFbTC7yKJUseyvkPUQZtHA8uFGSIJVsu8tM2J5hVFOTsY0rlteMPSQ4mTaX+0\np27BPJIcgUpCbOLtoskJ8xrYwMvVnNh0hipttxwhzWSleOBgRA5Jr2RuNqgx/pm7\nlJh8uAR2naXG09olpg2LPWKyGhYbPRUcXuK+kfe/0QKBgQDu/P5Wm9Mi0aJTokKa\n4OzWEr3C9PXZ413d+euNWA9V/C6/UpixaDV+d+S7NKSiBpqSMPqU+3I3+RClKSvs\nFqQONVrJ6cPxX+SaR2HmaixMsHpx+zJyOErL+vog+EYp2h0+QncinlLPuFOgp35Q\n9Xi/GMMHgVglUJg6j2me7EtneQKBgQDi6O1C0xPd3Za7Z6IlAd9ASsBSqhlCD91X\nwU3STuT0SxyIdclN0QBb3Ebej2R6l36iyfq6MQRj2T4u+JV36wEkNMZCL/UR4o5F\nH0BNhm0EPDN/txPsDlAoqa+1abcTr8dJmNMZ+7RGg5ieidpEySR4iFU6pYZ/yTzx\nQP1u84z1vwKBgQDqeyVceqTsm7xlzGUHKrqUy2yOFOQG9TMK8QPw+T6KwdRn+TVB\nkxoxTJcKKnuBUXNlDlM9y3tkeaWgNsYWbJxoKGc8hnSupcRYrsLaXL+8OsbYgHsd\nYCfa/RNfN9k3hP5+MJ5NRAPCNHswvEWOT1o6PKRV/80pR2skwcMCn5rYGQKBgGdt\nJDhBXdzTE9F3+0BDCi+T4vXK8phaAtntEju6GkH/upG4nnkJutAkJ2lqkrIOO3qX\n9eDIVufsLZvbUsXGKE8IfxXMJjhwu8hl5jlv/GDhz9d26229WGwwbBaUiQ5AIOY6\n8n31bMZ3VSluTD7uL+GAwthoelXktBKDPQFFogqhAoGBAKYs2DVBvaZO/fSCbprE\nlhK6dVuCBo7sWuBiOtKj0jW4tAHc2bWfyc509EjktbdbKc8p6vXbcOHHxYnf11it\nMGXvSJP4VWcMUERGHwK0luP11h5K9f6nAXeYoJ58ZFbyQCqjKLpnnPgwsz2LlKyY\n+h4DthclV8Rfw0ncgRqhHtpv\n-----END PRIVATE KEY-----',
            }
        },
        {
            'name': "{}-loadbalancer-target-proxy".format(deployment),
            'type': "gcp-types/compute-v1:targetHttpsProxies",
            'properties': {
                'protocol': "HTTPS",
                'sslCertificates': [
                    "$(ref.{}-sslcert.selfLink)".format(deployment)
                    # "global/sslCertificates/viya-sslcert"
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
