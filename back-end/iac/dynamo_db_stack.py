from constructs import Construct
from aws_cdk import PhysicalName
from aws_cdk import (
    Stack, RemovalPolicy,
    aws_dynamodb as ddb
)

class DynamoDbStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.artists = ddb.Table(
            self, "Artists",
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="artist_id", type=ddb.AttributeType.STRING),
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES, # maybe we dont need this?
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )

        # fast lookup by name
        self.artists.add_global_secondary_index(
            index_name="byName",
            partition_key=ddb.Attribute(name="name_lc", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.NUMBER),
        )

        self.albums = ddb.Table(
            self, "Albums",
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="album_id", type=ddb.AttributeType.STRING),
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES,   # subscribed notifications and feed update
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )

        self.albums.add_global_secondary_index(
            index_name="byReleased",
            partition_key=ddb.Attribute(name="released", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.NUMBER),
        )

        # many to many artists on albums
        self.album_artists = ddb.Table(
            self, "AlbumArtists",
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="album_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="artist_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )

        # getting all tracks for an artist
        self.album_artists.add_global_secondary_index(
            index_name="byArtist",
            partition_key=ddb.Attribute(name="artist_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="album_id", type=ddb.AttributeType.STRING),
        )

        self.songs = ddb.Table(
            self, "Songs",
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="song_id", type=ddb.AttributeType.STRING),
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES,   # notify subscribers and start transcription
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )

        # fast lookup for album and song order
        self.songs.add_global_secondary_index(
            index_name="byAlbum",
            partition_key=ddb.Attribute(name="album_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="song_no", type=ddb.AttributeType.NUMBER)
        )

        # fast lookup for singles
        self.songs.add_global_secondary_index(
            index_name="byHasAlbum",
            partition_key=ddb.Attribute(name="has_album", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_at", type=ddb.AttributeType.NUMBER),
        )

        self.genres = ddb.Table(
            self, "Genres",
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="PK", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="genre_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )

        # many to many artists on songs
        self.song_artists = ddb.Table(
            self, "SongArtists",
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="song_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="artist_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )

        # getting all songs for an artist
        self.song_artists.add_global_secondary_index(
            index_name="byArtist",
            partition_key=ddb.Attribute(name="artist_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="song_id", type=ddb.AttributeType.STRING),
        )

        # keeps track of genres for songs/albums/artists
        self.content_genres = ddb.Table(
            self, "ContentGenres",
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="genre", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="entity", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
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
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )

        # fast lookup of users by email
        self.users.add_global_secondary_index(
            index_name="byEmail",
            partition_key=ddb.Attribute(name="email", type=ddb.AttributeType.STRING),
            projection_type=ddb.ProjectionType.ALL,
        )

        self.playlists = ddb.Table(
            self, "Playlists",
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="playlist_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
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
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="playlist_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="position", type=ddb.AttributeType.NUMBER),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )

        # rate songs (song_id = id) -- new
        self.ratings = ddb.Table(
            self, "Ratings",
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="song_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES, # update rating sum for content
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )

        # fast lookup of users song-ratings
        self.ratings.add_global_secondary_index(
            index_name="byUser",
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="song_id", type=ddb.AttributeType.STRING),
        )

        # also generic topic = ARTIST#id, GENRE#pop
        self.subscriptions = ddb.Table(
            self, "Subscriptions",
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="topic", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            stream=ddb.StreamViewType.NEW_IMAGE, # refresh feed
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )
        
        self.subscriptions.add_global_secondary_index(
            index_name="byUser",
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="topic", type=ddb.AttributeType.STRING),
        )

        self.interactions = ddb.Table(
            self, "Interactions",
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="ts", type=ddb.AttributeType.NUMBER),
            stream=ddb.StreamViewType.NEW_IMAGE, # refresh feed
            time_to_live_attribute="ttl",         # enable ttl to keep only recent interactions
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )

        self.feed = ddb.Table(
            self, "Feed",
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="item_id", type=ddb.AttributeType.STRING),
            time_to_live_attribute="ttl",         # enable ttl to keep feed fresh
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )

        self.transcriptions = ddb.Table(
            self, "Transcriptions",
            table_name=PhysicalName.GENERATE_IF_NEEDED,
            partition_key=ddb.Attribute(name="song_id", type=ddb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=ddb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1
        )