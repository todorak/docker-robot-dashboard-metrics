"""
Robot Framework Metrics Dashboard
Flask API и Web Interface
"""
import os
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, send_from_directory, request, Response

from metrics_parser import MetricsParser
import logging

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Flask setup
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Directories
METRICS_DATA_DIR = os.getenv('METRICS_DATA_DIR', '/app/data')
ROBOT_RESULTS_DIR = os.getenv('ROBOT_RESULTS_DIR', '/robot_results')
HISTORY_DIR = os.path.join(METRICS_DATA_DIR, 'history')

# Initialize parser
parser = MetricsParser(ROBOT_RESULTS_DIR, HISTORY_DIR)

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_runs():
    """Get all runs using parser"""
    return parser.get_all_runs()


def load_run_data(run_id):
    """Load specific run data using parser"""
    return parser.get_run_by_id(run_id)


# ============================================================================
# WEB ROUTES
# ============================================================================

@app.route('/')
def dashboard():
    """Главен dashboard"""
    return render_template('dashboard.html')


@app.route('/run/<run_id>')
def run_details(run_id):
    """Детайли за конкретен run"""
    run = parser.get_run_by_id(run_id)
    if not run:
        return "Run not found", 404
    return render_template('run_details.html', run=run)


@app.route('/run/<run_id>/<filename>')
def serve_archived_file(run_id, filename):
    """Serve archived Robot Framework reports and screenshots"""
    archive_dir = Path(HISTORY_DIR) / run_id

    if not archive_dir.exists():
        return f"Archive not found for run {run_id}", 404

    file_path = archive_dir / filename
    if not file_path.exists():
        return f"File {filename} not found in archive", 404

    return send_from_directory(str(archive_dir), filename)


@app.route('/robot-report')
def robot_report():
    """Показва Robot Framework HTML report"""
    report_path = Path(ROBOT_RESULTS_DIR) / 'report.html'

    if not report_path.exists():
        return "Report not found. Run tests first!", 404

    return send_from_directory(ROBOT_RESULTS_DIR, 'report.html')


@app.route('/robot-log')
def robot_log():
    """Показва Robot Framework HTML log"""
    log_path = Path(ROBOT_RESULTS_DIR) / 'log.html'

    if not log_path.exists():
        return "Log not found. Run tests first!", 404

    return send_from_directory(ROBOT_RESULTS_DIR, 'log.html')


# FIXED: Serve log.html directly (за links от report.html)
@app.route('/log.html')
def log_html():
    """Direct access to log.html"""
    log_path = Path(ROBOT_RESULTS_DIR) / 'log.html'

    if not log_path.exists():
        return "Log not found. Run tests first!", 404

    return send_from_directory(ROBOT_RESULTS_DIR, 'log.html')


# FIXED: Serve report.html directly (за consistency)
@app.route('/report.html')
def report_html():
    """Direct access to report.html"""
    report_path = Path(ROBOT_RESULTS_DIR) / 'report.html'

    if not report_path.exists():
        return "Report not found. Run tests first!", 404

    return send_from_directory(ROBOT_RESULTS_DIR, 'report.html')


@app.route('/<path:filename>')
def serve_robot_files(filename):
    """Serve robot result files (screenshots, logs, etc)"""
    if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
        try:
            return send_from_directory(ROBOT_RESULTS_DIR, filename)
        except:
            return "File not found", 404
    return "Not allowed", 403


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'metrics-dashboard'
    })


@app.route('/api/status')
def api_status():
    """API status информация"""
    runs = parser.get_all_runs()
    latest_run = runs[0] if runs else None

    return jsonify({
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'total_runs': len(runs),
        'latest_run': {
            'run_id': latest_run['run_id'],
            'timestamp': latest_run['timestamp'],
            'pass_rate': latest_run['summary']['pass_rate']
        } if latest_run else None,
        # Добави тези полета на топ ниво за frontend-а
        'total_tests': latest_run['summary']['total'] if latest_run else 0,
        'pass_rate': latest_run['summary']['pass_rate'] if latest_run else 0,
        'avg_duration': latest_run['duration'] if latest_run else 0,
        'last_run': latest_run['timestamp'] if latest_run else 'N/A'
    })


@app.route('/api/runs')
def api_runs():
    """Връща всички runs"""
    limit = request.args.get('limit', type=int, default=50)
    runs = parser.get_all_runs()[:limit]

    # Simplified version за списък
    simplified = [{
        'run_id': run['run_id'],
        'timestamp': run['timestamp'],
        'suite_name': run['suite_name'],
        'duration': run['duration'],
        'summary': run['summary']
    } for run in runs]

    return jsonify({
        'total': len(runs),
        'runs': simplified
    })


@app.route('/api/runs/<run_id>')
def api_run_details(run_id):
    """Детайли за конкретен run"""
    run = parser.get_run_by_id(run_id)

    if not run:
        return jsonify({'error': 'Run not found'}), 404

    return jsonify(run)


@app.route('/api/trends')
def api_trends():
    """Trend данни за графики"""
    runs_count = request.args.get('runs', type=int, default=20)
    runs = parser.get_all_runs()[:runs_count]

    if not runs:
        return jsonify({
            'runs': [],
            'timestamps': [],
            'totals': [],
            'passed': [],
            'failed': [],
            'pass_rates': [],
            'durations': []
        })

    return jsonify({
        'runs': [r['run_id'] for r in runs],
        'timestamps': [r['timestamp'] for r in runs],
        'totals': [r['summary']['total'] for r in runs],
        'passed': [r['summary']['passed'] for r in runs],
        'failed': [r['summary']['failed'] for r in runs],
        'pass_rates': [r['summary']['pass_rate'] for r in runs],
        'durations': [r['duration'] for r in runs]
    })


@app.route('/api/flaky-tests')
def api_flaky_tests():
    """Flaky тестове"""
    runs_count = request.args.get('runs', type=int, default=10)
    flaky = parser.get_flaky_tests(runs_count=runs_count)

    return jsonify({
        'total': len(flaky),
        'tests': flaky
    })


@app.route('/api/slowest-tests')
def api_slowest_tests():
    """Най-бавни тестове"""
    run_id = request.args.get('run_id')
    slowest = parser.get_slowest_tests(run_id=run_id)

    return jsonify({
        'total': len(slowest),
        'tests': slowest
    })


@app.route('/api/tag-stats')
def api_tag_stats():
    """Статистики по тагове от последния run"""
    runs = parser.get_all_runs()
    if not runs:
        return jsonify({'tags': []})

    latest_run = runs[0]
    return jsonify({
        'run_id': latest_run['run_id'],
        'tags': latest_run.get('tag_stats', [])
    })


@app.route('/api/suite-stats')
def api_suite_stats():
    """Статистики по suites от последния run"""
    runs = parser.get_all_runs()
    if not runs:
        return jsonify({'suites': []})

    latest_run = runs[0]
    return jsonify({
        'run_id': latest_run['run_id'],
        'suites': latest_run.get('suite_stats', [])
    })


@app.route('/api/parse', methods=['POST'])
def api_parse():
    """Force парсване на output.xml"""
    xml_path = Path(ROBOT_RESULTS_DIR) / 'output.xml'

    if not xml_path.exists():
        return jsonify({'error': 'output.xml not found'}), 404

    try:
        metrics = parser.parse_output_xml(xml_path)
        if metrics:
            parser.save_metrics(metrics)
            return jsonify({
                'status': 'success',
                'run_id': metrics['run_id'],
                'message': 'Metrics parsed and saved'
            })
        else:
            return jsonify({'error': 'Failed to parse XML'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare')
def api_compare():
    """Сравнява два runs"""
    run1_id = request.args.get('run1')
    run2_id = request.args.get('run2')

    if not run1_id or not run2_id:
        return jsonify({'error': 'Both run1 and run2 parameters required'}), 400

    run1 = parser.get_run_by_id(run1_id)
    run2 = parser.get_run_by_id(run2_id)

    if not run1 or not run2:
        return jsonify({'error': 'One or both runs not found'}), 404

    comparison = {
        'run1': {
            'run_id': run1['run_id'],
            'timestamp': run1['timestamp'],
            'summary': run1['summary'],
            'duration': run1['duration']
        },
        'run2': {
            'run_id': run2['run_id'],
            'timestamp': run2['timestamp'],
            'summary': run2['summary'],
            'duration': run2['duration']
        },
        'difference': {
            'pass_rate': round(run2['summary']['pass_rate'] - run1['summary']['pass_rate'], 2),
            'total': run2['summary']['total'] - run1['summary']['total'],
            'passed': run2['summary']['passed'] - run1['summary']['passed'],
            'failed': run2['summary']['failed'] - run1['summary']['failed'],
            'duration': round(run2['duration'] - run1['duration'], 2)
        }
    }

    return jsonify(comparison)


@app.route('/api/delete/<run_id>', methods=['DELETE'])
def api_delete_run(run_id):
    """Изтрива run от историята"""
    file_path = Path(HISTORY_DIR) / f"{run_id}.json"

    if not file_path.exists():
        return jsonify({'error': 'Run not found'}), 404

    try:
        file_path.unlink()
        return jsonify({
            'status': 'success',
            'message': f'Run {run_id} deleted'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def clear_data():
    """Clear all historical metrics data"""
    try:
        history_path = Path(HISTORY_DIR)
        deleted_count = 0

        # Изтрий само JSON файловете (директорията е mounted volume)
        if history_path.exists():
            for json_file in history_path.glob('*.json'):
                try:
                    json_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"Warning: Could not delete {json_file}: {e}")

        # Reload parser за да почне с празна история
        global parser
        parser = MetricsParser(ROBOT_RESULTS_DIR, HISTORY_DIR)

        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} history file(s)',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recent-runs')
def api_recent_runs():
    """Recent test runs"""
    limit = request.args.get('limit', type=int, default=10)
    runs = parser.get_all_runs()[:limit]

    return jsonify({
        'runs': [{
            'timestamp': run['timestamp'],
            'run_id': run['run_id'],
            'total': run['summary']['total'],
            'passed': run['summary']['passed'],
            'failed': run['summary']['failed'],
            'pass_rate': run['summary']['pass_rate'],
            'duration': run.get('duration', 0)
        } for run in runs]
    })


@app.route('/api/tag/<tag>')
def api_tag_details(tag):
    """Tag details - показва всички тестове за даден tag"""
    runs = parser.get_all_runs()
    if not runs:
        return jsonify({'tests': [], 'test_count': 0, 'pass_rate': 0})

    latest_run = runs[0]

    # Намери тестове с този tag
    tests = []
    if 'tests' in latest_run:
        for test in latest_run['tests']:
            if tag in test.get('tags', []):
                tests.append({
                    'name': test['name'],
                    'status': test['status'],
                    'duration': test.get('duration', 0) * 1000,  # конвертирай в ms
                    'message': test.get('message', '')
                })

    passed = sum(1 for t in tests if t['status'] == 'PASS')
    pass_rate = (passed / len(tests) * 100) if tests else 0

    return jsonify({
        'tag': tag,
        'test_count': len(tests),
        'pass_rate': pass_rate,
        'tests': tests
    })


@app.route('/screenshots/<filename>')
def screenshot(filename):
    """Serve screenshot files"""
    return send_from_directory(ROBOT_RESULTS_DIR, filename)


@app.route('/tag/<tag_name>')
def tag_analysis(tag_name):
    """Detailed tag analysis page"""
    try:
        data = get_tag_analysis(tag_name)
        return render_template('tag_analysis.html',
                               tag=tag_name,
                               data=data)
    except Exception as e:
        logger.error(f"Error loading tag analysis: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/api/tag/<tag_name>/history')
def tag_history_api(tag_name):
    """Get tag performance history across runs"""
    try:
        limit = request.args.get('limit', 20, type=int)
        data = get_tag_history(tag_name, limit)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting tag history: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tag/<tag_name>/tests')
def tag_tests_api(tag_name):
    """Get individual test performance for this tag"""
    try:
        data = get_tag_test_performance(tag_name)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting tag tests: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tag/<tag_name>/export')
def export_tag_data(tag_name):
    """Export tag data as CSV"""
    try:
        import csv
        from io import StringIO

        data = get_tag_analysis(tag_name)

        output = StringIO()
        writer = csv.writer(output)

        # Headers
        writer.writerow(['Test Name', 'Total Runs', 'Passed', 'Failed', 'Pass Rate %', 'Avg Duration (s)'])

        # Data
        for test in data['tests']:
            writer.writerow([
                test['name'],
                test['total_runs'],
                test['passed'],
                test['failed'],
                f"{test['pass_rate']:.2f}",
                f"{test['avg_duration']:.2f}"
            ])

        output.seek(0)

        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=tag_{tag_name}_analysis.csv'}
        )
    except Exception as e:
        logger.error(f"Error exporting tag data: {e}")
        return jsonify({'error': str(e)}), 500


def get_tag_analysis(tag_name):
    """Get comprehensive tag analysis"""
    runs = get_all_runs()

    # Find all runs containing this tag
    tag_runs = []
    all_tests = {}

    for run in runs:
        run_data = load_run_data(run['run_id'])
        if not run_data:
            continue

        # Check if this run has tests with the tag
        tests_with_tag = [t for t in run_data.get('tests', [])
                          if tag_name in t.get('tags', [])]

        if tests_with_tag:
            passed = sum(1 for t in tests_with_tag if t['status'] == 'PASS')
            failed = sum(1 for t in tests_with_tag if t['status'] == 'FAIL')
            total = len(tests_with_tag)
            pass_rate = (passed / total * 100) if total > 0 else 0

            tag_runs.append({
                'run_id': run['run_id'],
                'timestamp': run['timestamp'],
                'suite_name': run_data.get('suite_name', 'Unknown'),
                'total': total,
                'passed': passed,
                'failed': failed,
                'pass_rate': round(pass_rate, 2),
                'duration': sum(t.get('duration', 0) for t in tests_with_tag) / 1000
            })

            # Track individual test performance
            for test in tests_with_tag:
                test_name = test['name']
                if test_name not in all_tests:
                    all_tests[test_name] = {
                        'name': test_name,
                        'total_runs': 0,
                        'passed': 0,
                        'failed': 0,
                        'durations': [],
                        'last_failed_run': None,
                        'last_status': None
                    }

                all_tests[test_name]['total_runs'] += 1
                all_tests[test_name]['durations'].append(test.get('duration', 0) / 1000)
                all_tests[test_name]['last_status'] = test['status']

                if test['status'] == 'PASS':
                    all_tests[test_name]['passed'] += 1
                else:
                    all_tests[test_name]['failed'] += 1
                    all_tests[test_name]['last_failed_run'] = run['run_id']

    # Calculate test statistics
    test_stats = []
    for test_name, stats in all_tests.items():
        pass_rate = (stats['passed'] / stats['total_runs'] * 100) if stats['total_runs'] > 0 else 0
        avg_duration = sum(stats['durations']) / len(stats['durations']) if stats['durations'] else 0

        test_stats.append({
            'name': test_name,
            'total_runs': stats['total_runs'],
            'passed': stats['passed'],
            'failed': stats['failed'],
            'pass_rate': round(pass_rate, 2),
            'avg_duration': round(avg_duration, 2),
            'last_failed_run': stats['last_failed_run'],
            'last_status': stats['last_status'],
            'is_flaky': 0 < stats['failed'] < stats['total_runs']  # Failed sometimes but not always
        })

    # Sort by pass rate (unstable first)
    test_stats.sort(key=lambda x: (x['pass_rate'], -x['total_runs']))

    # Overall statistics
    total_test_count = len(all_tests)
    total_executions = sum(r['total'] for r in tag_runs)
    total_passed = sum(r['passed'] for r in tag_runs)
    total_failed = sum(r['failed'] for r in tag_runs)
    overall_pass_rate = (total_passed / total_executions * 100) if total_executions > 0 else 0

    return {
        'tag_name': tag_name,
        'total_runs': len(tag_runs),
        'total_test_count': total_test_count,
        'total_executions': total_executions,
        'overall_pass_rate': round(overall_pass_rate, 2),
        'runs': sorted(tag_runs, key=lambda x: x['timestamp'], reverse=True),
        'tests': test_stats,
        'flaky_count': sum(1 for t in test_stats if t['is_flaky'])
    }


def get_tag_history(tag_name, limit=20):
    """Get tag pass rate history"""
    runs = get_all_runs()[:limit]

    history = {
        'timestamps': [],
        'pass_rates': [],
        'test_counts': [],
        'run_ids': []
    }

    for run in runs:
        run_data = load_run_data(run['run_id'])
        if not run_data:
            continue

        tests_with_tag = [t for t in run_data.get('tests', [])
                          if tag_name in t.get('tags', [])]

        if tests_with_tag:
            passed = sum(1 for t in tests_with_tag if t['status'] == 'PASS')
            total = len(tests_with_tag)
            pass_rate = (passed / total * 100) if total > 0 else 0

            history['timestamps'].append(run['timestamp'])
            history['pass_rates'].append(round(pass_rate, 2))
            history['test_counts'].append(total)
            history['run_ids'].append(run['run_id'])

    return history


def get_tag_test_performance(tag_name):
    """Get detailed test performance for tag"""
    data = get_tag_analysis(tag_name)
    return {
        'tests': data['tests'],
        'total_count': len(data['tests']),
        'flaky_count': data['flaky_count']
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return f'<h1>404 Not Found</h1><p>{request.path}</p><a href="/">Back to Dashboard</a>', 404


@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return f'<h1>500 Internal Server Error</h1><p>{error}</p>', 500


# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 Robot Framework Metrics Dashboard")
    print("=" * 60)
    print(f"Results Dir: {ROBOT_RESULTS_DIR}")
    print(f"History Dir: {HISTORY_DIR}")
    print(f"Dashboard: http://localhost:5000")
    print("=" * 60)

    # NOTE: Auto-parsing is handled by entrypoint.sh periodic checker
    # No need to parse here to avoid duplicates

    app.run(host='0.0.0.0', port=5000, debug=True)
