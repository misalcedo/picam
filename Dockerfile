FROM resin/raspberrypi3-python:3-onbuild

EXPOSE 443

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y build-essential cmake unzip pkg-config \
    libjpeg-dev libpng-dev libtiff-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev gfortran

WORKDIR /opt

ARG domain
ARG camera
ARG port
ARG opencv_version
ENV CAMERA=$camera DOMAIN=$domain PORT=$port OPENCV_VERSION=$opencv_version

RUN wget -O opencv.zip https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip && \
  wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/${OPENCV_VERSION}.zip && \
  unzip opencv.zip && unzip opencv_contrib.zip && rm -rf opencv*.zip

WORKDIR /opt/opencv-${OPENCV_VERSION}/build

RUN cmake \
  -D CMAKE_BUILD_TYPE=RELEASE \
  -D CMAKE_INSTALL_PREFIX=/usr/local \
  -D ENABLE_NEON=ON \
  -D ENABLE_VFPV3=ON \
  -D BUILD_TESTS=OFF \
  -D OPENCV_ENABLE_NONFREE=ON \
  -D OPENCV_EXTRA_MODULES_PATH=/opt/opencv_contrib-${OPENCV_VERSION}/modules \
  -D PYTHON_EXECUTABLE=$(which python3) \
  -D INSTALL_PYTHON_EXAMPLES=OFF \
  -D INSTALL_C_EXAMPLES=OFF \
  -D BUILD_EXAMPLES=OFF \
  .. && make -j12 && make install
RUN ldconfig

WORKDIR /usr/src/app

CMD python3 -u main.py --port $PORT --camera $CAMERA --domain $DOMAIN --users $USERS
