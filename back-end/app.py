from iac.domain_stacks.subscriptions_stack import SubscriptionsStack
from iac.domain_stacks.interactions_stack import InteractionsStack
from iac.domain_stacks.email_test_stack import EmailTestStack
from iac.domain_stacks.playlists_stack import PlaylistsStack
from iac.domain_stacks.artists_stack import ArtistsStack
from iac.domain_stacks.albums_stack import AlbumsStack
from iac.domain_stacks.genres_stack import GenresStack
from iac.domain_stacks.songs_stack import SongsStack
from iac.shared_layer_stack import SharedLayerStack
from iac.domain_stacks.auth_stack import AuthStack
from iac.api_gateway_stack import ApiGatewayStack
from iac.auth_layer_stack import AuthLayerStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.cognito_stack import CognitoStack
from iac.email_stack import EmailStack
from aws_cdk import App, Environment
from iac.s3_stack import S3Stack
import os

app = App()
ENV = Environment(account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION"))

# shared resources
cognito_stack = CognitoStack(app, "CognitoStack", env=ENV)
dynamo_db_stack = DynamoDbStack(app, "DynamoDbStack", env=ENV)
s3_stack = S3Stack(app, "S3Stack", env=ENV)
shared_layer_stack = SharedLayerStack(app, "SharedLayerStack", env=ENV)
auth_layer_stack = AuthLayerStack(app, "AuthLayerStack", env=ENV)
email_stack = EmailStack(app, "EmailStack", env=ENV)

env_vars = {
    "AUDIO_BUCKET": s3_stack.audio_bucket.bucket_name,
    "IMAGES_BUCKET": s3_stack.images_bucket.bucket_name,
    "TRANSCRIPTS_BUCKET": s3_stack.transcripts_bucket.bucket_name,
    "ARTISTS_TABLE": dynamo_db_stack.artists.table_name,
    "ALBUMS_TABLE": dynamo_db_stack.albums.table_name,
    "ALBUM_ARTISTS_TABLE": dynamo_db_stack.album_artists.table_name,
    "SONGS_TABLE": dynamo_db_stack.songs.table_name,
    "SONG_ARTISTS_TABLE": dynamo_db_stack.song_artists.table_name,
    "GENRES_TABLE": dynamo_db_stack.genres.table_name,
    "CONTENT_GENRES_TABLE": dynamo_db_stack.content_genres.table_name,
    "USERS_TABLE": dynamo_db_stack.users.table_name,
    "PLAYLISTS_TABLE": dynamo_db_stack.playlists.table_name,
    "PLAYLIST_ITEMS_TABLE": dynamo_db_stack.playlist_items.table_name,
    "RATINGS_TABLE": dynamo_db_stack.ratings.table_name,
    "SUBSCRIPTIONS_TABLE": dynamo_db_stack.subscriptions.table_name,
    "INTERACTIONS_TABLE": dynamo_db_stack.interactions.table_name,
    "FEED_TABLE": dynamo_db_stack.feed.table_name,
    "TRANSCRIPTIONS_TABLE": dynamo_db_stack.transcriptions.table_name,
    "USER_POOL_ID": cognito_stack.user_pool.user_pool_id,
    "USER_POOL_CLIENT_ID": cognito_stack.app_client.user_pool_client_id,
    "REGION": str(os.getenv("CDK_DEFAULT_REGION")),
    "S3_ENDPOINT_URL": 'https://s3.' + str(os.getenv("CDK_DEFAULT_REGION")) + '.amazonaws.com',
    "FROM_EMAIL": "noreply@jb.moma.rs",
}

# API Gateway
api_gateway = ApiGatewayStack(app, "ApiGatewayStack", user_pool=cognito_stack.user_pool, env=ENV)

# Email test stack
email_test_stack = EmailTestStack(app, "EmailTestStack", dynamo_db_stack, s3_stack, shared_layer_stack, auth_layer_stack, api_gateway, email_stack, env_vars, env=ENV)

# Auth stack
auth_stack = AuthStack(app, "AuthStack", cognito_stack, dynamo_db_stack, s3_stack, shared_layer_stack, auth_layer_stack, api_gateway, env_vars, env=ENV)

# Domain stacks
albums = AlbumsStack(app, "AlbumsStack", dynamo_db_stack, s3_stack, shared_layer_stack, auth_layer_stack, api_gateway, env_vars, env=ENV)

artists = ArtistsStack(app, "ArtistsStack", dynamo_db_stack, s3_stack, shared_layer_stack, auth_layer_stack, api_gateway, env_vars, env=ENV)

genres = GenresStack(app, "GenresStack", dynamo_db_stack, s3_stack, shared_layer_stack, auth_layer_stack, api_gateway, env_vars, env=ENV)

interactions = InteractionsStack(app, "InteractionsStack", dynamo_db_stack, env_vars, env=ENV)

playlists = PlaylistsStack(app, "PlaylistsStack", dynamo_db_stack, s3_stack, shared_layer_stack, auth_layer_stack, api_gateway, env_vars, env=ENV)

songs = SongsStack(app, "SongsStack", cognito_stack, dynamo_db_stack, s3_stack, shared_layer_stack, auth_layer_stack, api_gateway, env_vars, env=ENV)

subscriptions = SubscriptionsStack(app, "SubscriptionsStack", dynamo_db_stack, s3_stack, shared_layer_stack, auth_layer_stack, api_gateway, env_vars, env=ENV)

app.synth()
