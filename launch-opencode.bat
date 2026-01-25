@echo off
REM Script pour lancer OpenCode dans le container
docker exec -it trad-bot-opencode bash -c "set -a; source /root/.config/opencode/.env 2>/dev/null; set +a; opencode"
