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

def lambda_handler(event, context):
    uid = _uid(event)
    if not uid: return _resp(401, {"message":"unauthorized"})
    pid = event["pathParameters"]["id"]

    p = PL.get_item(Key={"playlist_id": pid}).get("Item")
    if not p or p["owner_user_id"] != uid:
        return _resp(404, {"message":"Not found"})

    # delete items
    cur = PLI.query(KeyConditionExpression=Key("playlist_id").eq(pid))
    with PLI.batch_writer() as bw:
        for it in cur.get("Items", []):
            bw.delete_item(Key={"playlist_id": pid, "track_id": it["track_id"]})

    PL.delete_item(Key={"playlist_id": pid})
    return _resp(204, "")
