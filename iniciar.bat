@echo off
chcp 65001 >nul
title Dr. José - Assistente Jurídico Português

echo.
echo ============================================================
echo  ⚖️  Dr. José - Assistente Jurídico Português
echo ============================================================
echo.

REM Verificar se o .env existe
if not exist ".env" (
    echo [AVISO] Ficheiro .env não encontrado!
    echo Copia .env.example para .env e preenche a tua API key.
    echo.
    copy .env.example .env
    echo Ficheiro .env criado. Abre-o e preenche a OPENROUTER_API_KEY.
    pause
    exit /b 1
)

REM Instalar dependências se necessário
echo A verificar dependências...
pip install -r requirements.txt -q
echo.

REM Menu
:menu
echo Escolhe uma opção:
echo.
echo   [1] Iniciar interface web (Streamlit)
echo   [2] Descarregar leis do DRE
echo   [3] Indexar base de conhecimento
echo   [4] Modo linha de comandos (CLI)
echo   [5] Sair
echo.
set /p opcao="Opção: "

if "%opcao%"=="1" goto streamlit
if "%opcao%"=="2" goto fetch
if "%opcao%"=="3" goto ingest
if "%opcao%"=="4" goto cli
if "%opcao%"=="5" exit /b 0
goto menu

:streamlit
echo.
echo A iniciar interface web...
echo Abre o browser em: http://localhost:8501
echo (Ctrl+C para parar)
echo.
streamlit run app.py
goto menu

:fetch
echo.
echo A descarregar leis do DRE...
python scripts/fetch_laws.py
echo.
pause
goto menu

:ingest
echo.
echo A indexar base de conhecimento...
python scripts/ingest.py
echo.
pause
goto menu

:cli
echo.
echo A iniciar modo CLI...
python bot/jose.py
echo.
pause
goto menu
