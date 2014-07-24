#!/bin/bash
message() {
  echo -e "\e[32m$1\e[0m"
}
message 'launching remotely'
ssh vitrine.ovh "srv/lcsg/command.sh $1"
