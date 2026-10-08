@echo off
chcp 65001 >nul
title MiniEx beta
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
  echo Node.js не встановлено. Завантажте LTS-версію з https://nodejs.org , встановіть і запустіть цей файл знову.
  start https://nodejs.org
  pause
  exit /b 1
)
node beta.js
pause
