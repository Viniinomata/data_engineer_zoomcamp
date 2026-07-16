output "bucket_name" {
  description = "Name of the workshop S3 bucket"
  value       = aws_s3_bucket.data_lake.bucket
}

output "taxi_data_uri" {
  description = "S3 location for the taxi dataset"
  value       = "s3://${aws_s3_bucket.data_lake.bucket}/taxi-data/"
}