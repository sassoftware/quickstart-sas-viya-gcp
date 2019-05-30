# quickstart-sas-viya-gcp

Google Cloud Platform Quick Start for SAS Viya development repository

## HARD HAT AREA: This section is under construction.

Deploying Quick Start for SAS Viya from Google Cloud CLI environment

## Prerequisites
 * [Google cloud SDK](https://cloud.google.com/sdk/downloads)
 * The `Compute Engine API` and the `Cloud Runtime Configuration API` services need to be enabled under the navigation menu `APIs & Services` subitem. Click on "ENABLE APIS AND SERVICES" then type the service names in the filter and enable it.  
 * In a terminal with Google Cloud CLI installed, retrieve the Quick Start for SAS Viya template code. (using develop branch until we push to master)                                
    ```
    git clone https://github.com/sassoftware/quickstart-sas-viya-gcp -b develop
    ```


#### Please review and customize the following fields of templates/sas-viya-config.yaml file first
```yaml
* For a list of available machine types: gcloud compute machine-types list
AnsibleControllerMachineType: Anisible Controller machine type, default listed
ServicesMachineType: Viya Services machine type, default listed
ControllerMachineType: CAS Controller machine type, default listed
 
* For a list of availale zones run: gcloud compute zones list
Zone: Update which zone you want to deploy to. ex. us-east1-b  
 
SSHPublicKey: Enter your SSH PUBLIC KEY.  This will get added to the authorized_keys file on Bastian Host so you connect using ssh.
 
SASAdminPass: password
 
SASUSerPass: password
 
DeploymentDataLocation: Enter the CGP bucket location of the SAS License zip file. ex. gs://<bucket name>/<path>/<filename>.zip
 
AdminIngressLocation: CIDR address range for machines that can access the Bastian Host. x.x.x.x/x format 
  
WebIngressLocation: CIDR address range for machines that can access the Viya HTTP(S) server.  x.x.x.x/x format
```
       
## Deploy templates
 * Run the following command where `STACK` represents the name of your deployment:
    * NOTE: Your deployment name must be all lowercase.  
    ```
    gcloud deployment-manager deployments create STACK --config <PATH to quickstart-sas-viya-gcp/templates>/sas-viya-config.yaml --automatic-rollback-on-error
    ```

 * The deployment of SAS Viya takes roughly 2 hours. 
    
#### To connect to your deployment, open a terminal with Google Cloud CLI.

* You will need access to the ssh private key that matches the public key you added to the sas-viya-config.yaml file.
* To find the EXTERNAL_IP address of your ansible controller VM run:
    ```
    gcloud compute instances list
    ```
Look for this instance where STACK is the name of your deployment:
`STACK-ansible-controller`
* To connect to your ansible controller VM run:
`ssh -i <PATH TO SSH PRIVATE KEY> sasinstall@<EXTERNAL_IP>`
* After the Quick Start has finished you can ssh to the services or controller machines by simply running `ssh services` or 
`ssh controller` from the `STACK`-ansible-controller machine.

To connect the Viya login page:
   * Login to [Google Cloud Console](https://console.cloud.google.com/)
   * Ensure that you are connected to the project associated with your deployment.
   * Using the Navagation Menu at the top left go to "Network services" and then "Load balancing".
   * From there click on the "advanced menu" link at the bottom of the list of Load balancer.
   * Click on the Address associated with your deployment in the `STACK`-forwarding-rules row.
    
## Delete deployment
 * Run the following command where `STACK` represents the name of your deployment:
    ```
    gcloud deployment-manager deployments delete STACK
    ```        


    
