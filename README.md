## Home Assistant SVT Play

[![Daily test](https://github.com/lindell/home-assistant-svt-play/workflows/Daily%20test/badge.svg)](https://github.com/lindell/home-assistant-svt-play/actions?query=workflow%3A%22Daily+test%22)

Play svt play programs or channels on home assistant media players.

## Available actions

### Play Suggested

Play the suggested video that is shown on svtplay.se. This is the recomended way of starting a program.

```yaml
- service: svt_play.play_suggested
  entity_id: media_player.living_room_tv
  data:
    program_name: rapport
```

### Play Latest

Play the latest video or clip from a specific program. There exists two options to exclude or include videos matching specific categories.

```yaml
- service: svt_play.play_latest
  entity_id: media_player.living_room_tv
  data:
    program_name: skavlan
    category: Intervjuer # Optional
    exclude_category: utan filmer # Optional
```

### Play random

Play a random video or clip from a specific program. There exist an option to just random from specific categories.

```yaml
- service: svt_play.play_random
  entity_id: media_player.living_room_tv
  data:
    program_name: skavlan
    category: Intervjuer # Optional
```

### Play Channel

Play one of the svt channels.

```yaml
- service: svt_play.play_channel
  entity_id: media_player.living_room_tv
  data:
    channel: svt1 # Available channels: svt1, svt2, barnkanalen, kunskapskanalen, svt24
```

### Play video id

If a specific video should be played, its "id" can be extracted from the url. For example `jXvZLoG` is the id found in the following url: `https://www.svtplay.se/video/jXvZLoG/ifs-invandrare-for-svenskar/avsnitt-3`

```yaml
- service: svt_play.play_videoid
  entity_id: media_player.living_room_tv
  data:
    videoid: jXvZLoG
```

## Installation

### Add the code

Copy the `custom_components/svt_play` folder in this repository to `<home assistant config>/custom_components/svt_play`

Or:

Install via [Home Assistant Community Store](https://hacs.xyz/)

### Active the service

Add:

```yaml
svt_play:
```

to your configuration.yaml file.

### Configuration options

You can optionally configure the video formats to use per service call. The first format in the list that is available for a video will be used. This can be useful if your media player only supports certain formats.

```yaml
- service: svt_play.play_suggested
  entity_id: media_player.living_room_tv
  data:
    program_name: rapport
    formats: # Optional
      - hls-cmaf-full
      - dash
```

Some of the supported formats: `dash-full`, `hls-cmaf-full`, `dash-lb-full`, `dash-hbbtv-avc`, `hls-ts-full`, `dash-avc`, `hls-cmaf-lb-full`, `dash`, `hls-cmaf-avc`, `hls`, `hls-ts-lb-full`, `dash-hbbtv-hevc`.

### Use in automations

And then add the automation you want:

```yaml
automation:
  - alias:
    trigger:
    # Some trigger
    action:
      - service: svt_play.play_suggested
        entity_id: media_player.living_room_tv
        data:
          program_name: rapport
```

## Get the `program_name` field

1. Search an click on the program you want at [svtplay.se](https://www.svtplay.se/)
2. From the url, grab the name.

![](https://share.lindell.me/2020/02/SardonicBonobo.png)
