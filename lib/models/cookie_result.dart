/// Model for LinkedIn cookie validation results
class CookieResult {
  final String cookieValue;
  final bool isValid;
  final String? firstName;
  final String? lastName;
  final String? fullName;
  final String? title;
  final String? company;
  final String? profileUrl;
  final String? vanityName;
  final DateTime? expirationDate;
  final String? error;
  final DateTime testedAt;

  CookieResult({
    required this.cookieValue,
    required this.isValid,
    this.firstName,
    this.lastName,
    this.fullName,
    this.title,
    this.company,
    this.profileUrl,
    this.vanityName,
    this.expirationDate,
    this.error,
    DateTime? testedAt,
  }) : testedAt = testedAt ?? DateTime.now();

  // Full cookie value accessor
  String get cookie => cookieValue;
  
  // Preview of cookie (first 50 chars)
  String get cookiePreview => cookieValue.length > 50 
      ? '${cookieValue.substring(0, 50)}...' 
      : cookieValue;

  // Status text
  String get statusText => isValid ? 'Valid' : 'Invalid';

  // Convert to JSON for export
  Map<String, dynamic> toJson() => {
        'cookie_preview': cookiePreview,
        'is_valid': isValid,
        'first_name': firstName,
        'last_name': lastName,
        'full_name': fullName,
        'title': title,
        'company': company,
        'profile_url': profileUrl,
        'vanity_name': vanityName,
        'expiration_date': expirationDate?.toIso8601String(),
        'error': error,
        'tested_at': testedAt.toIso8601String(),
      };

  // Convert to CSV row
  List<dynamic> toCsvRow() => [
        cookiePreview,
        isValid ? 'Valid' : 'Invalid',
        firstName ?? 'N/A',
        lastName ?? 'N/A',
        fullName ?? 'N/A',
        title ?? 'N/A',
        company ?? 'N/A',
        profileUrl ?? 'N/A',
        expirationDate?.toIso8601String() ?? 'N/A',
        testedAt.toIso8601String(),
      ];

  static List<String> csvHeaders() => [
        'Cookie Preview',
        'Status',
        'First Name',
        'Last Name',
        'Full Name',
        'Title',
        'Company',
        'Profile URL',
        'Expiration Date',
        'Tested At',
      ];
}
