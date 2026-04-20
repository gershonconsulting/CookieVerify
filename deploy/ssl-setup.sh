#!/bin/bash
# CookieVerify - SSL Certificate Setup
# Run as root on the VPS:
#   bash ssl-setup.sh

DOMAIN_WEB="cookieverify.com"
DOMAIN_API="api.cookieverify.com"
EMAIL="admin@cookieverify.com"

echo "=== Installing certbot (if not already installed) ==="
apt-get install -y certbot python3-certbot-nginx 2>/dev/null

echo "=== Checking Nginx config is valid ==="
nginx -t || { echo "ERROR: Nginx config is invalid. Fix it first."; exit 1; }

echo "=== Requesting SSL certificates from Let's Encrypt ==="
certbot --nginx \
  -d $DOMAIN_WEB \
  -d www.$DOMAIN_WEB \
  -d $DOMAIN_API \
  --non-interactive \
  --agree-tos \
  -m $EMAIL

if [ $? -eq 0 ]; then
  echo ""
  echo "=== SSL installed successfully! ==="
  echo "Web:  https://$DOMAIN_WEB"
  echo "API:  https://$DOMAIN_API/api/health"
  echo ""
  echo "Auto-renewal is configured. Certificates renew every 90 days automatically."
else
  echo ""
  echo "=== SSL setup failed ==="
  echo "Most common reasons:"
  echo "  1. DNS not pointing to this server yet (wait 5-10 min and retry)"
  echo "  2. Port 80 is blocked by firewall"
  echo ""
  echo "Check DNS is correct:"
  echo "  dig $DOMAIN_WEB"
  echo "  dig $DOMAIN_API"
  echo ""
  echo "Expected: both should resolve to $(curl -s ifconfig.me 2>/dev/null || echo 'this server IP')"
fi
