# PowerShell script to add Docker to PATH

Write-Host "Adding Docker to PATH..." -ForegroundColor Cyan

# Docker installation paths to check
$dockerPaths = @(
    "C:\Program Files\Docker\Docker\resources\bin",
    "C:\Program Files\Docker\Docker\resources",
    "C:\Program Files\Docker\Docker"
)

# Check if Docker paths already exist in PATH
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$pathsToAdd = @()

foreach ($path in $dockerPaths) {
    if (Test-Path "$path\docker.exe") {
        Write-Host "Found Docker at: $path" -ForegroundColor Green
        
        # Check if this path is already in PATH
        if ($currentPath -notlike "*$path*") {
            $pathsToAdd += $path
        } else {
            Write-Host "Path $path is already in PATH" -ForegroundColor Yellow
        }
    }
}

# If we found paths to add
if ($pathsToAdd.Count -gt 0) {
    # Add to user PATH permanently
    $newPath = $currentPath
    foreach ($path in $pathsToAdd) {
        $newPath += ";$path"
    }
    
    try {
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        Write-Host "Docker paths added to PATH successfully." -ForegroundColor Green
        Write-Host "Please restart any open command prompts for changes to take effect." -ForegroundColor Yellow
        
        # Also add to current session
        $env:PATH = "$env:PATH;$($pathsToAdd -join ';')"
    }
    catch {
        Write-Host "Error setting PATH environment variable: $_" -ForegroundColor Red
        Write-Host "You may need to run this script as administrator." -ForegroundColor Yellow
    }
} else {
    Write-Host "Could not find Docker executable in standard locations." -ForegroundColor Red
    Write-Host "Please manually add the Docker installation directory to your PATH." -ForegroundColor Yellow
}

# Test if docker is now accessible
try {
    $dockerPath = Get-Command docker -ErrorAction Stop
    Write-Host "Docker is now accessible from PATH at: $($dockerPath.Source)" -ForegroundColor Green
    Write-Host "Docker version:" -ForegroundColor Cyan
    docker --version
}
catch {
    Write-Host "Docker is still not accessible from PATH." -ForegroundColor Red
    Write-Host "You may need to restart your PowerShell session or computer." -ForegroundColor Yellow
}

Write-Host "`nPress any key to continue..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")