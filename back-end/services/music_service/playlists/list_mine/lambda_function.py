import os, json, boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

def _json_default(o):
    if isinstance(o, Decimal):
        return int(o) if o % 1 == 0 else float(o)
    raise TypeError

def _resp(code, body):
    return {"statusCode": code,
            "headers": {"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body, default=_json_default)}

def _uid(event):
    claims = (event.get("requestContext") or {}).get("authorizer", {}).get("claims", {})
    return claims.get("sub")

dynamodb = boto3.resource("dynamodb")
PL = dynamodb.Table(os.environ["PLAYLISTS_TABLE"])

def lambda_handler(event, context):
    uid = _uid(event)
    if not uid: return _resp(401, {"message":"unauthorized"})
    r = PL.query(IndexName="byOwner", KeyConditionExpression=Key("owner_user_id").eq(uid))
    items = r.get("Items", [])
    items.sort(key=lambda x: int(x.get("created_at",0)), reverse=True)
    return _resp(200, items)
