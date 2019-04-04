# quickstart-sas-viya-gcp

Google Cloud Platform Quick Start development repository for Viya


** HARD HAT AREA: This section is under construction. **

Deploying Quick Start for SAS Viya from Google Cloud CLI environment
    
    *PREREQ: Google Cloud SDK.  
    Install and initialize the Google Cloud SDK for your environment 
    by following the instructions found here: 
    https://cloud.google.com/sdk/docs/quickstarts
     
     
    Run the following commands in a terminal with Google Cloud CLI
    configured.
    - Clone github repo: (using develop branch until initial pull to master)
        git clone https://github.com/sassoftware/quickstart-sas-viya-gcp -b develop

    - Before you can deploy the Quick Start templates you need to 
      modify the following config file with your specific values.
        - File: templates/sas-viya-config.yaml
            - zone: Update which zone you want to deploy to. ex. us-east1-b  
              For a list of availale zones run:
              gcloud compute zones list
            - ssh-key: Enter your SSH PUBLIC KEY.  This will get added 
              to the authorized_keys file on all VMs created by this 
              Quick Start so you connect using ssh.
            - OLCROOTPW and OLCUSERPW: passwords.
              Used for initial identity for SAS Viya adminuser and sasuser
            - DEPLOYMENT_DATA_LOCATION:
              
        (Optional)
        - File: templates/vms.jinja
            - machineType: This is set to minimum configuration for each VM.  
              For a complete list of machines available run: 
              gcloud compute machine-types list
            
    - To deploy templates run the following command where STACK represents
      the name of your deployment:  
        gcloud deployment-manager deployments create STACK --config <PATH to quickstart-sas-viya-gcp/templates>/sas-viya-config.yaml --automatic-rollback-on-error
    
    
    To connect to your deployment, open a terminal with Google Cloud CLI.
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


    To delete an existing deployment
    - Run the following command where STACK represents the 
      name of your deployment:  
        gcloud deployment-manager deployments delete STACK
    