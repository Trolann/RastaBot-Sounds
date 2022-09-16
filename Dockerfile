FROM trolann/rbimage:latest

ENV DIR_PATH='/rastabot/'
ENV DB_DIR='/dealcatcher/'

RUN mkdir -p /rastabot
RUN mkdir -p /dealcatcher

COPY . /rastabot

CMD ["/rastabot/main.py"]