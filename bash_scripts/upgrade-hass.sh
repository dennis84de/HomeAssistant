#!/bin/bash

sudo su -s /bin/bash homeassistant <<'EOF'
source /srv/homeassistant/bin/activate
pip3 install --upgrade homeassistant
exit
EOF

sudo systemctl restart home-assistant@homeassistant.service