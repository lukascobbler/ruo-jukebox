from general_utils import response, generate_s3_download_url
from pre_authorize import pre_authorize
from urllib.parse import unquote
from read import search
import os

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]

@pre_authorize(["Admin", "User"])
def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    query = path_params.get("query")
    query = unquote(query)

    if not query:
        return response(400, error="Missing query")

    result = search(query)

    for artist in result["artists"]:
        if "cover_key" in artist:
            artist["cover_url"] = generate_s3_download_url(IMAGES_BUCKET, artist["cover_key"])

    for album in result["albums"]:
        if "cover_key" in album:
            album["cover_url"] = generate_s3_download_url(IMAGES_BUCKET, album["cover_key"])

    for song in result["songs"]:
        if "cover_key" in song:
            song["cover_url"] = generate_s3_download_url(IMAGES_BUCKET, song["cover_key"])

    return response(200, result)