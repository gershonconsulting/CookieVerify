module.exports = {
  apps: [
    {
      name: 'cookieverify-api',
      script: 'python3',
      args: 'proxy_server.py',
      cwd: '/home/user/webapp',
      env: {
        PORT: 5061,
        FLASK_ENV: 'production'
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'cookieverify-web',
      script: 'python3',
      args: '-m http.server 5060 --bind 0.0.0.0',
      cwd: '/home/user/webapp/build/web',
      env: {
        PORT: 5060
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
}
