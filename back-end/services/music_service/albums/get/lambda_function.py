import os, json, boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET_NAME"]
ALBUMS = dynamodb.Table(os.environ["ALBUMS_TABLE"])

def _json_default(o):
    if isinstance(o, Decimal):
        return int(o) if o % 1 == 0 else float(o)
    raise TypeError

def _resp(code, body):
    return {"statusCode": code,
            "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body, default=_json_default)}

def lambda_handler(event, context):
    album_id = event["pathParameters"]["id"]
    r = ALBUMS.get_item(Key={"album_id": album_id})
    item = r.get("Item")
    if not item:
        return _resp(404, {"message": "Not found"})
    ck = item.get("cover_key")
    if ck:
        item["cover_url"] = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": ck},
            ExpiresIn=600
        )
    return _resp(200, item)
