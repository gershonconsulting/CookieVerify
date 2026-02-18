#!/bin/bash

echo "🚀 Starting CookieVerify.com Deployment"
echo "========================================"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if Flutter is available
if ! command -v flutter &> /dev/null; then
    echo "⚠️  Flutter not found, skipping build..."
    echo "ℹ️  Using pre-built web files if available"
else
    # Build Flutter web app
    echo "🔨 Building Flutter web app..."
    flutter pub get
    flutter build web --release
fi

# Clean up any existing processes on ports
echo "🧹 Cleaning up ports..."
fuser -k 5060/tcp 2>/dev/null || true
fuser -k 5061/tcp 2>/dev/null || true

# Start services with PM2
echo "🚀 Starting services with PM2..."
pm2 delete all 2>/dev/null || true
pm2 start ecosystem.config.cjs

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Web App: http://localhost:5060"
echo "🔗 API: http://localhost:5061"
echo ""
echo "📊 Check status: pm2 status"
echo "📝 View logs: pm2 logs"
echo ""
