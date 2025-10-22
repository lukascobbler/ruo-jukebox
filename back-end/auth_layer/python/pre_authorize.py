from authorization_exception import AuthorizationException
from inject_userdata import inject_userdata
from verify_role import verify_role
from general_utils import response


def pre_authorize(allowed_groups: list):
    def decorator(handler):
        def wrapper(event, context):
            try:
                verify_role(event, allowed_groups)
                inject_userdata(event)
                return handler(event, context)
            except AuthorizationException as e:
                return response(401, error=str(e))

        return wrapper

    return decorator
