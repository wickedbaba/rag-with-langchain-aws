
import json
import os
import boto3

service_name = "s3"

null, true, false = None, True, False

def get_s3_resource():
    resource = boto3.resource(service_name=service_name, region_name=os.environ["S3_REGION"])
    return resource

def get_s3_client():
    client = boto3.client(service_name=service_name, region_name=os.environ["S3_REGION"])
    return client

def read_json_from_s3(bucket, s3Key):
    try:
        s3_client = get_s3_client()
        response = s3_client.get_object(Bucket=bucket, Key=s3Key)
        response_json = json.loads(response['Body'].read().decode('utf-8'))
        return response_json
    except Exception as err:
        print("Exception occurred while reading json from s3 in s3 {}".format(str(err)))

def upload_to_s3(file_name, bucket_name, s3_file_name):
    s3_client = get_s3_client()
    try:
        print(f"Uploading {file_name} to S3 bucket {bucket_name} as {s3_file_name}")
        s3_client.upload_file(file_name, bucket_name, s3_file_name)
        print("Upload successful.")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")

def write_json_to_s3(data, bucket, s3_key):
    try:
        s3_client = get_s3_client()
        data = json.dumps(data).encode('UTF-8')
        s3_client.put_object(Body=data, Bucket=bucket, Key=s3_key)
        return True
    except Exception as err:
        print("Exception occurred while writing json from s3 :: {}".format(str(err)))
        return False
