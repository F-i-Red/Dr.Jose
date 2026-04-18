@echo off
echo ============================================
echo   Dr. Jose -- Assistente Juridico Portugues
echo ============================================
echo.

REM Activar ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Verificar se o .env existe
if not exist .env (
    echo AVISO: Ficheiro .env nao encontrado.
    echo Copia .env.example para .env e preenche a API key.
    echo.
    pause
    exit /b 1
)

REM Menu de opcoes
echo Escolhe uma opcao:
echo  1 - Iniciar API (servidor web, porta 8000)
echo  2 - Chat linha de comandos
echo  3 - Indexar documentos legais
echo.
set /p opcao="Opcao: "

if "%opcao%"=="1" (
    echo A iniciar servidor API em http://localhost:8000 ...
    echo Documentacao em http://localhost:8000/docs
    echo.
    python -m uvicorn bot.api:app --reload --host 0.0.0.0 --port 8000
)

if "%opcao%"=="2" (
    python bot/jose.py
)

if "%opcao%"=="3" (
    python scripts/ingest.py
)
