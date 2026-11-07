@echo off
setlocal
cd /d "%~dp0"
echo [1/3] Menyiapkan adapter agent...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-shared-adapters.ps1" %*
if errorlevel 1 goto failed
echo.
echo [2/3] Menyuntikkan shared policy...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0inject-agent-policy.ps1"
if errorlevel 1 goto failed
echo.
echo [3/3] Memasang tool lintas OS...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-tools.ps1"
if errorlevel 1 goto failed
echo.
echo Selesai. Adapter, policy, dan tool berhasil diproses.
set "rc=0"
goto finish
:failed
set "rc=%ERRORLEVEL%"
echo.
echo Gagal dengan kode %rc%. Baca pesan di atas.
:finish
echo.
pause
exit /b %rc%
