import json

def main(event, context):
    """
    Lambda handler for user service.
    """
    print("Received event:", json.dumps(event))

    # Example response
    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": "Hello from User Lambda!",
            "input": event
        })
    }

    return response
