# Script pour capturer les logs Docker
Set-Location F:\deploy-trad-bot-contanier

Write-Host "Demarrage du container et capture des logs..." -ForegroundColor Cyan
docker-compose up 2>&1 | Tee-Object -FilePath "docker-debug.log"
