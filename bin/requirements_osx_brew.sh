#!/bin/bash

# Cloud SDK and App Engine
curl https://sdk.cloud.google.com | bash
gcloud components install app-engine-python

# Node.js
brew install node

# Yarn
brew install yarn

# Gulp.js
yarn global add gulp-cli

# Python related
curl https://bootstrap.pypa.io/get-pip.py | python
pip install virtualenv

# Git
brew install git
