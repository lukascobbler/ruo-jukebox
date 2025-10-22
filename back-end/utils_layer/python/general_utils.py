from botocore.exceptions import ClientError
from read import get_contents
from typing import Any
import boto3
import json
import os

CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))
s3 = boto3.client('s3', os.environ["REGION"], endpoint_url=os.environ["S3_ENDPOINT_URL"])


def response(status: int, body: dict, error: str | None = None):
    body = {"message": error} if error else body
    return {"statusCode": status, "headers": CORS_HEADERS, "body": json.dumps(body, default=str)}


def generate_s3_download_url(bucket, key):
    if not key: return None
    return s3.generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=3600)


def generate_s3_upload_url(bucket, key):
    if not key: return None
    return s3.generate_presigned_url("put_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=120)


def file_exists_on_s3(bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
    except ClientError as _:
        return False
    return True


def get_genre_objects(genres: list[str]) -> tuple[list[dict[str, Any]] | None, str]:
    if not genres or not isinstance(genres, list) or len(genres) == 0:
        return None, "Field 'genres' must contain at least one genre"
    for genre in genres:
        if not genre or not isinstance(genre, str) or not genre.startswith("GENRE~"):
            return None, "Each genre must be a valid 'genre_id' starting with 'GENRE~'"
    genre_items = get_contents(genres)
    if len(genre_items) != len(genres):
        return None, "Some genres not found"
    return [{"genre_id": g["PK"], "name": g["name"]} for g in genre_items], "Success"


def get_artist_objects(artists: list[str]) -> tuple[list[dict[str, Any]] | None, str]:
    if not artists or not isinstance(artists, list) or len(artists) == 0:
        return None, "Field 'artists' must contain at least one artist"
    for artist in artists:
        if not artist or not isinstance(artist, str) or not artist.startswith("ARTIST~"):
            return None, "Each artist must be a valid 'artist_id' starting with 'ARTIST~'"
    artist_items = get_contents(artists)
    if len(artist_items) != len(artists):
        return None, "Some artists not found"
    return [{"artist_id": g["PK"], "name": g["name"]} for g in artist_items], "Success"
