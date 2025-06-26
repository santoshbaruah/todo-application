variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "The name of the project."
  type        = string
  default     = "todo-app"
}

variable "db_username" {
  description = "The username for the RDS database."
  type        = string
  default     = "postgres"
} 