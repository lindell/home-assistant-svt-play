from video_fetch import video_url_by_channel, video_id_by_time, video_url_by_video_id, suggested_video_id
import pytest


def test_rapport_by_time():
    id = video_id_by_time('skavlan')
    url = video_url_by_video_id(id)
    assert url.startswith('http')


def test_rapport_by_suggested():
    id = suggested_video_id('skavlan')
    url = video_url_by_video_id(id)
    assert url.startswith('http')


def test_svt1():
    url = video_url_by_channel("svt1")
    assert url.startswith('http')


def test_not_found_by_time():
    with pytest.raises(Exception, match="Could not find program with id: bogus"):
        video_id_by_time('bogus')


def test_not_found_by_suggested():
    with pytest.raises(Exception, match="Could not find program with id: bogus"):
        suggested_video_id('bogus')


def test_not_found_channel():
    with pytest.raises(Exception, match="Could not fetch video url: Not found"):
        video_url_by_channel("svt1337")
