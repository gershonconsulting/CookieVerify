#!/usr/bin/env python3
"""
LinkedIn Cookie Validator - Backend Proxy Server
Handles LinkedIn API requests to bypass CORS restrictions
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import re
import json
import os
from datetime import datetime
from profile_sanitizer import sanitize_profile

VERSION = "1.2.2"

app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)  # Enable CORS for all routes

@app.route('/api/validate', methods=['POST'])
def validate_cookie():
    """Validate a LinkedIn cookie and extract profile information"""
    try:
        data = request.get_json()
        cookie_value = data.get('cookie')
        email = data.get('email')  # Optional: email for better Google search
        name = data.get('name')    # Optional: name for better Google search
        
        if not cookie_value:
            return jsonify({'error': 'No cookie provided'}), 400
        
        # Validate cookie with optional context
        result = validate_linkedin_cookie(cookie_value, email=email, name=name)
        # Sanitize profile data: strip trailing punctuation, reject vanity-slug-as-name,
        # add username + profileComplete + nameSource derived fields.
        result = sanitize_profile(result)
        result["version"] = VERSION
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def validate_linkedin_cookie(cookie_value, email=None, name=None):
    """Validate LinkedIn cookie and extract profile info"""
    try:
        # Step 1: Test authentication with feed
        feed_url = 'https://www.linkedin.com/feed/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'Cookie': f'li_at={cookie_value}',
        }
        
        response = requests.get(feed_url, headers=headers, timeout=15)
        # LinkedIn doesn't always set charset=utf-8; force it so accented chars
        # (e.g. "Séguin") decode correctly instead of becoming "SÃ©guin".
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            return {
                'isValid': False,
                'error': f'Cookie validation failed (Status: {response.status_code})',
                'cookieValue': cookie_value,
            }
        
        # Step 2: Extract vanity name
        vanity_name = None
        vanity_patterns = [
            r'/in/([a-zA-Z0-9\-]+)/',
            r'linkedin\.com/in/([a-zA-Z0-9\-]+)',
            r'"publicIdentifier":"([^"]+)"',
            r'\"vanityName\":\"([^\"]+)\"',
        ]
        
        for pattern in vanity_patterns:
            vanity_match = re.search(pattern, response.text)
            if vanity_match:
                vanity_name = vanity_match.group(1)
                break
        
        # Step 2b: Extract name directly from feed response.
        # The feed page embeds the user's name as memberFirstName / memberLastName
        # inside escaped JSON blobs (e.g. \"memberFirstName\":\"Bruno\").
        # This is the most reliable source — the Voyager API often omits the
        # firstName/lastName fields entirely for some accounts.
        feed_first_name = None
        feed_last_name = None
        feed_name_patterns = [
            (r'\\"memberFirstName\\":\\"([^"\\]+)\\"',
             r'\\"memberLastName\\":\\"([^"\\]+)\\"'),
            (r'"memberFirstName":"([^"]+)"',
             r'"memberLastName":"([^"]+)"'),
            (r'"firstName":"([^"]+)"',
             r'"lastName":"([^"]+)"'),
        ]
        for fn_pat, ln_pat in feed_name_patterns:
            fn_m = re.search(fn_pat, response.text)
            ln_m = re.search(ln_pat, response.text)
            if fn_m and ln_m:
                feed_first_name = fn_m.group(1)
                feed_last_name = ln_m.group(1)
                break
        
        # Step 3: Get detailed profile from API (if we have vanity name)
        profile_info = {}
        if feed_first_name:
            profile_info['firstName'] = feed_first_name
        if feed_last_name:
            profile_info['lastName'] = feed_last_name
        if vanity_name:
            api_profile = extract_profile_from_api(cookie_value, vanity_name)
            # Merge API profile into existing profile_info (which may already have
            # firstName/lastName from the feed extraction). Only overwrite when the
            # incoming value is truthy.
            for k, v in (api_profile or {}).items():
                if v: profile_info[k] = v
            
            # Fallback: Infer name from vanity name
            if not profile_info.get('firstName'):
                inferred = infer_name_from_vanity(vanity_name)
                profile_info.update(inferred)
        
        # Step 4: Try to get member ID from cookie for alternative approach
        if not vanity_name or not profile_info.get('firstName'):
            # Try to extract member ID from cookie
            member_id_match = re.search(r'member:(\d+)', cookie_value)
            if member_id_match:
                member_id = member_id_match.group(1)
                # Try to get profile using member ID
                alt_profile = get_profile_by_member_id(cookie_value, member_id)
                if alt_profile:
                    profile_info.update(alt_profile)
                    if not vanity_name and alt_profile.get('vanityName'):
                        vanity_name = alt_profile['vanityName']
        
        # Step 5: Get actual LinkedIn URL from Google search
        # Use email or name if provided for better search results
        search_context = {
            'email': email,
            'name': name,
        }
        actual_linkedin_url = get_linkedin_url_from_google(profile_info, vanity_name, search_context)
        if actual_linkedin_url:
            profile_info['profileUrl'] = actual_linkedin_url
            # Extract vanity name from Google URL if we don't have it
            if not vanity_name:
                url_match = re.search(r'/in/([a-zA-Z0-9\-]+)', actual_linkedin_url)
                if url_match:
                    vanity_name = url_match.group(1)
        elif vanity_name:
            profile_info['profileUrl'] = f'https://www.linkedin.com/in/{vanity_name}/'
        
        # Validate that we have minimum required data
        if not profile_info.get('profileUrl') and not vanity_name:
            return {
                'isValid': False,
                'error': 'Cookie authenticated but profile data unavailable - account may be incomplete, restricted, or without custom URL',
                'cookieValue': cookie_value,
            }
        
        profile_info['vanityName'] = vanity_name
        profile_info['isValid'] = True
        profile_info['cookieValue'] = cookie_value
        profile_info['testedAt'] = datetime.now().isoformat()
        profile_info['expirationDate'] = datetime.now().replace(year=datetime.now().year + 1).isoformat()
        
        return profile_info
        
    except Exception as e:
        return {
            'isValid': False,
            'error': f'Error: {str(e)}',
            'cookieValue': cookie_value,
        }

def extract_profile_from_api(cookie_value, vanity_name):
    """Extract profile information from LinkedIn Voyager API"""
    profile_info = {}
    
    # Try TopCard Supplementary API
    api_url = f'https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={vanity_name}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.TopCardSupplementary-132'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/vnd.linkedin.normalized+json+2.1',
        'Cookie': f'li_at={cookie_value}; JSESSIONID="ajax:1234567890"',
        'Csrf-Token': 'ajax:1234567890',
        'X-Li-Lang': 'en_US',
        'X-Restli-Protocol-Version': '2.0.0',
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Parse profile data from included array
            if 'included' in data:
                for item in data['included']:
                    item_type = item.get('$type', '')
                    
                    # Profile entity
                    if 'Profile' in item_type:
                        fn = item.get('firstName')
                        ln = item.get('lastName')
                        if fn: profile_info['firstName'] = fn
                        if ln: profile_info['lastName'] = ln
                        headline = item.get('headline', profile_info.get('headline'))
                        if headline:
                            profile_info['headline'] = headline
                            profile_info['title'] = headline
                    
                    # Position entity (for company)
                    if 'Position' in item_type or 'profilePosition' in item.get('entityUrn', ''):
                        if 'companyName' in item:
                            profile_info['company'] = item['companyName']
                        elif 'company' in item and isinstance(item['company'], dict):
                            profile_info['company'] = item['company'].get('name')
                    
                    # Company entity
                    if 'Company' in item_type:
                        profile_info['company'] = item.get('name', profile_info.get('company'))
            
            # Extract company from headline if not found
            if 'company' not in profile_info and 'headline' in profile_info:
                company = extract_company_from_headline(profile_info['headline'])
                if company:
                    profile_info['company'] = company
            
            # Build full name (only if both are truthy — avoids "None None" when API returns nulls)
            if profile_info.get('firstName') and profile_info.get('lastName'):
                profile_info['fullName'] = f"{profile_info['firstName']} {profile_info['lastName']}"
            elif profile_info.get('firstName'):
                profile_info['fullName'] = profile_info['firstName']
                
    except Exception as e:
        pass  # Fail silently and use fallback
    
    return profile_info

def extract_company_from_headline(headline):
    """Extract company name from headline text"""
    if ' at ' in headline:
        return headline.split(' at ')[-1].strip()
    if ' @ ' in headline:
        return headline.split(' @ ')[-1].strip()
    if ' | ' in headline:
        parts = headline.split(' | ')
        if len(parts) > 1:
            return parts[1].strip()
    return None

def infer_name_from_vanity(vanity_name):
    """Infer first/last name from vanity name.

    Returns an empty dict whenever the slug doesn't carry reliable name
    structure — i.e. anything other than a hyphenated 'firstname-lastname'
    pattern. Single-token slugs ('zaksirlin', 'ouryc'), digit-laden slugs
    ('brunoseguin9178874'), and slugs with attached digits all return {}
    so the downstream sanitizer flags the response as nameSource='vanity_only'.
    """
    if not vanity_name:
        return {}

    # Strip a real LinkedIn collision suffix like "-12345" or "_12345".
    # Crucially: do NOT strip digits concatenated directly to the name
    # (e.g. "brunoseguin9178874") — that pattern indicates the slug is
    # garbage, not a real name with a numeric suffix.
    clean_vanity = re.sub(r'[-_]\d+$', '', vanity_name)

    # If anything digit-like remains, the slug is unusable.
    if not clean_vanity or re.search(r'\d', clean_vanity):
        return {}

    # Only extract names from hyphenated slugs (LinkedIn's standard
    # 'firstname-lastname' format). Single-token slugs like 'zaksirlin'
    # are concatenated firstname+lastname with no reliable split point
    # and must not be used as a name source.
    if '-' not in clean_vanity:
        return {}

    parts = clean_vanity.split('-')
    result = {
        'firstName': capitalize_first(parts[0]),
    }
    if len(parts) > 1 and not re.match(r'^\d', parts[1]):
        result['lastName'] = capitalize_first(parts[1])
        result['fullName'] = f"{result['firstName']} {result['lastName']}"
    else:
        result['fullName'] = result['firstName']

    return result

def capitalize_first(text):
    """Capitalize first letter"""
    if not text:
        return text
    return text[0].upper() + text[1:].lower()

def get_profile_by_member_id(cookie_value, member_id):
    """Try to get profile information using member ID"""
    try:
        # Try to get profile using member ID endpoint
        api_url = f'https://www.linkedin.com/voyager/api/identity/profiles/{member_id}/profileView'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/vnd.linkedin.normalized+json+2.1',
            'Cookie': f'li_at={cookie_value}; JSESSIONID="ajax:1234567890"',
            'Csrf-Token': 'ajax:1234567890',
            'X-Li-Lang': 'en_US',
            'X-Restli-Protocol-Version': '2.0.0',
        }
        
        response = requests.get(api_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            profile_info = {}
            
            # Parse profile data
            if 'profile' in data:
                profile = data['profile']
                profile_info['firstName'] = profile.get('firstName')
                profile_info['lastName'] = profile.get('lastName')
                profile_info['headline'] = profile.get('headline')
                
                # Get vanity name
                if 'miniProfile' in profile and 'publicIdentifier' in profile['miniProfile']:
                    profile_info['vanityName'] = profile['miniProfile']['publicIdentifier']
            
            # Look in included array
            if 'included' in data:
                for item in data['included']:
                    item_type = item.get('$type', '')
                    
                    if 'Profile' in item_type:
                        fn = item.get('firstName')
                        ln = item.get('lastName')
                        hl = item.get('headline')
                        if fn: profile_info['firstName'] = fn
                        if ln: profile_info['lastName'] = ln
                        if hl: profile_info['headline'] = hl
                        
                        if 'publicIdentifier' in item:
                            profile_info['vanityName'] = item['publicIdentifier']
                    
                    if 'Position' in item_type or 'profilePosition' in item.get('entityUrn', ''):
                        if 'companyName' in item:
                            profile_info['company'] = item['companyName']
            
            if profile_info.get('headline') and not profile_info.get('company'):
                company = extract_company_from_headline(profile_info['headline'])
                if company:
                    profile_info['company'] = company
            
            if profile_info.get('headline'):
                profile_info['title'] = profile_info['headline']
            
            if profile_info.get('firstName') and profile_info.get('lastName'):
                profile_info['fullName'] = f"{profile_info['firstName']} {profile_info['lastName']}"
            
            return profile_info
            
    except Exception as e:
        pass
    
    return None

def get_linkedin_url_from_google(profile_info, vanity_name, search_context=None):
    """Get the actual LinkedIn profile URL from Google search"""
    try:
        search_context = search_context or {}
        
        # Build search query based on available information
        # Priority: email > name parameter > profile_info > vanity_name
        
        if search_context.get('email'):
            # Best option: use email
            email = search_context['email']
            email_name = email.split('@')[0].replace('.', ' ').replace('_', ' ')
            search_query = f"{email_name} LinkedIn"
        elif search_context.get('name'):
            # Second best: use provided name
            search_query = f"{search_context['name']} LinkedIn"
        else:
            # Fall back to extracted profile info
            first_name = profile_info.get('firstName', '')
            last_name = profile_info.get('lastName', '')
            company = profile_info.get('company', '')
            
            # Construct search query
            if first_name and last_name:
                search_query = f"{first_name} {last_name}"
            elif first_name:
                search_query = first_name
            elif vanity_name:
                search_query = vanity_name.replace('-', ' ')
            else:
                return None
            
            if company:
                search_query += f" {company}"
            
            search_query += " LinkedIn"
        
        # Google search URL
        google_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(google_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Extract LinkedIn URLs from Google results
            # Look for patterns including country-specific domains
            linkedin_urls = re.findall(r'https://(?:[a-z]{2}\.)?linkedin\.com/in/[a-zA-Z0-9\-]+/?', response.text)
            
            if linkedin_urls:
                # Normalize URL: convert country-specific domains to www.linkedin.com
                url = linkedin_urls[0].rstrip('/')
                # Replace country codes (ca., in., kr., hr., etc.) with www.
                url = re.sub(r'https://[a-z]{2}\.linkedin\.com', 'https://www.linkedin.com', url)
                return url
        
        return None
        
    except Exception as e:
        # Fail silently and return None
        return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'CookieVerify.com API', 'version': VERSION})

@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """API documentation endpoint"""
    from api_docs import get_api_docs
    return jsonify(get_api_docs())

@app.route('/api/quick-start', methods=['GET'])
def quick_start():
    """Quick start guide"""
    from api_docs import get_quick_start_guide
    return get_quick_start_guide(), 200, {'Content-Type': 'text/plain'}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_web(path):
    """Serve the web frontend for all non-API routes"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'CookieVerify API starting on port {port}')
    app.run(host='0.0.0.0', port=port, debug=False)
