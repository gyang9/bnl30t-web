#!/bin/bash
cd "$(dirname "$0")"

echo "Cleaning up old git configuration..."
rm -rf .git

echo "Re-initializing git..."
git init
git add .
git commit -m "Fresh start"
git branch -M main

echo "---------------------------------------------------"
echo "Git has been reset!"
echo "Now run this command (replace with YOUR URL):"
echo "git remote add origin https://github.com/YOUR_USERNAME/bnl1t-web.git"
echo "git push -u origin main --force"
echo "---------------------------------------------------"
