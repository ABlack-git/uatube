from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Replace 'YOUR_API_KEY' with the actual API key you obtained
api_key = 'AIzaSyDDC5mVnrcOaBLXybz8S2B7E5w0zMKkaDM'

# Create a YouTube API client
youtube = build('youtube', 'v3', developerKey=api_key)

channel_id = 'UCig7t6LFOjS2fKkhjbVLpjw'
# channel_info = youtube.channels().list(part='snippet,contentDetails,statistics,status', id=channel_id).execute()
#
# print(channel_info)
#
channel_subscriptions = youtube.subscriptions().list(
        part='snippet',
        channelId=channel_id,
        maxResults=50,
        pageToken='CDIQAA'
    ).execute()
#
print(channel_subscriptions)

print(len(channel_subscriptions['items']))

#
# for item in channel_subscriptions['items']:
#     print(item['subscriberSnippet']['title'], item['subscriberSnippet']['channelId'])
# video_id = '6H66AmS6kMc'
# response = youtube.commentThreads().list(
#     part='snippet',
#     videoId=video_id,
#     textFormat='plainText',  # Specify the text format of the comments
#     maxResults=100  # Adjust as needed, maximum is 100
# ).execute()
#
# print(response)
#
# channel_ids = set()
# for item in response['items']:
#     topLevelComment = item['snippet']['topLevelComment']['snippet']
#     channel_ids.add(topLevelComment['authorChannelId']['value'])
#     # print(topLevelComment['authorChannelId']['value'], topLevelComment['authorDisplayName'],
#     #       topLevelComment['textDisplay'])
#
# channel_dict = dict()
# for ch_id in channel_ids:
#     channel_info = youtube.channels().list(part='snippet,contentDetails,statistics,status', id=ch_id).execute()
#     snippet = channel_info['items'][0]['snippet']
#     status = channel_info['items'][0]['status']
#     # print(channel_info['items'][0]['id'], snippet['title'], snippet['customUrl'], status['privacyStatus'])
#     channel_dict[ch_id] = {
#         "id":channel_info['items'][0]['id'],
#         "title": snippet['title'],
#         "customUrl": snippet['customUrl'],
#         "privacyStatus": status['privacyStatus']
#     }
#
# for ch_id in channel_ids:
#     try:
#         channel_subscriptions = youtube.subscriptions().list(
#                 part='snippet',
#                 channelId=ch_id,
#                 maxResults=50  # Adjust as needed, maximum is 50
#             ).execute()
#         print(channel_subscriptions)
#     except HttpError:
#         print(f"Cannot read subscriptions of channel with id {ch_id}, privacyStatus: {channel_dict[ch_id]['privacyStatus']}")

# response = youtube.search().list(
#     part='id, snippet',
#     channelId=channel_id,
#     type='video',
#     maxResults=50,  # Adjust as needed, maximum is 50,
#     order='date'
# ).execute()
# print(response)