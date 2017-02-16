#!/bin/sh
########################################
#          Set box to standby          #
########################################

/usr/bin/wget -q -O - "http://127.0.0.1/web/powerstate?newstate=2" >/dev/null
