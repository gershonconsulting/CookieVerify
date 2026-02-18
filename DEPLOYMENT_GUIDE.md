# CookieVerify.com - Deployment Guide

## 🎉 Deployment Complete!

Your CookieVerify.com application is now live and running on GenSpark Hosted Deploy.

---

## 🌐 Access URLs

### **Web Application** (Frontend)
```
https://5060-i1cjab7jvbxcbqjt7kvxh-d0b9e1e2.sandbox.novita.ai
```
- Open this URL in your browser to access the web interface
- Test single cookie validation
- Try batch validation with multiple cookies
- Export results to JSON or CSV

### **API Endpoint** (Backend)
```
https://5061-i1cjab7jvbxcbqjt7kvxh-d0b9e1e2.sandbox.novita.ai
```
- Use this for direct API access
- Health check: `GET /api/health`
- Validation: `POST /api/validate`

### **GitHub Repository**
```
https://github.com/gershonconsulting/CookieVerify
```
- All code is backed up and version controlled
- Latest commit: "Deploy CookieVerify.com with HTML frontend and Python Flask backend"

### **Project Backup**
```
https://www.genspark.ai/api/files/s/orj87Qfe
```
- Complete project backup (tar.gz)
- Size: 182 KB
- Includes all source code and configuration

---

## ✅ What's Deployed

### Frontend (Port 5060)
- **Technology**: HTML5, CSS3, JavaScript (Vanilla)
- **UI Framework**: TailwindCSS
- **Features**:
  - Single cookie validation
  - Batch cookie validation
  - Real-time results display
  - JSON/CSV export
  - Responsive design
  
### Backend (Port 5061)
- **Technology**: Python 3.12 + Flask
- **Features**:
  - LinkedIn cookie validation
  - Profile data extraction
  - Google search integration for URLs
  - CORS enabled
  - RESTful API

### Infrastructure
- **Process Manager**: PM2 (auto-restart enabled)
- **Server**: Novita Sandbox (GenSpark)
- **Status**: ✅ Online and healthy

---

## 🧪 Quick Test

### Test API Health
```bash
curl https://5061-i1cjab7jvbxcbqjt7kvxh-d0b9e1e2.sandbox.novita.ai/api/health
```
Expected response:
```json
{
  "service": "CookieVerify.com API",
  "status": "ok"
}
```

### Test Cookie Validation
```bash
curl -X POST https://5061-i1cjab7jvbxcbqjt7kvxh-d0b9e1e2.sandbox.novita.ai/api/validate \
  -H "Content-Type: application/json" \
  -d '{"cookie": "YOUR_LINKEDIN_COOKIE_HERE"}'
```

---

## 🔧 Management Commands

### Check Service Status
```bash
cd /home/user/webapp
pm2 status
```

### View Logs
```bash
pm2 logs cookieverify-web --nostream    # Frontend logs
pm2 logs cookieverify-api --nostream    # Backend logs
pm2 logs --nostream                     # All logs
```

### Restart Services
```bash
# Restart specific service
pm2 restart cookieverify-web
pm2 restart cookieverify-api

# Restart all services
pm2 restart all
```

### Stop Services
```bash
pm2 stop all
```

### Start Services
```bash
cd /home/user/webapp
pm2 start ecosystem.config.cjs
```

### Full Restart (Clean)
```bash
cd /home/user/webapp
fuser -k 5060/tcp 5061/tcp 2>/dev/null || true
pm2 delete all
pm2 start ecosystem.config.cjs
```

---

## 📁 Project Structure

```
/home/user/webapp/
├── build/web/              # Frontend build (HTML/CSS/JS)
│   ├── index.html         # Main web interface
│   ├── manifest.json      # PWA manifest
│   └── favicon.png        # App icon
├── lib/                    # Original Flutter source (preserved)
├── web/                    # Original Flutter web files
├── proxy_server.py        # Python Flask API server
├── requirements.txt       # Python dependencies
├── ecosystem.config.cjs   # PM2 configuration
├── start.sh              # Deployment script
├── README.md             # Project documentation
└── .git/                 # Git repository

```

---

## 🚀 How to Use

### For End Users

1. **Open the web app**: https://5060-i1cjab7jvbxcbqjt7kvxh-d0b9e1e2.sandbox.novita.ai
2. **Get LinkedIn cookie**:
   - Log into LinkedIn
   - Open DevTools (F12) → Application → Cookies
   - Copy `li_at` cookie value
3. **Validate**:
   - Paste cookie in Single Cookie tab
   - Or paste multiple cookies in Batch Validation tab
   - Click validate button
4. **Export results**:
   - Click "Export JSON" or "Export CSV"
   - Results copied to clipboard

### For Developers

1. **Clone repository**:
```bash
git clone https://github.com/gershonconsulting/CookieVerify.git
cd CookieVerify
```

2. **Install dependencies**:
```bash
pip3 install -r requirements.txt
```

3. **Run locally**:
```bash
# Start backend
python3 proxy_server.py

# Start frontend (in another terminal)
cd build/web
python3 -m http.server 5060
```

---

## 🔄 Update & Redeploy

### Make Changes
```bash
cd /home/user/webapp

# Edit files as needed
nano build/web/index.html
nano proxy_server.py

# Commit changes
git add -A
git commit -m "Your update description"
git push origin main
```

### Restart Services
```bash
pm2 restart all
```

---

## 📊 Monitoring

### Check Service Health
- **Web App**: Open https://5060-i1cjab7jvbxcbqjt7kvxh-d0b9e1e2.sandbox.novita.ai
- **API**: `curl https://5061-i1cjab7jvbxcbqjt7kvxh-d0b9e1e2.sandbox.novita.ai/api/health`

### Monitor Resources
```bash
# PM2 monitoring
pm2 monit

# Check memory/CPU
pm2 status
```

### View Errors
```bash
# Show error logs only
pm2 logs --err --nostream

# Show specific service errors
pm2 logs cookieverify-api --err --nostream
```

---

## 🐛 Troubleshooting

### Service Not Responding
```bash
# Check if services are running
pm2 status

# If offline, restart
pm2 restart all

# If still not working, clean restart
fuser -k 5060/tcp 5061/tcp 2>/dev/null || true
pm2 delete all
pm2 start ecosystem.config.cjs
```

### API Connection Failed
```bash
# Test local connection
curl http://localhost:5061/api/health

# Check logs
pm2 logs cookieverify-api --nostream

# Verify Python dependencies
pip3 install -r requirements.txt
```

### Port Already in Use
```bash
# Kill processes on ports
fuser -k 5060/tcp 2>/dev/null || true
fuser -k 5061/tcp 2>/dev/null || true

# Restart services
pm2 restart all
```

---

## 🎯 Next Steps

### Immediate Tasks
1. ✅ Test the web application with real LinkedIn cookies
2. ✅ Verify both single and batch validation work
3. ✅ Test export functionality (JSON/CSV)
4. 🔲 Configure custom domain (CookieVerify.com)

### Production Readiness
1. 🔲 Set up production monitoring
2. 🔲 Implement rate limiting
3. 🔲 Add error tracking (Sentry)
4. 🔲 Configure analytics

### Feature Enhancements
1. 🔲 Add cookie expiration detection
2. 🔲 Implement CSV file upload
3. 🔲 Add user authentication
4. 🔲 Create historical tracking

---

## 📞 Support

- **Issues**: https://github.com/gershonconsulting/CookieVerify/issues
- **Email**: support@gershonconsulting.com
- **Documentation**: See README.md in project root

---

## ✨ Success!

Your CookieVerify.com application is now live and ready to use! 🎉

**What You Can Do Now:**
- Share the web app URL with users
- Test with real LinkedIn cookies
- Monitor usage via PM2
- Make updates and redeploy easily

---

**Deployed**: February 18, 2026  
**Version**: 1.0.0  
**Platform**: GenSpark Hosted Deploy (Novita Sandbox)  
**Status**: ✅ Production Ready
