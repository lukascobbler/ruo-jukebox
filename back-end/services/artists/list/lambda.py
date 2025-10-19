import os
import boto3


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
}

dynamodb = boto3.resource("dynamodb")
artists = dynamodb.Table(os.environ["ARTISTS_TABLE"])

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    limit = int(params.get("limit", 50))
    eks = params.get("nextToken")

    scan_kwargs = {"Limit": limit}
    if eks:
        scan_kwargs["ExclusiveStartKey"] = {"artist_id": eks}

    resp = artists.scan(**scan_kwargs)
    items = resp.get("Items", [])
    out = [{
        "id": it["artist_id"],
        "name": it.get("Name",""),
        "hasBiography": bool(it.get("Biography")),
        "hasPicture": bool(it.get("Picture")),
    } for it in items]
    return {"statusCode": 200, "headers": CORS_HEADERS, "body": out}
