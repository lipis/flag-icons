#!/bin/bash

# Cloud SDK and App Engine
curl https://sdk.cloud.google.com | bash
gcloud components install app-engine-python

# Node.js
sudo port install nodejs

# Gulp.js
npm install -g gulp

# Python related
curl https://bootstrap.pypa.io/get-pip.py | python
pip install virtualenv

# Git
sudo port install git-core
