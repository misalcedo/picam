FROM ubuntu
MAINTAINER miguel@salcedo.cc

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /var/output/dash

CMD ffmpeg \
    -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -i /dev/zero \
    -f v4l2 -r 5 -s hd1080 -i /dev/video0 \
    -vcodec libx264 -vprofile high -level "4.2" \
    -preset ultrafast -tune zerolatency -pix_fmt yuv420p \
    -vb 1M -g 60 \
    -acodec aac -ab 128k \
    -f dash -min_seg_duration 100 -remove_at_exit 1 -window_size 864000 live.mpd
