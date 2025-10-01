import os, json, uuid, boto3
from decimal import Decimal
import time
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
    body = json.loads(event.get("body") or "{}")
    name = (body.get("name") or "").strip()
    desc = body.get("description") or ""
    if not name: return _resp(400, {"message":"name is required"})
    item = {
        "playlist_id": str(uuid.uuid4()),
        "owner_user_id": uid,
        "name": name,
        "description": desc,
        "cover_key": None,
        "created_at": int(time.time()*1000)
    }
    PL.put_item(Item=item)
    return _resp(201, item)
