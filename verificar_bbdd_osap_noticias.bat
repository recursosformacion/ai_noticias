@echo off
setlocal
pushd "%~dp0"
title Verificar osap_noticias

py -3 tools\verify_database.py
set "RESULT=%ERRORLEVEL%"

echo.
if "%RESULT%"=="0" (
  echo La base de datos esta correcta.
) else (
  echo La verificacion ha detectado problemas. Consulta el resultado anterior.
)
echo.
pause
popd
exit /b %RESULT%
