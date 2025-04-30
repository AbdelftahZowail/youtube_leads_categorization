from googleapiclient.discovery import build
from datetime import datetime
import re
import scrapetube
import glob
import csv


# def get_channel_info1(api_key, channel_url):
#     username = re.search(r"@([\w\d]+)", channel_url)
#     if not username:
#         return None, None, None
#
#     youtube = build('youtube', 'v3', developerKey=api_key)
#     response = youtube.search().list(
#         part="snippet",
#         type="channel",
#         q=username.group(1),
#         maxResults=1
#     ).execute()
#
#     if response["items"]:
#         channel_id = response["items"][0]["id"]["channelId"]
#         channel_name = response["items"][0]["snippet"]["channelTitle"]
#
#         # Get Uploads Playlist ID
#         channel_response = youtube.channels().list(
#             part="contentDetails",
#             id=channel_id
#         ).execute()
#         uploads_playlist = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
#
#         # print(channel_id, channel_name, uploads_playlist)
#         return channel_id, channel_name, uploads_playlist
#     return None, None, None


def get_channel_info(youtube_url):
    match = re.search(r"(?:youtube\.com/(?:c/|channel/|user/|@)?([A-Za-z0-9_-]+))", youtube_url)
    username = match.group(1)
    videos = scrapetube.get_search(username, results_type='channel', limit=10)
    for video in videos:
        if video.get("navigationEndpoint", {}).get("commandMetadata", {}).get("webCommandMetadata", {}).get(
                "url") == f'/@{username}':
            return video.get("channelId"), video.get("title").get("simpleText", ""), rsc(video.get("channelId"))


def get_videos(channel):
    months = [0, 0, 0]
    videos = scrapetube.get_channel(channel_url=channel, )
    j = 0
    for video in videos:
        date = video['publishedTimeText']['simpleText']
        j = j+1
        if date.__contains__('year') and j < 8:
            break
        if date.__contains__('month') and int(date.split(' ')[0]) >= 3:
            break
        if date.__contains__('month'):
            months[int(date.split(' ')[0])] = months[int(date.split(' ')[0])] + 1
        else:
            months[0] = months[0] + 1
    return [months[0], months[1], months[2]]


# def get_videos1(api_key, playlist_id):
#     youtube = build('youtube', 'v3', developerKey=api_key)
#     now = datetime.utcnow()
#     months = {0: 0, 1: 0, 2: 0}
#
#     request = youtube.playlistItems().list(
#         part="snippet",
#         playlistId=playlist_id,
#         maxResults=50  # Get the most recent 50 videos in one call
#     )
#
#     while request:
#         response = request.execute()
#         for item in response.get("items", []):
#             published_at = item["snippet"]["publishedAt"]
#             pub_date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
#             days_ago = (now - pub_date).days
#
#             if days_ago <= 30:
#                 months[0] += 1
#             elif days_ago <= 60:
#                 months[1] += 1
#             elif days_ago <= 90:
#                 months[2] += 1
#
#         request = youtube.playlistItems().list_next(request, response)  # Get next page (if exists)
#
#     return [months[0], months[1], months[2]]


def get_recent_shorts(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    now = datetime.utcnow()
    shorts_dates = []

    search_response = youtube.search().list(
        channelId=channel_id,
        part="id",
        type="video",
        videoDuration="short",
        maxResults=3,
        order="date"
    ).execute()

    for item in search_response.get('items', []):
        video_id = item['id']['videoId']
        video_response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()

        if video_response["items"]:
            pub_date = datetime.strptime(video_response["items"][0]["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
            shorts_dates.append(pub_date)

    return shorts_dates


def classify_shorts(shorts_dates):
    now = datetime.utcnow()

    if not shorts_dates:
        return "Sample"
    if all((now - date).days <= 7 for date in shorts_dates):
        return "posts shorts"
    elif all((now - date).days <= 30 for date in shorts_dates):
        return "maybe later"
    else:
        return "Sample"


def classify_channel(video_counts, api_key, channel_id):
    total_videos = sum(video_counts)

    if total_videos < 5:
        return "probably stopped"
    elif total_videos >= 12:
        shorts_dates = get_recent_shorts(api_key, channel_id)
        return classify_shorts(shorts_dates)
    else:
        return "inconsistent"


def check_video_frequency(api_key, channel_url):
    print(get_channel_info(channel_url))
    channel_id, channel_name, uploads_playlist = get_channel_info(channel_url)
    if not channel_id:
        print(f"{channel_url}: Invalid channel URL")
        return None

    video_counts = get_videos(channel_url)
    label = classify_channel(video_counts, api_key, channel_id)
    tiktok_url = f'https://www.tiktok.com/search?q={channel_name.replace(" ", "%20")}' if label in ["maybe later",
                                                                                                    "Sample"] else ""
    if label == 'maybe later':
        channel_url = channel_url + '/shorts'
    else:
        channel_url = channel_url + '/videos'

    print(
        f'Channel: {channel_name} ({channel_url}) | Last 3 months: {video_counts} | Label: {label} {"| TikTok: " + tiktok_url if tiktok_url else ""}')
    return [channel_name, channel_url, label, tiktok_url]


def rsc(s):
    return s[:1] + 'U' + s[2:] if len(s) > 1 else s


try:
    apis = [''] # enter API key(s) here
    n = input('which api? ')
    api_key = apis[int(n)]

    input_files = [f for f in glob.glob("*.csv") if f != "output.csv"]

    channel_urls = []
    for file in input_files:
        with open(file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                channel_urls.append(row["URL"])  # Ensure 'URL' is the correct column name

    results = []
    for url in channel_urls:
        try:
            result = check_video_frequency(api_key, url)
            results.append(result)
        except Exception:
            print(f'Error: {url}')

    print('all done')

    with open("output.csv", mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Channel Name", "Channel URL", "Label", "TikTok URL"]
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        writer.writerows(results)

except Exception as e:
    print(f'Error: {e}')
finally:
    input('press enter to exit')