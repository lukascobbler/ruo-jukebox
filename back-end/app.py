import aws_cdk

from iac.api_gateway_stack import ApiGatewayStack
from iac.cognito_stack import CognitoStack
from iac.domain_stacks.albums_stack import AlbumsStack
from iac.domain_stacks.artists_stack import ArtistsStack
from iac.domain_stacks.genres_stack import GenresStack
from iac.domain_stacks.interactions_stack import InteractionsStack
from iac.domain_stacks.playlists_stack import PlaylistsStack
from iac.domain_stacks.songs_stack import SongsStack
from iac.domain_stacks.subscriptions_stack import SubscriptionsStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack


def generate_environment(cognito, dynamo_db: DynamoDbStack, s3_bucket: S3Stack):
    return {
            "AUDIO_BUCKET": s3_bucket.audio_bucket.bucket_name,
            "IMAGES_BUCKET": s3_bucket.images_bucket.bucket_name,
            "TRANSCRIPTS_BUCKET": s3_bucket.transcripts_bucket.bucket_name,
            "ARTISTS_TABLE": dynamo_db.artists.table_name,
            "ALBUMS_TABLE": dynamo_db.albums.table_name,
            "TRACKS_TABLE": dynamo_db.tracks.table_name,
            "TRACK_ARTISTS_TABLE": dynamo_db.track_artists.table_name,
            "GENRES_TABLE": dynamo_db.genres.table_name,
            "CONTENT_GENRES_TABLE": dynamo_db.content_genres.table_name,
            "USERS_TABLE": dynamo_db.users.table_name,
            "PLAYLISTS_TABLE": dynamo_db.playlists.table_name,
            "PLAYLIST_ITEMS_TABLE": dynamo_db.playlist_items.table_name,
            "RATINGS_TABLE": dynamo_db.ratings.table_name,
            "SUBSCRIPTIONS_TABLE": dynamo_db.subscriptions.table_name,
            "INTERACTIONS_TABLE": dynamo_db.interactions.table_name,
            "FEED_TABLE": dynamo_db.feed.table_name,
            "TRANSCRIPTIONS_TABLE": dynamo_db.transcriptions.table_name,
            "USER_POOL_ID": cognito.user_pool.user_pool_id,
            "USER_POOL_CLIENT_ID": cognito.app_client.user_pool_client_id,
            # Email (SES verified sender) TODO wtf
            "FROM_EMAIL": "no-reply@jukebox.example.com",
        }


REGION = 'eu-central-1'
app = aws_cdk.App()

cognito_stack = CognitoStack(app, "CognitoStack")
dynamo_db_stack = DynamoDbStack(app, "DynamoDbStack")
s3_stack = S3Stack(app, "S3Stack")
api_gateway = ApiGatewayStack(app, "ApiGatewayStack")
env = generate_environment(cognito_stack, dynamo_db_stack, s3_stack)

albums = AlbumsStack(
    app, "AlbumsStack", cognito_stack, dynamo_db_stack, s3_stack, api_gateway, env
)

artists = ArtistsStack(
    app, "ArtistsStack", cognito_stack, dynamo_db_stack, s3_stack, api_gateway, env
)

genres = GenresStack(
    app, "GenresStack", cognito_stack, dynamo_db_stack, s3_stack, api_gateway, env
)

interactions = InteractionsStack(
    app, "InteractionsStack", dynamo_db_stack, env
)

playlists = PlaylistsStack(
    app, "PlaylistsStack", cognito_stack, dynamo_db_stack, s3_stack, api_gateway, env
)

songs = SongsStack(
    app, "SongsStack", cognito_stack, dynamo_db_stack, s3_stack, api_gateway, env
)

subscriptions = SubscriptionsStack(
    app, "SubscriptionsStack", cognito_stack, dynamo_db_stack, s3_stack, api_gateway, env
)

app.synth()