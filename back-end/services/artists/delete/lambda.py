from general_utils import response, file_exists_on_s3
from botocore.exceptions import ClientError
from pre_authorize import pre_authorize
from delete import delete_artist
from read import get_content
import boto3, os

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]

s3 = boto3.client('s3', os.environ["REGION"], endpoint_url=os.environ["S3_ENDPOINT_URL"])


@pre_authorize(['Admin'])
def lambda_handler(event, context):
    try:
        artist_id = event.get("pathParameters", {}).get("id")
        if not artist_id:
            return response(400, error="Missing artist ID")

        delete_artist(artist_id)

        for bucket, key in [
            (IMAGES_BUCKET, f"artists/{artist_id}.jpg"),
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
