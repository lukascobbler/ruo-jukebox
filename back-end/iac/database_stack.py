from aws_cdk import Stack, RemovalPolicy, aws_dynamodb as ddb, aws_s3 as s3
from constructs import Construct

class DatabaseStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.content_bucket = s3.Bucket(
            self, "ContentBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            cors=[s3.CorsRule(
                allowed_methods=[s3.HttpMethods.PUT, s3.HttpMethods.GET],
                allowed_origins=["*"],   # dev mode rn
                allowed_headers=["*"]
            )],
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        self.artists = ddb.Table(
            self, "Artists",
            partition_key=ddb.Attribute(name="artist_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        self.albums = ddb.Table(
            self, "Albums",
            partition_key=ddb.Attribute(name="album_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        self.tracks = ddb.Table(
            self, "Tracks",
            partition_key=ddb.Attribute(name="track_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )
        self.tracks.add_global_secondary_index(
            index_name="GSI1",
            partition_key=ddb.Attribute(name="album_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.NUMBER)
        )

        self.track_artists = ddb.Table(
            self, "TrackArtists",
            partition_key=ddb.Attribute(name="track_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="artist_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )
        self.track_artists.add_global_secondary_index(
            index_name="byArtist",
            partition_key=ddb.Attribute(name="artist_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="track_id", type=ddb.AttributeType.STRING)
        )

        self.track_genres = ddb.Table(
            self, "TrackGenres",
            partition_key=ddb.Attribute(name="genre", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="track_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )
        self.genres = ddb.Table(
            self, "Genres",
            partition_key=ddb.Attribute(name="genre_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        self.albums.add_global_secondary_index(
            index_name="byArtist",
            partition_key=ddb.Attribute(name="artist_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.NUMBER)
        )
        self.track_genres.add_global_secondary_index(
            index_name="byTrack",
            partition_key=ddb.Attribute(name="track_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="genre", type=ddb.AttributeType.STRING)
        )
        # Users profile (optional mirror of Cognito attrs; handy for FE)
        self.users = ddb.Table(
            self, "Users",
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Playlists
        self.playlists = ddb.Table(
            self, "Playlists",
            partition_key=ddb.Attribute(name="playlist_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )
        self.playlists.add_global_secondary_index(
            index_name="byOwner",
            partition_key=ddb.Attribute(name="owner_user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.NUMBER)
        )
        
        # Playlist items (fast remove & ordering)
        self.playlist_items = ddb.Table(
            self, "PlaylistItems",
            partition_key=ddb.Attribute(name="playlist_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="track_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )
        # ratings (1..3)
        self.ratings = ddb.Table(
            self, "Ratings",
            partition_key=ddb.Attribute(name="track_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )
        # GSI to list my ratings quickly (optional)
        self.ratings.add_global_secondary_index(
            index_name="byUser",
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="track_id", type=ddb.AttributeType.STRING)
        )
        self.subscriptions = ddb.Table(
            self, "Subscriptions",
            partition_key=ddb.Attribute(name="artist_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )
        self.subscriptions.add_global_secondary_index(
            index_name="byUser",
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="artist_id", type=ddb.AttributeType.STRING)
        )