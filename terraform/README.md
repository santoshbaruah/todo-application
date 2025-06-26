# Todo App AWS Infrastructure

This directory contains Terraform scripts to provision the necessary AWS infrastructure to run the Todo application.

## Prerequisites

- [Terraform CLI](https://learn.hashicorp.com/tutorials/terraform/install-cli) installed.
- [AWS CLI](https://aws.amazon.com/cli/) installed and configured with your credentials.

## Architecture

The scripts will provision the following resources:
- A new **VPC** with public and private subnets.
- An **Application Load Balancer** to route traffic.
- **ECS on Fargate** to run the frontend and backend containers.
- **ECR** repositories to store Docker images.
- An **RDS PostgreSQL** instance for the database.
- **IAM roles and Security Groups** for security.

## How to Use

### 1. Initialize Terraform

Navigate to this directory and run:

terraform init


### 2. Plan the Deployment

Run a plan to see what resources will be created. You will be prompted to enter a `db_password`.

terraform plan -out=tfplan

> **Note:** For production, it's recommended to manage secrets using a `.tfvars` file or a secrets manager, rather than entering them on the command line.

### 3. Apply the Configuration

Apply the plan to create the AWS resources:

terraform apply "tfplan"

This process can take several minutes. Once complete, the application URL will be displayed as an output.

### 4. Destroy the Infrastructure

To tear down all the resources created by Terraform, run:

terraform destroy

Type `yes` when prompted to confirm. This will remove all the resources from your AWS account. 