variable "name" {
  description = "Name prefix for security groups"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where security groups will be created"
  type        = string
}

variable "ssh_cidr" {
  description = "CIDR allowed to access EC2 via SSH"
  type        = string
}