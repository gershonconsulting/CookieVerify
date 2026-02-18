#!/usr/bin/env python3
"""Test title/headline extraction from LinkedIn API"""
import requests
import json

def test_cookie(cookie_value, label):
    """Test a single cookie and extract title"""
    print(f"\n{'='*60}")
    print(f"Testing: {label}")
    print('='*60)
    
    # Step 1: Get vanity name
    feed_url = 'https://www.linkedin.com/feed/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'Cookie': f'li_at={cookie_value}',
    }
    
    response = requests.get(feed_url, headers=headers, timeout=15)
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code}")
        return
    
    import re
    vanity_match = re.search(r'/in/([a-zA-Z0-9\-]+)/', response.text)
    if not vanity_match:
        print("❌ Could not extract vanity name")
        return
    
    vanity_name = vanity_match.group(1)
    print(f"✅ Vanity Name: {vanity_name}")
    
    # Step 2: Get detailed profile from API
    api_url = f'https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={vanity_name}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.TopCardSupplementary-132'
    
    api_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/vnd.linkedin.normalized+json+2.1',
        'Cookie': f'li_at={cookie_value}; JSESSIONID="ajax:1234567890"',
        'Csrf-Token': 'ajax:1234567890',
        'X-Li-Lang': 'en_US',
        'X-Restli-Protocol-Version': '2.0.0',
    }
    
    try:
        api_response = requests.get(api_url, headers=api_headers, timeout=15)
        
        if api_response.status_code == 200:
            data = api_response.json()
            
            # Extract profile information
            profile_info = {}
            
            if 'included' in data:
                for item in data['included']:
                    item_type = item.get('$type', '')
                    
                    if 'Profile' in item_type:
                        profile_info['firstName'] = item.get('firstName', profile_info.get('firstName'))
                        profile_info['lastName'] = item.get('lastName', profile_info.get('lastName'))
                        profile_info['headline'] = item.get('headline', profile_info.get('headline'))
                    
                    if 'Position' in item_type or 'profilePosition' in item.get('entityUrn', ''):
                        if 'companyName' in item:
                            profile_info['company'] = item['companyName']
            
            print(f"\n📊 Extracted Profile Data:")
            print(f"   First Name: {profile_info.get('firstName', 'N/A')}")
            print(f"   Last Name: {profile_info.get('lastName', 'N/A')}")
            print(f"   Title/Headline: {profile_info.get('headline', 'N/A')}")
            print(f"   Company: {profile_info.get('company', 'N/A')}")
            print(f"   Profile URL: https://www.linkedin.com/in/{vanity_name}/")
            
            return profile_info
        else:
            print(f"❌ API call failed: {api_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    # Test with the two working cookies
    cookies = [
        {
            'label': "Olivier Attia",
            'cookie': "AQEFAQsBAAAAABY_3nsAAAGZFW-DMQAAAZk5fAcxTgAArnVybjpsaTplbnRlcnByaXNlQXV0aFRva2VuOmVKeGpaQUFDbGp2UEMwRTBXL3RtRlJETm1ydXZrUkhFa0Y4ZVpRMW1jQ2d5VnpNd0FnQzVLd2RVXnVybjpsaTplbnRlcnByaXNlUHJvZmlsZToodXJuOmxpOmVudGVycHJpc2VBY2NvdW50OjgxNTg2MDMzLDEwOTU1NjUxNiledXJuOmxpOm1lbWJlcjozNTc0M55xXhvfNKM4_w6ixRyiBitXdcHCfuoRmvQOeuTz9ml4a9T3sppdUUvkVIwk-k-yF01PGkQ7pIzj7PxzlqHMySeG5AScsXNBSy8_RkaXvJOzki6KOIa8sPjIdlsuPf9A4MvbQWR6eWWvmM1Bchof6I1sC9DcK4EVDu6Owp9JKz9uiAGYPbRRy3loyO4BRVMg7LFP65A"
        },
        {
            'label': "Aissa Khelifa",
            'cookie': "AQEFAQwBAAAAABgAdqwAAAGZERQAQgAAAZk1IIRCTgAAr3VybjpsaTplbnRlcnByaXNlQXV0aFRva2VuOmVKeGpaQUNCeFJjbFFSU2p0ZEFHRUsyMGUrMHVSaENqZ3NmeUM1Z1J2bCtvaVlFUkFLc0VDTEE9XnVybjpsaTplbnRlcnByaXNlUHJvZmlsZToodXJuOmxpOmVudGVycHJpc2VBY2NvdW50OjEwNzM1ODk3LDIwNjQ4NjI0KV51cm46bGk6bWVtYmVyOjg0NjE2NDM38imQ9cACruxBEHWx7NkcLX0F7hqBUPpkUxX3GyNNhyjhpRTkqMnlu8qxskj4SMAR71vU2xp6MsKuoqT0VauyKvpCvoUL9ZWxVwH69YRb3OUCz12PR57C8FK0whk342Jydv5iavR6qYLAC1ijRMf8j3O7qgRPPA_VlMu0OkO2FzCh7rLqkBOabQhBSom-D2uHHP7W"
        }
    ]
    
    for cookie_data in cookies:
        test_cookie(cookie_data['cookie'], cookie_data['label'])
