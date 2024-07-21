FROM python:3

WORKDIR /usr/src

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --upgrade opencv-python
RUN pip install pytesseract

# todo need to patch pytube after installing due to 400 bad request bugs
RUN pip install pytube
RUN pip install psutil
RUN pip install ffmpeg

COPY ./*py /usr/src
ADD ./assets /usr/src/assets
CMD [ "python", "./vf_match_analyzer.py" ]
