variable "aws_region" {
  description = "AWS region used by the workshop"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name used to identify the workshop resources"
  type        = string
  default     = "zoomcamp-airflow"
}

variable "bucket_name" {
  description = "Globally unique S3 bucket name"
  type        = string
}