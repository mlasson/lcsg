#!/bin/bash
message() {
  echo -e "\e[31m$1\e[0m"
}
message 'setting up the environement'
source activate.sh || exit
message 'moving to the root of the project'
cd lettera  || exit
message 'killing all servers'
for x in $(ps aux | grep "python manage.py" | grep -v grep | awk '{print $2}'); do kill -s 9 $x; done
message 'erasing the database'
rm -f db.sqlite3
message 'python manage.py syncdb'
python manage.py syncdb || exit
message 'python manage.py loaddata datas'
python manage.py loaddata datas || exit
message 'python manage.py create_users'
python manage.py create_users || exit
message 'python manage.py initdb'
python manage.py initdb || exit
message 'python manage.py filter'
python manage.py filter || exit
message 'python manage.py precomp'
python manage.py precomp || exit
message 'python manage.py frequency'
python manage.py frequency || exit
message 'python manage.py corpus_period'
python manage.py corpus_period || exit
message 'python manage.py runserver'
screen -d -m python manage.py runserver || exit
