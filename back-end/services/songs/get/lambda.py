import boto3, os, json

dynamodb = boto3.resource("dynamodb")
SONGS_TABLE = os.environ["SONGS_TABLE"]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}


def lambda_handler(event, context):
    song_id = event["pathParameters"]["id"]
    res = dynamodb.Table(SONGS_TABLE).get_item(Key={"id": song_id})
    if "Item" not in res:
        return {"statusCode": 404, "headers": CORS_HEADERS, "body": json.dumps({"error": "Song not found"})}
    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps(res["Item"])}
