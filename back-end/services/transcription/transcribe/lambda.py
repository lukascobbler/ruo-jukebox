import os
import json
import boto3
import whisper
from urllib.parse import unquote_plus

s3 = boto3.client('s3', os.environ["REGION"], endpoint_url=os.environ["S3_ENDPOINT_URL"])

AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
TRANSCRIPTS_BUCKET = os.environ["TRANSCRIPTS_BUCKET"]
MODEL_TYPE = os.environ.get("MODEL_TYPE", "small")

MODEL_PATH = f"/models/{MODEL_TYPE}.pt"

whisper_model = None


def load_model():
    global whisper_model
    if whisper_model is None:
        print(f"Loading Whisper model from {MODEL_PATH}...")
        whisper_model = whisper.load_model(MODEL_PATH, device="cpu")
        print(f"Model {MODEL_TYPE} loaded successfully.")


def lambda_handler(event, context):
    try:
        load_model()

        for record in event.get("Records", []):
            body = json.loads(record["body"])
            bucket = body.get("bucket", AUDIO_BUCKET)
            key = unquote_plus(body["key"])

            print(f"Processing audio file: s3://{bucket}/{key}")

            filename = os.path.basename(key)
            base_name, _ = os.path.splitext(filename)
            input_path = f"/tmp/{filename}"
            output_path = f"/tmp/{base_name}.txt"

            print("Downloading audio from S3...")
            s3.download_file(bucket, key, input_path)

            print("Running Whisper transcription...")
            result = whisper_model.transcribe(input_path)
            lyrics = result.get("text", "").strip()
            print("Transcription completed.")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(lyrics)

            if key.startswith("songs/"):
                output_key = key.replace("songs/", "transcriptions/", 1)
            else:
                output_key = f"transcriptions/{key}"

            output_key = os.path.splitext(output_key)[0] + ".txt"

            print(f"Uploading lyrics to s3://{TRANSCRIPTS_BUCKET}/{output_key}")
            s3.upload_file(output_path, TRANSCRIPTS_BUCKET, output_key)

            try:
                os.remove(input_path)
                os.remove(output_path)
            except Exception as cleanup_err:
                print(f"Cleanup warning: {cleanup_err}")

            print(f"Finished processing {filename}")

        return {
            "statusCode": 200,
            "body": json.dumps("All transcriptions completed successfully."),
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error: {str(e)}"),
        }
