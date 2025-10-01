import os, json, boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
ARTISTS = dynamodb.Table(os.environ["ARTISTS_TABLE"])
ALBUMS  = dynamodb.Table(os.environ["ALBUMS_TABLE"])
TA      = dynamodb.Table(os.environ["TRACK_ARTISTS_TABLE"])
def _claims(event):
    return (event.get("requestContext") or {}).get("authorizer", {}).get("claims", {}) or {}

def _require_admin(event):
    claims = _claims(event)
    groups = (claims.get("cognito:groups") or "")
    if "admin" not in groups.split(","):
        return {
            "statusCode": 403,
            "headers": {"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps({"message":"admin only"})
        }

def _json_default(o):
    if isinstance(o, Decimal):
        return int(o) if o % 1 == 0 else float(o)
    raise TypeError

def _resp(code, body):
    return {"statusCode": code,
            "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body, default=_json_default)}
def lambda_handler(event, context):
    guard = _require_admin(event)
    if guard: 
        return guard
    artist_id = event["pathParameters"]["id"]

    # Block delete if referenced by albums or tracks
    a = ALBUMS.query(IndexName="byArtist", KeyConditionExpression=Key("artist_id").eq(artist_id), Limit=1)
    t = TA.query(IndexName="byArtist", KeyConditionExpression=Key("artist_id").eq(artist_id), Limit=1)
    if a.get("Count",0) or t.get("Count",0):
        return _resp(409, {"message":"artist has related albums/tracks; delete or detach them first"})

    try:
        ARTISTS.delete_item(
            Key={"artist_id": artist_id},
            ConditionExpression="attribute_exists(artist_id)"
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return _resp(404, {"message":"Not found"})

    return _resp(204, "")
