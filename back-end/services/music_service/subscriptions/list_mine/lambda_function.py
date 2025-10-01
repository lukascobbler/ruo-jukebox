import os, json, boto3
from boto3.dynamodb.conditions import Key
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
    r = SUBS.query(IndexName="byUser", KeyConditionExpression=Key("user_id").eq(uid))
    items = r.get("Items", [])
    # return just artist_ids (and ts) for FE
    out = [{"artist_id": it["artist_id"], "ts": it.get("ts")} for it in items]
    return _resp(200, out)
