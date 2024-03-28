# aws_s3.py

import boto3
from dotenv import load_dotenv
import os


load_dotenv()

s3 = boto3.resource(
    service_name= os.getenv("AWS_SERVICE_NAME"),
    region_name= os.getenv("AWS_REGION_NAME"),
    aws_access_key_id= os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_ACCESS_KEY_ID")
)
bucket_name = os.getenv("AWS_BUCKET_NAME")


