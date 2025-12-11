$ErrorActionPreference = "Stop"

# --- Configuration ---
$ImageName = "nmap-python"
$ContainerName = "nmap-scanner"
$Mode="auto"

# --- Execution ---

# Check if the image exists locally; if not, try to load it from the tar file
if (-not (docker images -q $ImageName)) {
    if (Test-Path "$ImageName.tar") {
        Write-Host "Loading image from tar file..." -ForegroundColor Cyan
        docker load -i "$ImageName.tar"
    } else {
        Write-Warning "Image not found and .tar file is missing!"
    }
}

Write-Host "Starting container: $ContainerName in mode $Mode" -ForegroundColor Cyan

# Run the container
# --rm: Automatically remove the container when it exits
# -it: Interactive mode (useful if you want to see the output live)
docker run --rm -it --env-file .env $ImageName $Mode

Write-Host "Execution finished." -ForegroundColor Green