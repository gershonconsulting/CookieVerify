#!/usr/bin/env node

/**
 * CookieVerify.com - Deployment Startup Script
 * This script starts both the Python Flask API and the static web server
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🚀 Starting CookieVerify.com Services...\n');

// Install Python dependencies first
console.log('📦 Installing Python dependencies...');
const pipInstall = spawn('pip3', ['install', '-r', 'requirements.txt', '-q'], {
  cwd: __dirname,
  stdio: 'inherit'
});

pipInstall.on('close', (code) => {
  if (code !== 0) {
    console.error('❌ Failed to install Python dependencies');
    process.exit(1);
  }

  console.log('✅ Python dependencies installed\n');

  // Start Python Flask API
  console.log('🔧 Starting API Server (port 5061)...');
  const apiServer = spawn('python3', ['proxy_server.py'], {
    cwd: __dirname,
    stdio: 'inherit',
    env: { ...process.env, PORT: '5061' }
  });

  apiServer.on('error', (err) => {
    console.error('❌ Failed to start API server:', err);
  });

  // Start Python HTTP server for static files
  console.log('🌐 Starting Web Server (port 5060)...');
  const webServer = spawn('python3', ['-m', 'http.server', '5060', '--bind', '0.0.0.0', '--directory', 'build/web'], {
    cwd: __dirname,
    stdio: 'inherit'
  });

  webServer.on('error', (err) => {
    console.error('❌ Failed to start web server:', err);
  });

  // Handle cleanup on exit
  process.on('SIGINT', () => {
    console.log('\n⏹️  Stopping services...');
    apiServer.kill();
    webServer.kill();
    process.exit(0);
  });

  process.on('SIGTERM', () => {
    console.log('\n⏹️  Stopping services...');
    apiServer.kill();
    webServer.kill();
    process.exit(0);
  });

  console.log('\n✅ CookieVerify.com is running!');
  console.log('📍 Web App: http://localhost:5060');
  console.log('📍 API: http://localhost:5061\n');
});
