FROM trolann/rbimage:latest

ENV DIR_PATH='/rastabot-sounds/'
ENV DB_DIR='/rastabotdb/'

RUN mkdir -p '/rastabot-sounds/'
RUN mkdir -p '/rastabotdb/'

COPY . /rastabot-sounds/

CMD ["/rastabot-sounds/main.py"]