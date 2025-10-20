import os
from dataclasses import asdict
import boto3
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from model.model import Artist, GenreItem
from pre_authorize import pre_authorize

dynamodb = boto3.resource("dynamodb")
ddb = boto3.client("dynamodb")
s3 = boto3.client('s3', os.environ["REGION"], endpoint_url=os.environ["S3_ENDPOINT_URL"])

artists = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genres_table_name = os.environ["GENRES_TABLE"]
content_genres = dynamodb.Table(os.environ["CONTENT_GENRES_TABLE"])
images_bucket = os.environ["IMAGES_BUCKET"]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
}

def _genre_names(ids: list[str]) -> dict[str, str]:
    if not ids:
        return {}
    keys = [{"PK": {"S": "genres"}, "genre_id": {"S": gid}} for gid in ids]
    resp = ddb.batch_get_item(RequestItems={genres_table_name: {"Keys": keys}})
    items = resp.get("Responses", {}).get(genres_table_name, [])
    # convert Dynamo types to plain dict
    plain = [{k: list(v.values())[0] for k, v in it.items()} for it in items]
    return {it["genre_id"]: it.get("Name", "") for it in plain}


@pre_authorize(['Admin', 'LoggedInUser'])
def lambda_handler(event, context):
    artist_id = (event.get("pathParameters") or {}).get("id")
    if not artist_id:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Artist id missing"})}

    it = artists.get_item(Key={"artist_id": artist_id}).get("Item")
    if not it:
        return {"statusCode": 404, "headers": CORS_HEADERS, "body": json.dumps({"message": "Artist not found"})}

    resp = content_genres.query(
        IndexName="byEntity",
        KeyConditionExpression=Key("entity").eq(artist_id)
    )
    gids = [r["genre"] for r in resp.get("Items", [])]

    name_by_genre = _genre_names(gids)

    picture_key = it.get("Picture")
    picture_url = None
    if picture_key:
        try:
            picture_url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": images_bucket, "Key": picture_key},
                ExpiresIn=3600
            )
        except ClientError:
            picture_url = None

    artist = Artist(
        id=it["artist_id"],
        name=it.get("Name", ""),
        biography=it.get("Biography", ""),
        pictureKey=picture_key,
        pictureUrl=picture_url,
        genres=[GenreItem(id=gid, name=name_by_genre.get(gid, "")) for gid in gids]
    )
    return {"statusCode": 200, "headers": CORS_HEADERS, "body": asdict(artist)}
