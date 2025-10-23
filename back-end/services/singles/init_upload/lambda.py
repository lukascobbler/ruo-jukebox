from general_utils import response, file_exists_on_s3, generate_s3_upload_url
from botocore.exceptions import ClientError
from pre_authorize import pre_authorize
import os, json, uuid

AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]


@pre_authorize(['Admin'])
def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        single_id = "SINGLE~" + str(uuid.uuid4())
        song_id = f"SONG~{uuid.uuid4()}"
        cover = body.get("cover") == True

        audio_key = f"songs/{song_id}.mp3"
        cover_key = f"singles/{single_id}.jpg" if cover else None

        audio_url = generate_s3_upload_url(AUDIO_BUCKET, audio_key)
        res = {
            "song_id": song_id,
            "single_id": single_id,
            "audio_url": audio_url
        }

        if cover_key:
            res["cover_url"] = generate_s3_upload_url(IMAGES_BUCKET, cover_key)

        return response(200, res)
    except ClientError as e:
        return response(500, error=f"AWS error: {str(e)}")
    except Exception as e:
        return response(500, error=f"Internal server error: {str(e)}")
