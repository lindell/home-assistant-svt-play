import logging
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from .video_url_fetch.video_fetch import video_url_by_video_id, video_id_by_time, video_url_by_channel, suggested_video_id, random_video_id
from .validation import category_names

DOMAIN = "svt_play"

DEPENDENCIES = ['media_player']

CONF_ENTITY_ID = 'entity_id'
CONF_PROGRAM_NAME = 'program_name'
CONF_CHANNEL = 'channel'
CONF_CATEGORY = 'category'

SERVICE_PLAY_SUGGESTED = 'play_suggested'
SERVICE_PLAY_SUGGESTED_SCHEMA = vol.Schema({
    CONF_ENTITY_ID: cv.entity_ids,
    CONF_PROGRAM_NAME: str,
})

SERVICE_PLAY_LATEST = 'play_latest'
SERVICE_PLAY_LATEST_SCHEMA = vol.Schema({
    CONF_ENTITY_ID: cv.entity_ids,
    CONF_PROGRAM_NAME: str,
    CONF_CATEGORY: category_names,
})

SERVICE_PLAY_RANDOM = 'play_random'
SERVICE_PLAY_RANDOM_SCHEMA = vol.Schema({
    CONF_ENTITY_ID: cv.entity_ids,
    CONF_PROGRAM_NAME: str,
    CONF_CATEGORY: category_names,
})

SERVICE_PLAY_CHANNEL = 'play_channel'
SERVICE_PLAY_CHANNEL_SCHEMA = vol.Schema({
    CONF_ENTITY_ID: cv.entity_ids,
    CONF_CHANNEL: str,
})


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):

    async def play_suggested(service):
        """Play the suggested svt play video from a specified program"""

        entity_id = service.data.get(CONF_ENTITY_ID)
        program_name = service.data.get(CONF_PROGRAM_NAME)

        def fetch_video_url():
            return video_url_by_video_id(
                suggested_video_id(program_name)
            )
        video_url = await hass.async_add_executor_job(fetch_video_url)

        await hass.services.async_call('media_player', 'play_media', {
            'entity_id': entity_id,
            'media_content_id': video_url,
            'media_content_type': 'video'
        })
    hass.services.async_register(
        DOMAIN, SERVICE_PLAY_SUGGESTED, play_suggested, SERVICE_PLAY_SUGGESTED_SCHEMA
    )

    async def play_latest(service):
        """Play the latest svt play video from a specified program"""

        entity_id = service.data.get(CONF_ENTITY_ID)
        program_name = service.data.get(CONF_PROGRAM_NAME)
        category = service.data.get(CONF_CATEGORY)

        def fetch_video_url():
            return video_url_by_video_id(
                video_id_by_time(program_name, categories=category)
            )
        video_url = await hass.async_add_executor_job(fetch_video_url)

        await hass.services.async_call('media_player', 'play_media', {
            'entity_id': entity_id,
            'media_content_id': video_url,
            'media_content_type': 'video'
        })
    hass.services.async_register(
        DOMAIN, SERVICE_PLAY_LATEST, play_latest, SERVICE_PLAY_LATEST_SCHEMA
    )

    async def play_random(service):
        """Play a random svt play video from a specified program"""

        entity_id = service.data.get(CONF_ENTITY_ID)
        program_name = service.data.get(CONF_PROGRAM_NAME)
        category = service.data.get(CONF_CATEGORY)

        def fetch_video_url():
            return video_url_by_video_id(
                random_video_id(program_name, categories=category)
            )
        video_url = await hass.async_add_executor_job(fetch_video_url)

        await hass.services.async_call('media_player', 'play_media', {
            'entity_id': entity_id,
            'media_content_id': video_url,
            'media_content_type': 'video'
        })
    hass.services.async_register(
        DOMAIN, SERVICE_PLAY_RANDOM, play_random, SERVICE_PLAY_RANDOM_SCHEMA
    )

    async def play_channel(service):
        """Play the specified channel"""

        entity_id = service.data.get(CONF_ENTITY_ID)
        channel = service.data.get(CONF_CHANNEL)

        def fetch_video_url():
            return video_url_by_channel(channel)
        video_url = await hass.async_add_executor_job(fetch_video_url)

        await hass.services.async_call('media_player', 'play_media', {
            'entity_id': entity_id,
            'media_content_id': video_url,
            'media_content_type': 'video'
        })
    hass.services.async_register(
        DOMAIN, SERVICE_PLAY_CHANNEL, play_channel, SERVICE_PLAY_CHANNEL_SCHEMA
    )

    return True
