$ErrorActionPreference = "Stop"

$ImageName = "nmap-python"
$OutputFile = "nmap-python.tar"

Write-Host "🐳 Budowanie obrazu: $ImageName..." -ForegroundColor Cyan
docker build -t $ImageName .

Write-Host "💾 Zapisywanie do pliku: $OutputFile..." -ForegroundColor Cyan
docker save "$ImageName`:latest" -o $OutputFile

Write-Host "✅ Gotowe! Utworzono $OutputFile" -ForegroundColor Green