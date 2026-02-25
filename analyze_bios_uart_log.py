#!/usr/bin/env python3
"""
BIOS UART Log Analyzer
=====================

This script analyzes BIOS UART logs to extract key information, detect errors,
and provide insights into the boot process.

Features:
- Parse timestamped log entries
- Detect common BIOS error patterns
- Extract hardware initialization information
- Identify boot sequence timing
- Generate summary statistics

Usage:
    python analyze_bios_uart_log.py <log_file_path>
    python analyze_bios_uart_log.py --help
"""

import argparse
import re
import sys
from datetime import datetime
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional


class BIOSLogAnalyzer:
    def __init__(self):
        # Common BIOS error patterns
        self.error_patterns = [
            r'(?i)error',
            r'(?i)fail',
            r'(?i)timeout',
            r'(?i)invalid',
            r'(?i)corrupt',
            r'(?i)not found',
            r'(?i)unsupported',
            r'(?i)exception',
            r'(?i)assert',
            r'(?i)panic',
        ]
        
        # Hardware initialization patterns
        self.hardware_patterns = {
            'CPU': r'(?i)(cpu|processor|core).*?(init|detected|enabled)',
            'Memory': r'(?i)(memory|ram|dram).*?(init|detected|size)',
            'PCIe': r'(?i)(pcie|pci express).*?(init|enumerat|link)',
            'SATA': r'(?i)(sata|storage|disk).*?(init|detected|port)',
            'USB': r'(?i)usb.*?(init|controller|port)',
            'Network': r'(?i)(network|ethernet|nic).*?(init|detected)',
        }
        
        # Boot phase markers
        self.boot_phases = [
            'Reset Vector',
            'Early Initialization',
            'PEI (Pre-EFI Initialization)',
            'DXE (Driver Execution Environment)',
            'BDS (Boot Device Selection)',
            'OS Loader',
        ]

    def parse_log_file(self, file_path: str) -> List[str]:
        """Read and return log lines from file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return [line.rstrip('\n') for line in f.readlines()]
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)

    def extract_timestamps(self, lines: List[str]) -> List[Tuple[Optional[datetime], str]]:
        """Extract timestamps from log lines if present."""
        timestamped_lines = []
        
        # Common timestamp formats in BIOS logs
        timestamp_patterns = [
            r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]',  # [YYYY-MM-DD HH:MM:SS]
            r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',      # YYYY-MM-DDTHH:MM:SS
            r'^\[?(\d+\.\d+)\]?',                            # [seconds.microseconds]
        ]
        
        for line in lines:
            timestamp = None
            clean_line = line
            
            for pattern in timestamp_patterns:
                match = re.search(pattern, line)
                if match:
                    timestamp_str = match.group(1)
                    clean_line = line[match.end():].strip()
                    
                    # Try to parse different timestamp formats
                    if '.' in timestamp_str and len(timestamp_str) <= 10:  # seconds format
                        # Store as float for relative timing
                        timestamp = float(timestamp_str)
                    else:
                        try:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                timestamp = datetime.fromisoformat(timestamp_str.replace('T', ' '))
                            except ValueError:
                                pass
                    break
            
            timestamped_lines.append((timestamp, clean_line))
        
        return timestamped_lines

    def find_errors(self, lines: List[str]) -> List[Tuple[int, str]]:
        """Find lines containing error patterns."""
        errors = []
        for i, line in enumerate(lines):
            for pattern in self.error_patterns:
                if re.search(pattern, line):
                    errors.append((i + 1, line))
                    break
        return errors

    def extract_hardware_info(self, lines: List[str]) -> Dict[str, List[str]]:
        """Extract hardware initialization information."""
        hardware_info = defaultdict(list)
        
        for line in lines:
            for hw_type, pattern in self.hardware_patterns.items():
                if re.search(pattern, line):
                    hardware_info[hw_type].append(line)
        
        return dict(hardware_info)

    def analyze_boot_timing(self, timestamped_lines: List[Tuple[Optional[datetime], str]]) -> Dict:
        """Analyze boot timing if timestamps are available."""
        timing_info = {
            'total_duration': None,
            'has_timestamps': False,
            'first_timestamp': None,
            'last_timestamp': None,
        }
        
        # Filter out lines with valid timestamps
        valid_timestamps = [ts for ts, _ in timestamped_lines if ts is not None]
        
        if valid_timestamps:
            timing_info['has_timestamps'] = True
            timing_info['first_timestamp'] = min(valid_timestamps)
            timing_info['last_timestamp'] = max(valid_timestamps)
            
            if isinstance(timing_info['first_timestamp'], float):
                # Relative timing (seconds)
                timing_info['total_duration'] = timing_info['last_timestamp'] - timing_info['first_timestamp']
            else:
                # Absolute timing
                timing_info['total_duration'] = (
                    timing_info['last_timestamp'] - timing_info['first_timestamp']
                ).total_seconds()
        
        return timing_info

    def generate_summary(self, lines: List[str], timestamped_lines: List[Tuple[Optional[datetime], str]]) -> Dict:
        """Generate overall summary statistics."""
        summary = {
            'total_lines': len(lines),
            'unique_lines': len(set(lines)),
            'empty_lines': sum(1 for line in lines if not line.strip()),
        }
        
        # Count common keywords
        keywords = ['init', 'detect', 'start', 'complete', 'success', 'fail', 'error']
        keyword_counts = {}
        for keyword in keywords:
            keyword_counts[keyword] = sum(1 for line in lines if keyword.lower() in line.lower())
        
        summary['keyword_counts'] = keyword_counts
        return summary

    def analyze(self, file_path: str) -> Dict:
        """Main analysis function."""
        print(f"Analyzing BIOS UART log: {file_path}")
        print("=" * 50)
        
        # Read log file
        lines = self.parse_log_file(file_path)
        if not lines:
            print("Warning: Log file is empty.")
            return {}
        
        # Extract timestamps
        timestamped_lines = self.extract_timestamps(lines)
        
        # Find errors
        errors = self.find_errors(lines)
        
        # Extract hardware info
        hardware_info = self.extract_hardware_info(lines)
        
        # Analyze timing
        timing_info = self.analyze_boot_timing(timestamped_lines)
        
        # Generate summary
        summary = self.generate_summary(lines, timestamped_lines)
        
        # Compile results
        results = {
            'file_path': file_path,
            'summary': summary,
            'errors': errors,
            'hardware_info': hardware_info,
            'timing_info': timing_info,
            'total_lines': len(lines),
        }
        
        return results

    def print_results(self, results: Dict):
        """Print analysis results in a readable format."""
        if not results:
            return
        
        # Summary
        print("\n📊 SUMMARY")
        print("-" * 30)
        print(f"Total lines: {results['summary']['total_lines']}")
        print(f"Unique lines: {results['summary']['unique_lines']}")
        print(f"Empty lines: {results['summary']['empty_lines']}")
        
        if results['summary']['keyword_counts']:
            print("\nKeyword occurrences:")
            for keyword, count in results['summary']['keyword_counts'].items():
                if count > 0:
                    print(f"  {keyword}: {count}")
        
        # Timing info
        if results['timing_info']['has_timestamps']:
            print(f"\n⏱️  BOOT TIMING")
            print("-" * 30)
            if isinstance(results['timing_info']['total_duration'], float):
                print(f"Total boot time: {results['timing_info']['total_duration']:.3f} seconds")
            else:
                print(f"Total boot time: {results['timing_info']['total_duration']} seconds")
        
        # Errors
        if results['errors']:
            print(f"\n❌ ERRORS FOUND ({len(results['errors'])})")
            print("-" * 30)
            for line_num, error_line in results['errors'][:10]:  # Show first 10 errors
                print(f"Line {line_num}: {error_line}")
            if len(results['errors']) > 10:
                print(f"... and {len(results['errors']) - 10} more errors")
        else:
            print("\n✅ No errors detected")
        
        # Hardware info
        if results['hardware_info']:
            print(f"\n🔧 HARDWARE INITIALIZATION")
            print("-" * 30)
            for hw_type, lines in results['hardware_info'].items():
                print(f"{hw_type}: {len(lines)} entries")
                # Show first few entries for each type
                for line in lines[:3]:
                    print(f"  - {line[:80]}{'...' if len(line) > 80 else ''}")
                if len(lines) > 3:
                    print(f"  ... and {len(lines) - 3} more")


def main():
    parser = argparse.ArgumentParser(description='Analyze BIOS UART logs')
    parser.add_argument('log_file', help='Path to the BIOS UART log file')
    parser.add_argument('--output', '-o', help='Output file for detailed results (JSON)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show verbose output')
    
    args = parser.parse_args()
    
    analyzer = BIOSLogAnalyzer()
    results = analyzer.analyze(args.log_file)
    
    if results:
        analyzer.print_results(results)
        
        # Save detailed results if requested
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\nDetailed results saved to: {args.output}")


if __name__ == '__main__':
    main()