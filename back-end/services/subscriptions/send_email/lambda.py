import os, json, boto3

ses = boto3.client("ses", region_name=os.environ.get("AWS_REGION", "eu-central-1"))
FROM_EMAIL  = os.environ["FROM_EMAIL"]

def _fmt_list(xs):
    xs = [x for x in (xs or []) if x]
    return ", ".join(xs) if xs else "N/A"

def lambda_handler(event, context):
    for record in event.get("Records", []):
        try:
            body = json.loads(record["body"])
        except Exception:
            continue

        to = body.get("to")
        if not to:
            continue
        
        subject = body.get("subject")
        html    = body.get("html")

        if not subject or not html:
            name         = body.get("name", "New content")
            artist_names = body.get("artist_names", [])
            genre_names  = body.get("genre_names", [])
            type = body.get('type', "type")

            artists_str = _fmt_list(artist_names)
            genres_str  = _fmt_list(genre_names)

            subject = f"New {type}: {name}"
            html = f"""
            <html><body>
                <p><strong>New {type}</strong> '<em>{name}</em>'</p>
                <p><strong>Artists:</strong> {artists_str}</p>
                <p><strong>Genres:</strong> {genres_str}</p>
            </body></html>
            """

        ses.send_email(
            Source=FROM_EMAIL,
            Destination={"ToAddresses": [to]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Html": {"Data": html}}
            }
        )
