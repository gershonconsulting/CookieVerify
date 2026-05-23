#!/bin/bash
# caddy-fix.sh — restore TLS for app.cookieverify.com on 187.124.235.148
# Run as root (or sudo): bash <(curl -s https://raw.githubusercontent.com/gershonconsulting/CookieVerify/main/deploy/caddy-fix.sh)
# Or after cloning: sudo bash deploy/caddy-fix.sh

set -euo pipefail

CADDYFILE_SRC="$(dirname "$0")/Caddyfile"
CADDYFILE_DST="/etc/caddy/Caddyfile"
CADDYFILE_BAK="/etc/caddy/Caddyfile.bak.$(date +%Y%m%d_%H%M%S)"

echo "=== [1/5] Checking Caddy is installed and running ==="
systemctl is-active --quiet caddy || { echo "ERROR: caddy service is not active"; exit 1; }
caddy version

echo "=== [2/5] Backing up existing Caddyfile ==="
if [ -f "$CADDYFILE_DST" ]; then
  cp "$CADDYFILE_DST" "$CADDYFILE_BAK"
    echo "Backed up to $CADDYFILE_BAK"
      echo "--- Current Caddyfile ---"
        cat "$CADDYFILE_DST"
          echo "-------------------------"
          fi

          echo "=== [3/5] Installing new Caddyfile ==="
          if [ -f "$CADDYFILE_SRC" ]; then
            cp "$CADDYFILE_SRC" "$CADDYFILE_DST"
              echo "Copied from $CADDYFILE_SRC"
              else
                # Inline fallback if run via curl
                  cat > "$CADDYFILE_DST" << 'EOF'
                  # Caddyfile for 187.124.235.148
                  # Serves: app.cookieverify.com, api.cookieverify.com, cookieverify.com
                  # Flask/gunicorn listens on 127.0.0.1:5000

                  app.cookieverify.com {
                  	encode gzip
                    	reverse_proxy 127.0.0.1:5000
                      }

                      api.cookieverify.com {
                      	encode gzip
                        	reverse_proxy 127.0.0.1:5000
                          }

                          cookieverify.com, www.cookieverify.com {
                          	encode gzip
                            	reverse_proxy 127.0.0.1:5000
                              }
                              EOF
                                echo "Wrote inline Caddyfile"
                                fi

                                echo "=== [4/5] Validating and reloading Caddy ==="
                                caddy validate --config "$CADDYFILE_DST"
                                systemctl reload caddy
                                echo "Caddy reloaded. Watching logs for 30s..."
                                journalctl -u caddy -f --no-pager &
                                LOG_PID=$!
                                sleep 30
                                kill "$LOG_PID" 2>/dev/null || true

                                echo "=== [5/5] Verifying from this host ==="
                                for host in app.cookieverify.com api.cookieverify.com cookieverify.com; do
                                  CODE=$(curl -sk -o /dev/null -w "%{http_code}" "https://$host/" 2>/dev/null || echo "ERR")
                                    printf "  %-35s %s\n" "https://$host/" "$CODE"
                                    done

                                    echo ""
                                    echo "=== Done. All 200s = success. If you see curl SSL errors, wait 30s and re-run the verify step. ==="
