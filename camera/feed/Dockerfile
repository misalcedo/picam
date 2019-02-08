FROM ubuntu
MAINTAINER miguel@salcedo.cc

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /var/output/dash

ENTRYPOINT ["ffmpeg"]
CMD ["-fflags", "+genpts+igndts", \
        "-ar", "44100", "-ac", "2", "-acodec", "pcm_s16le", "-f", "s16le", "-i", "/dev/zero", \
        "-f", "v4l2", "-r", "30", "-video_size", "hd1080", "-input_format", "h264", "-i", "/dev/video0", \
        "-vcodec", "copy", "-r", "30", "-b:v", "4M", "-g", "60", \
        "-acodec", "aac", "-ab", "128k", \
        "-f", "dash", "-min_seg_duration", "2000", "-remove_at_exit", "1", "-window_size", "10", "live.mpd"]
