import os, json, boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
sqs = boto3.client("sqs")

BUCKET = os.environ["BUCKET_NAME"]
TRACKS = dynamodb.Table(os.environ["TRACKS_TABLE"])
TA = dynamodb.Table(os.environ["TRACK_ARTISTS_TABLE"])
TG = dynamodb.Table(os.environ["TRACK_GENRES_TABLE"])
QUEUE_URL = os.environ["QUEUE_URL"]
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
    track_id = body.get("track_id")
    audio_key = body.get("audio_key")
    artists = body.get("artist_ids") or []
    genres  = body.get("genres") or []
    album_id= body.get("album_id")  # may be None
    file_created_time = body.get("file_created_time")
    file_modified_time= body.get("file_modified_time")

    if not (track_id and audio_key):
        return _resp(400, {"message":"track_id and audio_key required"})

    head = s3.head_object(Bucket=BUCKET, Key=audio_key)
    file_size = head.get("ContentLength")
    if not file_modified_time:
        file_modified_time = head.get("LastModified").isoformat()

    # Build update expression dynamically
    set_expr = ["file_size=:sz", "file_created_time=:fc", "file_modified_time=:fm"]
    eav = {":sz": file_size, ":fc": file_created_time, ":fm": file_modified_time}

    if album_id:  # only set when provided
        set_expr.append("album_id=:al")
        eav[":al"] = album_id

    TRACKS.update_item(
        Key={"track_id": track_id},
        UpdateExpression="SET " + ", ".join(set_expr),
        ExpressionAttributeValues=eav
    )

    # Joins
    for aid in artists:
        TA.put_item(Item={"track_id": track_id, "artist_id": aid})
    for g in genres:
        TG.put_item(Item={"genre": g, "track_id": track_id})

    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps({"type":"TRACK_UPLOADED","track_id":track_id}))
    return _resp(200, {"message":"completed", "track_id": track_id})
