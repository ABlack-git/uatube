import mongoengine as mongoe
from dataclasses import asdict
from uatube.scraper.client import SubscriptionDto, CommentDto


class Comment(mongoe.Document):
    comment_id = mongoe.StringField(primary_key=True)
    channel_id = mongoe.StringField(required=True)
    video_id = mongoe.StringField(required=True)

    published_at = mongoe.DateTimeField()
    text = mongoe.StringField()
    like_count = mongoe.IntField()

    author_id = mongoe.StringField()
    author_display_name = mongoe.StringField()
    author_channel_url = mongoe.URLField()

    meta = {
        "collection": "Comments",
        "indexes": ['channel_id', 'author_id']
    }

    @classmethod
    def from_dataclass(cls, data_cls: CommentDto) -> 'Comment':
        return cls(**asdict(data_cls))


class Subscription(mongoe.Document):
    subscription_id = mongoe.StringField(primary_key=True)
    # id of a user that created subscription
    subscriber_id = mongoe.StringField(required=True)
    # id of a channel that user subscribed to
    channel_id = mongoe.StringField(required=True)
    channel_title = mongoe.StringField()
    published_at = mongoe.DateTimeField(required=True)

    meta = {
        "collection": "Subscriptions",
        "indexes": ['channel_id', 'subscriber_id']
    }

    @classmethod
    def from_dataclass(cls, data_cls: SubscriptionDto) -> 'Subscription':
        return cls(**asdict(data_cls))


class ChannelDetails(mongoe.EmbeddedDocument):
    pass


class Channel(mongoe.Document):
    channel_id = mongoe.StringField(primary_key=True)
    channel_display_name = mongoe.StringField()
    channel_url = mongoe.URLField()
    from_subscriptions = mongoe.BooleanField(default=False)
    details = mongoe.EmbeddedDocumentField(ChannelDetails, required=False)

    meta = {"collection": "Channels"}
