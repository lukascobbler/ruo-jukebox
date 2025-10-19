import os
import boto3
import json
from boto3.dynamodb.conditions import Key
from pre_authorize import pre_authorize

dynamodb = boto3.resource("dynamodb")
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
}

@pre_authorize(['Admin', 'LoggedInUser'])
def lambda_handler(event, context):
    items, lek = [], None

    while True:
        kwargs = {
            "KeyConditionExpression": Key("PK").eq("genres"),
            "ProjectionExpression": "#pk, genre_id, #n",
            "ExpressionAttributeNames": {"#pk": "PK", "#n": "Name"},
        }
        if lek:
            kwargs["ExclusiveStartKey"] = lek

        resp = genres_table.query(**kwargs)
        items.extend(resp.get("Items", []))
        lek = resp.get("LastEvaluatedKey")
        if not lek:
            break

    out = [
        {
            "id": it["genre_id"],
            "name": it.get("Name", ""),
            "isSubscribed": None,
        }
        for it in items
    ]
    return {"statusCode": 200, "headers": CORS_HEADERS, "body": out}
