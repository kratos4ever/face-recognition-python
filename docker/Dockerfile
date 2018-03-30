# This is a sample Dockerfile you can modify to deploy your own app based on face_recognition

FROM python:3.4-slim

RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    libmysqlclient-dev \
    software-properties-common \
    zip \
    python-mysqldb \    
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS


# The rest of this file just runs an example script.

COPY ./face_recognition/ /root/face_recognition
COPY ./face-recognition-python/ /biometric-sense

RUN cd /biometric-sense && \
    pip3 install -r requirements.txt

RUN cd /root/face_recognition && \
    python3 setup.py install

#run cmd to query the mysql db 

WORKDIR /biometric-sense
RUN chmod +x /biometric-sense/run.sh

ENTRYPOINT ["/biometric-sense/run.sh"]
CMD echo "running the job"
