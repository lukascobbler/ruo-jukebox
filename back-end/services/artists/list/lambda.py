from general_utils import response, generate_s3_download_url
from pre_authorize import pre_authorize
from read import list_artists
import os

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]


@pre_authorize(['Admin', 'User'])
def lambda_handler(event, context):
    artists = list_artists()

    for artist in artists:
        if "cover_key" in artist:
            artist["cover_url"] = generate_s3_download_url(IMAGES_BUCKET, artist["cover_key"])

    return response(200, artists)
