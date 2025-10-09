#!/usr/bin/env python3
"""
Robot Framework Test Runner with Pabot support
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


class TestRunner:
    def __init__(self):
        self.output_dir = os.getenv('OUTPUT_DIR', '/robot_results')
        self.test_dir = '/robot_src/tests'
        self.processes = int(os.getenv('PROCESSES', '6'))
        self.browser = os.getenv('BROWSER', 'headlesschrome')
        
    def build_command(self, tag=None, suite=None, test=None, processes=None):
        """Build robot/pabot command"""
        procs = processes or self.processes
        
        # Base command
        if procs > 1:
            cmd = ['pabot', '--processes', str(procs)]
        else:
            cmd = ['robot']
        
        # Output options
        cmd.extend([
            '--outputdir', self.output_dir,
            '--output', 'output.xml',
            '--log', 'log.html',
            '--report', 'report.html',
            '--loglevel', os.getenv('LOGLEVEL', 'INFO')
        ])
        
        # Variables
        cmd.extend([
            '--variable', f'BROWSER:{self.browser}',
            '--variable', f'ODOO_HOST:{os.getenv("ODOO_HOST", "odoo")}',
            '--variable', f'ODOO_PORT:{os.getenv("ODOO_PORT", "8069")}'
        ])
        
        # Filters
        if tag:
            cmd.extend(['--include', tag])
        
        if suite:
            cmd.extend(['--suite', suite])
            
        if test:
            cmd.extend(['--test', test])
        
        # Test directory
        cmd.append(self.test_dir)
        
        return cmd
    
    def run(self, tag=None, suite=None, test=None, processes=None):
        """Execute tests"""
        cmd = self.build_command(tag, suite, test, processes)
        
        print("=" * 60)
        print("Command:", ' '.join(cmd))
        print("=" * 60)
        print()
        
        try:
            result = subprocess.run(cmd, check=False)
            return result.returncode
        except Exception as e:
            print(f"Error running tests: {e}")
            return 1


def main():
    parser = argparse.ArgumentParser(description='Robot Framework Test Runner')
    parser.add_argument('--tag', '-t', help='Run tests with specific tag')
    parser.add_argument('--suite', '-s', help='Run specific suite')
    parser.add_argument('--test', help='Run specific test')
    parser.add_argument('--processes', '-p', type=int, help='Number of parallel processes')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.interactive:
        print("\n🤖 Robot Framework Interactive Mode")
        print("=" * 60)
        tag = input("Enter tag (or press Enter for all): ").strip() or None
        processes = input(f"Number of processes [{runner.processes}]: ").strip()
        processes = int(processes) if processes else runner.processes
        
        return runner.run(tag=tag, processes=processes)
    else:
        return runner.run(
            tag=args.tag,
            suite=args.suite,
            test=args.test,
            processes=args.processes
        )


if __name__ == '__main__':
    sys.exit(main())
