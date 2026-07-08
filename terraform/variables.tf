variable "region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Name of the S3 bucket"
  default     = "vinii-tf-test-bucket-20260708-001"
}

variable "glue_catalog_name" {
  description = "Name of the Glue catalog database"
  default     = "vinii_my_catalog_database"
}