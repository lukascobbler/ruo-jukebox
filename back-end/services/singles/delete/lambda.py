from general_utils import response, file_exists_on_s3
from botocore.exceptions import ClientError
from pre_authorize import pre_authorize
from delete import delete_single
from read import get_content
import boto3, os

AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
TRANSCRIPTS_BUCKET = os.environ.get("TRANSCRIPTS_BUCKET", "")

s3 = boto3.client('s3', os.environ["REGION"], endpoint_url=os.environ["S3_ENDPOINT_URL"])


@pre_authorize(['Admin'])
def lambda_handler(event, context):
    try:
        single_id = event.get("pathParameters", {}).get("id")
        if not single_id:
            return response(400, error="Missing single ID")

        single = get_content(single_id)
        audio_key = single.get("audio_key", None)
        transcription_key = single.get("transcription_key")
        delete_single(single_id)

        for bucket, key in [
            (AUDIO_BUCKET, audio_key),
            (IMAGES_BUCKET, f"singles/{single_id}.jpg"),
            (TRANSCRIPTS_BUCKET, transcription_key if TRANSCRIPTS_BUCKET else None),
        ]:
            if key and file_exists_on_s3(bucket, key):
                _safe_delete_s3(bucket, key)

        return response(200, {"message": "Song and related data deleted successfully"})

    except ClientError as e:
        return response(500, error=f"AWS error: {str(e)}")
    except Exception as e:
        return response(500, error=f"Internal server error: {str(e)}")


def _safe_delete_s3(bucket, key):
    try:
        s3.delete_object(Bucket=bucket, Key=key)
    except Exception:
        pass
