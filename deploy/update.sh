#!/bin/bash
# Run this on the VPS to pull latest code and restart
# Usage: bash /var/www/cookieverify/deploy/update.sh

APP_DIR="/var/www/cookieverify"

cd $APP_DIR
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --quiet
systemctl restart cookieverify
echo "Updated and restarted."
systemctl status cookieverify --no-pager
