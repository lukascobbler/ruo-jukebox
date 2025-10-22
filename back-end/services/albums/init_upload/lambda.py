from general_utils import response, generate_s3_upload_url
import json, os, uuid

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]

def lambda_handler(event, context):
    body = json.loads(event.get("body"))

    try:
        number_of_songs = int(body["numberOfSongs"])
        wants_cover = bool(body["wantsCover"])
    except Exception:
        return response(400, error="Number of songs or cover request not defined correctly")

    album_id = f"ALBUM~{uuid.uuid4()}"

    response_body = {}
    response_body["album_id"] = album_id

    if wants_cover:
        cover_key = f"albums/{album_id}.jpg"
        response_body["cover_url"] = generate_s3_upload_url(IMAGES_BUCKET, cover_key)

    response_body["upload_urls"] = []
    for _ in range(number_of_songs):
        song_id = f"SONG~{uuid.uuid4()}"
        audio_key = f"songs/{song_id}.mp3"
        audio_url = generate_s3_upload_url(audio_key)
        response_body["upload_urls"].append({
            "id": song_id,
            "url": generate_s3_upload_url(AUDIO_BUCKET, audio_url)
        })

    return response(200, **response_body)