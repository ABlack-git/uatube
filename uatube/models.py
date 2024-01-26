import mongoengine as mongoe
import datetime as dt
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
    found_from_channel = mongoe.ListField(mongoe.StringField())
    details = mongoe.EmbeddedDocumentField(ChannelDetails, required=False)
    has_opened_subscriptions = mongoe.BooleanField(default=False)
    meta = {"collection": "Channels"}


class SubscriptionCheckpoint(mongoe.Document):
    channel_id = mongoe.StringField()
    channel_order = mongoe.IntField()
    next_page_token = mongoe.StringField()
    has_next_page = mongoe.BooleanField()
    run_id = mongoe.StringField()
    created_at = mongoe.DateTimeField(default=dt.datetime.utcnow)
    meta = {"collection": "SubscriptionCheckpoint"}
