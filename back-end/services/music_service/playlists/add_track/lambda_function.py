import os, json, time, boto3
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
PL  = dynamodb.Table(os.environ["PLAYLISTS_TABLE"])
PLI = dynamodb.Table(os.environ["PLAYLIST_ITEMS_TABLE"])
TRACKS = dynamodb.Table(os.environ["TRACKS_TABLE"])

def lambda_handler(event, context):
    uid = _uid(event)
    if not uid: return _resp(401, {"message":"unauthorized"})
    pid = event["pathParameters"]["id"]
    body = json.loads(event.get("body") or "{}")
    track_id = (body.get("track_id") or "").strip()
    if not track_id: return _resp(400, {"message":"track_id required"})

    p = PL.get_item(Key={"playlist_id": pid}).get("Item")
    if not p or p["owner_user_id"] != uid:
        return _resp(404, {"message":"Not found"})

    # ensure track exists
    tr = TRACKS.get_item(Key={"track_id": track_id})
    if "Item" not in tr:
        return _resp(400, {"message":"track not found"})

    # idempotent add
    PLI.put_item(
        Item={"playlist_id": pid, "track_id": track_id, "added_at": int(time.time()*1000)},
        ConditionExpression="attribute_not_exists(track_id)"
    )
    return _resp(200, {"message":"added", "track_id": track_id})
