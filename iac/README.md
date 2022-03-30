
# IaC (Infrastructure as Code)

This module is responsible to create required Google Cloud resources that are needed for the project.
Unfortunately, yet the whole resource creation is not automated and some resources needs to be created in advance manually. Therefore regardless of local or cicd development options the steps in [Prerequsite Manual Steps section](#prerequsite-manual-steps-for-resource-creation) are necessary.
## 0. Prerequsite Manual Steps for Resource Creation
0. Create an account GCP account with Google Email
1. Create GCP Project in GCP Console (note the unique project id)
2. Create GCP Service Account
    2.1. Grant Owner role
    2.2. Download service-account-keys (.json) for authentication
3. Enable  *Cloud Resource Manager API* for the project
4. Create GCS bucket with name *dtc_capstone_terraform_state* to store & version terraform-state files. (suggested to enabkle object versioning)

## Development Options
---
## Local Development
0. Download [SDK](https://cloud.google.com/sdk/docs/quickstart) for local setup
1. Set environment variable to point to your downloaded GCP keys:`
    ```shell
    export GOOGLE_APPLICATION_CREDENTIALS="<./.google/credentials/service-account-authkeys>.json"
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
   terraform destroy

## CI/CD Development
To be able to automate resource creation and deletion in GCP, we need to authenticate the Github Actions.
There is Action [google-github-actions/auth](https://github.com/google-github-actions/auth) that establish authentication to google cloud in two different approach.

Caution: Both of the steps below, assume that, the resources mentioned in [Prerequsite Manual Steps part](#0-prerequsite-manual-steps-for-resource-creation) are created and exist.

---
**[Option 1] Traditional Service Account Key Approach**

 To enable authentication, the the content of `"<./.google/credentials/service-account-authkeys>.json"` should be copied and create a GitHub Secret `GCP_SA_KEY`.
 After the secret saved, the setup for authentication and the secret usage can be seen as part of *Auth GCP Service Account* step in `.github/workflows/infrastruce-destroy.yaml`

 ---
**[Option 2] Keyless Auth via Workload Identity Federation**

Keyless Authentication approach requires creation of additional resources in Google Cloud. To ease the process, i have created a go file which enable you to create all additional resources and assoications through the console.
```shell
./go create_workload_identity_pool <project-name>
./go create_workload_identity_provider <project-name>
./go associate_service_account_2_workload_identity_pool <project_name> <service_account> <workload_identity_pool_id>
```
After resources created, the setup for authentication can be seen as part of *Auth GCP Service Account* step in `.github/workflows/infrastruce-apply.yaml`. Detailed explanation for setting up workload identity federation, can be read through [setup](https://github.com/google-github-actions/auth#setting-up-workload-identity-federation) and [troubleshooting](https://github.com/google-github-actions/auth/blob/db6919d07466cc48f0294f11cd9b28bb8d3130d2/docs/TROUBLESHOOTING.md#troubleshooting)

Additionally, the advantages of Keyless Authentication to Google Cloud can be read in [here](https://cloud.google.com/blog/products/identity-security/enabling-keyless-authentication-from-github-actions)


## Resources:
---
- [Automating Terraform with GitHub Actions](https://blog.searce.com/automating-terraform-with-github-actions-5b3aac5abea7)
- [Automating Terraform Deployment to Google Cloud with GitHub Actions](https://medium.com/interleap/automating-terraform-deployment-to-google-cloud-with-github-actions-17516c4fb2e5)
- [Automate Infrastructure Provisioning Workflows with the GitHub Action for Terraform](https://www.hashicorp.com/blog/automate-infrastructure-provisioning-workflows-with-the-github-action-for-terraform)
