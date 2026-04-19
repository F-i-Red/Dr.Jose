@echo off
title Dr. José - Assistente Jurídico Português
color 0A

echo ========================================
echo    Iniciando Dr. José...
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instala Python 3.10 ou superior
    pause
    exit /b 1
)

REM Verificar .env
if not exist .env (
    echo [AVISO] Ficheiro .env nao encontrado!
    echo Copia .env.example para .env e adiciona a tua API key
    echo.
    pause
    exit /b 1
)

REM Verificar base vetorial
if not exist "data\chroma_db" (
    echo [INFO] Base vetorial nao encontrada. A criar...
    python scripts\ingest.py
    if errorlevel 1 (
        echo [ERRO] Falha ao criar base vetorial
        pause
        exit /b 1
    )
)

REM Iniciar bot
echo [INFO] A iniciar Dr. Jose...
python bot\jose.py

echo.
echo Dr. Jose terminou.
pause
