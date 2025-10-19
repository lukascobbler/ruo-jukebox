import os, json
import boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

artists = dynamodb.Table(os.environ["ARTISTS_TABLE"])
images_bucket = os.environ["IMAGES_BUCKET"]
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
}

_ALLOWED = {"image/jpeg":"jpg", "image/png":"png", "image/webp":"webp", "image/avif":"avif"}

def lambda_handler(event, context):
    artist_id = (event.get("pathParameters") or {}).get("id")
    if not artist_id:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message":"Artist id missing"})}

    if not artists.get_item(Key={"artist_id": artist_id}).get("Item"):
        return {"statusCode": 404, "headers": CORS_HEADERS, "body": json.dumps({"message":"Artist not found"})}

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        body = {}

    ct = (body.get("contentType") or "").strip().lower()
    if ct not in _ALLOWED:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message":"Unsupported or missing contentType", "allowed": list(_ALLOWED)})}

    ext = _ALLOWED[ct]
    uuid_part = artist_id.split("~",1)[-1]
    key = f"artists/{uuid_part}/main.{ext}"

    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": images_bucket, "Key": key, "ContentType": ct},
        ExpiresIn=900
    )
    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({"uploadUrl": url, "key": key, "expiresIn": 900})}
