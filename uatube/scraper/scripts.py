import json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from uatube.scraper import client
from uatube.models import Comment, Channel, Subscription, SubscriptionCheckpoint
from mongoengine import connect
from tqdm import tqdm


def scrap_users(youtube, channel_id, num_users):
    authors = set()
    video_ids = client.get_channel_video_ids(youtube, channel_id)
    num_exec = 0
    while len(authors) < num_users or num_exec >= 3:
        for v_id in tqdm(video_ids, desc="Processing videos", leave=False):
            if len(authors) >= num_users:
                break
            try:
                comments = client.get_comments_for_video(youtube, v_id)
            except HttpError as e:
                if e.error_details[0]['reason'] == 'quotaExceeded':
                    raise e
                continue
            comment_models = []
            channel_models = []
            for comment in tqdm(comments, desc="Processing comments", leave=False):
                if len(authors) >= num_users:
                    break
                if comment.author_id in authors or comment.author_id == channel_id:
                    continue
                comment_models.append(Comment.from_dataclass(comment))
                authors.add(comment.author_id)
                channel_models.append(
                    Channel(channel_id=comment.author_id, channel_display_name=comment.author_display_name,
                            channel_url=comment.author_channel_url, found_from_channel=[channel_id])
                )

            if comment_models:
                Comment.objects.insert(comment_models)

            if channel_models:
                existing_channels = Channel.objects(channel_id__in=[c.channel_id for c in channel_models])

                if len(existing_channels) > 0:
                    existing_ids = [c.channel_id for c in existing_channels]
                    channel_models = list(filter(lambda c: c.channel_id not in existing_ids, channel_models))

                    for channel in existing_channels:
                        if channel_id not in channel.found_from_channel:
                            channel.found_from_channel.append(channel_id)
                            channel.save()

                Channel.objects.insert(channel_models)
        num_exec += 1


def scrap_subscriptions_for_user(youtube, channel_id, channel_order, start_page_token, run_id):
    paginator = client.Paginator(client.get_channel_subscriptions, start_page_token=start_page_token,
                                 youtube=youtube, channel_id=channel_id)

    chckpt_meta = None
    has_subs = False
    try:
        for subs, meta in tqdm(paginator, desc=f'Processing subscriptions for user with channel_id: {channel_id}',
                               leave=False, disable=False):
            subs_model = [Subscription.from_dataclass(sub) for sub in subs]
            if subs_model:
                Subscription.objects.insert(subs_model)
            has_subs = True
            chckpt_meta = meta
    except Exception as e:
        print('Error encountered, saving checkpoint')
        print(e)
        next_page_token = start_page_token
        has_next_page = True
        if chckpt_meta is not None:
            next_page_token = chckpt_meta.next_page_token
            if chckpt_meta.next_page_token is None:
                has_next_page = False

        checkpoint = SubscriptionCheckpoint(channel_id=channel_id, channel_order=channel_order, run_id=run_id,
                                            next_page_token=next_page_token, has_next_page=has_next_page)
        checkpoint.save()

        raise e

    return has_subs


def run_scrap_users():
    api_key = 'AIzaSyDDC5mVnrcOaBLXybz8S2B7E5w0zMKkaDM'
    youtube = build('youtube', 'v3', developerKey=api_key)
    connect(db='uatube', host='localhost', port=51999)

    with open('sample_20_with_props.json', 'r', encoding='utf-8') as f:
        sample = json.load(f)

    for channel in tqdm(sample, desc='Processing channels'):
        channel_id = channel['channel_id']
        num_users = channel['num_users']

        scrap_users(youtube, channel_id, num_users)


def run_scrap_subscriptions():
    api_key = 'AIzaSyDDC5mVnrcOaBLXybz8S2B7E5w0zMKkaDM'
    youtube = build('youtube', 'v3', developerKey=api_key)
    connect(db='uatube', host='localhost', port=51999)

    run_id = 'run_1'
    start_from_checkpoint = False

    channel_order = 2573
    next_page_token = None
    if start_from_checkpoint:
        checkpoint = SubscriptionCheckpoint.objects(run_id=run_id).order_by('-created_at').first()
        if checkpoint is not None:
            channel_order = checkpoint.channel_order
            next_page_token = checkpoint.next_page_token
            if not checkpoint.has_next_page:
                channel_order += 1
                next_page_token = None

    channels = Channel.objects(from_subscriptions=False)
    total = Channel.objects(from_subscriptions=False).count()
    pbar = tqdm(enumerate(channels[channel_order:]), desc='Processing channels', disable=False, total=total,
                initial=channel_order)
    for i, channel in pbar:
        pbar.set_postfix({"channel_id": channel.channel_id})
        has_subs = scrap_subscriptions_for_user(youtube, channel.channel_id, i+channel_order, next_page_token, run_id)
        if has_subs:
            channel.has_opened_subscriptions = True
            channel.save()
