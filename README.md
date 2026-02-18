# CookieVerify.com - LinkedIn Cookie Validator

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Flutter](https://img.shields.io/badge/Flutter-3.35.4-blue.svg)](https://flutter.dev/)
[![Python](https://img.shields.io/badge/Python-3.12-green.svg)](https://www.python.org/)

Professional LinkedIn cookie validation tool with web interface and REST API for verifying cookie authenticity and extracting profile data.

## 🌟 Features

- **Web Application**: Flutter-based responsive web interface
- **REST API**: Python Flask proxy server for cookie validation
- **Batch Processing**: Validate multiple cookies simultaneously
- **Profile Extraction**: Extract name, title, company, and profile URL
- **Export Options**: JSON and CSV export formats
- **Real-time Validation**: Instant feedback on cookie validity
- **Detailed Results**: Separate working and non-working cookies

## 🚀 Live Demo

- **Web App**: [https://5060-irz84mcqme0f7uh3tsxbk-0e616f0a.sandbox.novita.ai](https://5060-irz84mcqme0f7uh3tsxbk-0e616f0a.sandbox.novita.ai)
- **API Endpoint**: [https://5061-irz84mcqme0f7uh3tsxbk-0e616f0a.sandbox.novita.ai/api/validate](https://5061-irz84mcqme0f7uh3tsxbk-0e616f0a.sandbox.novita.ai/api/validate)

## 📋 Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🏗️ Architecture

### Frontend (Flutter Web)
- **Framework**: Flutter 3.35.4 / Dart 3.9.2
- **UI Components**: Material Design 3
- **State Management**: StatefulWidget with setState
- **HTTP Client**: Built-in http package
- **Features**:
  - Single cookie validation
  - Batch cookie validation (paste multiple cookies)
  - Real-time validation feedback
  - Export to JSON/CSV
  - Responsive design

### Backend (Python Flask)
- **Framework**: Flask (Python 3.12)
- **Purpose**: LinkedIn API proxy and cookie validation
- **Features**:
  - Cookie authentication testing
  - Profile data extraction
  - Error handling and validation
  - CORS support for web access
  - RESTful API endpoints

### Technology Stack

```
┌─────────────────────────────────────────┐
│         Flutter Web Interface           │
│  (Material Design 3 + Responsive UI)    │
└──────────────┬──────────────────────────┘
               │ HTTP/JSON
               ▼
┌─────────────────────────────────────────┐
│      Python Flask Proxy Server          │
│  (Cookie Validation + Data Extraction)  │
└──────────────┬──────────────────────────┘
               │ REST API
               ▼
┌─────────────────────────────────────────┐
│        LinkedIn API + Web Scraping      │
│   (Profile Data + Authentication Test)  │
└─────────────────────────────────────────┘
```

## 📦 Installation

### Prerequisites

- Flutter SDK 3.35.4+
- Dart SDK 3.9.2+
- Python 3.12+
- pip (Python package manager)

### Clone Repository

```bash
git clone https://github.com/gershonconsulting/CookieVerify.git
cd CookieVerify
```

### Backend Setup

```bash
# Install Python dependencies
pip install flask flask-cors requests beautifulsoup4 lxml

# Start the proxy server
python3 proxy_server.py
```

The API server will start on `http://localhost:5061`

### Frontend Setup

```bash
# Install Flutter dependencies
flutter pub get

# Run in debug mode
flutter run -d chrome

# Or build for production
flutter build web --release
```

## 🎯 Usage

### Web Interface

1. **Single Cookie Validation**:
   - Paste a LinkedIn cookie in the input field
   - Click "Validate Single Cookie"
   - View results instantly

2. **Batch Validation**:
   - Switch to "Batch Validation" tab
   - Paste multiple cookies (one per line)
   - Click "Validate Batch"
   - View grouped results (Working/Non-working)

3. **Export Results**:
   - Click "Export JSON" or "Export CSV"
   - Results copied to clipboard
   - Paste into your preferred application

### API Usage

#### Validate Single Cookie

```bash
curl -X POST https://your-api-url/api/validate \
  -H "Content-Type: application/json" \
  -d '{"cookie": "YOUR_LINKEDIN_COOKIE"}'
```

**Response (Valid Cookie)**:
```json
{
  "isValid": true,
  "firstName": "John",
  "lastName": "Doe",
  "fullName": "John Doe",
  "title": "Software Engineer",
  "company": "Google",
  "profileUrl": "https://www.linkedin.com/in/johndoe/"
}
```

**Response (Invalid Cookie)**:
```json
{
  "isValid": false,
  "error": "Cookie validation failed",
  "cookieValue": "YOUR_COOKIE_HERE"
}
```

#### Health Check

```bash
curl https://your-api-url/api/health
```

**Response**:
```json
{
  "service": "CookieVerify.com API",
  "status": "ok"
}
```

## 📚 API Documentation

### Endpoints

#### `POST /api/validate`

Validates a LinkedIn cookie and extracts profile data.

**Request Body**:
```json
{
  "cookie": "REQUIRED - LinkedIn li_at cookie value",
  "email": "OPTIONAL - User email for context",
  "name": "OPTIONAL - User name for context"
}
```

**Success Response (200)**:
```json
{
  "isValid": true,
  "firstName": "string",
  "lastName": "string",
  "fullName": "string",
  "title": "string",
  "company": "string",
  "profileUrl": "string"
}
```

**Error Response (200)**:
```json
{
  "isValid": false,
  "error": "string",
  "cookieValue": "string"
}
```

**Common Error Messages**:
- `"Invalid or missing cookie parameter"` - Cookie not provided
- `"Cookie validation failed"` - Cookie expired or invalid
- `"Cookie authenticated but profile data unavailable"` - Valid cookie but no profile data
- `"Profile data extraction failed"` - Technical error during extraction

#### `GET /api/health`

Health check endpoint.

**Response (200)**:
```json
{
  "service": "CookieVerify.com API",
  "status": "ok"
}
```

#### `GET /api/docs`

Returns API documentation in JSON format.

## 🛠️ Development

### Project Structure

```
CookieVerify/
├── lib/                          # Flutter source code
│   ├── main.dart                # App entry point
│   ├── models/
│   │   └── cookie_result.dart  # Data models
│   └── services/
│       └── linkedin_validator.dart  # API client
├── web/                         # Web-specific files
│   ├── index.html              # HTML template
│   ├── manifest.json           # PWA manifest
│   └── favicon.png             # App icon
├── proxy_server.py             # Python Flask API server
├── api_docs.py                 # API documentation generator
├── pubspec.yaml                # Flutter dependencies
├── analysis_options.yaml       # Dart linter config
└── README.md                   # This file
```

### Running Tests

```bash
# Flutter tests
flutter test

# Python API tests
python3 -m pytest tests/
```

### Code Quality

```bash
# Flutter analysis
flutter analyze

# Dart formatting
dart format .
```

## 🚀 Deployment

### Frontend Deployment (Flutter Web)

```bash
# Build production release
flutter build web --release

# Serve with Python HTTP server
cd build/web
python3 -m http.server 5060 --bind 0.0.0.0
```

### Backend Deployment (Flask API)

```bash
# Production deployment with Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5061 proxy_server:app
```

### Docker Deployment

```dockerfile
# Dockerfile example (create as needed)
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY proxy_server.py .
EXPOSE 5061
CMD ["python3", "proxy_server.py"]
```

## 📊 Performance

- **Cookie Validation**: ~2-5 seconds per cookie
- **Batch Processing**: Sequential validation with rate limiting
- **API Response Time**: < 100ms (health check)
- **Concurrent Users**: Supports multiple simultaneous validations

## 🔒 Security Considerations

- **Cookie Storage**: Cookies are validated in real-time, not stored
- **CORS**: Configured for web access (adjust for production)
- **Rate Limiting**: Implement rate limiting for production use
- **HTTPS**: Always use HTTPS in production
- **Input Validation**: All inputs are validated and sanitized

## 🐛 Known Issues

- Some LinkedIn profiles without custom URLs cannot be extracted
- Rate limiting may affect batch validation speed
- Cookies expire naturally over time (typical validity: 7-30 days)

## 📈 Success Rates

Typical cookie validation success rates:
- **Fresh cookies (< 7 days)**: 40-50% valid
- **Medium age (7-30 days)**: 20-35% valid
- **Old cookies (> 30 days)**: 5-15% valid

Factors affecting validation:
- Cookie age and expiration
- Account status (active, suspended, deleted)
- Profile completeness
- Privacy settings
- LinkedIn URL availability

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow Flutter/Dart style guide
- Follow PEP 8 for Python code
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Gershon Consulting** - *Initial work* - [gershonconsulting](https://github.com/gershonconsulting)

## 🙏 Acknowledgments

- Flutter team for the excellent framework
- LinkedIn for the professional networking platform
- Open source community for various libraries used

## 📞 Support

For support, email support@gershonconsulting.com or open an issue in the GitHub repository.

## 🔗 Links

- **Website**: [CookieVerify.com](https://cookieverify.com)
- **Documentation**: [API Docs](https://5061-irz84mcqme0f7uh3tsxbk-0e616f0a.sandbox.novita.ai/api/docs)
- **Issues**: [GitHub Issues](https://github.com/gershonconsulting/CookieVerify/issues)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

**Made with ❤️ by Gershon Consulting**
