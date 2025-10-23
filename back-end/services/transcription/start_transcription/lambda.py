import os
import json
import boto3

sqs = boto3.client("sqs")
QUEUE_URL = os.environ["QUEUE_URL"]

def lambda_handler(event, context):
    print("Received S3 event:", json.dumps(event))

    messages_sent = 0

    for record in event.get("Records", []):
        s3_info = record.get("s3", {})
        bucket_name = s3_info["bucket"]["name"]
        object_key = s3_info["object"]["key"]

        if not object_key.startswith("songs/") or not object_key.lower().endswith(".mp3"):
            continue

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
            messages_sent += 1
        except Exception as e:
            print(f"Failed to send message for {object_key}: {str(e)}")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "queued",
            "messages_sent": messages_sent
        })
    }
