import boto3
import json
import os

sqs = boto3.client("sqs")
QUEUE_URL = os.environ["QUEUE_URL"]


def lambda_handler(event, context):
    body = json.loads(event["body"])
    name = body["name"]
    value = body["value"]

    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps({"name": name, "value": value})
    )

    return {"statusCode": 200, "body": json.dumps({"message": "Added to queue"})}
