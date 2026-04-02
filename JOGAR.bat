@echo off
chcp 65001 >nul 2>&1
title Brasil Fut

:: ─────────────────────────────────────────
:: Brasil Fut - Launcher
:: Abre o jogo como app standalone (sem interface de navegador)
:: ─────────────────────────────────────────

set "GAME_DIR=%~dp0"
set "GAME_FILE=%GAME_DIR%brasil-fut.html"

:: Verifica se Python está disponível (para launcher.pyw)
where python >nul 2>&1
if %errorlevel%==0 (
    echo Iniciando Brasil Fut via Python...
    start "" pythonw "%GAME_DIR%launcher.pyw"
    exit /b
)

where python3 >nul 2>&1
if %errorlevel%==0 (
    echo Iniciando Brasil Fut via Python3...
    start "" python3w "%GAME_DIR%launcher.pyw"
    exit /b
)

:: Sem Python: tenta Edge em modo app
set "EDGE=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not exist "%EDGE%" set "EDGE=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
if exist "%EDGE%" (
    echo Iniciando Brasil Fut no Microsoft Edge...
    start "" "%EDGE%" --app="file:///%GAME_FILE:\=/%"  --window-size=1400,900 --no-first-run --disable-extensions --user-data-dir="%USERPROFILE%\.brasilfut_edge"
    exit /b
)

:: Tenta Chrome em modo app
set "CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME%" set "CHROME=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME%" set "CHROME=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
if exist "%CHROME%" (
    echo Iniciando Brasil Fut no Google Chrome...
    start "" "%CHROME%" --app="file:///%GAME_FILE:\=/%"  --window-size=1400,900 --no-first-run --user-data-dir="%USERPROFILE%\.brasilfut_chrome"
    exit /b
)

:: Último recurso: abre no navegador padrão
echo Abrindo no navegador padrão...
start "" "%GAME_FILE%"
