# Script de test interactif OpenCode dans le container

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Test du fork Aux-petits-Oignons" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Verification de l'installation..." -ForegroundColor Yellow
docker exec trad-bot-opencode bash -c "opencode --version"

Write-Host ""
Write-Host "2. Verification des modeles configures..." -ForegroundColor Yellow
docker exec trad-bot-opencode bash -c "cat /root/.config/opencode/enterprise-config.json | grep -A 3 '\"id\"' | grep 'id\|name'"

Write-Host ""
Write-Host "3. Verification des endpoints Azure..." -ForegroundColor Yellow
docker exec trad-bot-opencode bash -c "cat /root/.config/opencode/.env | grep -E '(ENDPOINT|BASE_URL)' | head -5"

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Fork operationnel !" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

Write-Host "Pour tester interactivement:" -ForegroundColor Cyan
Write-Host "  docker exec -it trad-bot-opencode bash" -ForegroundColor White
Write-Host "  Puis dans le container:" -ForegroundColor White
Write-Host "    opencode    # Demarrer une nouvelle conversation" -ForegroundColor White
Write-Host ""
