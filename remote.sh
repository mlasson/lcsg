#!/bin/bash
message() {
  echo -e "\e[32m$1\e[0m"
}
message "killing remotely"
ssh vitrine.ovh "srv/lcsg/stop.sh"
message "do you want to send the database (Y/N) ?"
read -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then
  message "do you want to recompute before (Y/N) ?"
  read -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]
  then
    message "do you want to regenerate fixture (Y/N) ?"
    read -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
      cd initdata || exit
      ./initdata.sh || exit
    fi
    message 'resetting ...'
    cd .. 
    ./reset.sh
  fi
  message 'compression the database ...'
  zip db.zip lettera/db.sqlite3
  message 'sending the database ...'
  scp db.zip vitrine.ovh:/tmp/ || exit
  message 'unzipping remotely ...'
  ssh vitrine.ovh unzip /tmp/db.zip -d ~/srv/lcsg/ || exit
  message 'erasing local archive'
  rm -f db.zip 
fi
message 'launching remotely'
ssh vitrine.ovh "srv/lcsg/launch.sh 192.168.1.1:8087"
