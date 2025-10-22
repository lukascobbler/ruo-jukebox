from general_utils import generate_s3_download_url, response
from pre_authorize import pre_authorize
from read import list_singles
import os

AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]


@pre_authorize(['Admin'])
def lambda_handler(event, context):
    all_singles = list_singles()

    for single in all_singles:
        if "cover_key" in single:
            single["cover_url"] = generate_s3_download_url(IMAGES_BUCKET, single["cover_key"])

    return response(200, all_singles)
