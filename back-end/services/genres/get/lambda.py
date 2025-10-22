from pre_authorize import pre_authorize
from read import list_by_genre
from general_utils import response


@pre_authorize(["Admin", "User"])
def lambda_handler(event, context):
    albums_and_artists = list_by_genre()

    return response(200, albums_and_artists)