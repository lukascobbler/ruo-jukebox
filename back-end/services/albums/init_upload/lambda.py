from general_utils import response, generate_s3_upload_url
import json, os, uuid

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]


def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    album_id = f"ALBUM~{uuid.uuid4()}"
    cover = body.get("cover") == True
    no_songs = int(body.get("numberOfSongs", 0))
    cover_key = f"albums/{album_id}.jpg" if cover else None

    songs = []

    for i in range(no_songs):
        song_id = f"SONG~{uuid.uuid4()}"
        songs.append({
            "song_id": song_id,
            "audio_url": generate_s3_upload_url(AUDIO_BUCKET, f"songs/{song_id}.mp3"),
        })

    res = {
        "album_id": album_id,
        "songs": songs
    }

    if cover_key:
        res["cover_url"] = generate_s3_upload_url(IMAGES_BUCKET, cover_key)

    return response(200, res)
