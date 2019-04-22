#!/bin/sh
source ../venv/bin/activate
platformlist="douyu egame"
for platform in $platformlist;do
platform_id=`ps -ef |grep $platform | grep lottery_main.py | grep -v grep|awk '{print $2}'`
if [ ! -n "$platform_id" ]; then
    nohup python lottery_main.py $platform &
fi
sleep 1
done
