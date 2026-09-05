variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-1"
}

variable "db_password" {
  description = "Password for RDS PostgreSQL"
  type        = string
  sensitive   = true
}

variable "ssh_cidr" {
  description = "CIDR allowed to access EC2 via SSH"
  type        = string
}