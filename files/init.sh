#!/bin/bash

cd /root/
/usr/sbin/service atd start
/usr/sbin/service cron start
/usr/bin/env python3 /root/atcoder_alert.py
sleep infinity