@echo off
chcp 1251 >nul
setlocal enabledelayedexpansion

echo Starting Python script...
echo.

:: Simple animation frames
set "frames=....oooOOO000"
set "frame_count=15"
set "i=0"

:: Start Python script
python main.py
set "err_code=%errorlevel%"

:animation
ping -n 1 -w 100 127.0.0.1 >nul 2>&1

set /a "idx=i %% frame_count"
call set "char=%%frames:~!idx!,1%%

set /a "i+=1"
<nul set /p "=Processing !char! [%time%]"

:: Check if we should stop animation (simple timeout based)
if !i! lss 30 goto animation

echo.
echo.

:: Check exit code
if %err_code% neq 0 (
    echo ----------------------------------------
    echo ERROR: Script failed!
    echo Error code: %err_code%
    echo ----------------------------------------
    pause
    exit /b %err_code%
)

echo ----------------------------------------
echo SUCCESS: Script completed successfully!
echo Time: %time%
echo ----------------------------------------
pause