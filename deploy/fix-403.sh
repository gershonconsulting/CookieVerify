#!/bin/bash
# Quick fix for 403 on already-deployed server
# Run as root: bash fix-403.sh

APP_DIR="/var/www/cookieverify"
APP_USER="www-data"

echo "=== Fixing file permissions ==="
chown -R $APP_USER:$APP_USER $APP_DIR
chmod -R 755 $APP_DIR

echo "=== Removing default Nginx site ==="
rm -f /etc/nginx/sites-enabled/default

echo "=== Reloading Nginx ==="
nginx -t && systemctl reload nginx

echo "=== Restarting app ==="
systemctl restart cookieverify

echo "=== Status ==="
systemctl is-active cookieverify && echo "App: RUNNING" || echo "App: FAILED"
curl -s http://localhost:5000/api/health && echo "" || echo "App not responding on port 5000"

echo "=== Done. Test: curl https://api.cookieverify.com/api/health ==="
