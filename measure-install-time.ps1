# Mesure du temps d'installation du fork

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Mesure temps installation fork" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Arret du container actuel..." -ForegroundColor Yellow
docker stop trad-bot-opencode 2>&1 | Out-Null
docker rm trad-bot-opencode 2>&1 | Out-Null

Write-Host "2. Demarrage du nouveau container..." -ForegroundColor Yellow
$StartTime = Get-Date

docker run -d `
  --name trad-bot-opencode `
  -p 5545:8080 `
  -v "${env:USERPROFILE}/AuxPetitsOignons/clients:/app/src/clients" `
  -v "${env:USERPROFILE}/AuxPetitsOignons/Solution:/app/src/Solution" `
  -v "${PWD}/conf_opencode:/app/conf_opencode_mount" `
  -v "${env:USERPROFILE}/.azure:/root/.azure" `
  -it `
  deploy-trad-bot-contanier-trad-bot-opencode:latest `
  bash -c "python /app/doc_server.py & exec bash" | Out-Null

Write-Host ""
Write-Host "3. Attente installation fork (bun install ~5 min)..." -ForegroundColor Yellow
Write-Host ""

for ($i = 0; $i -lt 420; $i++) {
    Start-Sleep -Seconds 1

    if ($i % 30 -eq 0) {
        $Elapsed = [math]::Round($i / 60, 1)
        Write-Host "   Temps ecoule: $Elapsed min..." -ForegroundColor Cyan
    }

    # Verifier si .build_done existe
    $result = docker exec trad-bot-opencode test -f /opt/aux-petits-oignons/.build_done 2>&1
    if ($LASTEXITCODE -eq 0) {
        $EndTime = Get-Date
        $Duration = ($EndTime - $StartTime).TotalMinutes
        Write-Host ""
        Write-Host "======================================" -ForegroundColor Green
        Write-Host "  Installation terminee !" -ForegroundColor Green
        Write-Host "  Duree: $([math]::Round($Duration, 1)) minutes" -ForegroundColor Green
        Write-Host "======================================" -ForegroundColor Green
        Write-Host ""

        # Tester OpenCode
        Write-Host "4. Test OpenCode (warning baseline?)..." -ForegroundColor Yellow
        docker exec trad-bot-opencode bash -c "echo 'exit' | timeout 5 opencode 2>&1 | head -5"

        Write-Host ""
        Write-Host "Pour acceder au container:" -ForegroundColor Cyan
        Write-Host "  docker exec -it trad-bot-opencode bash" -ForegroundColor White
        Write-Host ""
        exit 0
    }
}

Write-Host ""
Write-Host "TIMEOUT - L'installation a depasse 7 minutes" -ForegroundColor Red
Write-Host "Verifiez les logs: docker logs trad-bot-opencode" -ForegroundColor Yellow
