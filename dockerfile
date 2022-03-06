FROM python:3.9

ENV TZ=Asia/Tokyo

ADD files/* /root/

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r /root/requirements.txt

RUN apt update
RUN apt install -y at

RUN echo "0  0    * * *   root    python3 /root/atcoder_alert.py" >> /etc/crontab

CMD ["/bin/bash", "/root/init.sh"]