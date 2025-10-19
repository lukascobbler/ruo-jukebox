from authorization_exception import AuthorizationException


def inject_user_id(event: dict):
    authorizer = event.get('requestContext', {}).get('authorizer', {})
    claims = authorizer.get('claims', {})
    if not claims:
        raise AuthorizationException("No claims found in requestContext.authorizer")

    event["userId"] = claims.get("sub")

    return claims
