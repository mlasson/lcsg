#!/bin/bash

OUTPUT=backup.json

message() {
  echo -e "\e[31m$1\e[0m"
}
message 'moving to script location'
cd "$( dirname "${BASH_SOURCE[0]}" )"
message "current directory is : $(pwd)"
message 'setting up the environement'
source activate.sh || exit
message "current python version : $(python --version)"
message 'moving to the root of the project'
cd lettera  || exit
message "Generating fixture ..."
python manage.py dumpdata auth.User browser.Subcorpus --indent 4 > $OUTPUT || exit
message "Success"

