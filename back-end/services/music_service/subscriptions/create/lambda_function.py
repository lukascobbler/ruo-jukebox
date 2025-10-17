import os, json, time, boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
SUBS = dynamodb.Table(os.environ["SUBSCRIPTIONS_TABLE"])
ARTISTS = dynamodb.Table(os.environ["ARTISTS_TABLE"])

from decimal import Decimal

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
    body = json.loads(event.get("body") or "{}")
    artist_id = (body.get("artist_id") or "").strip()
    if not artist_id: return _resp(400, {"message":"artist_id required"})

    # ensure artist exists
    ar = ARTISTS.get_item(Key={"artist_id": artist_id})
    if "Item" not in ar:
        return _resp(400, {"message":"artist not found"})

    # idempotent subscribe
    SUBS.put_item(
        Item={"artist_id": artist_id, "user_id": uid, "ts": int(time.time()*1000)},
        ConditionExpression="attribute_not_exists(user_id)"
    )
    return _resp(201, {"message": "subscribed", "artist_id": artist_id})
