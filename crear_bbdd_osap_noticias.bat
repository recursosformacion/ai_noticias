@echo off
setlocal
pushd "%~dp0"
title Inicializar base de datos ai_noticias

echo.
echo Aplicando migraciones de osap_noticias mediante osap.toml...
echo No se solicitan credenciales: se utiliza la configuracion local.
echo.

py -3 tools\migrate.py
set "RESULT=%ERRORLEVEL%"

echo.
if "%RESULT%"=="0" (
  echo Migraciones finalizadas correctamente.
) else (
  echo La inicializacion ha fallado. Consulta el error anterior.
)
echo.
pause
popd
exit /b %RESULT%
