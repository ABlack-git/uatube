import math
import typing as t
from dataclasses import dataclass
from datetime import datetime
from googleapiclient.errors import HttpError


@dataclass
class Meta:
    prev_page_token: str | None
    next_page_token: str | None
    total_results: int
    results_per_page: int


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


def get_channel_video_ids(youtube, channel_id, max_results=50) -> t.List[str]:
    response = youtube.search().list(
        part='id',
        channelId=channel_id,
        type='video',
        maxResults=max_results,
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


def get_channel_subscriptions(
        youtube,
        channel_id,
        next_page_token=None) -> t.Tuple[t.Optional[t.List[SubscriptionDto]], t.Optional[Meta]]:
    try:
        response = youtube.subscriptions().list(channelId=channel_id, part='snippet', maxResults=50,
                                                pageToken=next_page_token).execute()
    except HttpError as e:
        if e.error_details[0]['reason'] in ('subscriptionForbidden', 'accountClosed', 'accountSuspended'):
            return None, None
        raise e

    page_info = response.get('pageInfo')
    meta = Meta(
        prev_page_token=response.get('prevPageToken'),
        next_page_token=response.get('nextPageToken'),
        total_results=None if page_info is None else page_info.get('totalResults'),
        results_per_page=None if page_info is None else page_info.get('resultsPerPage')
    )

    subscriptions = []
    for item in response['items']:
        snippet = item['snippet']
        subscription = SubscriptionDto(
            subscription_id=item['id'],
            subscriber_id=channel_id,
            published_at=str_to_datetime(snippet['publishedAt']),
            channel_id=snippet['resourceId']['channelId'],
            channel_title=snippet.get('title')
        )
        subscriptions.append(subscription)

    return subscriptions, meta


def get_channel_info(youtube, channel_id):
    pass


class Paginator:
    def __init__(self, func, start_page_token, **kwargs):
        self.func = func
        self.next_page_token = start_page_token
        self.kwargs = kwargs
        self.len = None
        self.index = 0

        self.resp = None
        self.meta = None
        self.return_cached = False

    def __len__(self):
        if self.len is None:
            _, meta = next(self)
            self.return_cached = True
            if meta is None:
                self.len = 0
                return self.len
            self.len = math.ceil(meta.total_results / meta.results_per_page)

        return self.len

    def __next__(self):
        if self.len is not None and self.index >= self.len:
            raise StopIteration

        if self.return_cached:
            self.return_cached = False
        else:
            self.resp, self.meta = self.func(**self.kwargs, next_page_token=self.next_page_token)
            if self.meta is not None:
                self.next_page_token = self.meta.next_page_token
            self.index += 1

        return self.resp, self.meta

    def __iter__(self):
        return self


def str_to_datetime(dt_str: str):
    if "." in dt_str:
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")
