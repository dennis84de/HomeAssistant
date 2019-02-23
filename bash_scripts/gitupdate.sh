#!/bin/bash

cd /home/homeassistant/.homeassistant
source /srv/homeassistant/bin/activate
hass --script check_config

sudo git add .
sudo git status
echo -n "Enter the Description for the Change: " [Minor Update]
read CHANGE_MSG
sudo git commit -m "${CHANGE_MSG}"
sudo git push origin master

exit
