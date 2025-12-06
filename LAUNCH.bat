@echo off
chcp 65001 > nul
title Steam GameLoader - Premium Edition (Dezembro 2025)
echo.
echo ========================================
echo    STEAM GAMELOADER - PREMIUM EDITION
echo    Versão: Dezembro 2025
echo ========================================
echo.
echo 🔍 Verificando ambiente...
timeout /t 2 /nobreak > nul

if not exist "dist\SteamGameLoader.exe" (
    echo ❌ ERRO: Executável não encontrado!
    echo 📁 Verifique se o build foi realizado com sucesso
    pause
    exit /b 1
)

echo ✅ Executável encontrado
echo 🚀 Iniciando Steam GameLoader...
echo.

start "" "dist\SteamGameLoader.exe"

echo 💡 A aplicação está iniciando...
echo 📢 Verifique a interface em alguns segundos
timeout /t 3 /nobreak > nul
