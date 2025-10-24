from general_utils import generate_s3_download_url, response
from read import songs_for_album, get_content
from pre_authorize import pre_authorize
import os

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]


@pre_authorize(['Admin', 'User'])
def lambda_handler(event, context):
    album_id = event.get("pathParameters", {}).get("id")
    if not album_id:
        return response(400, {"error": "Missing album id"})

    album = get_content(album_id)

    if "cover_key" in album:
        album["cover_url"] = generate_s3_download_url(IMAGES_BUCKET, album["cover_key"])

    all_songs_for_album = songs_for_album(album_id.strip())
    for song in all_songs_for_album:
        song["audio_url"] = generate_s3_download_url(AUDIO_BUCKET, song["audio_key"])

    album["songs"] = all_songs_for_album

    return response(200, album)
