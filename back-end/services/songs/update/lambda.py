import json, boto3, os

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

SONGS_TABLE = dynamodb.Table(os.environ["SONGS_TABLE"])
IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}


def _generate_upload_url(bucket, key):
    return s3.generate_presigned_url("put_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=3600)


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        song_id = body.get("song_id")

        if not song_id:
            return _response(400, {"error": "Missing song_id"})

        update_expr = []
        expr_values = {}
        expr_names = {}
        response_data = {}

        if "name" in body:
            expr_names["#name"] = "title"
            update_expr.append("#name = :title")
            expr_values[":title"] = body["name"]

        if "artist_ids" in body:
            update_expr.append("artist_ids = :artist_ids")
            expr_values[":artist_ids"] = body["artist_ids"]

        if "genre_ids" in body:
            update_expr.append("genre_ids = :genre_ids")
            expr_values[":genre_ids"] = body["genre_ids"]

        if "cover_filename" in body:
            ext = os.path.splitext(body["cover_filename"])[1]
            new_cover_key = f"singles/{song_id}{ext}"
            cover_url = _generate_upload_url(IMAGES_BUCKET, new_cover_key)

            update_expr.append("cover_key = :cover_key")
            expr_values[":cover_key"] = new_cover_key
            response_data["cover_upload_url"] = cover_url

        if not update_expr:
            return _response(400, {"error": "Nothing to update"})

        update_statement = "SET " + ", ".join(update_expr)

        SONGS_TABLE.update_item(
            Key={"song_id": song_id},
            UpdateExpression=update_statement,
            ExpressionAttributeValues=expr_values,
            ExpressionAttributeNames=expr_names if expr_names else None
        )

        response_data["message"] = "Song updated"
        return _response(200, response_data)

    except Exception as e:
        return _response(500, {"error": str(e)})


def _response(status, body):
    return {"statusCode": status, "headers": CORS_HEADERS, "body": json.dumps(body, default=str)}
