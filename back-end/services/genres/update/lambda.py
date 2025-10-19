import os, json, time
import boto3
from botocore.exceptions import ClientError
from services.common import _response

dynamodb = boto3.resource("dynamodb")
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])

def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    genre_id = path_params.get("id")
    if not genre_id:
        return _response(400, {"message": "Genre id missing in path"})

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"message": "Invalid JSON body"})

    if "name" not in body:
        return _response(400, {"message": "Nothing to update (provide 'name')"})

    new_name = (body.get("name") or "").strip()
    if not new_name:
        return _response(400, {"message": "Field 'name' cannot be empty"})

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
        code = e.response["Error"]["Code"]
        if code == "ConditionalCheckFailedException":
            return _response(404, {"message": "Genre not found"})
        return _response(500, {"message": "Failed to update genre", "error": str(e)})

    item = resp.get("Attributes", {})
    return _response(200, {"id": item.get("genre_id"), "name": item.get("Name")})
