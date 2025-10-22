from botocore.exceptions import ClientError
from pre_authorize import pre_authorize
import os, json, time, boto3

dynamodb = boto3.resource("dynamodb")
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])
CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))


@pre_authorize(['Admin', 'User'])
def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    genre_id = path_params.get("id")
    if not genre_id:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Genre id missing in path"})}

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Invalid JSON body"})}

    if "name" not in body:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Nothing to update (provide 'name')"})}
    new_name = (body.get("name") or "").strip()
    if not new_name:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Field 'name' cannot be empty"})}

    now = int(time.time())
    try:
        resp = genres_table.update_item(
            Key={"PK": "genres", "genre_id": genre_id},
            UpdateExpression="SET #N = :n, #nlc = :nlc, #u = :now",
            ExpressionAttributeNames={"#N": "Name", "#nlc": "name_lc", "#u": "updated_at"},
            ExpressionAttributeValues={":n": new_name, ":nlc": new_name.lower(), ":now": now},
            ConditionExpression="attribute_exists(genre_id)",
            ReturnValues="ALL_NEW",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {"statusCode": 404, "headers": CORS_HEADERS, "body": json.dumps({"message": "Genre not found"})}
        return {"statusCode": 500, "headers": CORS_HEADERS, "body": json.dumps({"message": "Failed to update genre", "error": str(e)})}

    item = resp.get("Attributes", {})
    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({"id": item.get("genre_id"), "name": item.get("Name")})}
