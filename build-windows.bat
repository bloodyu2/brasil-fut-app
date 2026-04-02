@echo off
chcp 65001 >nul 2>&1
title Brasil Fut - Build Electron

echo ═══════════════════════════════════════
echo   Brasil Fut - Construir App Nativo
echo ═══════════════════════════════════════
echo.

:: Verifica Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Node.js não encontrado!
    echo Baixe em: https://nodejs.org
    pause
    exit /b 1
)

:: Verifica npm
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] npm não encontrado!
    pause
    exit /b 1
)

echo [OK] Node.js encontrado:
node --version
echo.

:: Instala dependências
echo Instalando dependências (pode demorar alguns minutos)...
npm install
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependências!
    pause
    exit /b 1
)

echo.
echo Construindo aplicativo para Windows...
npm run build-win
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao construir!
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════
echo   Concluído! App em: dist\
echo ═══════════════════════════════════════
echo.
explorer dist
pause
