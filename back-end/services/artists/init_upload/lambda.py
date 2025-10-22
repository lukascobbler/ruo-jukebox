from general_utils import response, generate_s3_upload_url
from pre_authorize import pre_authorize
import os, uuid

images_bucket = os.environ["IMAGES_BUCKET"]

@pre_authorize(['Admin'])
def lambda_handler(event, context):
    artist_id = f"ARTIST~{uuid.uuid4()}"

    key = f"artists/{artist_id}.jpg"
    url = generate_s3_upload_url(images_bucket, key)

    return response(200, {"artistId": artist_id, "upload_url": url})