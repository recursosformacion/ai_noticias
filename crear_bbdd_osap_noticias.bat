@echo off
setlocal
pushd "%~dp0"

title Inicializar base de datos ai_noticias

echo.
echo ============================================
echo   Inicializacion de osap_noticias
echo   Servidor local MariaDB - 127.0.0.1:3306
echo ============================================
echo.

where mysql >nul 2>&1
if errorlevel 1 (
    echo ERROR: No se encuentra el cliente mysql.exe.
    echo Comprueba que MariaDB esta instalado y que su carpeta bin esta en PATH.
    goto :error
)

set "DB_USER="
set /p "DB_USER=Usuario MariaDB de desarrollo: "
if not defined DB_USER (
    echo ERROR: Debes indicar un usuario.
    goto :error
)

echo.
echo Se aplicara la migracion inicial. MariaDB solicitara la contrasena.
echo La cuenta necesita permiso para crear la base osap_noticias.
echo.

mysql --default-character-set=utf8mb4 --host=127.0.0.1 --port=3306 --user="%DB_USER%" --password < "database\migrations\001_initial_schema.sql"
if errorlevel 1 (
    echo.
    echo ERROR: Ha fallado la migracion 001. La migracion 002 no se ejecutara.
    goto :error
)

echo.
echo Primera migracion completada.
echo MariaDB volvera a solicitar la contrasena para cargar los tipos de contenido.
echo.

mysql --default-character-set=utf8mb4 --host=127.0.0.1 --port=3306 --user="%DB_USER%" --password < "database\migrations\002_seed_content_types.sql"
if errorlevel 1 (
    echo.
    echo ERROR: Ha fallado la migracion 002.
    goto :error
)

echo.
echo ============================================
echo   Base osap_noticias inicializada.
echo ============================================
echo.
echo Puedes cerrar esta ventana.
pause
popd
exit /b 0

:error
echo.
echo No se ha completado la inicializacion.
pause
popd
exit /b 1
