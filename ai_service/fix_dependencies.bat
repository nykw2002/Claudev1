@echo off
echo Fixing OpenAI library dependencies...
echo.

echo Step 1: Uninstalling old packages...
pip uninstall openai httpx -y

echo.
echo Step 2: Installing updated requirements...
pip install -r requirements.txt

echo.
echo Step 3: Verifying installation...
pip show openai
pip show httpx

echo.
echo Done! Now try running: python main.py
pause
