#!/bin/bash
# CookieVerify - Hostinger VPS Setup Script
# Run once as root after SSHing into your VPS:
#   bash hostinger-setup.sh

set -e

APP_DIR="/var/www/cookieverify"
APP_USER="www-data"
DOMAIN_WEB="cookieverify.com"
DOMAIN_API="api.cookieverify.com"

echo "=== Installing system packages ==="
apt-get update -y
apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git

echo "=== Cloning repo ==="
mkdir -p $APP_DIR
git clone https://github.com/gershonconsulting/CookieVerify.git $APP_DIR
cd $APP_DIR

echo "=== Setting up Python virtualenv ==="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Creating systemd service ==="
cat > /etc/systemd/system/cookieverify.service <<EOF
[Unit]
Description=CookieVerify Flask App
After=network.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PORT=5000"
ExecStart=$APP_DIR/venv/bin/gunicorn proxy_server:app --bind 127.0.0.1:5000 --workers 2 --timeout 60
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cookieverify
systemctl start cookieverify

echo "=== Configuring Nginx ==="
cat > /etc/nginx/sites-available/cookieverify <<EOF
server {
    listen 80;
    server_name $DOMAIN_WEB www.$DOMAIN_WEB;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 60s;
    }
}

server {
    listen 80;
    server_name $DOMAIN_API;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 60s;
    }
}
EOF

ln -sf /etc/nginx/sites-available/cookieverify /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

echo "=== Setting up SSL with Let's Encrypt ==="
certbot --nginx -d $DOMAIN_WEB -d www.$DOMAIN_WEB -d $DOMAIN_API --non-interactive --agree-tos -m admin@cookieverify.com

echo ""
echo "=== DONE ==="
echo "Web:  https://$DOMAIN_WEB"
echo "API:  https://$DOMAIN_API/api/health"
echo ""
echo "Useful commands:"
echo "  systemctl status cookieverify   # check app status"
echo "  systemctl restart cookieverify  # restart app"
echo "  journalctl -u cookieverify -f   # view logs"
