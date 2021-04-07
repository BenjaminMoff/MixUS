#!/bin/sh
apt-get update

#Python
sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev
wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz
sudo tar zxf Python-3.7.0.tgz
cd Python-3.7.0
sudo ./configure
sudo make -j 4
sudo make altinstall
sudo apt-get install python3-pip

# Libraries
pip install PyQt5
pip install pyserial
pip install gpiozero
pip install inquirer
pip install RPi.GPIO