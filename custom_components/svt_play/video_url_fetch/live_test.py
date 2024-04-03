from video_fetch import video_url_by_channel, video_id_by_time, video_url_by_video_id, suggested_video_id, random_video_id
import pytest


def test_rapport_by_time():
    id = video_id_by_time('rapport')
    url = video_url_by_video_id(id)
    assert url.startswith('http')


def test_rapport_by_suggested():
    id = suggested_video_id('rapport')
    url = video_url_by_video_id(id)
    assert url.startswith('http')


def test_channels():
    errors = []
    
    for channel in ['svt1', 'svt2', 'barnkanalen', 'kunskapskanalen', 'svt24']:
        url = video_url_by_channel(channel)
        if not url.startswith('http'):
            errors.append(channel)
    assert not errors


def test_not_found_by_time():
    with pytest.raises(Exception, match="Could not find program with id: bogus"):
        video_id_by_time('bogus')


def test_not_found_by_suggested():
    with pytest.raises(Exception, match="Could not find program with id: bogus"):
        suggested_video_id('bogus')


def test_not_found_channel():
    with pytest.raises(Exception, match="Could not fetch video url: Not found"):
        video_url_by_channel("svt1337")


def test_random():
    id = random_video_id('aktuellt')
    same_counter = 0
    for _ in range(5):
        new_id = random_video_id('aktuellt')
        print(new_id)
        if id == new_id:
            same_counter += 1
    assert same_counter != 5
