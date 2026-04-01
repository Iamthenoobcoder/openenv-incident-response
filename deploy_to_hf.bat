@echo off
setlocal
echo ========================================================
echo   Hugging Face Spaces Deployment Script (Incident AI)
echo ========================================================
echo.
echo Make sure you have already created an empty "Docker" space 
echo on Hugging Face before running this!
echo.
set /p HF_USERNAME="1. Enter your Hugging Face Username: "
set /p HF_SPACE_NAME="2. Enter your Target Space Name (e.g. openenv-agent): "
set /p HF_TOKEN="3. Enter your Hugging Face Access Token (WRITE permission): "
echo.
echo Authenticating and uploading codebase to %HF_USERNAME%/%HF_SPACE_NAME%...
echo.

REM Add the remote with the token temporarily
git remote add hf https://%HF_USERNAME%:%HF_TOKEN%@huggingface.co/spaces/%HF_USERNAME%/%HF_SPACE_NAME%

REM Push the local primary branch to Hugging Face remote 'main' branch
git push --force hf master:main

REM Immediately delete the remote so your token is completely scrubbed from local config
git remote remove hf

echo.
echo ========================================================
echo Deployment command complete! 
echo If the push was successful, your container is now building!
echo Check your dashboard at: 
echo   https://huggingface.co/spaces/%HF_USERNAME%/%HF_SPACE_NAME%
echo ========================================================
pause
