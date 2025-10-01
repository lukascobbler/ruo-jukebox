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
PL  = dynamodb.Table(os.environ["PLAYLISTS_TABLE"])
PLI = dynamodb.Table(os.environ["PLAYLIST_ITEMS_TABLE"])
TRACKS = boto3.resource("dynamodb").Table(os.environ["TRACKS_TABLE"])

def lambda_handler(event, context):
    uid = _uid(event)
    if not uid: return _resp(401, {"message":"unauthorized"})
    pid = event["pathParameters"]["id"]

    p = PL.get_item(Key={"playlist_id": pid}).get("Item")
    if not p or p["owner_user_id"] != uid:
        return _resp(404, {"message":"Not found"})

    # list track ids in the playlist
    r = PLI.query(KeyConditionExpression=Key("playlist_id").eq(pid))
    items = r.get("Items", [])
    items.sort(key=lambda x: int(x.get("added_at",0)))
    track_ids = [it["track_id"] for it in items]

    # optional expansion
    q = event.get("queryStringParameters") or {}
    if q.get("include") == "full" and track_ids:
        keys = [{"track_id": t} for t in track_ids[:100]]
        br = boto3.resource("dynamodb").batch_get_item(RequestItems={TRACKS.table_name: {"Keys": keys}})
        tracks = br["Responses"].get(TRACKS.table_name, [])
        return _resp(200, {"playlist": p, "tracks": tracks})

    return _resp(200, {"playlist": p, "track_ids": track_ids})
