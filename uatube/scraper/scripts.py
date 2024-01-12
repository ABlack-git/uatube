from googleapiclient.discovery import build
from uatube.scraper import client
from uatube.models import Comment, Subscription, Channel
from mongoengine import connect
from tqdm import tqdm


def scrap_kinomany():
    api_key = 'AIzaSyDDC5mVnrcOaBLXybz8S2B7E5w0zMKkaDM'
    youtube = build('youtube', 'v3', developerKey=api_key)
    connect(db='uatube', host='localhost', port=51999)

    channel_id = 'UCig7t6LFOjS2fKkhjbVLpjw'

    authors = set()
    video_ids = client.get_channel_video_ids(youtube, channel_id)
    for v_id in tqdm(video_ids, desc="Processing videos", leave=True, position=0):
        comments = client.get_comments_for_video(youtube, v_id)
        for comment in tqdm(comments, desc="Processing comments", leave=False, position=1):
            comment_model = Comment.from_dataclass(comment)
            comment_model.save()
            if comment.author_id in authors:
                continue
            authors.add(comment.author_id)
            Channel(channel_id=comment.author_id, channel_display_name=comment.author_display_name,
                    channel_url=comment.author_channel_url).save()
            subscriptions = client.get_channel_subscriptions(youtube, comment.author_id)
            if subscriptions is not None:
                for subscription in subscriptions:
                    Subscription.from_dataclass(subscription).save()


scrap_kinomany()

# with open("channels.json", 'r', encoding='utf-8') as f:
#     channels = json.load(f)
#
# channels_w_subs = [c for c in channels if len(c['subscriptions']) > 0]
# unique_users = len(channels)
# unique_users_w_subs = len(channels_w_subs)
# print(
#     f'Total unique users: {unique_users}, Unique users with subs: {unique_users_w_subs}, Proportion: {unique_users_w_subs / unique_users}')
#
# subs_count = [len(u['subscriptions']) for u in channels_w_subs]
# average_sub_count = sum(subs_count) / len(subs_count)
# max_sub_count = max(subs_count)
# min_subs_count = min(subs_count)
# print(f'Avg: {average_sub_count}, max: {max_sub_count}, min: {min_subs_count}')
#
# unique_channels = set()
# for c in channels_w_subs:
#     for s in c['subscriptions']:
#         if s['channel_id'] not in unique_channels:
#             unique_channels.add(s['channel_id'])
# print(len(unique_channels))
