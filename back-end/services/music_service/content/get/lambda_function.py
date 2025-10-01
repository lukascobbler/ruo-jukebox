import os, json, boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET_NAME"]
TRACKS = dynamodb.Table(os.environ["TRACKS_TABLE"])

def _json_default(o):
    if isinstance(o, Decimal):
        return int(o) if o % 1 == 0 else float(o)
    raise TypeError

def _resp(code, body):
    return {"statusCode": code,
            "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body, default=_json_default)}

def lambda_handler(event, context):
    track_id = event["pathParameters"]["id"]
    r = TRACKS.get_item(Key={"track_id": track_id})
    item = r.get("Item")
    if not item:
        return _resp(404, {"message":"Not found"})

    if item.get("audio_key"):
        item["stream_url"] = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": item["audio_key"]},
            ExpiresIn=600
        )
    if item.get("cover_key"):
        item["cover_url"] = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": item["cover_key"]},
            ExpiresIn=600
        )

    return _resp(200, item)
