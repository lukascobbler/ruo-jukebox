from boto3.dynamodb.conditions import Key
import boto3
import json
import os

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]


def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)

    for record in event["Records"]:
        msg = json.loads(record["body"])
        name = msg.get("name")
        value_str = msg.get("value", "0")

        try:
            value = int(value_str)
        except ValueError:
            value = 0

        response = table.query(
            KeyConditionExpression=Key("name").eq(name),
            ScanIndexForward=False,
            Limit=1
        )

        latest_seq = 0
        latest_value = 0
        if response["Items"]:
            latest_seq = int(response["Items"][0].get("seq", 0))
            latest_value = int(response["Items"][0].get("value", 0))

        new_seq = latest_seq + 1
        new_value = latest_value + value

        table.put_item(Item={"name": name, "seq": new_seq, "value": new_value})
