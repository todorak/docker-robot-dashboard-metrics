"""
Robot Framework Metrics Parser
Парсва output.xml и генерира метрики + архивира Robot Framework reports
"""
import os
import json
import hashlib
import time
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from xml.etree import ElementTree as ET


class MetricsParser:
    def __init__(self, results_dir: str, history_dir: str):
        self.results_dir = Path(results_dir)
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def _get_local_timezone(self) -> timezone:
        """Auto-detect system timezone"""
        if time.daylight:
            utc_offset = -time.altzone
        else:
            utc_offset = -time.timezone
        offset_hours = utc_offset / 3600
        return timezone(timedelta(hours=offset_hours))

    def parse_output_xml(self, xml_path: Path) -> Optional[Dict]:
        """Парсва Robot Framework output.xml файл"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Основна информация
            suite = root.find('.//suite')
            stats = root.find('.//statistics')

            if not suite or not stats:
                return None

            # Timestamp от root suite status
            suite_status = suite.find('status')
            start_time = suite_status.get('start') if suite_status is not None else None
            elapsed = float(suite_status.get('elapsed', 0)) if suite_status is not None else 0.0

            # FIXED: Add timezone - AUTO-DETECT from system
            if start_time and 'Z' not in start_time and '+' not in start_time:
                dt = datetime.fromisoformat(start_time)
                local_tz = self._get_local_timezone()
                dt = dt.replace(tzinfo=local_tz)
                start_time = dt.isoformat()

            # Парсване на статистиките
            total_stats = stats.find('.//total/stat')
            passed = int(total_stats.get('pass', 0)) if total_stats is not None else 0
            failed = int(total_stats.get('fail', 0)) if total_stats is not None else 0
            skipped = int(total_stats.get('skip', 0)) if total_stats is not None else 0
            total = passed + failed + skipped

            # Парсване на тестовете
            tests = self._parse_tests(suite)

            # Парсване на tags
            tag_stats = self._parse_tag_stats(stats)

            # Парсване на suites
            suite_stats = self._parse_suite_stats(stats)

            # Генериране на уникален ID
            file_mtime = xml_path.stat().st_mtime
            run_id = self._generate_run_id(start_time, total, passed, failed, file_mtime)

            metrics = {
                'run_id': run_id,
                'timestamp': start_time or datetime.now().isoformat(),
                'start_time': start_time,
                'end_time': self._calculate_end_time(start_time, elapsed),
                'duration': round(elapsed, 2),
                'summary': {
                    'total': total,
                    'passed': passed,
                    'failed': failed,
                    'skipped': skipped,
                    'pass_rate': round((passed / total * 100), 2) if total > 0 else 0
                },
                'tests': tests,
                'tag_stats': tag_stats,
                'suite_stats': suite_stats,
                'suite_name': suite.get('name', 'Unknown')
            }

            return metrics

        except Exception as e:
            print(f"Error parsing XML: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _parse_tests(self, suite_element) -> List[Dict]:
        """Извлича информация за всички тестове"""
        tests = []
        local_tz = self._get_local_timezone()

        for test in suite_element.findall('.//test'):
            status = test.find('status')
            if status is None:
                continue

            start_time = status.get('start')
            elapsed = float(status.get('elapsed', 0))

            # Add timezone to test start_time
            if start_time and 'Z' not in start_time and '+' not in start_time:
                dt = datetime.fromisoformat(start_time)
                dt = dt.replace(tzinfo=local_tz)
                start_time = dt.isoformat()

            test_info = {
                'name': test.get('name', 'Unknown'),
                'status': status.get('status', 'UNKNOWN'),
                'start_time': start_time,
                'end_time': self._calculate_end_time(start_time, elapsed),
                'duration': round(elapsed, 2),
                'message': status.text.strip() if status.text else '',
                'tags': [tag.text for tag in test.findall('.//tag')]
            }
            tests.append(test_info)

        return tests

    def _parse_tag_stats(self, stats_element) -> List[Dict]:
        """Парсва статистики по тагове"""
        tag_stats = []

        tags = stats_element.findall('.//tag/stat')
        for tag in tags:
            tag_info = {
                'name': tag.text,
                'total': int(tag.get('pass', 0)) + int(tag.get('fail', 0)),
                'passed': int(tag.get('pass', 0)),
                'failed': int(tag.get('fail', 0)),
                'pass_rate': round(
                    (int(tag.get('pass', 0)) /
                     (int(tag.get('pass', 0)) + int(tag.get('fail', 0))) * 100),
                    2
                ) if (int(tag.get('pass', 0)) + int(tag.get('fail', 0))) > 0 else 0
            }
            tag_stats.append(tag_info)

        return tag_stats

    def _parse_suite_stats(self, stats_element) -> List[Dict]:
        """Парсва статистики по suites"""
        suite_stats = []

        suites = stats_element.findall('.//suite/stat')
        for suite in suites:
            suite_info = {
                'name': suite.text,
                'total': int(suite.get('pass', 0)) + int(suite.get('fail', 0)),
                'passed': int(suite.get('pass', 0)),
                'failed': int(suite.get('fail', 0)),
                'pass_rate': round(
                    (int(suite.get('pass', 0)) /
                     (int(suite.get('pass', 0)) + int(suite.get('fail', 0))) * 100),
                    2
                ) if (int(suite.get('pass', 0)) + int(suite.get('fail', 0))) > 0 else 0
            }
            suite_stats.append(suite_info)

        return suite_stats

    def _calculate_end_time(self, start_time: str, elapsed: float) -> str:
        """Изчислява end time от start time + elapsed"""
        if not start_time:
            return None

        try:
            # Parse ISO 8601 format (with or without timezone)
            start = datetime.fromisoformat(start_time)
            end = start + timedelta(seconds=elapsed)
            return end.isoformat()
        except:
            return None

    def _generate_run_id(self, timestamp: str, total: int, passed: int, failed: int, file_mtime: float = None) -> str:
        """Генерира уникален ID за run"""
        current_time = datetime.now().isoformat()
        data = f"{timestamp}-{total}-{passed}-{failed}-{current_time}-{file_mtime}"
        return hashlib.md5(data.encode()).hexdigest()[:12]

    def archive_robot_reports(self, run_id: str) -> bool:
        """
        Архивира Robot Framework HTML reports, log и screenshots за даден run
        """
        try:
            # Създай archive директория за този run
            archive_dir = self.history_dir / run_id
            archive_dir.mkdir(exist_ok=True)

            archived_files = []

            # 1. Архивирай основните Robot Framework файлове
            robot_files = ['report.html', 'log.html', 'output.xml']
            for filename in robot_files:
                src = self.results_dir / filename
                if src.exists():
                    dst = archive_dir / filename
                    shutil.copy2(src, dst)
                    archived_files.append(filename)

            # 2. Архивирай всички screenshots и лог файлове
            for pattern in ['*.png', '*.jpg', '*.jpeg']:
                for file in self.results_dir.glob(pattern):
                    dst = archive_dir / file.name
                    shutil.copy2(file, dst)
                    archived_files.append(file.name)

            if archived_files:
                print(f"📦 Archived {len(archived_files)} files for run {run_id}")
                return True
            else:
                print(f"⚠️  No files to archive for run {run_id}")
                return False

        except Exception as e:
            print(f"❌ Error archiving reports for {run_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def save_metrics(self, metrics: Dict) -> bool:
        """Записва метриките в history и архивира Robot reports"""
        try:
            run_id = metrics['run_id']
            file_path = self.history_dir / f"{run_id}.json"

            if file_path.exists():
                print(f"⏭️  Run {run_id} already exists, skipping...")
                return False  # Don't create duplicate

            # Запази JSON метриките
            with open(file_path, 'w') as f:
                json.dump(metrics, f, indent=2)

            print(f"✓ Metrics saved: {metrics['run_id']}")

            # Архивирай Robot Framework reports
            self.archive_robot_reports(run_id)

            return True

        except Exception as e:
            print(f"✗ Error saving metrics: {e}")
            return False

    def get_all_runs(self) -> List[Dict]:
        """Връща всички runs от историята - SORTED BY TIMESTAMP"""
        runs = []

        for json_file in self.history_dir.glob('*.json'):
            try:
                with open(json_file, 'r') as f:
                    metrics = json.load(f)
                    runs.append(metrics)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")

        # Sort by timestamp descending (newest first)
        runs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return runs

    def get_run_by_id(self, run_id: str) -> Optional[Dict]:
        """Връща конкретен run по ID"""
        file_path = self.history_dir / f"{run_id}.json"

        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading run {run_id}: {e}")
            return None

    def get_trend_data(self, limit: int = 20) -> Dict:
        """Генерира trend данни за графиките"""
        runs = self.get_all_runs()[:limit]

        trend = {
            'timestamps': [],
            'pass_rates': [],
            'totals': [],
            'passed': [],
            'failed': [],
            'durations': []
        }

        for run in reversed(runs):
            trend['timestamps'].append(run['timestamp'])
            trend['pass_rates'].append(run['summary']['pass_rate'])
            trend['totals'].append(run['summary']['total'])
            trend['passed'].append(run['summary']['passed'])
            trend['failed'].append(run['summary']['failed'])
            trend['durations'].append(run['duration'])

        return trend

    def get_flaky_tests(self, runs_count: int = 10) -> List[Dict]:
        """Открива flaky тестове"""
        runs = self.get_all_runs()[:runs_count]
        test_results = {}

        for run in runs:
            for test in run.get('tests', []):
                name = test['name']
                if name not in test_results:
                    test_results[name] = {'passed': 0, 'failed': 0, 'total': 0}

                test_results[name]['total'] += 1
                if test['status'] == 'PASS':
                    test_results[name]['passed'] += 1
                else:
                    test_results[name]['failed'] += 1

        flaky = []
        for name, results in test_results.items():
            if results['total'] >= 3:
                fail_rate = (results['failed'] / results['total']) * 100
                if 20 <= fail_rate <= 80:
                    flaky.append({
                        'name': name,
                        'fail_rate': round(fail_rate, 2),
                        'passed': results['passed'],
                        'failed': results['failed'],
                        'total': results['total']
                    })

        return sorted(flaky, key=lambda x: x['fail_rate'], reverse=True)

    def get_slowest_tests(self, run_id: Optional[str] = None) -> List[Dict]:
        """Връща най-бавните тестове"""
        if run_id:
            run = self.get_run_by_id(run_id)
            runs = [run] if run else []
        else:
            runs = self.get_all_runs()[:1]

        all_tests = []
        for run in runs:
            all_tests.extend(run.get('tests', []))

        slowest = sorted(all_tests, key=lambda x: x['duration'], reverse=True)[:10]

        return slowest


if __name__ == '__main__':
    parser = MetricsParser('/robot_results', '/app/data/history')

    xml_path = Path('/robot_results/output.xml')
    if xml_path.exists():
        metrics = parser.parse_output_xml(xml_path)
        if metrics:
            parser.save_metrics(metrics)
            print(json.dumps(metrics, indent=2))