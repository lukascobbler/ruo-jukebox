import os, json, boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
TRACKS = dynamodb.Table(os.environ["TRACKS_TABLE"])
TA = dynamodb.Table(os.environ["TRACK_ARTISTS_TABLE"])
TG = dynamodb.Table(os.environ["TRACK_GENRES_TABLE"])

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
    genre = q.get("genre")
    artist_id = q.get("artistId")
    album_id = q.get("albumId")

    if genre:
        r = TG.query(KeyConditionExpression=Key("genre").eq(genre))
        ids = [it["track_id"] for it in r.get("Items", [])]
    elif artist_id:
        r = TA.query(IndexName="byArtist", KeyConditionExpression=Key("artist_id").eq(artist_id))
        ids = [it["track_id"] for it in r.get("Items", [])]
    elif album_id:
        r = TRACKS.query(IndexName="GSI1", KeyConditionExpression=Key("album_id").eq(album_id))
        return _resp(200, r.get("Items", []))
    else:
        r = TRACKS.scan(Limit=100)
        return _resp(200, r.get("Items", []))

    if not ids:
        return _resp(200, [])

    keys = [{"track_id": tid} for tid in ids[:100]]
    br = dynamodb.batch_get_item(RequestItems={TRACKS.table_name: {"Keys": keys}})
    return _resp(200, br["Responses"].get(TRACKS.table_name, []))
