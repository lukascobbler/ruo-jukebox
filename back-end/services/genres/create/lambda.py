from botocore.exceptions import ClientError
from pre_authorize import pre_authorize
import os, json, time, uuid, boto3

dynamodb = boto3.resource("dynamodb")
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))


@pre_authorize(['Admin'])
def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Invalid JSON body"})}

    name = (body.get("name") or "").strip()
    if not name:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Field 'name' is required"})}

    genre_id = f"GENRE~{uuid.uuid4()}"
    now = int(time.time())

    item = {
        "PK": "genres",
        "genre_id": genre_id,
        "Name": name,
        "name_lc": name.lower(),
        "created_at": now,
        "updated_at": now,
    }

    try:
        genres_table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(genre_id)"
        )
        return {"statusCode": 201, "headers": CORS_HEADERS, "body": json.dumps({"id": genre_id, "name": name})}
    except ClientError as e:
        return {"statusCode": 500, "headers": CORS_HEADERS, "body": json.dumps({"message": "Failed to create genre", "error": str(e)})}
