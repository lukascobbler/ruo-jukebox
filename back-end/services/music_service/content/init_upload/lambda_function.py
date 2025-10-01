import os, json, time, uuid, boto3
from decimal import Decimal

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
BUCKET = os.environ["BUCKET_NAME"]
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
    return {
        "statusCode": code,
        "headers": {"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
        "body": json.dumps(body, default=_json_default)
    }

def lambda_handler(event, context):
    guard = _require_admin(event)
    if guard: 
        return guard
    body = json.loads(event.get("body") or "{}")
    title = (body.get("title") or "").strip()
    artists = body.get("artist_ids") or []
    genres  = body.get("genres") or []
    album_id= body.get("album_id")  # may be None
    file_name = (body.get("file_name") or "").strip()
    file_type = (body.get("file_type") or "").strip()
    file_size = int(body.get("file_size") or 0)

    if not (title and file_name and file_type):
        return _resp(400, {"message":"title, file_name, file_type are required"})

    track_id = str(uuid.uuid4())
    audio_key = f"tracks/{track_id}/{file_name}"

    put_url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": BUCKET, "Key": audio_key, "ContentType": file_type},
        ExpiresIn=600
    )

    item = {
        "track_id": track_id,
        "title": title,
        # DON'T write album_id if it's not provided — avoids GSI NULL error
        "file_name": file_name,
        "file_type": file_type,
        "file_size": file_size,
        "audio_key": audio_key,
        "cover_key": None,
        "created_at": int(time.time()*1000)
    }
    if album_id:  # only include when not None/empty
        item["album_id"] = album_id

    TRACKS.put_item(Item=item)

    return _resp(200, {"track_id": track_id, "upload_url": put_url, "audio_key": audio_key})
