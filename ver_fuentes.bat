@echo off
setlocal
pushd "%~dp0"
title Fuentes RSS registradas

py -3 -m pip install -r requirements.txt
if errorlevel 1 goto :error

py -3 -m app.cli sources
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
