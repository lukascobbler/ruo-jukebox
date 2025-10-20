import os, json, time
import boto3
from botocore.exceptions import ClientError
from pre_authorize import pre_authorize

dynamodb = boto3.resource("dynamodb")
ddb = boto3.client("dynamodb")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,DELETE,PATCH"
}

subs_table         = dynamodb.Table(os.environ["SUBSCRIPTIONS_TABLE"])
artists_table      = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genres_table_name  = os.environ["GENRES_TABLE"]

def _genre_exists(genre_id: str) -> bool:
    try:
        resp = ddb.get_item(
            TableName=genres_table_name,
            Key={"PK":{"S":"genres"}, "genre_id":{"S": genre_id}},
            ProjectionExpression="genre_id"
        )
        return "Item" in resp
    except ClientError:
        return False

def _artist_exists(artist_id: str) -> bool:
    try:
        return bool(artists_table.get_item(Key={"artist_id": artist_id}).get("Item"))
    except ClientError:
        return False

@pre_authorize(['Admin', 'LoggedInUser'])
def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message":"Invalid JSON"})}

    topic = (body.get("topic") or "").strip()
    artist_id = (body.get("artistId") or "").strip()
    genre_id  = (body.get("genreId") or "").strip()
    if not topic:
        if artist_id: topic = artist_id
        elif genre_id: topic = genre_id

    if not topic:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message":"Field 'topic' (ARTIST~.. or GENRE~..) is required"})}

    user_id = event.get("userId")
    if not user_id:
        return {"statusCode": 401, "headers": CORS_HEADERS, "body": json.dumps({"message":"Unauthorized"})}

    if topic.startswith("GENRE~"):
        if not _genre_exists(topic):
            return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message":"Unknown genre id"})}
        topic_type = "GENRE"
    elif topic.startswith("ARTIST~"):
        if not _artist_exists(topic):
            return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message":"Unknown artist id"})}
        topic_type = "ARTIST"
    else:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message":"Unsupported topic format"})}

    now = int(time.time())
    try:
        subs_table.put_item(
            Item={"topic": topic, "user_id": user_id, "topic_type": topic_type, "created_at": now},
            ConditionExpression="attribute_not_exists(user_id)"
        )
        created = True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            created = False
        else:
            return {"statusCode": 500, "headers": CORS_HEADERS,
                    "body": json.dumps({"message":"Failed to subscribe", "error": str(e)})}

    return {"statusCode": 201 if created else 200, "headers": CORS_HEADERS,
            "body": json.dumps({"topic": topic, "created": created})}
