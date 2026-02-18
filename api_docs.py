#!/usr/bin/env python3
"""
API Documentation and Examples
Provides interactive documentation for external integrations
"""

API_DOCUMENTATION = {
    "service": "CookieVerify API",
    "version": "1.0.0",
    "base_url": "https://api.cookieverify.com",
    "authentication": "None required",
    
    "endpoints": {
        "validate_cookie": {
            "path": "/api/validate",
            "method": "POST",
            "description": "Validate a LinkedIn cookie and extract profile information",
            "headers": {
                "Content-Type": "application/json"
            },
            "request_body": {
                "cookie": {
                    "type": "string",
                    "required": True,
                    "description": "LinkedIn li_at cookie value",
                    "example": "AQEFAQsBAAAAABY_3nsAAAGZFW-DMQAAAZk5fAcxTgAA..."
                },
                "email": {
                    "type": "string",
                    "required": False,
                    "description": "Optional email for better profile matching",
                    "example": "john.doe@company.com"
                },
                "name": {
                    "type": "string",
                    "required": False,
                    "description": "Optional name for better profile matching",
                    "example": "John Doe"
                }
            },
            "response_success": {
                "status_code": 200,
                "content_type": "application/json",
                "example": {
                    "isValid": True,
                    "firstName": "John",
                    "lastName": "Doe",
                    "fullName": "John Doe",
                    "title": "CEO at Company",
                    "company": "Company Name",
                    "profileUrl": "https://www.linkedin.com/in/johndoe/",
                    "vanityName": "johndoe",
                    "expirationDate": "2026-12-10T17:00:00.000000",
                    "testedAt": "2025-12-10T17:00:00.000000",
                    "cookieValue": "COOKIE_VALUE"
                }
            },
            "response_invalid": {
                "status_code": 200,
                "content_type": "application/json",
                "example": {
                    "isValid": False,
                    "error": "Cookie authenticated but profile data unavailable",
                    "cookieValue": "COOKIE_VALUE"
                }
            },
            "response_error": {
                "status_code": 400,
                "content_type": "application/json",
                "example": {
                    "error": "No cookie provided"
                }
            }
        },
        
        "health_check": {
            "path": "/api/health",
            "method": "GET",
            "description": "Check API health status",
            "response": {
                "status_code": 200,
                "example": {
                    "status": "ok",
                    "service": "LinkedIn Cookie Validator Proxy"
                }
            }
        },
        
        "documentation": {
            "path": "/api/docs",
            "method": "GET",
            "description": "Get API documentation (this endpoint)",
            "response": {
                "status_code": 200,
                "example": "Full API documentation JSON"
            }
        }
    },
    
    "code_examples": {
        "curl": '''curl -X POST https://api.cookieverify.com/api/validate \\
  -H "Content-Type: application/json" \\
  -d '{
    "cookie": "YOUR_LINKEDIN_COOKIE"
  }' ''',
        
        "python": '''import requests

url = "https://api.cookieverify.com/api/validate"

payload = {
    "cookie": "YOUR_LINKEDIN_COOKIE"
}

response = requests.post(url, json=payload)
result = response.json()

if result.get('isValid'):
    print(f"✅ Valid Cookie")
    print(f"Name: {result.get('fullName')}")
    print(f"Company: {result.get('company')}")
    print(f"URL: {result.get('profileUrl')}")
else:
    print(f"❌ Invalid Cookie: {result.get('error')}")''',
        
        "javascript": '''const response = await fetch('https://api.cookieverify.com/api/validate', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        cookie: 'YOUR_LINKEDIN_COOKIE'
    })
});

const result = await response.json();

if (result.isValid) {
    console.log('✅ Valid Cookie');
    console.log('Name:', result.fullName);
    console.log('Company:', result.company);
    console.log('URL:', result.profileUrl);
} else {
    console.log('❌ Invalid Cookie:', result.error);
}''',
        
        "php": '''<?php
$url = "https://api.cookieverify.com/api/validate";

$data = array('cookie' => 'YOUR_LINKEDIN_COOKIE');
$payload = json_encode($data);

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json'));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$result = curl_exec($ch);
curl_close($ch);

$response = json_decode($result, true);

if ($response['isValid']) {
    echo "✅ Valid Cookie\\n";
    echo "Name: " . $response['fullName'] . "\\n";
    echo "Company: " . $response['company'] . "\\n";
} else {
    echo "❌ Invalid Cookie: " . $response['error'] . "\\n";
}
?>'''
    },
    
    "rate_limits": {
        "requests_per_minute": 60,
        "burst_allowance": 10,
        "note": "Rate limits enforced to ensure service quality."
    },
    
    "cors": {
        "enabled": True,
        "allowed_origins": "*",
        "allowed_methods": ["GET", "POST", "OPTIONS"],
        "allowed_headers": ["Content-Type", "Authorization"]
    },
    
    "support": {
        "documentation": "See /api/docs endpoint",
        "website": "https://cookieverify.com",
        "api_url": "https://api.cookieverify.com",
        "github": "https://github.com/gershonconsulting/CookieVerify"
    }
}


def get_api_docs():
    """Get formatted API documentation"""
    return API_DOCUMENTATION


def get_quick_start_guide():
    """Get quick start guide for external integrations"""
    return """
# 🚀 CookieVerify API - Quick Start Guide

## 1. Test the API

```bash
curl https://api.cookieverify.com/api/health
```

## 2. Validate a Cookie

```bash
curl -X POST https://api.cookieverify.com/api/validate \\
  -H "Content-Type: application/json" \\
  -d '{"cookie": "YOUR_LINKEDIN_COOKIE"}'
```

## 3. Integration Checklist

✅ Test with /api/health endpoint
✅ Test with a known valid cookie
✅ Handle both valid and invalid responses
✅ Implement timeout (30 seconds recommended)
✅ Handle network errors gracefully
✅ Cache results for performance

## 4. Response Fields

**Valid Cookie:**
- isValid: true
- firstName, lastName, fullName
- title (job title)
- company
- profileUrl (LinkedIn profile)
- vanityName (URL slug)
- expirationDate
- testedAt

**Invalid Cookie:**
- isValid: false
- error (reason)

## 5. Error Handling

- 200: Success (check isValid field)
- 400: Bad request (missing cookie)
- 500: Server error (retry with backoff)

## 6. Best Practices

- **Cache results**: Valid cookies can be cached for 1 hour
- **Timeout**: Set 30-second timeout
- **Retry logic**: Retry failed requests with exponential backoff
- **Rate limiting**: Max 60 requests/minute
- **Error handling**: Always check isValid before using data

## 7. Need Help?

- API Docs: GET /api/docs
- Health Check: GET /api/health
"""
