import os, json, boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
GENRES = dynamodb.Table(os.environ["GENRES_TABLE"])

def _json_default(o):
    if isinstance(o, Decimal):
        return int(o) if o % 1 == 0 else float(o)
    raise TypeError

def _resp(code, body):
    return {"statusCode": code,
            "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body, default=_json_default)}

def lambda_handler(event, context):
    r = GENRES.scan(Limit=500)
    items = r.get("Items", [])
    # optional: sort by name
    items.sort(key=lambda x: (x.get("name") or "").lower())
    return _resp(200, items)
