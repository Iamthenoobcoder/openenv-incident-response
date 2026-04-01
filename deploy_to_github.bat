@echo off
setlocal
echo ========================================================
echo   GitHub Local Push Script (Incident AI)
echo ========================================================
echo.
echo Make sure you have created the "openenv-incident-response" 
echo repository on GitHub manually before running this!
echo.
set /p GH_TOKEN="Paste your GitHub Access Token (must have 'repo' permissions): "
echo.
echo Authenticating and uploading codebase...
echo.

REM Add the remote with your token temporarily
git remote add github https://Iamthenoobcoder:%GH_TOKEN%@github.com/Iamthenoobcoder/openenv-incident-response.git

REM Push the local branch
git push --force github master:main

REM Instantly delete the remote to keep your token perfectly secret from local logs!
git remote remove github

echo.
echo ========================================================
echo PUSH COMPLETE!
echo Check your shiny new repository at:
echo https://github.com/Iamthenoobcoder/openenv-incident-response
echo ========================================================
pause
