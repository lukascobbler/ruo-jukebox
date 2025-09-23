import json
import boto3
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]

def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)
    params = event.get("queryStringParameters") or {}

    name = params.get("name")
    seq = params.get("seq")

    try:
        if name:
            if seq:
                seq = int(seq)
                response = table.get_item(Key={"name": name, "seq": seq})
                items = [response["Item"]] if "Item" in response else []
            else:
                response = table.query(KeyConditionExpression=Key("name").eq(name))
                items = response.get("Items", [])
        else:
            response = table.scan()
            items = response.get("Items", [])
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Internal server error", "details": str(e)})
        }

    for item in items:
        if "seq" in item:
            item["seq"] = int(item["seq"])
        if "value" in item:
            item["value"] = int(item["value"])

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(items)
    }
