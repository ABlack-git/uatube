import typing as t
from dataclasses import dataclass
from datetime import datetime
from googleapiclient.errors import HttpError


@dataclass
class CommentDto:
    comment_id: str
    channel_id: str
    video_id: str

    published_at: datetime
    text: str
    like_count: int

    author_id: str
    author_display_name: str
    author_channel_url: str


@dataclass
class SubscriptionDto:
    subscription_id: str
    subscriber_id: str
    published_at: datetime

    channel_id: str
    channel_title: str


def get_channel_video_ids(youtube, channel_id) -> t.List[str]:
    response = youtube.search().list(
        part='id',
        channelId=channel_id,
        type='video',
        maxResults=10,
        order='date'
    ).execute()

    return [item['id']['videoId'] for item in response['items']]


def get_comments_for_video(youtube, video_id) -> t.List[CommentDto]:
    response = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText',
        maxResults=100
    ).execute()

    comments = []
    for item in response['items']:
        snippet = item['snippet']
        top_level_comment = snippet['topLevelComment']['snippet']
        comment = CommentDto(
            comment_id=item['id'],
            channel_id=snippet['channelId'],
            video_id=snippet['videoId'],
            published_at=str_to_datetime(top_level_comment['publishedAt']),
            text=top_level_comment['textDisplay'],
            author_id=top_level_comment['authorChannelId']['value'],
            author_display_name=top_level_comment['authorDisplayName'],
            author_channel_url=top_level_comment['authorChannelUrl'],
            like_count=top_level_comment.get('likeCount')
        )
        comments.append(comment)
    return comments


def get_channel_subscriptions(youtube, channel_id) -> t.Optional[t.List[SubscriptionDto]]:
    params = {"channelId": channel_id, "part": 'snippet', "maxResults": 50}
    subscriptions = []
    try:
        for response_page in _paginator(youtube.subscriptions, params):
            for item in response_page['items']:
                snippet = item['snippet']
                subscription = SubscriptionDto(
                    subscription_id=item['id'],
                    subscriber_id=channel_id,
                    published_at=str_to_datetime(snippet['publishedAt']),
                    channel_id=snippet['resourceId']['channelId'],
                    channel_title=snippet.get('title')
                )
                subscriptions.append(subscription)
        return subscriptions
    except HttpError:
        return None


def get_channel_info(youtube, channel_id):
    pass


def _paginator(func: t.Callable, params: dict):
    response = func().list(
        **params
    ).execute()
    yield response

    while next_page_token := response.get('nextPageToken'):
        response = func().list(
            **params,
            pageToken=next_page_token
        ).execute()
        yield response


def str_to_datetime(dt_str: str):
    if "." in dt_str:
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")
