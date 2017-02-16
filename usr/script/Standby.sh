#!/bin/sh
########################################
#          Set box to standby          #
########################################

wget -q -O - "http://127.0.0.1/web/powerstate?newstate=5" >/dev/null
