@echo off
cd /d F:\deploy-trad-bot-contanier
docker-compose up > docker-logs.txt 2>&1
