#!/bin/bash
echo "# MiniDropBox" >> README.md
git init
git add *
git commit -m "first commit"
git remote add origin https://github.com/plssreedhar/MiniDropBox.git
git push -u origin master
