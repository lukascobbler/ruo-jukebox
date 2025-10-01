import os, json, boto3, time
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
ALBUMS  = dynamodb.Table(os.environ["ALBUMS_TABLE"])
ARTISTS = dynamodb.Table(os.environ["ARTISTS_TABLE"])
def _claims(event):
    return (event.get("requestContext") or {}).get("authorizer", {}).get("claims", {}) or {}

def _require_admin(event):
    claims = _claims(event)
    groups = (claims.get("cognito:groups") or "")
    if "admin" not in groups.split(","):
        return {
            "statusCode": 403,
            "headers": {"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps({"message":"admin only"})
        }

def _json_default(o):
    if isinstance(o, Decimal):
        return int(o) if o % 1 == 0 else float(o)
    raise TypeError

def _resp(code, body):
    return {"statusCode": code,
            "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body, default=_json_default)}

def lambda_handler(event, context):
    guard = _require_admin(event)
    if guard: 
        return guard
    album_id = event["pathParameters"]["id"]
    body = json.loads(event.get("body") or "{}")

    fields = {}
    for f in ["name","genres","artist_id","cover_key"]:
        if f in body:
            fields[f] = body[f]

    if "artist_id" in fields:
        ar = ARTISTS.get_item(Key={"artist_id": fields["artist_id"]})
        if "Item" not in ar:
            return _resp(400, {"message":"artist not found", "artist_id": fields["artist_id"]})

    if not fields:
        return _resp(400, {"message":"no updatable fields"})

    expr, eav = [], {}
    for i,(k,v) in enumerate(fields.items(), start=1):
        expr.append(f"{k}=:v{i}")
        eav[f":v{i}"] = v
    expr.append("created_at = if_not_exists(created_at, :zero)")  # keep for safety
    eav[":zero"] = 0

    r = ALBUMS.update_item(
        Key={"album_id": album_id},
        UpdateExpression="SET " + ", ".join(expr),
        ExpressionAttributeValues=eav,
        ConditionExpression="attribute_exists(album_id)",
        ReturnValues="ALL_NEW"
    )
    return _resp(200, r["Attributes"])
