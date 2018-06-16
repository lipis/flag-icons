#!/bin/bash

# Hello, World!
cd ~
git clone https://github.com/gae-init/gae-init.git hello-world
cd hello-world
yarn
gulp
