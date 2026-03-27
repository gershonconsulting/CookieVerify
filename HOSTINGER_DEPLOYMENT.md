# CookieVerify on Hostinger — Setup Guide

This guide is for the Chrome extension (Claude in Chrome) to execute on your Hostinger VPS.

## Prerequisites

- **Hostinger KVM VPS** (or higher) — not shared hosting
- SSH access to the VPS (Hostinger provides this in the control panel)
- Root credentials from Hostinger

---

## Step 1: Connect to VPS via SSH

The extension should SSH into your Hostinger VPS using the credentials Hostinger provided.

**VPS details location:** Hostinger dashboard → VPS → Your VPS → SSH Access

---

## Step 2: Run the One-Command Setup

Once SSH is connected, execute:

```bash
curl -o setup.sh https://raw.githubusercontent.com/gershonconsulting/CookieVerify/main/deploy/hostinger-setup.sh && bash setup.sh
```

This script automatically:
- ✅ Installs Python 3, pip, nginx, certbot
- ✅ Clones the CookieVerify repo
- ✅ Sets up Python virtualenv + dependencies
- ✅ Creates systemd service (auto-starts on reboot)
- ✅ Configures Nginx reverse proxy
- ✅ Installs free SSL certificates (Let's Encrypt)
- ✅ Starts the app

**Expected runtime:** 5-10 minutes

---

## Step 3: Verify Installation

After the script completes, verify the app is running:

```bash
systemctl status cookieverify
```

Expected output:
```
● cookieverify.service - CookieVerify Flask App
   Loaded: loaded (/etc/systemd/system/cookieverify.service; enabled; vendor preset: enabled)
   Active: active (running) since...
```

Check logs:
```bash
journalctl -u cookieverify -n 20
```

---

## Step 4: Update DNS Records

Point your domains to the VPS IP address. **This must be done in your domain registrar, not Hostinger.**

Go to your **domain registrar** (GoDaddy, Namecheap, etc.) → DNS settings and add:

| Type | Name | Value | TTL |
|---|---|---|---|
| A | cookieverify.com | `<VPS_IP>` | 3600 |
| A | api.cookieverify.com | `<VPS_IP>` | 3600 |

Replace `<VPS_IP>` with the actual IP from Hostinger.

**TTL Note:** DNS propagation takes 10 minutes to 24 hours. CNAME records you set up earlier can be deleted.

---

## Step 5: Test

Wait 10+ minutes for DNS to propagate, then:

```bash
# Test web interface
curl https://cookieverify.com

# Test API
curl https://api.cookieverify.com/api/health
```

Both should return 200 status.

Visit in browser:
- **Web:** https://cookieverify.com
- **API:** https://api.cookieverify.com/api/health

---

## Useful Commands

```bash
# Check app status
systemctl status cookieverify

# View live logs
journalctl -u cookieverify -f

# Restart the app
systemctl restart cookieverify

# Pull latest code and restart
cd /var/www/cookieverify && bash deploy/update.sh

# Renew SSL (auto-renews daily)
certbot renew --dry-run

# Check Nginx config
nginx -t
```

---

## Troubleshooting

### App won't start
```bash
journalctl -u cookieverify -n 50
```
Look for error messages. Common issues:
- Port 5000 already in use
- Missing Python packages

### Domain not resolving
```bash
nslookup cookieverify.com
dig cookieverify.com
```
If it doesn't show your VPS IP, DNS hasn't propagated yet. Wait longer or check your registrar's DNS settings.

### SSL certificate errors
```bash
certbot certificates
```
If expired, renew manually:
```bash
certbot renew --force-renewal
```

### 502 Bad Gateway
Nginx can't reach the Flask app. Check:
```bash
systemctl status cookieverify
journalctl -u cookieverify
```

---

## Updating the App

To deploy new code:

```bash
cd /var/www/cookieverify
bash deploy/update.sh
```

This pulls the latest code from GitHub and restarts the service.

---

## Support

- **GitHub:** https://github.com/gershonconsulting/CookieVerify
- **App URL:** https://cookieverify.com
- **API URL:** https://api.cookieverify.com
