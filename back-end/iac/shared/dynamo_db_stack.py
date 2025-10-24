from aws_cdk import NestedStack, RemovalPolicy, aws_dynamodb as ddb
from aws_cdk.aws_dynamodb import Attribute, AttributeType
from constructs import Construct


class DynamoDbStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str, branch: str, **kwargs):
        super().__init__(scope, stack_id, **kwargs)

        suffix = f"-{branch}" if branch != "main" else ""

        # Content Table (ARTIST, ALBUM, SINGLE, SONG, GENRE)
        self.content = ddb.Table(
            self, "ContentTable",
            table_name=f"ContentTable{suffix}",
            partition_key=Attribute(name="PK", type=AttributeType.STRING),
            sort_key=Attribute(name="SK", type=AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # for search by name
        self.content.add_global_secondary_index(
            index_name="byName",
            partition_key=Attribute(name="name_lc", type=AttributeType.STRING),
            sort_key=Attribute(name="content_type", type=AttributeType.STRING)
        )

        # get by type
        self.content.add_global_secondary_index(
            index_name="byType",
            partition_key=Attribute(name="content_type", type=AttributeType.STRING),
            sort_key=Attribute(name="SK", type=AttributeType.STRING)
        )

        # Userdata Table (Users, Playlists, Ratings, Subscriptions)
        self.userdata = ddb.Table(
            self, "UserdataTable",
            table_name=f"UserdataTable{suffix}",
            partition_key=Attribute(name="user_id", type=AttributeType.STRING),
            sort_key=Attribute(name="SK", type=AttributeType.STRING),
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES,
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # ratings lookup by song
        self.userdata.add_global_secondary_index(
            index_name="ratingBySong",
            partition_key=Attribute(name="song_id", type=AttributeType.STRING),
            sort_key=Attribute(name="rating_user", type=AttributeType.STRING)
        )

        # subscriptions lookup by topic
        self.userdata.add_global_secondary_index(
            index_name="getSubscribed",
            partition_key=Attribute(name="sub_id", type=AttributeType.STRING)
        )

        # Interactions Table
        self.interactions = ddb.Table(
            self, "InteractionsTable",
            table_name=f"InteractionsTable{suffix}",
            partition_key=Attribute(name="user_id", type=AttributeType.STRING),
            sort_key=Attribute(name="ts", type=AttributeType.STRING),
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES,
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl"
        )

        # Feed Table
        self.feed = ddb.Table(
            self, "FeedTable",
            table_name=f"FeedTable{suffix}",
            partition_key=Attribute(name="user_id", type=AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
