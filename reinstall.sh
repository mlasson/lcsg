#!/bin/bash

message() {
  echo -e "\e[32m$1\e[0m"
}

PYTHON=3.4.1
VIRTUALENV=15.0.2

test -d py3env && echo "Error 'py3env' already exists." && exit


mkdir -p py3env/src
DIR=$(readlink -f py3env)

cd py3env/src
message "Download python ..."
wget http://www.python.org/ftp/python/$PYTHON/Python-$PYTHON.tgz || exit
message "Download virtual env ..."
wget -O virtualenv-$VIRTUALENV.zip https://github.com/pypa/virtualenv/archive/$VIRTUALENV.zip || exit

message "Installing dependencies ..."
sudo apt-get install libssl-dev openssl libsqlite3-dev || exit
message "Installing python $PYTHON ..." 
tar -zxvf Python-$PYTHON.tgz > /dev/null
cd Python-$PYTHON
./configure --prefix=$DIR -with-ensurepip=install > /dev/null 
make -j 5 > /dev/null 
make install > /dev/null

message "Installing virtual env $VIRTUALENV ..."
cd ..
unzip virtualenv-$VIRTUALENV.zip > /dev/null || exit
cd virtualenv-$VIRTUALENV/
$DIR/bin/python3 setup.py install > /dev/null || exit

message "Creating the virtual env ..."
$DIR/bin/python3 -m venv $DIR > /dev/null || exit 
cd $DIR/..
source activate.sh

message "Installing django ..."
pip3.4 install 'django==1.6.5' || exit
message "Finish with success !"
