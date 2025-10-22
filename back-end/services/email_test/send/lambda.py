from pre_authorize import pre_authorize
import boto3, os, json

ses = boto3.client("ses", region_name=os.environ.get("AWS_REGION", "eu-central-1"))
CORS_HEADERS = json.loads(os.environ.get("CORS_HEADERS", "{}"))
FROM_EMAIL = os.environ["FROM_EMAIL"]


@pre_authorize(['Admin', 'User'])
def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    recipient = body.get("to") or "test@example.com"
    subject = body.get("subject") or "Account Information"

    user_role = event.get("userRole", "Unknown")
    user_id = event.get("userId", "N/A")
    username = event.get("username", "N/A")
    email = event.get("email", "N/A")

    html_template = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; }}
            .container {{ background: white; padding: 20px; border-radius: 8px; }}
            h2 {{ color: #333; }}
            .info {{ margin-top: 10px; }}
            .info p {{ margin: 4px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Hello {username},</h2>
            <p>Your account details are shown below:</p>
            <div class="info">
                <p><b>User ID:</b> {user_id}</p>
                <p><b>Email:</b> {email}</p>
                <p><b>Role:</b> {user_role}</p>
            </div>
            <p style="margin-top:20px;">Thank you,<br>Team</p>
        </div>
    </body>
    </html>
    """

    response = ses.send_email(
        Source=FROM_EMAIL,
        Destination={"ToAddresses": [recipient]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Html": {"Data": html_template}}
        }
    )

    return {"statusCode": 200, "headers": CORS_HEADERS, "messageId": response["MessageId"], "sentTo": recipient}
