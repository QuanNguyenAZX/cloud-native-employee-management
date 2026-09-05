# Terraform Infrastructure

## Architecture

This project uses Terraform to provision AWS infrastructure.

## Environments

- dev
- prod

## Modules

- VPC
- Security Group
- EC2
- RDS
- S3

## AWS Infrastructure

### VPC

- CIDR: 10.0.0.0/16
- 2 public subnets
- 2 private subnets
- Internet Gateway
- Public route table

### Compute

- EC2
- Instance type: t3.micro
- Ubuntu 24.04

### Database

- PostgreSQL
- RDS
- Private subnet
- Port: 5432

### Storage

- S3
- Versioning enabled
- Server-side encryption enabled
- Public access blocked

## State

Terraform state is stored remotely in Amazon S3.

## Commands

```bash
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply