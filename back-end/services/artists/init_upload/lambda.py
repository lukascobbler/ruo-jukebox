from general_utils import response, generate_s3_upload_url
from pre_authorize import pre_authorize
import os, uuid, json

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]


@pre_authorize(['Admin'])
def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    artist_id = f"ARTIST~{uuid.uuid4()}"
    cover = body.get("cover") == True

    cover_key = f"artists/{artist_id}.jpg" if cover else None
    res = {"artist_id": artist_id}
    if cover_key: res["cover_url"] = generate_s3_upload_url(IMAGES_BUCKET, cover_key)

    return response(200, res)
