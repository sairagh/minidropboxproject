#!/bin/bash
echo "# minidropboxproject" >> README.md
git init
git add *
git commit -m "first commit"
git remote add origin https://github.com/sairagh/minidropboxproject.git
git push -u origin master
