import boto3, os, json

dynamodb = boto3.resource("dynamodb")
SONGS_TABLE = os.environ["SONGS_TABLE"]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}


def lambda_handler(event, context):
    res = dynamodb.Table(SONGS_TABLE).scan()
    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps(res.get("Items", []))}
