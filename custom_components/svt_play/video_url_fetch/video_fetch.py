from requests import get
from requests import post
from datetime import datetime
from datetime import timezone
import random
import iso8601

default_formats = ['hls', 'dash']


def video_information_by_id(svt_video_id, formats=default_formats):
    info = info_by_svt_id(svt_video_id)

    return {
        'url': video_url_by_video_id(svt_video_id),
        'name': '{} - {}'.format(info['parent']['name'], info['name']),
        'thumbnail': 'https://www.svtstatic.se/image/large/1024/{}/{}?format=auto&chromaSubSampling=false'
        .format(info['image']['id'], info['image']['changed']),
    }


def video_url_by_video_id(svt_video_id, formats=default_formats):
    "Get the CDN video url"
    url = 'https://api.svt.se/video/{}'.format(svt_video_id)
    return video_url_from_videoplayer_api(url, formats)


def video_url_by_channel(channel_id, formats=default_formats):
    "Get the CDN video url by a channel name"
    url = 'https://api.svt.se/videoplayer-api/video/ch-{}'.format(channel_id)
    return video_url_from_videoplayer_api(url, formats)


def video_url_from_videoplayer_api(url, formats):
    data = get(url).json()
    if 'message' in data:
        raise Exception(
            "Could not fetch video url: {}".format(data['message'])
        )

    for format in formats:
        for video_reference in data['videoReferences']:
            if video_reference['format'] == format:
                return video_reference['url']

    raise Exception(
        "Could not find video url with any of the formats: {}".format(formats))


def video_id_by_time(program_id, exclude_category=None, categories=None, index=0):
    "Get the video id of a video based on the time it became available"
    program_data = information_by_program_id(program_id)

    videos = []
    for content in program_data['associatedContent']:
        if ((categories is None or content['name'] in categories) and
                (exclude_category is None or exclude_category not in content['name'])):
            videos += content['items']

    # Remove episodes with no validity date
    videos = filter(lambda video: 'validFrom' in video['item'], videos)
    # Remove episodes where the validity hasn't happened
    now = datetime.now(tz=timezone.utc)
    videos = filter(
        lambda video: iso8601.parse_date(video['item']['validFrom']) < now,
        videos,
    )
    videos = list(videos)

    if len(videos) <= index:
        raise Exception("Could only find {} videos".format(len(videos)))

    videos = sorted(
        videos,
        key=lambda video: iso8601.parse_date(video['item']['validFrom']),
        reverse=True,
    )

    return videos[index]['item']['videoSvtId']


def random_video_id(program_id, categories=None, excluded_categories=["Upptäck mer"]):
    "Get a random video id from the specified program"
    program_data = information_by_program_id(program_id)

    videos = []
    for content in program_data['associatedContent']:
        if (categories is None or content['name'] in categories) and not (content['name'] in excluded_categories):
            videos += content['items']

    index = random.randint(0, len(videos) - 1)
    return videos[index]['item']['videoSvtId']


def suggested_video_id(program_id):
    "Get the video id if the suggested video"
    program_data = information_by_program_id(program_id)
    return program_data['videoSvtId']


def information_by_program_id(program_id):
    "Get information about the suggested episode based on the program name"
    query = """
        query($name: String!) {
            listablesBySlug(slugs: [$name]) {
                ... on TvShow {
                     videoSvtId
                }
                ... on TvSeries {
                    videoSvtId
                }
                ... on KidsTvShow {
                    videoSvtId
                }
                associatedContent{
                    name
                    items {
                        item {
                            videoSvtId
                            ... on Episode {
                                validFrom
                            }
                        }
                    }
                }
            }
        }
    """

    query_data = {
        'query': query,
        'variables': {
            'name': program_id,
        },
    }

    data = post('https://api.svt.se/contento/graphql', json=query_data).json()
    if len(data['data']['listablesBySlug']) < 1:
        raise Exception(
            "Could not find program with id: {}".format(program_id)
        )

    associated_content = data['data']['listablesBySlug'][0]

    return associated_content


def info_by_svt_id(svt_id):
    ""
    query = """
        query($id: String!) {
            contentById(ids: [$id]) {
                name
                parent {
                    name
                }
                image {
                    id
                    changed
                }
            }
        }
    """

    query_data = {
        'query': query,
        'variables': {
            'id': svt_id,
        },
    }

    data = post('https://api.svt.se/contento/graphql', json=query_data).json()
    if len(data['data']['contentById']) < 1:
        raise Exception(
            "Could not find video with id: {}".format(svt_id)
        )

    return data['data']['contentById'][0]
