import os, json, boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
ALBUMS = dynamodb.Table(os.environ["ALBUMS_TABLE"])

def _json_default(o):
    if isinstance(o, Decimal):
        return int(o) if o % 1 == 0 else float(o)
    raise TypeError

def _resp(code, body):
    return {"statusCode": code,
            "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body, default=_json_default)}

def lambda_handler(event, context):
    q = event.get("queryStringParameters") or {}
    by_artist = (q.get("artistId") or "").strip()

    if by_artist:
        r = ALBUMS.query(
            IndexName="byArtist",
            KeyConditionExpression=Key("artist_id").eq(by_artist)
        )
        items = r.get("Items", [])
    else:
        r = ALBUMS.scan(Limit=500)
        items = r.get("Items", [])

    # Sort newest first (optional)
    items.sort(key=lambda x: int(x.get("created_at", 0)), reverse=True)
    return _resp(200, items)
