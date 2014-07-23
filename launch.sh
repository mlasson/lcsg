#!/bin/bash
message() {
  echo -e "\e[31m$1\e[0m"
}
message 'moving to script location'
cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
message 'setting up the environement'
source activate.sh || exit
message 'moving to the root of the project'
cd lettera  || exit
message 'killing all servers'
for x in $(ps aux | grep "python manage.py" | grep -v grep | awk '{print $2}'); do kill -s 9 $x; done
message 'python manage.py runserver'
screen -d -m python manage.py runserver || exit
message 'finished without error'
