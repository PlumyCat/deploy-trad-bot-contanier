# Script pour démarrer le container avec le fork custom

Write-Host "Demarrage du container avec fork Aux-petits-Oignons..." -ForegroundColor Cyan

docker run -d `
  --name trad-bot-opencode `
  -p 5545:8080 `
  -v "${env:USERPROFILE}/AuxPetitsOignons/clients:/app/src/clients" `
  -v "${env:USERPROFILE}/AuxPetitsOignons/Solution:/app/src/Solution" `
  -v "${PWD}/conf_opencode:/app/conf_opencode_mount" `
  -v "${env:USERPROFILE}/.azure:/root/.azure" `
  -it `
  deploy-trad-bot-contanier-trad-bot-opencode:latest `
  bash -c "python /app/doc_server.py & exec bash"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Container demarre avec succes !" -ForegroundColor Green
    Write-Host ""
    Write-Host "Attendez 5-6 minutes pour le premier demarrage (bun install)..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commandes utiles:" -ForegroundColor Cyan
    Write-Host "  docker logs -f trad-bot-opencode   # Voir les logs"
    Write-Host "  docker exec -it trad-bot-opencode bash   # Acceder au shell"
    Write-Host "  http://localhost:5545/procedure   # Documentation"
    Write-Host ""
} else {
    Write-Host "ERREUR: Impossible de demarrer le container" -ForegroundColor Red
}
