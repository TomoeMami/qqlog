#!/bin/bash
#datime=$(date "+%Y-%m-%d %H:%M")
datime=$(date "+%Y年%m月%d日 %H:%M")
git add .
git commit -m "[Push脚本]自动上传于 $datime"
echo "git commit: 上传于 $datime"
git push origin main
echo "finished..."
