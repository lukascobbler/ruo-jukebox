import os, json, boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET_NAME"]
TRACKS = dynamodb.Table(os.environ["TRACKS_TABLE"])
TA     = dynamodb.Table(os.environ["TRACK_ARTISTS_TABLE"])
TG     = dynamodb.Table(os.environ["TRACK_GENRES_TABLE"])
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
def truthy(v): return v in ["1","true","True","yes"]

def lambda_handler(event, context):
    guard = _require_admin(event)
    if guard: 
        return guard
    track_id = event["pathParameters"]["id"]
    q = event.get("queryStringParameters") or {}
    delete_files = truthy(q.get("delete_files","false"))

    r = TRACKS.get_item(Key={"track_id": track_id})
    item = r.get("Item")
    if not item:
        return _resp(404, {"message":"Not found"})

    # Remove TA joins
    cur_ta = TA.query(KeyConditionExpression=Key("track_id").eq(track_id))
    with TA.batch_writer() as bw:
        for it in cur_ta.get("Items", []):
            bw.delete_item(Key={"track_id": track_id, "artist_id": it["artist_id"]})

    # Remove TG joins
    cur_tg = TG.query(IndexName="byTrack", KeyConditionExpression=Key("track_id").eq(track_id))
    with TG.batch_writer() as bw:
        for it in cur_tg.get("Items", []):
            bw.delete_item(Key={"genre": it["genre"], "track_id": track_id})

    # Delete S3 files if asked
    if delete_files:
        for key in [item.get("audio_key"), item.get("cover_key")]:
            if key:
                try: s3.delete_object(Bucket=BUCKET, Key=key)
                except Exception: pass

    TRACKS.delete_item(Key={"track_id": track_id})
    return _resp(204, "")
