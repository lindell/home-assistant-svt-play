"""Tests for the SVT Play config flow."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.svt_play.const import DOMAIN

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


async def test_user_flow_creates_entry(hass: HomeAssistant):
    """Test that the user flow creates a config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "SVT Play"
    assert result["data"] == {}


async def test_user_flow_aborts_if_already_configured(hass: HomeAssistant):
    """Test that the user flow aborts when already configured."""
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_setup_and_unload_entry(hass: HomeAssistant):
    """Test setting up and unloading a config entry registers and removes services."""
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)

    with patch(
        "custom_components.svt_play.video_url_fetch.video_fetch.video_information_by_id"
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, "play_suggested")
    assert hass.services.has_service(DOMAIN, "play_latest")
    assert hass.services.has_service(DOMAIN, "play_random")
    assert hass.services.has_service(DOMAIN, "play_channel")
    assert hass.services.has_service(DOMAIN, "play_videoid")

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not hass.services.has_service(DOMAIN, "play_suggested")
    assert not hass.services.has_service(DOMAIN, "play_latest")
    assert not hass.services.has_service(DOMAIN, "play_random")
    assert not hass.services.has_service(DOMAIN, "play_channel")
    assert not hass.services.has_service(DOMAIN, "play_videoid")
