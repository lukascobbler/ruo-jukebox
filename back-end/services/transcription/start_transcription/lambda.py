import os
import json
import boto3

sqs = boto3.client("sqs")
QUEUE_URL = os.environ["QUEUE_URL"]

def lambda_handler(event, context):
    print("Received EventBridge S3 event:", json.dumps(event))

    try:
        bucket_name = event["detail"]["bucket"]["name"]
        object_key = event["detail"]["object"]["key"]
    except KeyError as e:
        print(f"Malformed event: missing {e}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Malformed event: missing {e}"})
        }

    if not object_key.lower().endswith(".mp3"):
        print(f"Skipping object (not an MP3): {object_key}")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "skipped",
                "reason": "Not an MP3 file"
            })
        }

    message = {
        "bucket": bucket_name,
        "key": object_key
    }

    try:
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(message)
        )
        print(f"Sent message for s3://{bucket_name}/{object_key}")
    except Exception as e:
        print(f"Failed to send message for {object_key}: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "queued",
            "bucket": bucket_name,
            "key": object_key
        })
    }
