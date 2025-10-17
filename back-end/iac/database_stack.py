from aws_cdk import (
    Stack, RemovalPolicy, Duration,
    aws_dynamodb as ddb,
    aws_s3 as s3,
)
from constructs import Construct

class DatabaseStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # songs bucket

        self.audio_bucket = s3.Bucket(
            self, "AudioBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            cors=[s3.CorsRule(
                allowed_methods=[s3.HttpMethods.PUT, s3.HttpMethods.GET, s3.HttpMethods.HEAD, s3.HttpMethods.DELETE],
                allowed_origins=["*"],   # TODO change cors everywhere
                allowed_headers=["*"],
                max_age=3000
            )],
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # images bucket
        self.images_bucket = s3.Bucket(
            self, "ImagesBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            cors=[s3.CorsRule(
                allowed_methods=[s3.HttpMethods.PUT, s3.HttpMethods.GET, s3.HttpMethods.HEAD, s3.HttpMethods.DELETE],
                allowed_origins=["*"],
                allowed_headers=["*"],
                max_age=3000
            )],
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # transcripts bucket TODO
        self.transcripts_bucket = s3.Bucket(
            self, "TranscriptsBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            cors=[s3.CorsRule(
                allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.HEAD],
                allowed_origins=["*"],
                allowed_headers=["*"]
            )],
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # core artists/albums/tracks/genres tables

        self.artists = ddb.Table(
            self, "Artists",
            partition_key=ddb.Attribute(name="artist_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES, # maybe we dont need this?
            removal_policy=RemovalPolicy.DESTROY,
        )

        # fast lookup by name
        self.artists.add_global_secondary_index(
            index_name="byName",
            partition_key=ddb.Attribute(name="name_lc", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.NUMBER),
        )

        self.albums = ddb.Table(
            self, "Albums",
            partition_key=ddb.Attribute(name="album_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES,   # subscribed notifications and feed update
            removal_policy=RemovalPolicy.DESTROY,
        )

        # fast lookup by artist
        self.albums.add_global_secondary_index(
            index_name="byArtist",
            partition_key=ddb.Attribute(name="primary_artist_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.NUMBER),
        )

        self.tracks = ddb.Table(
            self, "Tracks",
            partition_key=ddb.Attribute(name="track_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES,   # notify subscribers and start transcription
            removal_policy=RemovalPolicy.DESTROY,
        )

        # fast lookup for album and track order
        self.tracks.add_global_secondary_index(
            index_name="byAlbum",
            partition_key=ddb.Attribute(name="album_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="track_no", type=ddb.AttributeType.NUMBER),
        )

        self.genres = ddb.Table(
            self, "Genres",
            partition_key=ddb.Attribute(name="genre_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # many to many artists on tracks

        self.track_artists = ddb.Table(
            self, "TrackArtists",
            partition_key=ddb.Attribute(name="track_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="artist_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # getting all tracks for an artist
        self.track_artists.add_global_secondary_index(
            index_name="byArtist",
            partition_key=ddb.Attribute(name="artist_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="track_id", type=ddb.AttributeType.STRING),
        )

        # keeps track of genres for tracks/albums/artists
        self.content_genres = ddb.Table(
            self, "ContentGenres",
            partition_key=ddb.Attribute(name="genre", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="entity", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # fast lookup for all entities for a genre
        self.content_genres.add_global_secondary_index(
            index_name="byEntity",
            partition_key=ddb.Attribute(name="entity", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="genre", type=ddb.AttributeType.STRING),
        )

        # mirrors cognito
        self.users = ddb.Table(
            self, "Users",
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.playlists = ddb.Table(
            self, "Playlists",
            partition_key=ddb.Attribute(name="playlist_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # fast lookup of playlists by owner
        self.playlists.add_global_secondary_index(
            index_name="byOwner",
            partition_key=ddb.Attribute(name="owner_user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.NUMBER),
        )

        # playlist items with ordering
        self.playlist_items = ddb.Table(
            self, "PlaylistItems",
            partition_key=ddb.Attribute(name="playlist_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="position", type=ddb.AttributeType.NUMBER),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )
        
        # fast lookup of playlists containing a track (maybe not needed?)
        self.playlist_items.add_global_secondary_index(
            index_name="byTrack",
            partition_key=ddb.Attribute(name="track_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="playlist_id", type=ddb.AttributeType.STRING),
        )

        # rate anything (content_key = ALBUM#id, ARTIST#id, PLAYLIST#id, TRACK#id)
        self.ratings = ddb.Table(
            self, "Ratings",
            partition_key=ddb.Attribute(name="content_key", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES, # update rating sum for content
            removal_policy=RemovalPolicy.DESTROY,
        )

        # fast lookup of users ratings
        self.ratings.add_global_secondary_index(
            index_name="byUser",
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="content_key", type=ddb.AttributeType.STRING),
        )

        # also generic topic = ARTIST#id, GENRE#pop
        self.subscriptions = ddb.Table(
            self, "Subscriptions",
            partition_key=ddb.Attribute(name="topic", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            stream=ddb.StreamViewType.NEW_IMAGE, # refresh feed
            removal_policy=RemovalPolicy.DESTROY,
        )
        self.subscriptions.add_global_secondary_index(
            index_name="byUser",
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="topic", type=ddb.AttributeType.STRING),
        )

        self.interactions = ddb.Table(
            self, "Interactions",
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="ts", type=ddb.AttributeType.NUMBER),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            stream=ddb.StreamViewType.NEW_IMAGE, # refresh feed
            time_to_live_attribute="ttl",         # enable ttl to keep only recent interactions
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.feed = ddb.Table(
            self, "Feed",
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="item_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute="ttl",         # enable ttl to keep feed fresh
            removal_policy=RemovalPolicy.DESTROY,
        )

        # TODO
        self.transcriptions = ddb.Table(
            self, "Transcriptions",
            partition_key=ddb.Attribute(name="track_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )