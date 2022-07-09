FROM python:3.8-slim-bullseye

ENV PREFIX="title here" \
    INTERVAL="1" \
    FB_TOKEN="your_token" \
    FPS="1" \
    WDIR="/opt/framebot"

WORKDIR $WDIR

RUN pip3 install decord facebook-sdk numpy opencv-python-headless schedule tqdm

COPY framebot/ .

RUN mkdir frames

CMD ["main.py"]
ENTRYPOINT ["python"]

# CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
