from general_utils import response, generate_s3_download_url
from pre_authorize import pre_authorize
from read import list_artists

@pre_authorize(['Admin', 'User'])
def lambda_handler(event, context):
    artists = list_artists()

    for artist in artists:
        artist["cover_url"] = generate_s3_download_url(artist["cover_key"])

    return response(200, artists)