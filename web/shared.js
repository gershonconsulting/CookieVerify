/* CookieVerify v2 — Shared JS: auth helpers, API client, utilities */

const API_BASE = 'https://api.cookieverify.com';
const TOKEN_KEY = 'cv_token';

// ── Token helpers ──────────────────────────────────────────────────────────────

function getToken() {
  return localStorage.getItem(TOKEN_KEY) || '';
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

// ── Authenticated fetch ────────────────────────────────────────────────────────

async function authFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };
  const res = await fetch(API_BASE + path, { ...options, headers });
  if (res.status === 401) {
    clearToken();
    window.location.href = '/login.html';
    return null;
  }
  return res;
}

// ── Auth guards ────────────────────────────────────────────────────────────────

async function requireLogin() {
  const token = getToken();
  if (!token) {
    window.location.href = '/login.html';
    return null;
  }
  try {
    const res = await authFetch('/api/auth/me');
    if (!res || !res.ok) {
      clearToken();
      window.location.href = '/login.html';
      return null;
    }
    return await res.json();
  } catch {
    clearToken();
    window.location.href = '/login.html';
    return null;
  }
}

async function redirectIfLoggedIn(dest = '/dashboard.html') {
  const token = getToken();
  if (!token) return;
  try {
    const res = await fetch(API_BASE + '/api/auth/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) window.location.href = dest;
  } catch { /* ignore */ }
}

async function logout() {
  try {
    await authFetch('/api/auth/logout', { method: 'POST' });
  } catch { /* ignore */ }
  clearToken();
  window.location.href = '/login.html';
}

// ── Toast ──────────────────────────────────────────────────────────────────────

function showToast(msg, type = 'success') {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.className = `show ${type}`;
  clearTimeout(el._timer);
  el._timer = setTimeout(() => { el.className = ''; }, 3200);
}

// ── Copy to clipboard ──────────────────────────────────────────────────────────

function copyText(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    if (btn) {
      const orig = btn.textContent;
      btn.textContent = 'Copied!';
      setTimeout(() => { btn.textContent = orig; }, 2000);
    }
    showToast('Copied to clipboard', 'success');
  }).catch(() => showToast('Copy failed', 'error'));
}

// ── XSS escape ─────────────────────────────────────────────────────────────────

function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Formatters ─────────────────────────────────────────────────────────────────

function truncate(str, n) {
  if (!str) return '';
  return str.length > n ? str.substring(0, n) + '…' : str;
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso + (iso.endsWith('Z') ? '' : 'Z'));
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) +
    ' ' + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function timeAgo(iso) {
  if (!iso) return '—';
  const diff = Date.now() - new Date(iso + (iso.endsWith('Z') ? '' : 'Z')).getTime();
  const s = Math.floor(diff / 1000);
  if (s < 60) return 'just now';
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const day = Math.floor(h / 24);
  if (day < 30) return `${day}d ago`;
  return formatDate(iso);
}

// ── File download ──────────────────────────────────────────────────────────────

function downloadFile(filename, content, type) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([content], { type }));
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
