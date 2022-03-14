
# IaC (Infrastructure as Code)

This module is responsible to create required Google Cloud resources that are needed for the project.
Unfortunately, yet the whole resource creation is not automated and some resources needs to be created in advance manually.
## Prerequsite Manual Steps for Resource Creation
0. Create an account GCP account with Google Email
1. Create GCP Project in GCP Console (note the unique project id)
2. Create GCP Service Account
    2.1. Grant Owner role 
    2.2. Download service-account-keys (.json) for authentication
3. Enable  *Cloud Resource Manager API* for the project
4. Create GCS bucket with name *dtc_capstone_terraform_state* to store & version terraform-state files. (suggested to enabkle object versioning)

## Local Development
0. Download [SDK](https://cloud.google.com/sdk/docs/quickstart) for local setup
1. Set environment variable to point to your downloaded GCP keys:`
    ```shell
    export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json"
   ```
2. Refresh token/session, and verify authentication
   ```shell
   gcloud auth application-default login
   ```
3. Initialize state file (.tfstate)
    ```shell
    terraform init
    ```
4. Run one of the terraform commands
   ```shell
   <!-- Plan the resource changes-->
   terraform plan   
   <!-- Create new resources-->
   terraform apply
    <!-- Delete resources-->
   terraform desytoy

## CI/CD Development
1. To be able to automate resource creation and deletion in GCP, we need to authenticate the Github Actions therefore copy the the content of `"<path/to/your/service-account-authkeys>.json"` and create a GitHub Secret `GCP_SA_KEY`. This secret will be used as part of *Auth GCP Service Account* step in `.github/workflows/infrastruce-apply.yaml` and `.github/workflows/infrastruce-destroy.yaml`

# todo & questions:
1. [try keylesss authentication](https://cloud.google.com/blog/products/identity-security/enabling-keyless-authentication-from-github-actions)
2. Automate project and service account creation -> (How to access service account keys in github actions)
3. Seperate service accounts and permissions..
4. Q: Create terraform-state bucket automated way (only one time, is automation really needed)
5. Q: github actions, seperate gcp and terraform setup in different jobs?
6. Q: default.tfstate in the gcp bucket?


# Resources:
- [Automating Terraform with GitHub Actions](https://blog.searce.com/automating-terraform-with-github-actions-5b3aac5abea7)
- [Automating Terraform Deployment to Google Cloud with GitHub Actions](https://medium.com/interleap/automating-terraform-deployment-to-google-cloud-with-github-actions-17516c4fb2e5)
- [Automate Infrastructure Provisioning Workflows with the GitHub Action for Terraform](https://www.hashicorp.com/blog/automate-infrastructure-provisioning-workflows-with-the-github-action-for-terraform)

