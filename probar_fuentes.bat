@echo off
setlocal
pushd "%~dp0"
title Prueba tecnica de feeds autorizados

py -3 -m pip install -r requirements.txt
if errorlevel 1 goto :error

py -3 -m app.cli probe
set "RESULT=%ERRORLEVEL%"

echo.
pause
popd
exit /b %RESULT%

:error
echo No se pudieron instalar las dependencias.
pause
popd
exit /b 1
