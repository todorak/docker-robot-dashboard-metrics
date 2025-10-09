"""
Sunday Natural Products GmbH - Robot Framework Metrics Dashboard
Flask API и Web Interface
"""
import os
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, send_from_directory, request

from metrics_parser import MetricsParser

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