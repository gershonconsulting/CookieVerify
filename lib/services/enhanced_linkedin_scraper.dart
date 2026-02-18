import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/cookie_result.dart';

/// Enhanced LinkedIn profile scraper with detailed information extraction
class EnhancedLinkedInScraper {
  /// Extract detailed profile information from LinkedIn profile page
  static Future<CookieResult> extractDetailedProfile(String cookieValue) async {
    try {
      // Use proxy server to bypass CORS restrictions
      final proxyUrl = 'https://5061-irz84mcqme0f7uh3tsxbk-18e660f9.sandbox.novita.ai/api/validate';
      
      final response = await http.post(
        Uri.parse(proxyUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'cookie': cookieValue}),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        return CookieResult(
          cookieValue: cookieValue,
          isValid: data['isValid'] ?? false,
          firstName: data['firstName'],
          lastName: data['lastName'],
          fullName: data['fullName'],
          title: data['title'],
          company: data['company'],
          profileUrl: data['profileUrl'],
          vanityName: data['vanityName'],
          expirationDate: data['expirationDate'] != null 
              ? DateTime.tryParse(data['expirationDate'])
              : null,
          error: data['error'],
        );
      } else {
        return CookieResult(
          cookieValue: cookieValue,
          isValid: false,
          error: 'Proxy server error: ${response.statusCode}',
        );
      }
    } catch (e) {
      return CookieResult(
        cookieValue: cookieValue,
        isValid: false,
        error: 'Connection error: ${e.toString()}',
      );
    }
  }

  /// Original method (kept as fallback)
  static Future<CookieResult> _extractDetailedProfileDirect(String cookieValue) async {
    try {
      // Step 1: Get vanity name from feed
      final feedUrl = 'https://www.linkedin.com/feed/';
      final feedHeaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'Cookie': 'li_at=$cookieValue',
      };

      final feedResponse = await http.get(
        Uri.parse(feedUrl),
        headers: feedHeaders,
      ).timeout(const Duration(seconds: 15));

      if (feedResponse.statusCode != 200) {
        return CookieResult(
          cookieValue: cookieValue,
          isValid: false,
          error: 'Cookie validation failed (Status: ${feedResponse.statusCode})',
        );
      }

      // Extract vanity name
      String? vanityName;
      final vanityMatch = RegExp(r'/in/([a-zA-Z0-9\-]+)/').firstMatch(feedResponse.body);
      if (vanityMatch != null) {
        vanityName = vanityMatch.group(1);
      }

      if (vanityName == null) {
        return CookieResult(
          cookieValue: cookieValue,
          isValid: true,
          error: 'Could not extract profile vanity name',
        );
      }

      // Step 2: Get detailed profile from TopCard API
      final profileUrl = 'https://www.linkedin.com/voyager/api/identity/profiles/$vanityName/profileView';
      
      final profileHeaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/vnd.linkedin.normalized+json+2.1',
        'Cookie': 'li_at=$cookieValue; JSESSIONID="ajax:1234567890"',
        'Csrf-Token': 'ajax:1234567890',
        'X-Li-Lang': 'en_US',
        'X-Restli-Protocol-Version': '2.0.0',
      };

      try {
        final profileResponse = await http.get(
          Uri.parse(profileUrl),
          headers: profileHeaders,
        ).timeout(const Duration(seconds: 15));

        if (profileResponse.statusCode == 200) {
          final data = json.decode(profileResponse.body);
          return _parseProfileData(cookieValue, vanityName, data);
        }
      } catch (e) {
        // API call failed, fall back to basic extraction
      }

      // Step 3: Try alternative TopCard Supplementary API
      final topCardUrl = 'https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity=$vanityName&decorationId=com.linkedin.voyager.dash.deco.identity.profile.TopCardSupplementary-132';
      
      try {
        final topCardResponse = await http.get(
          Uri.parse(topCardUrl),
          headers: profileHeaders,
        ).timeout(const Duration(seconds: 15));

        if (topCardResponse.statusCode == 200) {
          final data = json.decode(topCardResponse.body);
          return _parseTopCardData(cookieValue, vanityName, data);
        }
      } catch (e) {
        // API call failed
      }

      // Fallback: Return basic info with inferred name
      final inferredName = _inferNameFromVanity(vanityName);
      return CookieResult(
        cookieValue: cookieValue,
        isValid: true,
        firstName: inferredName['firstName'],
        lastName: inferredName['lastName'],
        fullName: inferredName['fullName'],
        profileUrl: 'https://www.linkedin.com/in/$vanityName/',
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

  /// Parse profile data from profileView API
  static CookieResult _parseProfileData(
    String cookieValue,
    String vanityName,
    Map<String, dynamic> data,
  ) {
    String? firstName;
    String? lastName;
    String? headline;
    String? company;
    String? location;
    String? pronouns;
    int? followerCount;
    int? connectionCount;

    // Extract from profile object
    if (data['profile'] != null) {
      final profile = data['profile'];
      firstName = profile['firstName'];
      lastName = profile['lastName'];
      headline = profile['headline'];
      
      if (profile['geoLocationName'] != null) {
        location = profile['geoLocationName'];
      }
    }

    // Extract from included array
    if (data['included'] != null) {
      for (var item in data['included']) {
        final itemType = item['\$type'] ?? '';
        
        // Profile entity
        if (itemType.contains('Profile')) {
          firstName ??= item['firstName'];
          lastName ??= item['lastName'];
          headline ??= item['headline'];
          
          if (item['geoLocation'] != null && location == null) {
            final geo = item['geoLocation'];
            if (geo is Map && geo['geo'] != null) {
              location = geo['geo']['defaultLocalizedName'];
            }
          }

          // Extract pronouns
          if (item['pronouns'] != null) {
            pronouns = item['pronouns'];
          }
        }

        // Position entity (current company)
        if (itemType.contains('Position') && company == null) {
          if (item['companyName'] != null) {
            company = item['companyName'];
          } else if (item['company'] != null && item['company'] is Map) {
            company = item['company']['name'];
          }
        }

        // Network info
        if (itemType.contains('NetworkInfo')) {
          if (item['followersCount'] != null) {
            followerCount = item['followersCount'];
          }
          if (item['connectionsCount'] != null) {
            connectionCount = item['connectionsCount'];
          }
        }
      }
    }

    // Extract company from headline if not found
    if (company == null && headline != null) {
      company = _extractCompanyFromHeadline(headline);
    }

    final fullName = firstName != null && lastName != null
        ? '$firstName $lastName'
        : firstName ?? lastName;

    return CookieResult(
      cookieValue: cookieValue,
      isValid: true,
      firstName: firstName,
      lastName: lastName,
      fullName: fullName,
      company: company,
      profileUrl: 'https://www.linkedin.com/in/$vanityName/',
      vanityName: vanityName,
      expirationDate: DateTime.now().add(const Duration(days: 365)),
    );
  }

  /// Parse TopCard supplementary data
  static CookieResult _parseTopCardData(
    String cookieValue,
    String vanityName,
    Map<String, dynamic> data,
  ) {
    String? firstName;
    String? lastName;
    String? headline;
    String? company;
    String? location;

    if (data['included'] != null) {
      for (var item in data['included']) {
        final itemType = item['\$type'] ?? '';
        
        if (itemType.contains('Profile')) {
          firstName ??= item['firstName'];
          lastName ??= item['lastName'];
          headline ??= item['headline'];
        }

        if (itemType.contains('Position') && company == null) {
          company = item['companyName'] ?? item['company']?['name'];
        }

        if (itemType.contains('Company') && company == null) {
          company = item['name'];
        }
      }
    }

    if (company == null && headline != null) {
      company = _extractCompanyFromHeadline(headline);
    }

    final fullName = firstName != null && lastName != null
        ? '$firstName $lastName'
        : firstName ?? lastName;

    return CookieResult(
      cookieValue: cookieValue,
      isValid: true,
      firstName: firstName,
      lastName: lastName,
      fullName: fullName,
      company: company,
      profileUrl: 'https://www.linkedin.com/in/$vanityName/',
      vanityName: vanityName,
      expirationDate: DateTime.now().add(const Duration(days: 365)),
    );
  }

  /// Extract company from headline text
  static String? _extractCompanyFromHeadline(String headline) {
    // Pattern: "Title at Company"
    if (headline.contains(' at ')) {
      return headline.split(' at ').last.trim();
    }
    // Pattern: "Title @ Company"
    if (headline.contains(' @ ')) {
      return headline.split(' @ ').last.trim();
    }
    // Pattern: "Title | Company"
    if (headline.contains(' | ')) {
      final parts = headline.split(' | ');
      if (parts.length > 1) {
        return parts[1].trim();
      }
    }
    return null;
  }

  /// Infer name from vanity name
  static Map<String, String?> _inferNameFromVanity(String vanityName) {
    // Remove numbers and special suffixes
    final cleanVanity = vanityName.replaceAll(RegExp(r'-\d+$'), '');
    
    if (cleanVanity.contains('-')) {
      final parts = cleanVanity.split('-');
      final firstName = _capitalizeFirst(parts[0]);
      final lastName = parts.length > 1 ? _capitalizeFirst(parts[1]) : null;
      return {
        'firstName': firstName,
        'lastName': lastName,
        'fullName': lastName != null ? '$firstName $lastName' : firstName,
      };
    } else {
      final firstName = _capitalizeFirst(cleanVanity);
      return {
        'firstName': firstName,
        'lastName': null,
        'fullName': firstName,
      };
    }
  }

  static String _capitalizeFirst(String text) {
    if (text.isEmpty) return text;
    return text[0].toUpperCase() + text.substring(1).toLowerCase();
  }
}
