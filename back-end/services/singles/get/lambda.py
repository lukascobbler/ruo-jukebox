from general_utils import generate_s3_download_url, response
from read import get_content
from pre_authorize import pre_authorize
import os

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]

@pre_authorize(['User', 'Admin'])
def lambda_handler(event, context):
    single_id = event.get("pathParameters", {}).get("id")
    if not single_id:
        return response(400, {"error": "Missing single id"})

    single = get_content(single_id)

    if "cover_key" in single:
        single["cover_url"] = generate_s3_download_url(IMAGES_BUCKET, single["cover_key"])

    return response(200, single)
