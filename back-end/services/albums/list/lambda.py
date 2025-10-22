from general_utilities import response, generate_s3_download_url
from read import list_albums
import os

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]

def lambda_handler(event, context):
    all_albums = list_albums()

    for album in all_albums:
        if "cover_key" in album:
            album["cover_url"] = generate_s3_download_url(IMAGES_BUCKET, album["cover_key"])

    return response(200, all_albums)