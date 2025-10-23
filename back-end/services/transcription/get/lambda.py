from general_utils import response, file_exists_on_s3, get_lyrics_from_s3
import os

transcriptions_bucket = os.environ["TRANSCRIPTS_BUCKET"]

def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    song_id = path_params.get("id")

    if not song_id:
        return response(400, error="Missing song ID")

    key = f"transcriptions/{song_id}.txt"

    if not file_exists_on_s3(transcriptions_bucket, key):
        return response(200, {"lyrics": "Lyrics not found"})

    lyrics_text = get_lyrics_from_s3(transcriptions_bucket, key)

    return response(200, {"lyrics": lyrics_text})