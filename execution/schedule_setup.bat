@echo off
:: Kør som administrator — opretter daglig Windows Task Scheduler-opgave
:: Korer run_daily_newsletter.py mandag-fredag kl. 08:00

set SCRIPT=%~dp0run_daily_newsletter.py

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo FEJL: Python ikke fundet. Installer Python og proev igen.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('where python') do set PY=%%i

schtasks /create ^
  /tn "DagligtNyhedsbrev" ^
  /tr "\"%PY%\" \"%SCRIPT%\"" ^
  /sc WEEKLY ^
  /d MON,TUE,WED,THU,FRI ^
  /st 08:00 ^
  /f

if %errorlevel% equ 0 (
    echo Opgave oprettet: korer nyhedsbrev mandag-fredag kl. 08:00
) else (
    echo FEJL: Proev at koere som administrator.
)
pause
