## SAS Viya Quickstart Template for Google Cloud Platform 

**Note**: Currently, SAS Viya has no license agreement with Google.  Therefore, there is no contractual support from Google. You are responsible for the costs of the resources that are consumed by your deployment. 

This README for  SAS Viya Quickstart Template for Google Cloud Platform (GCP) is used to deploy the following SAS Viya products in the GCP cloud: 

  

* SAS Visual Analytics 8.3.1 on Linux 

* SAS Visual Statistics 8.3.1 on Linux 

* SAS Visual Data Mining and Machine Learning 8.3.1 on Linux 

  

This Quickstart is a reference architecture for users who want to deploy the SAS platform, using microservices and other cloud-friendly technologies. By deploying the SAS platform in GCP, you get SAS analytics, data visualization, and machine-learning capabilities in a GCP-validated environment. 

## Contents
1. [Solution Summary](#Summary)
    1. [Costs and Licenses](#Costs)
1. [Prerequisites](#Prerequisites)
1. [Deployment Steps](#Deployment)
1. [Additional Deployment Details](#deploydetails)
   1. [User Accounts](#useraccounts)
   1. [Monitoring the Deployment](#depmonitoring)
1. [Optional Post Deployment Steps](#postDeployment)
   1. [Replace Self-Signed Certificate with Custom Certificate](#certificate)
1. [Usage](#usage)
1. [Configuration File](#configFile)
   1. [Parameters](#parameters)
   1. [Path to SAS License Zip File](#zipfilepath)
1. [Troubleshooting](#Tshoot)
   1. [Review the Log Files](#reviewLogs)
   1. [Restarting the Services](#restartServices)
   1. [Useful Google Cloud CLI Troubleshooting Commands](#tsCommands)
1. [Appendix A: Setting Up a Mirror Repository ](#AppendixA)
1. [Appendix B: Managing Users for the Provided OpenLDAP Server](#AppendixB)
   

<a name="Summary"></a>
## Solution Summary 

By default, Quickstart deployments enable Transport Layer Security (TLS) for secure communication. 

  

This SAS Viya Quickstart Template for GCP will take a generic license for SAS Viya and deploy SAS into its own network. The deployment will create the network and other infrastructure.  After the deployment process completes, you will have the outputs for the web endpoints for a SAS Viya deployment on recommended virtual machines (VMs).  

  

When you deploy the Quickstart with default parameters, the following SAS Viya environment is built in the GCP cloud: 

  

![Network Diagram](/images/GCP_Topology.jpg) 

  

For details, see [SAS Viya 3.4 for Linux: Deployment Guide](https://go.documentation.sas.com/?docsetId=dplyml0phy0lax&docsetTarget=titlepage.htm&docsetVersion=3.4&locale=en). 

<a name="Costs"></a>
### Costs and Licenses 

You are responsible for the cost of the GCP services used while running this Quickstart deployment. There is no additional cost for using the Quickstart. 

You will need a SAS license to launch this Quickstart. Your SAS account team and the SAS Enterprise Excellence Center can advise on the appropriate software licensing and sizing to meet workload and performance needs. 

SAS Viya Quickstart Template for GCP creates three instances, including:  

* 1 compute virtual machine (VM), the Cloud Analytic Services (CAS) controller 

* 1 VM for administration, the Ansible controller 

* 1 VM for the SAS Viya services 

**Note:** Resource costs vary by region. See ["Cloud Storage Pricing"](https://cloud.google.com/storage/pricing#price-tables) for additional information about pricing. 

<a name="Prerequisites"></a> 
## Prerequisites 

Before deploying SAS Viya Quickstart Template for GCP, you must have the following: 

* GCP user account 
* Access to a GCP project 

* A SAS Software Order Confirmation Email that contains supported Quickstart products: 

  

        SAS Visual Analytics 8.3.1 on Linux 

        SAS Visual Statistics 8.3.1 on Linux 

        SAS Visual Data Mining and Machine Learning 8.3.1 on Linux 

*  The license file in .zip format (attached to your Software Order Email) available in a storage bucket from your GCP project. The storage bucket must be in the same project as your deployment. See  ["Creating Storage Buckets"](https://cloud.google.com/storage/docs/creating-buckets) and ["Uploading Objects"](https://cloud.google.com/storage/docs/uploading-objects) for more information.


<a name="Deployment"></a> 

## Deployment Steps 

1. Install the Google Cloud SDK by following the instructions [here](https://cloud.google.com/sdk/docs/quickstarts). 

The *gcloud* command-line tool *(gcloud CLI)  is downloaded with the Google Cloud SDK. See ["What is the gcloud command-line tool?"](https://cloud.google.com/sdk/gcloud/) for more information.


 

2. Clone the github repository.  From a terminal with the gcloud CLI configured, run the following command: 

``` 
git clone https://github.com/sassoftware/quickstart-sas-viya-gcp -b develop 
  ```
 

3. Modify  the following configuration file with values that are specific to your deployment:
/\<path to quickstart-sas-viya-gcp\>/templates/sas-viya.config.yaml

See ["Configuration File"](#configFile) for more information.


4. Deploy the template. 

**Note:** The deployment name (*deployment* in the sample command below) must be all lowercase and begin with a character from *a* to *z*.

From a terminal with the gcloud CLI configured, run the following command:
```
gcloud deployment-manager deployments create deployment --config <path to quickstart-sas-viya-gcp/templates>/sas-viya-config.yaml --async
```

The deployment takes between 1 and 2 hours, depending on the quantity of software licensed. 
For information about how to monitor the deployment, see ["Additional Deployment Details"](#deploydetails). 

<a name=deploydetails></a>
## Additional Deployment Details

<a name="useraccounts"></a> 
### User Accounts
The *sasinstall* host operating system account is created during deployment. Use this account to log in via SSH to any of the machines.

The *sasadmin* and *sasuser* SAS Viya user accounts are also created during deployment.  These accounts exist in LDAP, and are the default user accounts for logging in to SAS Viya.  You cannot directly log on to the host operating system with these accounts.

**Note:** The passwords for the *sasadmin* and *sasuser* SAS Viya user accounts are specified in the *SASAdminPass* and *SASUserPass* variables within the [configuration file](#configFile). These passwords are displayed on the GCP Deployment Manager page that is only accessible to users with specific GCP permissions. If you are concerned that this is a security risk, you should change these passwords after the deployment. See ["Change a Password or Set the Password for a New User"](#passwordmgmt) for more information.

<a name="depmonitoring"></a> 
### Monitoring the Deployment

To monitor your deployment:
*  Log in to the Ansible controller to monitor the deployment log messages in real time. 

1. Log in to the GCP console [here](https://console.cloud.google.com/) with the correct Google account, and connect to the project that is associated with your deployment.
2. From the *Navigation Menu* at the top left, click *Compute Engine* and then *VM instances*.
3. Click the Ansible controller that is associated with your deployment.
4. From the "Logs" section, click on "Serial port 1 (console)".
5. You will see the log in real time from the Ansible controller.  Click *REFRESH* from the top to reload the log.

*  Check the resources that are deployed from the Deployment Manager window.

1. Log in to the GCP console [here](https://console.cloud.google.com/) with the correct Google account, and connect to the project that is associated with your deployment.
2. From the *Navigation Menu* at the top left, click *Deployment Manager* and then *Deployments*.
3. Click on your deployment.
4. You will see a list of the resources that are installed with your deployment. Click on each resource to get detailed property information.

*  Verify that you can log on to SAS Viya from the load balancer IP address.

1. Log in to the GCP console [here](https://console.cloud.google.com/) with the correct Google account, and connect to the project that is associated with your deployment.
2. From the *Navigation Menu* at the top left, click *Network services* and then *Load balancing*.
3. Click on *advanced menu* at the bottom of the list of load balancers.
4. Click the IP address associated with the load balancer from your deployment.
5. You should see a SAS log on screen.  Confirm that you can log on to SAS Viya as the *sasadmin* or *sasuser*. Use the password that you specified in the sas-viya.config.yaml configuration file.

<a name=postDeployment></a>
## Optional Post Deployment Steps

<a name=certificate></a>
## Replace Self-Signed TLS Certificate with Custom Certificate
To replace the default self-signed certificate with your own self-signed certificate:
1. Upload your self-signed certificate files to the Ansible controller VM by running the following commands from a terminal with the gcloud CLI installed:
```
 gcloud compute scp --ssh-key-file <path to ssh private key> <selfsigned.crt> sasinstall@<DEPLOYMENT>-ansible-controller:<path>
 gcloud compute scp --ssh-key-file <path to ssh private key> <private.key> sasinstall@<DEPLOYMENT>-ansible-controller:<path>
 ```
 2. Connect to the Ansible controller VM:
 ```
  ssh -i <path to ssh private key> sasinstall@<DEPLOYMENT>-ansible-controller
  ```
  3. Run the following commands to replace the default self-signed certificate with your own self-signed certificate:
  ```
  export DEPLOYMENT=<Deployment name>
  export PROJECT=<GCP Project name>
  gcloud compute ssl-certificates create $DEPLOYMENT-sslcert-tmp --certificate <path to crt file>/selfsigned.crt --private-key <path to key file>/private.key
  gcloud compute target-https-proxies update $DEPLOYMENT-loadbalancer-target-proxy --ssl-certificates=https://www.googleapis.com/compute/v1/projects/$PROJECT/global/sslCertificates/$DEPLOYMENT-sslcert-tmp
  gcloud compute ssl-certificates delete $DEPLOYMENT-sslcert --quiet
  gcloud compute ssl-certificates create $DEPLOYMENT-sslcert --certificate <path to crt file>/selfsigned.crt --private-key <path to key file>/private.key
 gcloud compute target-https-proxies update $DEPLOYMENT-loadbalancer-target-proxy --ssl-certificates=https://www.googleapis.com/compute/v1/projects/$PROJECT/global/sslCertificates/$DEPLOYMENT-sslcert
 cloud compute ssl-certificates delete $DEPLOYMENT-sslcert-tmp --quiet
 ```

<a name=usage></a>
## Usage
To connect to the SAS Viya login page:
1. Log in to the GCP Console [here](https://console.cloud.google.com/).
2. Ensure that you are logged in to the correct Google account.
3. Ensure that you are connected to the project that is associated with your deployment.
4. From the *Navigation Menu* at the top left, click *Network Services* and then *Load balancing*.
5. Click the *Advanced menu* link at the bottom of the list of load balancers.
6. Click on the address associated with your deployment from the *Forwarding rules* tab to open the SAS Viya login page. 

<a name=configFile></a>
## Configuration File

<a name=parameters></a>
### Parameters
You must modify the configuration file, /\<path_to_quickstart-sas-viya-gcp\>/templates/sas-viya-config.yaml, with values that are specific to your deployment. The parameters in the file are as follows:

|Parameter Name|Description|
|--------------|-----------|
|AnsibleControllerMachineType|Defines the Ansible Controller machine type in GCP.
|ServicesMachineType|Defines the SAS Viya Services machine type in GCP.
|ServicesDiskSize|Defines the SAS Viya Services boot disk size in GCP (minimum required is 25GB).
|ControllerMachineType|Defines the CAS Controller machine type in GCP.
|SSHPublicKey|Specifies your SSH public key.  This will get added to the authorized_keys file on the Bastion host so that you can connect using ssh.
|SASAdminPass|Specifies the password for the SAS Viya adminuser. Used for the initial identity for the SAS Viya adminuser.
|SASUserPass|Specifies the password for the SAS Viya sasuser. Used for the initial identity for the SAS Viya sasuser.
|DeploymentDataLocation|Specifies the GCP bucket location of the SAS license zip file (for example, gs://\<bucket name\>/\<path\>/\<filename\>.zip). See ["Path to SAS License Zip File"](#zipfilepath) for more information.
|AdminIngressLocation|Specifies the CIDR address range for machines that can access the Bastion host.
|WebIngressLocation|Specifies the CIDR address range for machines that can access the SAS Viya HTTP(S) server.

<a name=zipfilepath></a>
### Path to SAS License Zip File 
The DeploymentDataLocation parameter refers to the path to the SAS license zip file that was included with the Software Order Email (SOE), and subsequently uploaded to a storage bucket. You need the name of the bucket as well as any embedded folders (if any) to construct the path to the SAS license zip file. 
The path consists of the following:
```
gs://<bucket_name>/<path>/<license_file>.zip
```
To verify the path:
1. Click [here](https://console.cloud.google.com/projectselector2/storage/browser?_ga=2.254580111.-645135131.1554401290&supportedpurview=project) to open the Google Storage browser from the GCP console.
2. Ensure that you are logged in to the correct Google account.
3. Choose the project that contains the bucket with the license zip file. You should see a table with any buckets that are in the project.
4. From the buckets list, click on the bucket with the license zip file.
5. Click on any embedded folder(s) within the bucket to navigate to the license zip file.
6. When you are at the level of the license zip file itself, you should see a table that contains the license zip file. Above the table on the left, note the word *Buckets*. To the right of the word *Buckets*, you will see the bucket name and path to the license zip file. For example, the line above the table with the license zip file might appear as follows:
```
Buckets / testbucket-deployment-data/ viya3.4
```
In this example, the bucket name is *testbucket-deployment-data*, the path is *viya3.4*, and suppose that the license zip file is named *SAS_Viya_deployment_data.zip*.
Therefore, the value of the DeploymentDataLocation parameter would be the following:
```
gs://testbucket-deployment-data/viya3.4/SAS_Viya_deployment_data.zip
```

<a name="Tshoot"></a> 
## Troubleshooting
<a name="reviewLogs"></a>
### Review the Log Files

#### Deployment Logs

The following deployment logs are located in the /var/log/sas/install directory on the Ansible controller instance:
* prepare_nodes.log - Ansible logs for instance preparation
* openldap.log - Ansible logs for the OpenLDAP installation and configuration (if chosen)
* prepare_deployment.log - Ansible logs for SAS Viya deployment preparation steps
* virk.log - Ansible logs for the Viya-Ark pre-deployment node preparation playbook
* viya_deployment.log- Ansible log for SAS Viya main deployment
* post_deployment.log - Ansible logs for additional steps after the main deployment

#### SAS Viya Microservice Logs
The logs for SAS Viya microservices are located in the /var/log/sas/viya directory on the SAS Viya services instance.

<a name="restartServices"></a>
         
### Restarting the SAS Services
With some older licenses, some services might not be fully started after a full deployment. If
you receive a connection error when you connect to SASHome or SASDrive, you must
restart the services.

#### Checking the Status of the SAS Services through Viya-Ark
Viya-Ark can check the status of the services by issuing the following commands as the sasinstall user on the Ansible controller instance:
```
cd /sas/install/ansible/sas_viya_playbook
export ANSIBLE_CONFIG=`pwd`
ansible-playbook viya-ark/playbooks/viya-mmsu/viya-servicesstatus.yml
```
<a name="tsCommands"></a>

### Useful Google Cloud CLI Troubleshooting Commands
In the event of a deployment failure, take the following into consideration:

#### Receiving Waiter Failure Message
Here is an example of an error message that results from a waiter failure:
```
 {"ResourceType":"gcp-types/runtimeconfig-v1beta1:projects.configs.waiters","ResourceErrorCode":"412","ResourceErrorMessage":"Failure condition satisfied."}
 ```
 In the event of a waiter failure, run the following command:
```
gcloud beta runtime-config configs variables list --config-name <deployment>-deployment-waiters --values --format json
```
#### Check for Error in Console serial-port-output
1. Run this command from a terminal with the gcloud CLI installed:

```
gcloud compute instances get-serial-port-output <deployment>-ansible-controller --zone=$ZONE --project=$PROJECT
```

2. Look for **Error** in the output associated with a specific message.

3. Get specific log output related to the error message identified in the last step:

```
 gcloud compute ssh <deployment>-ansible-controller --command 'cat /var/log/sas/install/<log_file_name>.log' --zone $ZONE --project $PROJECT
 ```
 4. If necessary, perform steps 1 through 3 on the CAS controller and SAS Viya services instances, substituting the correct instance name: \<deployment\>-controller or \<deployment\>-services.
 
#### Receiving Timeout When Waiting for File Message
Here is an example of a message that results from a timeout:
```
gcloud compute instances get-serial-port-output <deployment>-<services or controller> --zone=$ZONE --project=$PROJECT
```
In the event of a timeout, run the following command:
```
gcloud compute instances get-serial-port-output <deployment>-<services or controller> --zone=$ZONE --project=$PROJECT
```

<a name="AppendixA"></a>
## Appendix A: Setting Up a Mirror Repository
1. To set up a mirror repository, refer to the instructions in ["Create a Mirror Repository"](https://go.documentation.sas.com/?docsetId=dplyml0phy0lax&docsetTarget=p1ilrw734naazfn119i2rqik91r0.htm&docsetVersion=3.4&locale=en) in the SAS Viya 3.4 for Linux: Deployment Guide.
2. Set up a GCP bucket that is accessible by the account where you deployed the SAS Viya Quick Start.
3. Move the file structure of your mirror repository to the GCP bucket.
4. Upload the mirror repository into your GCP bucket.

To upload the mirror using the GCP command line interface (CLI), run the following command:
```
gsutil rsync -r /path/to/your/local/mirror/sas_repos gs://yourbucket/your/mirror/
```
5. During your GCP Quickstart installation, specify the value for the **DeploymentMirror** parameter as follows:
```
gs://your-bucket/your/mirror/
```
<a name="AppendixB"></a>
## Appendix B: Managing Users for the Provided OpenLDAP Server
### List All Users and Groups
 1. From the Ansible controller VM, log in to the SAS Viya services VM:
 ```
 ssh services.viya.sas
 ```
 2. List all users and groups:
```
ldapsearch -x -h localhost -b "dc=sasviya,dc=com"
```
### Add a User
 1. From the Ansible controller VM, log in to the SAS Viya services VM:
 ```
 ssh services.viya.sas
 ```
2. Create a user file that contains all of the user information:

**Note:** You must increment the UID from the last one displayed by the ldapsearch command.
```
dn: uid=newuser,ou=users,dc=sasviya,dc=com
cn: newuser
givenName: New
sn: User
objectClass: top
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: posixAccount
loginShell: /bin/bash
uidNumber: 100011
gidNumber: 100001
homeDirectory: /home/newuser
mail: newuser@services.viya.sas
displayName: New User  
```
3. Run the following command:
```
ldapadd -x -h localhost -D "cn=admin,dc=sasviya,dc=com" -W -f
/path/to/user/file
```
**Note:** You will be prompted for the admin password (the same one you specified when you created the deployment).

4. To allow the new user to access SAS Viya products, add the user as a member of the sasusers
group by creating an ldif file with the following data:
```
dn: cn=sasusers,ou=groups,dc=sasviya,dc=com
changetype: modify
add: memberUid
memberUid: newuser
-
add: member
member: uid=newuser,ou=users,dc=sasviya,dc=com
ldapadd -x -h localhost -D "cn=admin,dc=sasviya,dc=com" -W -f
/path/to/user/file
```
5. Add the home directories for your new user on the SAS Viya services machine (services.viya.sas)
and the CAS controller machine (controller.viya.sas). From the Ansible controller VM:
```
ssh services.viya.sas
sudo mkdir -p /home/newuser
sudo chown newuser:sasusers /home/newuser
exit
ssh controller.viya.sas
sudo mkdir -p /home/newuser/casuser
sudo chown newuser:sasusers /home/newuser
sudo chown newuser:sasusers /home/newuser/casuser
exit
```
<a name="passwordmgmt"></a>
### Change a Password or Set the Password for a New User

 1. From the Ansible controller VM, log in to the SAS Viya services VM:
 ```
 ssh services.viya.sas
 ```
 2. Run the following command:
 ```
ldappasswd -h localhost -s USERPASSWORD -W -D
cn=admin,dc=sasviya,dc=com -x
"uid=newuser,ou=users,dc=sasviya,dc=com"
```
**Note:** To prevent the command from being saved to the bash history, preface this
command with a space. The string following the -x should match the dn: attribute of
the user.

### Delete a User
 1. From the Ansible controller VM, log in to the SAS Viya services VM:
 ```
 ssh services.viya.sas
 ```
 2. Run the following command: 
```
ldapdelete -h localhost -W -D "cn=admin,dc=sasviya,dc=com"
"uid=newuser,ou=users,dc=sasviya,dc=com"
```


    
