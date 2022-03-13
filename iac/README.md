
# IaC (Infrastructure as Code)

This module is responsible to create required Google Cloud resources that are needed for the project.
Unfortunately, yet the whole resource creation is not automated and some actions need to be taken manually before running the project workflow.

# Prerequsite Manual Steps
1. Create GCP Project
2. Create GCP Service Account
3. Enable  *Cloud Resource Manager API* for the project
4. Download Service Account Key
5. Save credentials in Github Secrets
    5.1. GCP_SA_EMAIL
    5.2. GCP_SA_KEY
6. Create bucket name *dtc_capstone_terraform_state* to store terraform-state files.


# todo:
1. [try keylesss authentication](https://cloud.google.com/blog/products/identity-security/enabling-keyless-authentication-from-github-actions)
2. Seperate service accounts and permissions..
2. Automate service account creation ? -> How to access service account keys in github actions
3. Is it possible to create terraform-state bucket in advance
4. github actions, seperate gcp and terraform setup in different jobs?


# Resources:
- [Automating Terraform with GitHub Actions](https://blog.searce.com/automating-terraform-with-github-actions-5b3aac5abea7)
- [Automating Terraform Deployment to Google Cloud with GitHub Actions](https://medium.com/interleap/automating-terraform-deployment-to-google-cloud-with-github-actions-17516c4fb2e5)
- [Automate Infrastructure Provisioning Workflows with the GitHub Action for Terraform](https://www.hashicorp.com/blog/automate-infrastructure-provisioning-workflows-with-the-github-action-for-terraform)

