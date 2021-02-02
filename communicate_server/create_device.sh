#!/bin/sh
if [ $# -ne 1 ]
  then
    echo "No device ID"
    exit -1
fi
EVENT_HUB_CONNECTION="Endpoint=sb://receivemsgsfromdevices.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=lM4liPS83Rni9DE72LJg2swfELncFmBKOIYTKm81eQY="
EVENT_HUB_NAME="receivemsg"

python3 communicate_server/create_device.py $1 $EVENT_HUB_CONNECTION $EVENT_HUB_NAME
ret=$?
if [ $ret -eq 0 ]
then
    echo "Successfull create IOT hub connection"
    exit 0
else
    echo "Fail to create IOT hub connection"
    exit -1
fi
