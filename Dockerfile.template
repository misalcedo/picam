FROM balenalib/%%BALENA_MACHINE_NAME%%-ubuntu
MAINTAINER miguel@salcedo.cc

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY stream stream
ENTRYPOINT ["stream"]
