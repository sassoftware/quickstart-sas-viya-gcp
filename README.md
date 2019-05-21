# quickstart-sas-viya-gcp

Google Cloud Platform Quick Start development repository for Viya


** HARD HAT AREA: This section is under construction. **

Deploying Quick Start for SAS Viya from Google Cloud CLI environment
    
- PREREQ: Google Cloud SDK.  
 Install and initialize the Google Cloud SDK for your environment 
 by following the instructions found here: 
 
        https://cloud.google.com/sdk/docs/quickstarts
     
     
- Run the following commands in a terminal with Google Cloud CLI
 configured.  
 Clone github repo: (using develop branch until initial pull to master)
                                       
        git clone https://github.com/sassoftware/quickstart-sas-viya-gcp -b develop

Before you can deploy the Quick Start templates you need to modify the following config file with your specific values.
- File: templates/sas-viya-config.yaml
 
        AdminIngressAccess: CIDR address range for machines that can access the Bastian Host. 
      
        WebIngressAccess: CIDR address range for machines that can access the Viya HTTP(S) server.
      
        Zone: Update which zone you want to deploy to. ex. us-east1-b  
          For a list of availale zones run:
        gcloud compute zones list
      
        SSHPublicKey: Enter your SSH PUBLIC KEY.  This will get added 
        to the authorized_keys file on Bastian Host so you connect using ssh.
      
        SASAdminPass and SASUSerPass: passwords.
        Used for initial identity for SAS Viya adminuser and sasuser
      
        DeploymentDataLocation: Enter the CGP bucket location of the SAS License zip file.
              ex. gs://<bucket name>/<path>/<filename>.zip
              
- (Optional) File: templates/vms.jinja

        machineType: This is set to minimum configuration for each VM.  
    For a complete list of machines available run: 

        gcloud compute machine-types list
            
    - To deploy templates run the following command where STACK represents
      the name of your deployment:
      NOTE: Your deployment name must be all lowercase.  
        gcloud deployment-manager deployments create STACK --config <PATH to quickstart-sas-viya-gcp/templates>/sas-viya-config.yaml --automatic-rollback-on-error
    
      The deployment of Viya takes roughly 2 hours.  You can check the progress by watching the logs in /var/log/sas/install on the ansible-controller machine.
    
- To connect to your deployment, open a terminal with Google Cloud CLI.
    - You will need access to the ssh private key that matches the public key 
      you added to the sas-viya-config.yaml file.
    - To find the EXTERNAL_IP address of your ansible controller VM run:
      gcloud compute instances list
      Look for this instance where STACK is the name of your deployment:
      "STACK-ansible-controller"
    - To connect to your ansible controller VM run:
      ssh -i <PATH TO SSH PRIVATE KEY> sasinstall@<EXTERNAL_IP>
    - After the Quick Start has finished you can ssh to the services
      or controller machines by simply running "ssh services" or 
      "ssh controller" from the STACK-ansible-controller machine.

- To connect the Viya login page:
    - Login into GCP Console https://console.cloud.google.com/
    - Ensure that you are connected to the project associated with your
      deployment.
    - Using the Navagation Menu at the top left go to "Network services"
      and then "Load balancing".
    - From there click on the "advanced menu" link at the bottom of the
      list of Load balancer.
    - Click on the Address associated with your deployment in the
      STACK-forwarding-rules row.
    
 - To delete an existing deployment
    - Run the following command where STACK represents the 
      name of your deployment:
        
            gcloud deployment-manager deployments delete STACK
    
    - Remove service account from deployment. STACK represents
      the name of your deployment and PROJECT represents the name
      of the Google Project that you deployed into.
      NOTE: If you do not remove this service account then future
      deployments of the same STACK name may not have access to GCP 
      resources. This command is sending output to NULL to avoid 
      unnecessarily printing a list of all role bindings in the project. 
      If the command fails for any reason it will print out the error 
      message.
      
            gcloud projects remove-iam-policy-binding PROJECT --member  serviceAccount:STACK-ansible-svc-account@PROJECT.iam.gserviceaccount.com --role roles/storage.objectAdmin 1>/dev/null

    
