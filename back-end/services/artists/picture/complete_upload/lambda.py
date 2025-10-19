import os, json, time
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
}

artists = dynamodb.Table(os.environ["ARTISTS_TABLE"])
images_bucket = os.environ["IMAGES_BUCKET"]

def lambda_handler(event, context):
    artist_id = (event.get("pathParameters") or {}).get("id")
    if not artist_id:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message":"Artist id missing"})}

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message":"Invalid JSON body"})}

    key = (body.get("key") or "").strip()
    if not key:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message":"Field 'key' is required"})}

    uuid_part = artist_id.split("~",1)[-1]
    if not key.startswith(f"artists/{uuid_part}/"):
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message":"Key does not match artist"})}

    try:
        s3.head_object(Bucket=images_bucket, Key=key)
    except ClientError as e:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message":"Uploaded object not found", "error": str(e)})}

    try:
        artists.update_item(
            Key={"artist_id": artist_id},
            UpdateExpression="SET #p=:k, #u=:now",
            ExpressionAttributeNames={"#p":"Picture", "#u":"updated_at"},
            ExpressionAttributeValues={":k": key, ":now": int(time.time())},
            ConditionExpression="attribute_exists(artist_id)"
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {"statusCode": 404, "headers": CORS_HEADERS, "body": json.dumps({"message":"Artist not found"})}
        return {"statusCode": 500, "headers": CORS_HEADERS, "body": json.dumps({"message":"Failed to save picture", "error": str(e)})}

    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({"id": artist_id, "pictureKey": key, "saved": True})}
