# LinkedIn Cookie Validator - Web App

## 🔗 Live URL
**https://5060-irz84mcqme0f7uh3tsxbk-18e660f9.sandbox.novita.ai/**

## 📱 App Features

### Core Functionality
- ✅ **Single Cookie Validation** - Test one cookie at a time
- ✅ **Batch Cookie Testing** - Test multiple cookies simultaneously
- ✅ **Profile Information Extraction** - Name, Company, Profile URL
- ✅ **Export Results** - JSON and CSV format support

### Extracted Information
- First Name (from vanity name)
- Last Name (from vanity name)
- Company/Organization
- LinkedIn Profile URL
- Cookie Expiration Date
- Validation Status

## 🚀 How to Use

1. Open the web app in your browser
2. Select "Single Cookie" or "Batch Validate" tab
3. Paste your LinkedIn `li_at` cookie value(s)
4. Click "Validate Cookie" or "Validate Batch"
5. View detailed results with profile information
6. Export results using JSON or CSV buttons

## 💡 Technical Stack

- **Frontend**: Flutter Web (Material Design 3)
- **Server**: Python HTTP Server
- **Validation**: HTTP-based LinkedIn authentication check
- **Data Extraction**: HTML parsing + LinkedIn Voyager API
- **Export**: JSON and CSV clipboard support

## 🔐 Privacy & Security

- No server-side data storage
- Client-side validation
- Results visible only to you
- CORS-enabled for cross-origin requests
- Secure HTTPS connection

## 📊 Testing Results

Successfully validated with test cookies:
- ✅ Cookie #1: Olivier Attia (Gershon Consulting)
- ✅ Cookie #2: Aissa Khelifa (MIT Sloan School of Management)

## ⚙️ Server Management

### Start Server
```bash
cd /home/user/linkedin_cookie_validator/build/web
python3 -m http.server 5060 --bind 0.0.0.0
```

### Stop Server
```bash
lsof -ti:5060 | xargs kill -9
```

### Rebuild App
```bash
cd /home/user/linkedin_cookie_validator
flutter build web --release
```

## 📁 Project Structure

```
linkedin_cookie_validator/
├── lib/
│   ├── main.dart                    # App entry point
│   ├── models/
│   │   └── cookie_result.dart       # Data model
│   ├── services/
│   │   └── linkedin_validator.dart  # Validation logic
│   ├── screens/
│   │   └── home_screen.dart         # Main UI screen
│   └── widgets/
│       └── result_card.dart         # Result display widget
├── build/web/                       # Production build
└── pubspec.yaml                     # Dependencies
```

## 🌟 Key Features Explained

### Single Cookie Validation
- Paste one LinkedIn cookie
- Instant validation (~2-3 seconds)
- Detailed profile information
- Direct link to LinkedIn profile

### Batch Cookie Testing
- Test multiple cookies (one per line)
- Bulk validation with progress
- Summary statistics (valid/invalid/total)
- Individual result cards for each cookie

### Profile Information Extraction
- Extracts vanity name from LinkedIn feed
- Infers first/last name from vanity name
- Calls LinkedIn API for company information
- Builds complete profile URL

### Export Functionality
- **JSON Export**: Structured data with all fields
- **CSV Export**: Spreadsheet-compatible format
- Clipboard copy for easy sharing
- Includes all extracted information

## 📝 Notes

- LinkedIn API has rate limiting - batch validation includes delays
- Some profile fields may show "Not available" due to API restrictions
- Name extraction works best with standard vanity name formats
- Company extraction requires API access (may fail for some cookies)

## 🎨 UI Design

- LinkedIn blue theme (#0A66C2)
- Material Design 3 components
- Responsive layout (mobile & desktop)
- Dark mode support
- Clean, professional interface

## 🔄 Validation Method

1. HTTP GET request to LinkedIn feed endpoint
2. Check response status (200 = valid, 401/403 = invalid)
3. Extract vanity name from HTML response
4. Call LinkedIn Voyager API for additional data
5. Parse and display results

## ⚠️ Important Warnings

- LinkedIn cookies provide full account access - keep them secure
- Automated access may violate LinkedIn Terms of Service
- Use responsibly and ethically
- Don't share cookies publicly
- Validate cookies periodically (expire after ~1 year)

---

**Built with Flutter** 🚀 | **Deployed on Novita Sandbox** ☁️ | **December 2025** 📅
