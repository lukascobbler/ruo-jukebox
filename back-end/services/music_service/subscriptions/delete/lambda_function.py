import os, json, boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
SUBS = dynamodb.Table(os.environ["SUBSCRIPTIONS_TABLE"])

def _json_default(o):
    if isinstance(o, Decimal): return int(o) if o % 1 == 0 else float(o)
    raise TypeError

def _resp(code, body):
    return {"statusCode": code,
            "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body, default=_json_default)}

def _uid(event):
    claims = (event.get("requestContext") or {}).get("authorizer", {}).get("claims", {}) or {}
    return claims.get("sub")

def lambda_handler(event, context):
    uid = _uid(event)
    if not uid: return _resp(401, {"message":"unauthorized"})
    artist_id = event["pathParameters"]["artistId"]
    SUBS.delete_item(Key={"artist_id": artist_id, "user_id": uid})
    return _resp(204, "")
