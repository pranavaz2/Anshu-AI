@echo off
title ANSHU Phase 27 - Fast Offline Voice Setup
cd /d "%~dp0"
echo ==========================================
echo ANSHU - Offline Fast English and Malayalam Voice
echo ==========================================
py -m pip install --upgrade pip
if errorlevel 1 goto failed
py -m pip install faster-whisper
if errorlevel 1 goto failed
echo.
echo Installation complete.
echo The Whisper Base model downloads automatically on first transcription.
echo That first model download requires internet. Later transcription is local.
echo.
echo Start ANSHU with: py server.py
pause
exit /b 0
:failed
echo.
echo Installation failed. Check your internet connection and Python installation.
pause
exit /b 1
