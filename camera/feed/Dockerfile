FROM ubuntu
MAINTAINER miguel@salcedo.cc

RUN apt-get update && apt-get install -y ffmpeg v4l-utils && rm -rf /var/lib/apt/lists/*

WORKDIR /var/output/video
COPY feed /usr/bin/feed

ENTRYPOINT ["/usr/bin/feed"]
