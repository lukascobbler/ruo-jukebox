import json, os, boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

SONGS_TABLE = os.environ["SONGS_TABLE"]
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
TRANSCRIPTS_BUCKET = os.environ["TRANSCRIPTS_BUCKET"]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}


def lambda_handler(event, context):
    song_id = event["pathParameters"]["id"]

    # 1. Delete from DynamoDB
    dynamodb.Table(SONGS_TABLE).delete_item(Key={"id": song_id})

    # 2. Delete MP3 from S3
    audio_prefix = f"songs/{song_id}/"
    audio_objects = s3.list_objects_v2(Bucket=AUDIO_BUCKET, Prefix=audio_prefix).get("Contents", [])
    for obj in audio_objects:
        s3.delete_object(Bucket=AUDIO_BUCKET, Key=obj["Key"])

    # 3. Delete cover image
    cover_prefix = f"songs/{song_id}/cover/"
    cover_objects = s3.list_objects_v2(Bucket=IMAGES_BUCKET, Prefix=cover_prefix).get("Contents", [])
    for obj in cover_objects:
        s3.delete_object(Bucket=IMAGES_BUCKET, Key=obj["Key"])

    # 4. Delete transcripts
    transcript_prefix = f"songs/{song_id}/"
    transcript_objects = s3.list_objects_v2(Bucket=TRANSCRIPTS_BUCKET, Prefix=transcript_prefix).get("Contents", [])
    for obj in transcript_objects:
        s3.delete_object(Bucket=TRANSCRIPTS_BUCKET, Key=obj["Key"])

    return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({"message": "Song deleted successfully"})}
