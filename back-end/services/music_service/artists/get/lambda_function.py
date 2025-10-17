import os, json, boto3
from decimal import Decimal

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
    artist_id = event["pathParameters"]["id"]
    r = ARTISTS.get_item(Key={"artist_id": artist_id})
    item = r.get("Item")
    if not item:
        return _resp(404, {"message": "Not found"})
    return _resp(200, item)
