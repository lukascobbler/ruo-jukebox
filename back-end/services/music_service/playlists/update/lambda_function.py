import os, json, boto3, time
from decimal import Decimal

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
    pid = event["pathParameters"]["id"]
    body = json.loads(event.get("body") or "{}")

    p = PL.get_item(Key={"playlist_id": pid}).get("Item")
    if not p or p["owner_user_id"] != uid:
        return _resp(404, {"message":"Not found"})

    fields = {}
    for f in ["name","description","cover_key"]:
        if f in body: fields[f] = body[f]
    if not fields: return _resp(400, {"message":"no updatable fields"})

    sets, eav = [], {}
    for i,(k,v) in enumerate(fields.items(), start=1):
        sets.append(f"{k}=:v{i}"); eav[f":v{i}"]=v
    sets.append("updated_at=:ts"); eav[":ts"]=int(time.time()*1000)

    r = PL.update_item(
        Key={"playlist_id": pid},
        UpdateExpression="SET " + ", ".join(sets),
        ExpressionAttributeValues=eav,
        ReturnValues="ALL_NEW"
    )
    return _resp(200, r["Attributes"])
