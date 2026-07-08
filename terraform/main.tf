terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.53.0"
    }
  }
}

provider "aws" {
  # Configuration options
  region = var.region
}    

resource "aws_s3_bucket" "test_terraform" {
  bucket = var.bucket_name

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}

resource "aws_glue_catalog_database" "test_terraform_dataset" {
  name = var.glue_catalog_name
}