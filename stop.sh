#!/bin/bash
message() {
  echo -e "\e[31m$1\e[0m"
}
message 'killing all servers'
for x in $(ps aux | grep "python manage.py" | grep -v grep | awk '{print $2}'); do kill -s 9 $x; done
