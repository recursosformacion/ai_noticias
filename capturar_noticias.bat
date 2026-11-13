@echo off
setlocal
pushd "%~dp0"
title Captura de noticias musicales

py -3 -m pip install -r requirements.txt
if errorlevel 1 goto :error

py -3 -m app.cli ingest
set "RESULT=%ERRORLEVEL%"

echo.
if "%RESULT%"=="0" (
  echo Captura terminada.
) else (
  echo La captura ha terminado con errores. Consulta el mensaje anterior.
)
echo.
pause
popd
exit /b %RESULT%

:error
echo No se pudieron instalar las dependencias.
pause
popd
exit /b 1
