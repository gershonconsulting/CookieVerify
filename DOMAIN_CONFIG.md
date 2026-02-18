# CookieVerify.com - Domain Configuration

## 🌐 Domain Structure

### Primary Domain: **CookieVerify.com**

#### Web Application (Frontend)
- **Production URL**: `https://cookieverify.com`
- **Current Staging URL**: `https://5060-i1cjab7jvbxcbqjt7kvxh-d0b9e1e2.sandbox.novita.ai`

#### API Endpoint (Backend)
- **Production URL**: `https://api.cookieverify.com`
- **Current Staging URL**: `https://5061-i1cjab7jvbxcbqjt7kvxh-d0b9e1e2.sandbox.novita.ai`

---

## ✅ Code Configuration Status

### Frontend (build/web/index.html)
✅ **Configured with automatic environment detection:**
```javascript
const API_URL = (() => {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:5061';
    }
    
    // GenSpark/Novita sandbox environment
    if (hostname.includes('sandbox.novita.ai')) {
        return protocol + '//' + hostname.replace('5060-', '5061-');
    }
    
    // Production environment (CookieVerify.com)
    if (hostname === 'cookieverify.com' || hostname.includes('cookieverify')) {
        return 'https://api.cookieverify.com';
    }
    
    // Fallback
    return window.location.origin.replace(':5060', ':5061');
})();
```

**Result**: ✅ Frontend will automatically use `https://api.cookieverify.com` when accessed via CookieVerify.com domain

### Backend API (proxy_server.py)
✅ **Root endpoint returns production URLs:**
```python
{
    'service': 'CookieVerify API',
    'version': '1.0.0',
    'status': 'operational',
    'endpoints': {...},
    'api_url': 'https://api.cookieverify.com',
    'web_url': 'https://cookieverify.com'
}
```

### API Documentation (api_docs.py)
✅ **All code examples use production URLs:**
- Base URL: `https://api.cookieverify.com`
- cURL examples: `https://api.cookieverify.com/api/validate`
- Python examples: `https://api.cookieverify.com/api/validate`
- JavaScript examples: `https://api.cookieverify.com/api/validate`
- PHP examples: `https://api.cookieverify.com/api/validate`

---

## 🚀 DNS Configuration Required

To complete the domain setup, you'll need to configure DNS records:

### Required DNS Records

#### For Web Application (cookieverify.com)
```
Type: CNAME or A
Name: @ (or cookieverify.com)
Value: [Your hosting provider's IP or domain]
TTL: 3600
```

#### For API (api.cookieverify.com)
```
Type: CNAME or A
Name: api
Value: [Your API server IP or domain]
TTL: 3600
```

### Example DNS Configuration

**If using Cloudflare**:
1. Go to DNS settings
2. Add record:
   - Type: CNAME
   - Name: @
   - Target: your-server.provider.com
   - Proxy status: Proxied (orange cloud)

3. Add record:
   - Type: CNAME
   - Name: api
   - Target: your-api-server.provider.com
   - Proxy status: Proxied (orange cloud)

**If using other DNS provider**:
- Similar process, but specific steps vary by provider
- Ensure SSL certificates are configured

---

## 🔄 Migration Path

### Current Status (GenSpark Staging)
- Web: `https://5060-i1cjab7jvbxcbqjt7kvxh-d0b9e1e2.sandbox.novita.ai` ✅ Live
- API: `https://5061-i1cjab7jvbxcbqjt7kvxh-d0b9e1e2.sandbox.novita.ai` ✅ Live

### After DNS Configuration
- Web: `https://cookieverify.com` → Will automatically point API requests to `https://api.cookieverify.com`
- API: `https://api.cookieverify.com` → Will serve all API endpoints

### No Code Changes Required
✅ All code is already configured to work with CookieVerify.com domain  
✅ Automatic environment detection handles staging vs production  
✅ API documentation shows production URLs  
✅ All examples use production domain  

---

## 📋 Deployment Checklist

### Domain Setup
- [ ] Purchase domain: CookieVerify.com (if not already owned)
- [ ] Configure DNS A/CNAME records for root domain
- [ ] Configure DNS A/CNAME records for api subdomain
- [ ] Verify DNS propagation (24-48 hours)

### SSL Certificates
- [ ] Obtain SSL certificate for cookieverify.com
- [ ] Obtain SSL certificate for api.cookieverify.com
- [ ] Configure web server to use SSL
- [ ] Configure API server to use SSL
- [ ] Test HTTPS connections

### Server Configuration
- [ ] Point cookieverify.com to web server (port 5060)
- [ ] Point api.cookieverify.com to API server (port 5061)
- [ ] Configure reverse proxy (Nginx/Apache) if needed
- [ ] Test both domains load correctly

### Testing
- [ ] Test web app loads at https://cookieverify.com
- [ ] Test API responds at https://api.cookieverify.com/api/health
- [ ] Test cookie validation via web interface
- [ ] Verify CORS headers work correctly
- [ ] Test all API endpoints

### Monitoring
- [ ] Set up uptime monitoring for both domains
- [ ] Configure error tracking
- [ ] Set up analytics
- [ ] Configure logging

---

## 🧪 Testing Commands

### Test DNS Resolution
```bash
# Test main domain
nslookup cookieverify.com

# Test API subdomain
nslookup api.cookieverify.com

# Test with dig
dig cookieverify.com
dig api.cookieverify.com
```

### Test API Endpoints
```bash
# Health check
curl https://api.cookieverify.com/api/health

# Validate cookie
curl -X POST https://api.cookieverify.com/api/validate \
  -H "Content-Type: application/json" \
  -d '{"cookie": "YOUR_COOKIE"}'
```

### Test Web Application
```bash
# Test main page loads
curl -I https://cookieverify.com

# Test in browser
# Open: https://cookieverify.com
```

---

## 📞 Support

If you need help with domain configuration:
- DNS setup guides: Your domain registrar's documentation
- SSL certificates: Let's Encrypt (free) or your hosting provider
- Technical support: support@gershonconsulting.com

---

## ✅ Summary

**Current State**: ✅ All code configured for CookieVerify.com domain  
**Action Required**: DNS configuration and SSL setup  
**Code Changes**: None needed - fully ready for production domain  

Once DNS is configured, your application will automatically:
- Serve the web interface at `https://cookieverify.com`
- Route API requests to `https://api.cookieverify.com`
- Work seamlessly without any code modifications

---

**Last Updated**: February 18, 2026  
**Status**: Ready for domain configuration
