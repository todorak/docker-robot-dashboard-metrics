#!/bin/bash
set -e

echo "=========================================="
echo "Robot Framework Metrics Dashboard"
echo "=========================================="
echo "Data Dir: ${METRICS_DATA_DIR}"
echo "Results Dir: ${ROBOT_RESULTS_DIR}"
echo "Port: 5000"
echo "=========================================="

# Wait for robot results directory
echo "Waiting for results directory..."
timeout=30
while [ ! -d "${ROBOT_RESULTS_DIR}" ] && [ $timeout -gt 0 ]; do
    sleep 1
    timeout=$((timeout-1))
done

if [ -d "${ROBOT_RESULTS_DIR}" ]; then
    echo "✓ Results directory ready"
else
    echo "⚠ Results directory not found, continuing anyway..."
fi

# FIXED: Only auto-parse if output.xml is recent (modified in last 5 minutes)
if [ -f "${ROBOT_RESULTS_DIR}/output.xml" ]; then
    output_mtime=$(stat -c %Y "${ROBOT_RESULTS_DIR}/output.xml" 2>/dev/null || echo 0)

    # Check newest history file
    newest_history=$(ls -t ${METRICS_DATA_DIR}/history/*.json 2>/dev/null | head -1)

    if [ -n "$newest_history" ]; then
        history_mtime=$(stat -c %Y "$newest_history" 2>/dev/null || echo 0)

        if [ $output_mtime -gt $history_mtime ]; then
            echo ""
            echo "📊 Found NEW output.xml, parsing..."
            python3 /app/metrics_parser.py
        else
            echo ""
            echo "⏭️  output.xml already processed, skipping"
        fi
    else
        echo ""
        echo "📊 No history found, parsing output.xml..."
        python3 /app/metrics_parser.py
    fi
fi

# Start file watcher in background
#echo ""
#echo "👁️  Starting file watcher for automatic parsing..."
#python3 - << 'PYTHON' &
#import time
#import os
#from pathlib import Path
#from watchdog.observers import Observer
#from watchdog.events import FileSystemEventHandler
#
#class XMLHandler(FileSystemEventHandler):
#    def __init__(self, results_dir):
#        self.results_dir = Path(results_dir)
#        self.parsed_files = {}  # Store file path + mtime
#
#    def on_created(self, event):
#        if event.src_path.endswith('output.xml'):
#            if 'pabot_results' in event.src_path:
#                return
#
#            file_path = event.src_path
#            time.sleep(3)
#
#            try:
#                file_mtime = os.path.getmtime(file_path)
#
#                if file_path in self.parsed_files and self.parsed_files[file_path] == file_mtime:
#                    print(f"\n⏭️  Already parsed this file version")
#                    return
#
#                # Create lock file to prevent concurrent parsing
#                lock_file = '/tmp/parsing.lock'
#                if os.path.exists(lock_file):
#                    print(f"\n⏭️  Parsing already in progress, skipping...")
#                    return
#
#                open(lock_file, 'w').close()
#                print(f"\n🔄 New output.xml created, parsing...")
#                os.system('python3 /app/metrics_parser.py')
#                self.parsed_files[file_path] = file_mtime
#                os.remove(lock_file)
#
#            except Exception as e:
#                print(f"\n❌ Error: {e}")
#                if os.path.exists(lock_file):
#                    os.remove(lock_file)
#
#results_dir = os.getenv('ROBOT_RESULTS_DIR', '/robot_results')
#print(f"Watching directory: {results_dir}")
#
#if os.path.exists(results_dir):
#    event_handler = XMLHandler(results_dir)
#    observer = Observer()
#    observer.schedule(event_handler, results_dir, recursive=False)
#    observer.start()
#    print("✓ File watcher started")
#
#    try:
#        while True:
#            time.sleep(1)
#    except KeyboardInterrupt:
#        observer.stop()
#    observer.join()
#else:
#    print("⚠ Results directory not found, file watcher disabled")
#PYTHON

# Start periodic checker in background (every 10 seconds)
echo ""
echo "👁️  Starting periodic parser (checks every 10s)..."
python3 - << 'PYTHON' &
import time
import os
from pathlib import Path

results_dir = os.getenv('ROBOT_RESULTS_DIR', '/robot_results')
history_dir = Path(os.getenv('METRICS_DATA_DIR', '/app/data')) / 'history'
output_file = Path(results_dir) / 'output.xml'
last_mtime = 0

print(f"Watching: {output_file}")
print("✓ Periodic checker started")

while True:
    try:
        if output_file.exists():
            current_mtime = output_file.stat().st_mtime

            if current_mtime > last_mtime:
                # Check if already parsed by comparing with newest history file
                history_files = list(history_dir.glob('*.json'))
                if history_files:
                    newest_history = max(history_files, key=lambda p: p.stat().st_mtime)
                    history_mtime = newest_history.stat().st_mtime

                    if current_mtime > history_mtime:
                        print(f"\n🔄 New output.xml detected, parsing...")
                        os.system('python3 /app/metrics_parser.py')
                        last_mtime = current_mtime
                else:
                    print(f"\n🔄 No history, parsing output.xml...")
                    os.system('python3 /app/metrics_parser.py')
                    last_mtime = current_mtime
    except Exception as e:
        print(f"Error: {e}")

    time.sleep(2)
PYTHON

echo ""
echo "🚀 Starting Metrics Dashboard..."
echo "Dashboard will be available at: http://localhost:5000"
echo ""

# Execute command
exec "$@"
