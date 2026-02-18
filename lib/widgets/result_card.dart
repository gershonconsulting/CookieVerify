import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import '../models/cookie_result.dart';
import 'package:url_launcher/url_launcher.dart' as url_launcher;

class ResultCard extends StatelessWidget {
  final CookieResult result;

  const ResultCard({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final dateFormat = DateFormat('MMM dd, yyyy - HH:mm');

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with status
            Row(
              children: [
                Icon(
                  result.isValid ? Icons.check_circle : Icons.cancel,
                  color: result.isValid ? Colors.green : Colors.red,
                  size: 28,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        result.isValid ? 'Valid Cookie' : 'Invalid Cookie',
                        style: theme.textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: result.isValid ? Colors.green : Colors.red,
                        ),
                      ),
                      Text(
                        'Tested: ${dateFormat.format(result.testedAt)}',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                        ),
                      ),
                    ],
                  ),
                ),
                if (result.profileUrl != null)
                  IconButton(
                    icon: const Icon(Icons.open_in_new),
                    tooltip: 'Open Profile',
                    onPressed: () => _openUrl(result.profileUrl!),
                  ),
              ],
            ),
            const Divider(height: 24),

            // Profile information
            if (result.isValid) ...[
              _buildInfoRow(
                icon: Icons.person,
                label: 'Name',
                value: result.fullName ?? result.firstName ?? 'Not available',
              ),
              const SizedBox(height: 12),
              _buildInfoRow(
                icon: Icons.business,
                label: 'Company',
                value: result.company ?? 'Not available',
              ),
              const SizedBox(height: 12),
              _buildInfoRow(
                icon: Icons.link,
                label: 'Profile URL',
                value: result.profileUrl ?? 'Not available',
                isUrl: true,
              ),
              const SizedBox(height: 12),
              _buildInfoRow(
                icon: Icons.calendar_today,
                label: 'Expires',
                value: result.expirationDate != null
                    ? dateFormat.format(result.expirationDate!)
                    : 'Unknown',
              ),
            ] else ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error, color: Colors.red),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        result.error ?? 'Cookie validation failed',
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            const Divider(height: 24),

            // Cookie preview
            InkWell(
              onTap: () => _copyCookie(context),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.code, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        result.cookiePreview,
                        style: theme.textTheme.bodySmall?.copyWith(
                          fontFamily: 'monospace',
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.copy, size: 20),
                      tooltip: 'Copy full cookie',
                      onPressed: () => _copyCookie(context),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow({
    required IconData icon,
    required String label,
    required String value,
    bool isUrl = false,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 20),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                  color: Colors.grey,
                ),
              ),
              const SizedBox(height: 4),
              isUrl && value != 'Not available'
                  ? InkWell(
                      onTap: () => _openUrl(value),
                      child: Text(
                        value,
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.blue,
                          decoration: TextDecoration.underline,
                        ),
                      ),
                    )
                  : Text(
                      value,
                      style: const TextStyle(fontSize: 14),
                    ),
            ],
          ),
        ),
      ],
    );
  }

  void _copyCookie(BuildContext context) {
    Clipboard.setData(ClipboardData(text: result.cookieValue));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Cookie copied to clipboard'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _openUrl(String url) {
    // Web platform - just open in new tab
    final uri = Uri.parse(url);
    url_launcher.launchUrl(uri, mode: url_launcher.LaunchMode.externalApplication);
  }
}
