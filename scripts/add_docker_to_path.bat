@echo off
setlocal enabledelayedexpansion

echo Adding Docker to PATH...

:: Docker installation paths to check
set "DOCKER_PATHS=C:\Program Files\Docker\Docker\resources\bin;C:\Program Files\Docker\Docker\resources;C:\Program Files\Docker\Docker"

:: Check if Docker paths already exist in PATH
set "CURRENT_PATH=%PATH%"
set "PATHS_TO_ADD="

for %%p in (%DOCKER_PATHS%) do (
    if exist "%%p\docker.exe" (
        echo Found Docker at: %%p
        
        :: Check if this path is already in PATH
        echo !CURRENT_PATH! | findstr /C:"%%p" >nul
        if errorlevel 1 (
            set "PATHS_TO_ADD=!PATHS_TO_ADD!%%p;"
        ) else (
            echo Path %%p is already in PATH
        )
    )
)

:: If we found paths to add
if not "!PATHS_TO_ADD!"=="" (
    :: Add to user PATH permanently
    for /f "tokens=2* delims= " %%a in ('reg query HKCU\Environment /v PATH') do set "USER_PATH=%%b"
    
    :: Combine paths
    setx PATH "!USER_PATH!;!PATHS_TO_ADD!"
    
    :: Also add to current session
    set "PATH=%PATH%;!PATHS_TO_ADD!"
    
    echo Docker paths added to PATH successfully.
    echo Please restart any open command prompts for changes to take effect.
) else (
    echo Could not find Docker executable in standard locations.
    echo Please manually add the Docker installation directory to your PATH.
)

:: Test if docker is now accessible
where docker >nul 2>&1
if %errorlevel% equ 0 (
    echo Docker is now accessible from PATH.
    echo Docker version:
    docker --version
) else (
    echo Docker is still not accessible from PATH.
    echo You may need to restart your command prompt or computer.
)

pause