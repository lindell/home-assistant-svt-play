import pytest
import json
from video_fetch import information_by_program_id, video_url_by_channel, video_id_by_time, video_url_by_video_id, suggested_video_id


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
