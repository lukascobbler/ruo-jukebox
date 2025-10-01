import os, boto3
from decimal import Decimal
import json

dynamodb = boto3.resource("dynamodb")
ARTISTS = dynamodb.Table(os.environ["ARTISTS_TABLE"])

def _json_default(o):
    if isinstance(o, Decimal):
        return int(o) if o % 1 == 0 else float(o)
    raise TypeError

def _resp(code, body):
    return {"statusCode": code,
            "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body, default=_json_default)}

def lambda_handler(event, context):
    r = ARTISTS.scan(Limit=200)
    items = r.get("Items", [])
    return _resp(200, items)
