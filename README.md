# quickstart-sas-viya-gcp
Google Cloud Platform QuickStart development repository for Viya

** HARD HAT AREA: This section is under construction. **

Deploying Quick Start for SAS Viya from Google Cloud CLI environment
    
    *PREREQ: Google Cloud SDK.  
    Install and initialize the Google Cloud SDK for your environment 
    by following the instructions found here: https://cloud.google.com/sdk/docs/quickstarts
     
     Run the following commands in a terminal with Google Cloud CLI
     configured.
    - Clone github repo:
        git clone https://github.com/sassoftware/quickstart-sas-viya-gcp -b dev-develop
        
    - Run the following command where STACK represents the 
      name of your deployment:  
        gcloud deployment-manager deployments create STACK --config quickstart-sas-viya-gcp/templates/sas-viya-config.yaml --automatic-rollback-on-error
    
    
    To delete existing deployment
    - Run the following command where STACK represents the 
      name of your deployment:  
        gcloud deployment-manager deployments delete STACK
