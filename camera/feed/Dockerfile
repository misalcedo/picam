FROM ubuntu
MAINTAINER miguel@salcedo.cc

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /var/output/dash

CMD ffmpeg -v verbose \
    -ar 48000 -ac 2 -f alsa -i hw:2,0 \
    -f v4l2 -s hd1080 -input_format mjpeg -i /dev/video0 \
    -vcodec libx264 -vprofile high422 -level "4.2" \
    -preset ultrafast -tune zerolatency \
    -g 30 -r 15 \
    -acodec aac -ab 128k \
    -f dash -min_seg_duration 1000 -remove_at_exit 1 -window_size 5 live.mpd
