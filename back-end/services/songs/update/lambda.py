import json, boto3, os

dynamodb = boto3.resource("dynamodb")
SONGS_TABLE = os.environ["SONGS_TABLE"]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}


def lambda_handler(event, context):
    body = json.loads(event["body"])
    song_id = body["song_id"]

    update_expr = []
    expr_values = {}
    for field in ["name", "artist_ids", "genre_ids"]:
        if field in body:
            update_expr.append(f"{field} = :{field}")
            expr_values[f":{field}"] = body[field]

    if not update_expr:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"error": "Nothing to update"})}

    update_expr = "SET " + ", ".join(update_expr)
    dynamodb.Table(SONGS_TABLE).update_item(
        Key={"id": song_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values
    )

    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({"message": "Song updated"})}
