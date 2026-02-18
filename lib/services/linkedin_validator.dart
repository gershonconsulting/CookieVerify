import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/cookie_result.dart';
import 'enhanced_linkedin_scraper.dart';

/// Service to validate LinkedIn cookies and extract profile information
class LinkedInValidator {
  /// Validate a single LinkedIn cookie with enhanced profile extraction
  static Future<CookieResult> validateCookie(String cookieValue) async {
    // Use enhanced scraper for better results
    return await EnhancedLinkedInScraper.extractDetailedProfile(cookieValue);
  }
  
  /// Original basic validation method (kept as fallback)
  static Future<CookieResult> validateCookieBasic(String cookieValue) async {
    try {
      // Test endpoints
      final testUrl = 'https://www.linkedin.com/feed/';
      
      final headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'Cookie': 'li_at=$cookieValue',
      };

      final response = await http.get(
        Uri.parse(testUrl),
        headers: headers,
      ).timeout(const Duration(seconds: 15));

      final isValid = response.statusCode == 200;

      if (!isValid) {
        return CookieResult(
          cookieValue: cookieValue,
          isValid: false,
          error: 'Cookie validation failed (Status: ${response.statusCode})',
        );
      }

      // Extract vanity name from response
      String? vanityName;
      String? firstName;
      String? lastName;
      String? company;

      try {
        final content = response.body;
        
        // Extract vanity name from URL pattern
        final vanityMatch = RegExp(r'/in/([a-zA-Z0-9\-]+)/').firstMatch(content);
        if (vanityMatch != null) {
          vanityName = vanityMatch.group(1);
          
          // Infer name from vanity name
          if (vanityName != null && !vanityName.contains('-')) {
            // Simple vanity like "olivierattia"
            firstName = _capitalizeFirst(vanityName);
          } else if (vanityName != null) {
            // Complex vanity like "aissa-khelifa-949a002"
            final parts = vanityName.split('-');
            if (parts.isNotEmpty) {
              firstName = _capitalizeFirst(parts[0]);
              if (parts.length > 1 && !RegExp(r'^\d').hasMatch(parts[1])) {
                lastName = _capitalizeFirst(parts[1]);
              }
            }
          }
        }
      } catch (e) {
        // Continue even if extraction fails
      }

      // Try to get more details from API
      try {
        if (vanityName != null) {
          final apiResult = await _extractProfileFromAPI(cookieValue, vanityName);
          if (apiResult['company'] != null) {
            company = apiResult['company'];
          }
        }
      } catch (e) {
        // Continue even if API call fails
      }

      final profileUrl = vanityName != null 
          ? 'https://www.linkedin.com/in/$vanityName/' 
          : null;

      final fullName = firstName != null && lastName != null
          ? '$firstName $lastName'
          : firstName;

      return CookieResult(
        cookieValue: cookieValue,
        isValid: true,
        firstName: firstName,
        lastName: lastName,
        fullName: fullName,
        company: company,
        profileUrl: profileUrl,
        vanityName: vanityName,
        expirationDate: DateTime.now().add(const Duration(days: 365)),
      );
    } catch (e) {
      return CookieResult(
        cookieValue: cookieValue,
        isValid: false,
        error: 'Error: ${e.toString()}',
      );
    }
  }

  /// Extract additional profile information from LinkedIn API
  static Future<Map<String, dynamic>> _extractProfileFromAPI(
    String cookieValue,
    String vanityName,
  ) async {
    try {
      final apiUrl = 'https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity=$vanityName&decorationId=com.linkedin.voyager.dash.deco.identity.profile.TopCardSupplementary-132';
      
      final headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/vnd.linkedin.normalized+json+2.1',
        'Cookie': 'li_at=$cookieValue; JSESSIONID="ajax:1234567890"',
        'Csrf-Token': 'ajax:1234567890',
      };

      final response = await http.get(
        Uri.parse(apiUrl),
        headers: headers,
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        String? company;
        
        // Extract company from included array
        if (data['included'] != null) {
          for (var item in data['included']) {
            if (item['companyName'] != null) {
              company = item['companyName'];
              break;
            }
            if (item['\$type'] != null && 
                item['\$type'].toString().contains('Company') &&
                item['name'] != null) {
              company = item['name'];
              break;
            }
          }
        }

        return {
          'company': company,
        };
      }
    } catch (e) {
      // Fail silently
    }

    return {};
  }

  /// Validate multiple cookies in batch
  static Future<List<CookieResult>> validateBatch(List<String> cookies) async {
    final results = <CookieResult>[];
    
    for (final cookie in cookies) {
      if (cookie.trim().isEmpty) continue;
      
      final result = await validateCookie(cookie.trim());
      results.add(result);
      
      // Small delay to avoid rate limiting
      await Future.delayed(const Duration(milliseconds: 500));
    }
    
    return results;
  }

  /// Helper to capitalize first letter
  static String _capitalizeFirst(String text) {
    if (text.isEmpty) return text;
    return text[0].toUpperCase() + text.substring(1).toLowerCase();
  }
}
