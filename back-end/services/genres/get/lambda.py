from general_utils import response, generate_s3_download_url
from pre_authorize import pre_authorize
from read import list_by_genre
import os

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]

@pre_authorize(["Admin", "User"])
def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    genre_id = path_params.get("id")

    if not genre_id:
        return response(400, error="Missing genre ID")

    content = list_by_genre(genre_id)

    for artist in content["artists"]:
        if "cover_key" in artist:
            artist["cover_url"] = generate_s3_download_url(IMAGES_BUCKET, artist["cover_key"])

    for album in content["albums"]:
        if "cover_key" in album:
            album["cover_url"] = generate_s3_download_url(IMAGES_BUCKET, album["cover_key"])

    return response(200, content)