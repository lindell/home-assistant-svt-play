"""Channel region URL and Home Assistant service contract tests."""

import asyncio
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, Mock
from urllib.parse import parse_qs, urlsplit

import pytest
import voluptuous as vol


COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "svt_play"


@pytest.fixture
def integration(monkeypatch):
    """Load the integration with only its HA validation import stubbed."""
    cv = ModuleType("homeassistant.helpers.config_validation")
    cv.entity_ids = lambda value: value
    cv.ensure_list = lambda value: value if isinstance(value, list) else [value]
    for name in ["homeassistant", "homeassistant.helpers"]:
        module = ModuleType(name)
        module.__path__ = []
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setitem(sys.modules, "homeassistant.helpers.config_validation", cv)
    name = "svt_play_region_test"
    spec = importlib.util.spec_from_file_location(
        name, COMPONENT / "__init__.py", submodule_search_locations=[str(COMPONENT)]
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    yield module
    for key in list(sys.modules):
        if key.startswith(name + "."):
            monkeypatch.delitem(sys.modules, key)


@pytest.fixture
def fetch(integration):
    return sys.modules[integration.__name__ + ".video_url_fetch.video_fetch"]


@pytest.mark.parametrize("region", [None, "jamtland", "skane"])
@pytest.mark.parametrize("source", ["svt1", "svt2", "programme"])
def test_region_preserves_format_selection(fetch, monkeypatch, region, source):
    url = "https://cdn.example/master.m3u8?format=hls&defaultSubLang=1&empty=#track"
    response = Mock()
    response.json.return_value = {
        "videoReferences": [
            {"format": "dash", "url": "https://cdn.example/manifest.mpd"},
            {"format": "hls", "url": url},
        ]
    }
    get = Mock(return_value=response)
    monkeypatch.setattr(fetch, "get", get)
    if source == "programme":
        actual = fetch.video_url_by_video_id("episode-id", formats=["hls"], region=region)
        get.assert_called_once_with("https://api.svt.se/video/episode-id")
    else:
        actual = fetch.video_url_by_channel(source, formats=["hls"], region=region)
        get.assert_called_once_with("https://api.svt.se/videoplayer-api/video/ch-" + source)
    if region is None:
        assert actual == url
    else:
        parsed = urlsplit(actual)
        assert parsed.fragment == "track"
        assert parse_qs(parsed.query, keep_blank_values=True) == {
            "format": ["hls"], "defaultSubLang": ["1"], "empty": [""],
            "region": [region],
        }


@pytest.mark.parametrize("query", ["", "?region=stockholm&format=hls"])
def test_region_adds_or_replaces_parameter(fetch, monkeypatch, query):
    response = Mock()
    response.json.return_value = {"videoReferences": [{
        "format": "hls", "url": "https://cdn.example/master.m3u8" + query,
    }]}
    monkeypatch.setattr(fetch, "get", Mock(return_value=response))
    result = fetch.video_url_by_channel("svt1", region="jamtland")
    assert parse_qs(urlsplit(result).query)["region"] == ["jamtland"]


@pytest.mark.parametrize("function", ["video_url_by_channel", "video_url_by_video_id"])
def test_invalid_region_rejected_before_fetch(fetch, monkeypatch, function):
    get = Mock()
    monkeypatch.setattr(fetch, "get", get)
    with pytest.raises(ValueError, match="Unknown SVT news region"):
        getattr(fetch, function)("id", region="Jämtland")
    get.assert_not_called()


@pytest.mark.parametrize("region", [None, "jamtland"])
def test_video_information_forwards_format_and_region(fetch, monkeypatch, region):
    monkeypatch.setattr(fetch, "info_by_svt_id", Mock(return_value={
        "parent": {"name": "Morgonstudion"}, "name": "Today",
        "image": {"id": "image", "changed": 123},
    }))
    video_url = Mock(return_value="https://cdn.example/master.m3u8")
    monkeypatch.setattr(fetch, "video_url_by_video_id", video_url)
    info = fetch.video_information_by_id("episode-id", formats=["hls"], region=region)
    video_url.assert_called_once_with("episode-id", formats=["hls"], region=region)
    assert info["url"] == video_url.return_value
    assert info["name"] == "Morgonstudion - Today"


SERVICES = ["play_channel", "play_suggested", "play_latest", "play_random", "play_videoid"]


@pytest.mark.parametrize("service", SERVICES)
def test_service_rejects_unknown_region(integration, service):
    schema = getattr(integration, "SERVICE_" + service.upper() + "_SCHEMA")
    with pytest.raises(vol.Invalid):
        schema({"entity_id": "media_player.tv", "region": "unknown"})


@pytest.mark.parametrize("region", [None, "jamtland"])
@pytest.mark.parametrize("service", SERVICES)
def test_service_forwards_region(integration, monkeypatch, region, service):
    url = "https://cdn.example/master.m3u8"
    info = {"url": url, "name": "Morgonstudion", "thumbnail": "https://image.example"}
    fetch_url = Mock(return_value=url)
    fetch_info = Mock(return_value=info)
    monkeypatch.setattr(integration, "video_url_by_channel", fetch_url)
    monkeypatch.setattr(integration, "video_information_by_id", fetch_info)
    selectors = {}
    for selector in ["suggested_video_id", "video_id_by_time", "random_video_id"]:
        selectors[selector] = Mock(return_value="episode-id")
        monkeypatch.setattr(integration, selector, selectors[selector])
    handlers = {}

    def register(domain, name, handler, schema):
        handlers[name] = (handler, schema)

    async def executor(job):
        return job()

    call = AsyncMock()
    hass = SimpleNamespace(
        services=SimpleNamespace(async_register=register, async_call=call),
        async_add_executor_job=executor,
    )

    async def exercise():
        assert await integration.async_setup(hass, {})
        handler, schema = handlers[service]
        data = {"entity_id": "media_player.tv", "formats": ["hls"]}
        if service == "play_channel":
            data["channel"] = "svt2"
        elif service == "play_videoid":
            data["videoid"] = "episode-id"
        else:
            data["program_name"] = "morgonstudion"
        if region is not None:
            data["region"] = region
        await handler(SimpleNamespace(data=schema(data)))

    asyncio.run(exercise())
    expected = {"entity_id": "media_player.tv", "media_content_id": url, "media_content_type": "video"}
    if service == "play_channel":
        fetch_url.assert_called_once_with("svt2", formats=["hls"], region=region)
        fetch_info.assert_not_called()
    else:
        fetch_info.assert_called_once_with("episode-id", formats=["hls"], region=region)
        fetch_url.assert_not_called()
        expected["extra"] = {"title": info["name"], "thumb": info["thumbnail"]}
        if service == "play_suggested":
            selectors["suggested_video_id"].assert_called_once_with("morgonstudion")
        elif service == "play_latest":
            selectors["video_id_by_time"].assert_called_once_with("morgonstudion", None, categories=None)
        elif service == "play_random":
            selectors["random_video_id"].assert_called_once_with("morgonstudion", categories=None)
    call.assert_awaited_once_with("media_player", "play_media", expected)
