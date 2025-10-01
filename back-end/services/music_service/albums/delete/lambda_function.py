import os, json, boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET_NAME"]
ALBUMS = dynamodb.Table(os.environ["ALBUMS_TABLE"])
TRACKS = dynamodb.Table(os.environ["TRACKS_TABLE"])
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
    q = (event.get("queryStringParameters") or {})
    force = (q.get("force") in ["1","true","True","yes"])
    delete_files = (q.get("delete_files") in ["1","true","True","yes"])

    # Get album
    r = ALBUMS.get_item(Key={"album_id": album_id})
    album = r.get("Item")
    if not album:
        return _resp(404, {"message":"Not found"})

    # Any tracks in the album?
    tr = TRACKS.query(IndexName="GSI1", KeyConditionExpression=Key("album_id").eq(album_id))
    items = tr.get("Items", [])

    if items and not force:
        return _resp(409, {"message":"album has tracks; call with ?force=true to detach tracks first", "count": len(items)})

    # Detach tracks if forcing
    if items:
        for it in items:
            TRACKS.update_item(Key={"track_id": it["track_id"]}, UpdateExpression="REMOVE album_id")

    # Optionally delete cover file
    if delete_files and album.get("cover_key"):
        try:
            s3.delete_object(Bucket=BUCKET, Key=album["cover_key"])
        except Exception:
            pass

    ALBUMS.delete_item(Key={"album_id": album_id})
    return _resp(204, "")
