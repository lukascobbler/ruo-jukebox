import json
import os

from boto3 import s3

CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))

def response(status, body):
    return {"statusCode": status, "headers": CORS_HEADERS, "body": json.dumps(body, default=str)}

def generate_s3_download_url(bucket, key):
    if not key: return None
    return s3.generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=3600)