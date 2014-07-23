#!/bin/bash
message() {
  echo -e "\e[32m$1\e[0m"
}
message 'sending the database'
scp 'lettera/db.sqlite3' vitrine.ovh:srv/lcsg/lettera/ || exit
message 'launching remotely'
scp ssh vitrine.ovh srv/lcsg/launch.sh
