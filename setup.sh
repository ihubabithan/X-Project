#!/bin/bash
# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get update
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Install Chromedriver (put in project dir)
CHROMEDRIVER_VERSION=114.0.5735.90
wget https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver ./chromedriver
chmod +x ./chromedriver

# Install Python dependencies
pip install -r requirements.txt
