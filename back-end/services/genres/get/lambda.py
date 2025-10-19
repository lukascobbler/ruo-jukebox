import os
from dataclasses import asdict
import boto3
import json
from boto3.dynamodb.conditions import Key
from model.model import Genre, AlbumFromGenre, ArtistFromGenre
from pre_authorize import pre_authorize

dynamodb = boto3.resource("dynamodb")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
}

GENRES_TABLE = os.environ["GENRES_TABLE"]
CONTENT_GENRES_TABLE = os.environ["CONTENT_GENRES_TABLE"]
ARTISTS_TABLE = os.environ["ARTISTS_TABLE"]
ALBUMS_TABLE = os.environ["ALBUMS_TABLE"]

genres_table = dynamodb.Table(GENRES_TABLE)
content_genres_table = dynamodb.Table(CONTENT_GENRES_TABLE)

@pre_authorize(['Admin', ''])
def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    genre_id = path_params.get("id")
    if not genre_id:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"message": "Genre id missing"})}

    genre_item = genres_table.get_item(Key={"PK": "genres", "genre_id": genre_id}).get("Item")
    if not genre_item:
        return {"statusCode": 404, "headers": CORS_HEADERS, "body": json.dumps({"message": "Genre not found"})}

    members = _query_entities_for_genre(genre_id)
    artist_ids = [it["entity"] for it in members if it.get("entity","").startswith("ARTIST~")]
    album_ids  = [it["entity"] for it in members if it.get("entity","").startswith("ALBUM~")]

    artists = _batch_get_items(ARTISTS_TABLE, "artist_id", artist_ids)
    albums  = _batch_get_items(ALBUMS_TABLE,  "album_id",  album_ids)

    artist_name_by_id = {a.get("artist_id"): a.get("Name") for a in artists}

    artist_models = [
        ArtistFromGenre(
            id=a.get("artist_id"),
            name=a.get("Name"),
            picture=a.get("Picture")
        )
        for a in artists
    ]

    album_models = [
        AlbumFromGenre(
            id=a.get("album_id"),
            name=a.get("Name"),
            picture=a.get("Picture"),
            artist=artist_name_by_id.get(a.get("primary_artist_id"))
        )
        for a in albums
    ]

    genre = Genre(
        id=genre_item.get("genre_id"),
        name=genre_item.get("Name"),
        albums=album_models,
        artists=artist_models,
    )
    return {"statusCode": 200, "headers": CORS_HEADERS, "body": asdict(genre)}

def _query_entities_for_genre(genre_id: str) -> list[dict]:
    items, lek = [], None
    while True:
        kwargs = {"KeyConditionExpression": Key("genre").eq(genre_id)}
        if lek:
            kwargs["ExclusiveStartKey"] = lek
        resp = content_genres_table.query(**kwargs)
        items.extend(resp.get("Items", []))
        lek = resp.get("LastEvaluatedKey")
        if not lek:
            break
    return items

def _batch_get_items(table_name: str, key_name: str, ids: list):
    if not ids:
        return []
    ddb = boto3.client("dynamodb")
    keys = [{key_name: {"S": _id}} for _id in ids]
    resp = ddb.batch_get_item(RequestItems={table_name: {"Keys": keys}})
    items = [
        {k: list(v.values())[0] for k, v in item.items()}
        for item in resp["Responses"].get(table_name, [])
    ]
    return items
