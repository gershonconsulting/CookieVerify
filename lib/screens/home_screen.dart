import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
import '../models/cookie_result.dart';
import '../services/linkedin_validator.dart';
import '../widgets/result_card.dart';
import 'package:csv/csv.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _cookieController = TextEditingController();
  final _batchController = TextEditingController();
  bool _isLoading = false;
  List<CookieResult> _results = [];
  int _currentTab = 0; // 0 = Single, 1 = Batch

  @override
  void dispose() {
    _cookieController.dispose();
    _batchController.dispose();
    super.dispose();
  }

  Future<void> _validateSingle() async {
    final cookie = _cookieController.text.trim();
    
    if (cookie.isEmpty) {
      _showError('Please enter a LinkedIn cookie');
      return;
    }

    setState(() {
      _isLoading = true;
      _results = [];
    });

    try {
      final result = await LinkedInValidator.validateCookie(cookie);
      setState(() {
        _results = [result];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      _showError('Validation failed: ${e.toString()}');
    }
  }

  Future<void> _validateBatch() async {
    final input = _batchController.text.trim();
    
    if (input.isEmpty) {
      _showError('Please enter LinkedIn cookies (one per line)');
      return;
    }

    final cookies = input
        .split('\n')
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toList();

    if (cookies.isEmpty) {
      _showError('No valid cookies found');
      return;
    }

    setState(() {
      _isLoading = true;
      _results = [];
    });

    try {
      final results = await LinkedInValidator.validateBatch(cookies);
      setState(() {
        _results = results;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      _showError('Batch validation failed: ${e.toString()}');
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
      ),
    );
  }

  Future<void> _exportToJson() async {
    if (_results.isEmpty) {
      _showError('No results to export');
      return;
    }

    final jsonData = json.encode(_results.map((r) => r.toJson()).toList());
    await Clipboard.setData(ClipboardData(text: jsonData));
    _showSuccess('Results copied to clipboard as JSON');
  }

  Future<void> _exportToCsv() async {
    if (_results.isEmpty) {
      _showError('No results to export');
      return;
    }

    final rows = [
      CookieResult.csvHeaders(),
      ..._results.map((r) => r.toCsvRow()),
    ];

    final csvData = const ListToCsvConverter().convert(rows);
    await Clipboard.setData(ClipboardData(text: csvData));
    _showSuccess('Results copied to clipboard as CSV');
  }

  void _clearResults() {
    setState(() {
      _results = [];
      _cookieController.clear();
      _batchController.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final validCount = _results.where((r) => r.isValid).length;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Icon(Icons.verified_user, color: theme.colorScheme.primary),
            const SizedBox(width: 12),
            const Text('CookieVerify.com'),
          ],
        ),
        elevation: 0,
        actions: [
          if (_results.isNotEmpty) ...[
            IconButton(
              icon: const Icon(Icons.file_download),
              tooltip: 'Export as JSON',
              onPressed: _exportToJson,
            ),
            IconButton(
              icon: const Icon(Icons.table_chart),
              tooltip: 'Export as CSV',
              onPressed: _exportToCsv,
            ),
            IconButton(
              icon: const Icon(Icons.clear_all),
              tooltip: 'Clear Results',
              onPressed: _clearResults,
            ),
          ],
        ],
      ),
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            final isWide = constraints.maxWidth > 900;
            
            return SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Center(
                child: Container(
                  constraints: const BoxConstraints(maxWidth: 1200),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Header
                      Card(
                        color: theme.colorScheme.primaryContainer,
                        child: Padding(
                          padding: const EdgeInsets.all(24),
                          child: Column(
                            children: [
                              Icon(
                                Icons.badge,
                                size: 64,
                                color: theme.colorScheme.primary,
                              ),
                              const SizedBox(height: 16),
                              Text(
                                'LinkedIn Cookie Validator',
                                style: theme.textTheme.headlineMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                                textAlign: TextAlign.center,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Test LinkedIn cookies and extract profile information',
                                style: theme.textTheme.bodyLarge?.copyWith(
                                  color: theme.colorScheme.onPrimaryContainer.withValues(alpha: 0.8),
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 32),

                      // Tab selector
                      SegmentedButton<int>(
                        segments: const [
                          ButtonSegment(
                            value: 0,
                            label: Text('Single Cookie'),
                            icon: Icon(Icons.cookie),
                          ),
                          ButtonSegment(
                            value: 1,
                            label: Text('Batch Validate'),
                            icon: Icon(Icons.list),
                          ),
                        ],
                        selected: {_currentTab},
                        onSelectionChanged: (Set<int> newSelection) {
                          setState(() {
                            _currentTab = newSelection.first;
                            _results = [];
                          });
                        },
                      ),
                      const SizedBox(height: 24),

                      // Input section
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(24),
                          child: _currentTab == 0
                              ? _buildSingleInput()
                              : _buildBatchInput(),
                        ),
                      ),
                      const SizedBox(height: 32),

                      // Results section
                      if (_isLoading)
                        Center(
                          child: Column(
                            children: [
                              const CircularProgressIndicator(),
                              const SizedBox(height: 16),
                              Text(
                                'Validating cookies...',
                                style: theme.textTheme.bodyLarge,
                              ),
                            ],
                          ),
                        )
                      else if (_results.isNotEmpty) ...[
                        // Summary
                        Card(
                          color: theme.colorScheme.secondaryContainer,
                          child: Padding(
                            padding: const EdgeInsets.all(20),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceAround,
                              children: [
                                _buildStat(
                                  icon: Icons.check_circle,
                                  label: 'Valid',
                                  value: validCount.toString(),
                                  color: Colors.green,
                                ),
                                _buildStat(
                                  icon: Icons.cancel,
                                  label: 'Invalid',
                                  value: (_results.length - validCount).toString(),
                                  color: Colors.red,
                                ),
                                _buildStat(
                                  icon: Icons.list,
                                  label: 'Total',
                                  value: _results.length.toString(),
                                  color: theme.colorScheme.primary,
                                ),
                              ],
                            ),
                          ),
                        ),
                        const SizedBox(height: 24),

                        // Show grouped results for batch mode
                        if (_currentTab == 1 && _results.length > 1)
                          _buildGroupedResults()
                        else ...[
                          // Single cookie result or normal list
                          Text(
                            'Validation Results',
                            style: theme.textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 16),
                          ..._results.map((result) => ResultCard(result: result)),
                        ],
                      ],
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildSingleInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Enter LinkedIn Cookie (li_at)',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _cookieController,
          maxLines: 3,
          decoration: const InputDecoration(
            hintText: 'Paste your LinkedIn li_at cookie here...',
            prefixIcon: Icon(Icons.cookie),
          ),
        ),
        const SizedBox(height: 16),
        ElevatedButton.icon(
          onPressed: _isLoading ? null : _validateSingle,
          icon: const Icon(Icons.check_circle),
          label: const Text('Validate Cookie'),
        ),
      ],
    );
  }

  Widget _buildBatchInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Enter Multiple Cookies (One Per Line)',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _batchController,
          maxLines: 8,
          decoration: const InputDecoration(
            hintText: 'Paste multiple cookies here, one per line...',
            prefixIcon: Icon(Icons.list),
          ),
        ),
        const SizedBox(height: 16),
        ElevatedButton.icon(
          onPressed: _isLoading ? null : _validateBatch,
          icon: const Icon(Icons.batch_prediction),
          label: const Text('Validate Batch'),
        ),
      ],
    );
  }

  Widget _buildStat({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Column(
      children: [
        Icon(icon, color: color, size: 32),
        const SizedBox(height: 8),
        Text(
          value,
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: color,
              ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodyMedium,
        ),
      ],
    );
  }

  Widget _buildGroupedResults() {
    final theme = Theme.of(context);
    final workingCookies = _results.where((r) => r.isValid).toList();
    final nonWorkingCookies = _results.where((r) => !r.isValid).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Working Cookies Section
        if (workingCookies.isNotEmpty) ...[
          Row(
            children: [
              Icon(Icons.check_circle, color: Colors.green, size: 28),
              const SizedBox(width: 12),
              Text(
                'Working Cookies (${workingCookies.length})',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // Table for working cookies
          Card(
            color: Colors.green.withValues(alpha: 0.05),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: DataTable(
                  headingRowColor: WidgetStateProperty.all(
                    Colors.green.withValues(alpha: 0.1),
                  ),
                  columns: const [
                    DataColumn(label: Text('First Name', style: TextStyle(fontWeight: FontWeight.bold))),
                    DataColumn(label: Text('Last Name', style: TextStyle(fontWeight: FontWeight.bold))),
                    DataColumn(label: Text('Title', style: TextStyle(fontWeight: FontWeight.bold))),
                    DataColumn(label: Text('Company', style: TextStyle(fontWeight: FontWeight.bold))),
                    DataColumn(label: Text('Profile URL', style: TextStyle(fontWeight: FontWeight.bold))),
                  ],
                  rows: workingCookies.map((cookie) {
                    return DataRow(
                      cells: [
                        DataCell(Text(cookie.firstName ?? 'N/A')),
                        DataCell(Text(cookie.lastName ?? 'N/A')),
                        DataCell(
                          SizedBox(
                            width: 150,
                            child: Text(
                              cookie.title ?? 'N/A',
                              overflow: TextOverflow.ellipsis,
                              maxLines: 2,
                            ),
                          ),
                        ),
                        DataCell(
                          SizedBox(
                            width: 150,
                            child: Text(
                              cookie.company ?? 'N/A',
                              overflow: TextOverflow.ellipsis,
                              maxLines: 2,
                            ),
                          ),
                        ),
                        DataCell(
                          cookie.profileUrl != null
                              ? InkWell(
                                  onTap: () {
                                    // Open URL in new tab
                                    // For web, we'd use url_launcher
                                  },
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(Icons.link, size: 16, color: theme.colorScheme.primary),
                                      const SizedBox(width: 4),
                                      Text(
                                        'View Profile',
                                        style: TextStyle(
                                          color: theme.colorScheme.primary,
                                          decoration: TextDecoration.underline,
                                        ),
                                      ),
                                    ],
                                  ),
                                )
                              : const Text('N/A'),
                        ),
                      ],
                    );
                  }).toList(),
                ),
              ),
            ),
          ),
          const SizedBox(height: 32),
        ],

        // Non-Working Cookies Section
        if (nonWorkingCookies.isNotEmpty) ...[
          Row(
            children: [
              Icon(Icons.cancel, color: Colors.red, size: 28),
              const SizedBox(width: 12),
              Text(
                'Non-Working Cookies (${nonWorkingCookies.length})',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.red,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // List of non-working cookies
          ...nonWorkingCookies.map((result) => Card(
            color: Colors.red.withValues(alpha: 0.05),
            child: ListTile(
              leading: const Icon(Icons.error, color: Colors.red),
              title: Text(
                'Cookie #${_results.indexOf(result) + 1}',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Text(
                result.error ?? 'Authentication failed or no profile data available',
                style: TextStyle(color: Colors.red.shade700),
              ),
              trailing: result.cookie.length > 50
                  ? IconButton(
                      icon: const Icon(Icons.copy),
                      tooltip: 'Copy Cookie',
                      onPressed: () {
                        Clipboard.setData(ClipboardData(text: result.cookie));
                        _showSuccess('Cookie copied to clipboard');
                      },
                    )
                  : null,
            ),
          )),
        ],
      ],
    );
  }
}
