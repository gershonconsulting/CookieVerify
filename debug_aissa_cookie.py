#!/usr/bin/env python3
"""Debug Aissa's cookie to see why vanity extraction fails"""
import requests
import re

cookie_value = "AQEFAQwBAAAAABgAdqwAAAGZERQAQgAAAZk1IIRCTgAAr3VybjpsaTplbnRlcnByaXNlQXV0aFRva2VuOmVKeGpaQUNCeFJjbFFSU2p0ZEFHRUsyMGUrMHVSaENqZ3NmeUM1Z1J2bCtvaVlFUkFLc0VDTEE9XnVybjpsaTplbnRlcnByaXNlUHJvZmlsZToodXJuOmxpOmVudGVycHJpc2VBY2NvdW50OjEwNzM1ODk3LDIwNjQ4NjI0KV51cm46bGk6bWVtYmVyOjg0NjE2NDM38imQ9cACruxBEHWx7NkcLX0F7hqBUPpkUxX3GyNNhyjhpRTkqMnlu8qxskj4SMAR71vU2xp6MsKuoqT0VauyKvpCvoUL9ZWxVwH69YRb3OUCz12PR57C8FK0whk342Jydv5iavR6qYLAC1ijRMf8j3O7qgRPPA_VlMu0OkO2FzCh7rLqkBOabQhBSom-D2uHHP7W"

feed_url = 'https://www.linkedin.com/feed/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Cookie': f'li_at={cookie_value}',
}

print("Testing Aissa's cookie...")
print("="*60)

response = requests.get(feed_url, headers=headers, timeout=15)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    print("✅ Authentication successful")
    
    # Try different patterns
    patterns = [
        r'/in/([a-zA-Z0-9\-]+)/',
        r'linkedin\.com/in/([a-zA-Z0-9\-]+)',
        r'"publicIdentifier":"([^"]+)"',
        r'\"vanityName\":\"([^\"]+)\"',
    ]
    
    for i, pattern in enumerate(patterns, 1):
        matches = re.findall(pattern, response.text)
        print(f"\nPattern {i}: {pattern}")
        if matches:
            print(f"  Found: {matches[:5]}")  # Show first 5 matches
        else:
            print("  No matches")
    
    # Save response for inspection
    with open('/home/user/linkedin_cookie_validator/aissa_feed_response.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"\n✅ Response saved to aissa_feed_response.html ({len(response.text)} chars)")
else:
    print(f"❌ Authentication failed: {response.status_code}")
