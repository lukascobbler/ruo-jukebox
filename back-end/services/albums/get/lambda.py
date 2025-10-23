from general_utils import generate_s3_download_url, response
from pre_authorize import pre_authorize
from read import songs_for_album
import os

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]


@pre_authorize(['Admin', 'User'])
def lambda_handler(event, context):
    album_id = event.get("pathParameters", {}).get("id")
    if not album_id:
        return response(400, {"error": "Missing album id"})

    all_songs_for_album = songs_for_album(album_id.strip())
    for song in all_songs_for_album:
        song["audio_url"] = generate_s3_download_url(IMAGES_BUCKET, song["audio_key"])

    return response(200, all_songs_for_album)
