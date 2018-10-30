#!/bin/bash

# Cloud SDK and App Engine
curl https://sdk.cloud.google.com | bash
gcloud components install app-engine-python

# Node.js
sudo apt-get install nodejs

# Yarn package manager
sudo apt-get install yarn

# Gulp.js
yarn global add gulp-cli

# Python related
curl https://bootstrap.pypa.io/get-pip.py | sudo python
sudo pip install virtualenv

# Git
sudo apt-get install git
