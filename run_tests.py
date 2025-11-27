#!/usr/bin/env python3
"""
Hexza Test Runner
Run all tests in the tests/ directory
"""

import os
import sys
import subprocess
from pathlib import Path

def run_test(test_file):
    """Run a single test file"""
    print(f"\n{'='*60}")
    print(f"Running: {test_file.name}")
    print('='*60)
    
    try:
        result = subprocess.run(
            ['python', 'hexza.py', str(test_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print(f">> {test_file.name} PASSED")
            return True
        else:
            print(f">> {test_file.name} FAILED")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f">> {test_file.name} TIMEOUT")
        return False
    except Exception as e:
        print(f">> {test_file.name} ERROR: {e}")
        return False

def main():
    """Run all tests"""
    tests_dir = Path('tests')
    
    if not tests_dir.exists():
        print(">> tests/ directory not found")
        return 1
    
    # Find all test files
    test_files = sorted(tests_dir.glob('test_*.hxza'))
    
    if not test_files:
        print(">> No test files found in tests/")
        return 1
    
    print(f"\n>> Hexza Test Suite")
    print(f"Found {len(test_files)} tests\n")
    
    passed = 0
    failed = 0
    
    for test_file in test_files:
        if run_test(test_file):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print('='*60)
    print(f"Total:  {len(test_files)}")
    print(f">> Passed: {passed}")
    print(f">> Failed: {failed}")
    
    if failed == 0:
        print("\n>> ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n>> {failed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
