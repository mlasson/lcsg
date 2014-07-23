#!/bin/bash
message() {
  echo -e "\e[32m$1\e[0m"
}
read -p "\e[32mdo you want to send the database (Y/N) ?\e[0m" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
  message 'sending the database ...'
  scp 'lettera/db.sqlite3' vitrine.ovh:srv/lcsg/lettera/ || exit
  message 'done.'
fi
message 'launching remotely'
ssh vitrine.ovh "srv/lcsg/launch.sh 192.168.1.1:8087"
