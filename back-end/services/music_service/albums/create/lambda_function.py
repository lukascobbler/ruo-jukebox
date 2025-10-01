import os, json, time, uuid, boto3
from decimal import Decimal

sqs = boto3.client("sqs")
NOTIFY_QUEUE_URL = os.environ["NOTIFY_QUEUE_URL"]
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
    body = json.loads(event.get("body") or "{}")
    name = (body.get("name") or "").strip()
    genres = body.get("genres") or []
    artist_id = (body.get("artist_id") or "").strip()

    if not name:
        return _resp(400, {"message": "name is required"})
    if not artist_id:
        return _resp(400, {"message": "artist_id is required"})

    # optional: validate artist exists
    ar = ARTISTS.get_item(Key={"artist_id": artist_id})
    if "Item" not in ar:
        return _resp(400, {"message": "artist not found", "artist_id": artist_id})

    item = {
        "album_id": str(uuid.uuid4()),
        "name": name,
        "genres": genres,
        "artist_id": artist_id,           # <-- NEW
        "cover_key": None,
        "created_at": int(time.time()*1000)
    }
    ALBUMS.put_item(Item=item)
    sqs.send_message(
        QueueUrl=NOTIFY_QUEUE_URL,
        MessageBody=json.dumps({"type":"ALBUM_CREATED","album_id": item["album_id"]})
    )
    return _resp(201, item)
