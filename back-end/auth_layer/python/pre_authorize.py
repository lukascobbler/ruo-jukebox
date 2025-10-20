from authorization_exception import AuthorizationException
import inject_user_id
import verify_role
import os, json


def pre_authorize(allowed_groups: list):
    def decorator(handler):
        def wrapper(event, context):
            try:
                verify_role.verify_role(event, allowed_groups)
                inject_user_id.inject_user_id(event)
                return handler(event, context)
            except AuthorizationException as e:
                return {"statusCode": 401, "headers": json.loads(os.environ.get("CORS_HEADERS", "{}")), "body": str(e)}

        return wrapper

    return decorator
