#!/bin/bash
# fix-site.sh - Fix SSL certs and Nginx config for all CookieVerify domains
# Run as root on the Hostinger VPS:
#   bash <(curl -s https://raw.githubusercontent.com/gershonconsulting/CookieVerify/main/deploy/fix-site.sh)

set -e

APP_DIR="/var/www/cookieverify"
APP_USER="www-data"
EMAIL="oattia@gmail.com"

echo "=== [1/6] Updating app from GitHub ==="
cd "$APP_DIR"
git fetch origin main
git reset --hard origin/main

echo "=== [2/6] Fixing file permissions ==="
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"
chmod -R 755 "$APP_DIR"

echo "=== [3/6] Removing default Nginx site ==="
rm -f /etc/nginx/sites-enabled/default

echo "=== [4/6] Writing Nginx config for all domains ==="
cat > /etc/nginx/sites-available/cookieverify << 'NGINXCONF'
server {
    listen 80;
    server_name cookieverify.com www.cookieverify.com app.cookieverify.com api.cookieverify.com;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / { return 301 https://$host$request_uri; }
}

server {
    listen 443 ssl;
    server_name cookieverify.com www.cookieverify.com app.cookieverify.com;
    ssl_certificate     /etc/letsencrypt/live/cookieverify.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cookieverify.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 443 ssl;
    server_name api.cookieverify.com;
    ssl_certificate     /etc/letsencrypt/live/cookieverify.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cookieverify.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
NGINXCONF

ln -sf /etc/nginx/sites-available/cookieverify /etc/nginx/sites-enabled/cookieverify

echo "=== [5/6] Issuing / renewing Let's Encrypt certs ==="
systemctl stop nginx || true
certbot certonly --standalone \
  -d cookieverify.com \
  -d www.cookieverify.com \
  -d app.cookieverify.com \
  -d api.cookieverify.com \
  --non-interactive --agree-tos -m "$EMAIL" \
  --expand || true
systemctl start nginx
nginx -t && systemctl reload nginx

echo "=== [6/6] Restarting app ==="
systemctl restart cookieverify
sleep 2

echo ""
echo "=== Verification ==="
for url in \
  "https://cookieverify.com" \
  "https://www.cookieverify.com" \
  "https://app.cookieverify.com" \
  "https://api.cookieverify.com/api/health"; do
  CODE=$(curl -sk -o /dev/null -w "%{http_code}" "$url")
  printf "  %-45s  %s\n" "$url" "$CODE"
done

echo ""
echo "=== Done. All 200s = fully fixed. ==="
