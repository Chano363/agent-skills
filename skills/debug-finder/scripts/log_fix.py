#!/usr/bin/env python3
"""
Log the fix to the logs folder
"""

import os
import sys
from datetime import datetime
from pathlib import Path


def log_fix(error_desc, file_path, line_num, fix_desc, test_script_path, project_root):
    """
    Log the fix to the logs folder
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path(project_root) / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Create log entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"""[{timestamp}] Error Type: {error_desc}
File: {file_path}:{line_num}
Original Error: {error_desc}
Applied Fix: {fix_desc}
Test Script: {test_script_path}
Verification: Pending
"""

    # Write to log file
    log_file = logs_dir / f"fix_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w') as f:
        f.write(log_entry)
    
    print(f"[LOG] Fix logged to: {log_file}")
    return str(log_file)


def main():
    if len(sys.argv) < 6:
        print("Usage: python log_fix.py <error_description> <file_path> <line_num> <fix_description> <test_script_path> <project_root>")
        sys.exit(1)
    
    error_description = sys.argv[1]
    file_path = sys.argv[2]
    line_num = sys.argv[3]
    fix_description = sys.argv[4]
    test_script_path = sys.argv[5]
    project_root = sys.argv[6]
    
    log_file = log_fix(error_description, file_path, line_num, fix_description, test_script_path, project_root)
    print(f"Fix logged successfully: {log_file}")


if __name__ == "__main__":
    main()