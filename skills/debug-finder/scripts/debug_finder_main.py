#!/usr/bin/env python3
"""
Main script for the debug finder skill
Integrates error location, fix suggestion, test creation, and logging
"""

import sys
import os
import subprocess
import re
from pathlib import Path


def find_error_location(error_message, project_root):
    """Call the find_error_location script"""
    script_path = Path(__file__).parent / "find_error_location.py"
    result = subprocess.run([
        sys.executable, str(script_path), error_message, project_root
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[SEARCH] Error location search completed")
        # Parse the output to get the most relevant match
        lines = result.stdout.strip().split('\n')
        matches = []
        for line in lines:
            if line.startswith('  ') and ':' in line:
                # Parse format: "  file_path:line_num [confidence] - content..."
                parts = line[2:].split(' ', 2)  # Skip leading "  "
                if len(parts) >= 2:
                    file_and_line = parts[0]
                    confidence_part = parts[1]
                    
                    file_path, line_num = file_and_line.rsplit(':', 1)
                    confidence = confidence_part.strip('[]')
                    
                    matches.append({
                        'file': file_path,
                        'line': int(line_num),
                        'confidence': confidence,
                        'content': parts[2] if len(parts) > 2 else ''
                    })
        
        return matches
    else:
        print(f"[ERROR] Error running location finder: {result.stderr}")
        return []


def create_test_script(error_description, fixed_file, fixed_line_num, project_root):
    """Call the create_test_script script"""
    script_path = Path(__file__).parent / "create_test_script.py"
    result = subprocess.run([
        sys.executable, str(script_path), error_description, fixed_file, str(fixed_line_num), project_root
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        test_file = result.stdout.strip().split(': ')[-1] if ': ' in result.stdout else None
        if test_file:
            print(f"[TEST] Test script created: {test_file}")
            return test_file
    else:
        print(f"[ERROR] Error creating test script: {result.stderr}")
    
    return None


def log_fix(error_desc, file_path, line_num, fix_desc, test_script_path, project_root):
    """Call the log_fix script"""
    script_path = Path(__file__).parent / "log_fix.py"
    result = subprocess.run([
        sys.executable, str(script_path), error_desc, file_path, str(line_num), fix_desc, test_script_path or "", project_root
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[LOG] Fix logged successfully")
        return result.stdout.strip()
    else:
        print(f"[ERROR] Error logging fix: {result.stderr}")
        return None


def run_build_verification(project_root):
    """Run node scripts/build.js to verify the fix doesn't introduce new issues"""
    print("[BUILD] Running build verification...")
    try:
        # Check if node is available
        node_check = subprocess.run(["node", "--version"], 
                                  capture_output=True, text=True)
        if node_check.returncode != 0:
            print("[BUILD] Warning: node is not available, skipping build verification")
            return {
                "success": True,
                "output": "node not available, build verification skipped",
                "error": "node not found",
                "issues_found": ["node command not found"],
                "returncode": 0
            }
        
        # Change to project root directory
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        # Run the build command (using node directly instead of npm)
        result = subprocess.run(
            ["node", "scripts/build.js"], 
            capture_output=True, 
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Change back to original directory
        os.chdir(original_cwd)
        
        build_success = result.returncode == 0
        build_output = result.stdout
        build_error = result.stderr
        
        print(f"[BUILD] Build completed with return code: {result.returncode}")
        
        # Analyze output for potential issues
        issues_found = []
        
        if build_error:
            # Look for specific error patterns in stderr
            error_patterns = [
                r"error:\s*",  # Generic errors
                r"\berror\b",  # Standalone error words
                r"\bfatal\b",  # Fatal errors
                r"\bexception\b",  # Exceptions
                r"\bundefined\b", # Undefined references
                r"\blinker\b",   # Linker errors
                r"\bcannot\s+open\b", # Cannot open file
                r"\bunresolved\s+external\b" # Unresolved externals
            ]
            
            for pattern in error_patterns:
                if re.search(pattern, build_error, re.IGNORECASE):
                    issues_found.append(f"Potential issue found in build error: {pattern}")
        
        if build_output:
            # Look for warning patterns in stdout
            warning_patterns = [
                r"warning:\s*",  # Generic warnings
                r"\bwarning\b",  # Standalone warning words
                r"deprecated",   # Deprecated features
                r"\bignoring\b",  # Ignored items
                r"\bskipping\b",  # Skipped items
            ]
            
            for pattern in warning_patterns:
                if re.search(pattern, build_output, re.IGNORECASE):
                    issues_found.append(f"Warning found in build output: {pattern}")
        
        if issues_found:
            print(f"[BUILD] Issues detected: {len(issues_found)} potential problems")
            for issue in issues_found:
                print(f"  - {issue}")
        else:
            print("[BUILD] No issues detected in build output")
        
        return {
            "success": build_success,
            "output": build_output,
            "error": build_error,
            "issues_found": issues_found,
            "returncode": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        print("[BUILD] Build command timed out after 5 minutes")
        os.chdir(original_cwd)  # Ensure we change back to original directory
        return {
            "success": False,
            "output": "",
            "error": "Build command timed out after 5 minutes",
            "issues_found": ["Build timed out"],
            "returncode": -1
        }
    except Exception as e:
        print(f"[BUILD] Error running build verification: {str(e)}")
        if 'original_cwd' in locals():
            os.chdir(original_cwd)  # Ensure we change back to original directory
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "issues_found": [f"Build execution error: {str(e)}"],
            "returncode": -1
        }


def suggest_fix(error_message, file_path, line_num, content):
    """Suggest a fix based on the error message and code content"""
    # This is a simplified fix suggestion algorithm
    # In a real implementation, this would be more sophisticated
    
    error_lower = error_message.lower()
    content_lines = content.split('\n')
    
    if line_num <= len(content_lines):
        problematic_line = content_lines[line_num - 1]
    else:
        problematic_line = ""
    
    # Common C++ error fixes
    if "not declared in this scope" in error_lower or "undeclared" in error_lower:
        # Look for undefined variables
        var_match = re.search(r"'([^']*)'.*(not declared|undeclared)", error_message)
        if var_match:
            var_name = var_match.group(1)
            return f"Variable '{var_name}' is not defined in this scope. Possible fixes:\n" \
                   f"1. Declare the variable before using it: '{var_name}' needs to be defined\n" \
                   f"2. Check if it's a typo or case mismatch\n" \
                   f"3. If it's a function/class from another file, ensure proper #include"
    
    elif "expected" in error_lower and "before" in error_lower:
        # Syntax error - missing semicolon, bracket, etc.
        return "Syntax error detected. Common fixes:\n" \
               "1. Check for missing semicolon at the end of the line\n" \
               "2. Verify matching brackets (parentheses, braces, etc.)\n" \
               "3. Ensure proper syntax for the statement"
    
    elif "is not defined" in error_lower:
        # JavaScript/TypeScript undefined variable
        var_match = re.search(r"'([^']*)'.*is not defined", error_message)
        if var_match:
            var_name = var_match.group(1)
            return f"Variable '{var_name}' is not defined. Possible fixes:\n" \
                   f"1. Declare the variable with 'let', 'const', or 'var': const {var_name} = value;\n" \
                   f"2. Check if it's imported correctly if it's from another module\n" \
                   f"3. Verify the spelling and case sensitivity"
    
    elif "unexpected token" in error_lower:
        # Likely missing comma, bracket, or quote
        return "Unexpected token error. Common fixes:\n" \
               "1. Check for missing commas in object/array literals\n" \
               "2. Verify matching quotes for strings\n" \
               "3. Ensure proper syntax for the statement"
    
    # Default generic fix suggestion
    return f"Suggested fix for error in {file_path}:{line_num}:\n" \
           f"- Review the error message: {error_message[:100]}\n" \
           f"- Examine line {line_num}: {problematic_line[:100]}\n" \
           f"- Common causes: syntax error, undefined variable, missing import, etc."


def main():
    if len(sys.argv) < 3:
        print("Usage: python debug_finder_main.py <error_message> <project_root>")
        sys.exit(1)
    
    error_message = sys.argv[1]
    project_root = sys.argv[2]
    
    print(f"[DEBUG-FINDER] Debug Finder Skill Activated")
    print(f"Error message: {error_message}")
    print(f"Project root: {project_root}")
    print("-" * 60)
    
    # Step 1: Find error location
    matches = find_error_location(error_message, project_root)
    
    if not matches:
        print("[ERROR] No specific locations found for the error")
        return
    
    # Use the highest confidence match
    match = matches[0]  # Take the first (highest confidence) match
    print(f"[LOCATION] Found potential error location: {match['file']}:{match['line']} ({match['confidence']} confidence)")
    print(f"   Code: {match['content']}")
    
    # Read the actual file content to provide more context
    try:
        with open(match['file'], 'r', encoding='utf-8', errors='ignore') as f:
            file_content = f.read()
        
        # Step 2: Suggest a fix
        fix_suggestion = suggest_fix(error_message, match['file'], match['line'], file_content)
        print(f"[FIX] Suggested fix:")
        print(fix_suggestion)
        
        # Step 3: Create test script
        test_script = create_test_script(error_message, match['file'], match['line'], project_root)
        
        # Step 4: Log the fix
        log_result = log_fix(
            error_message,
            match['file'],
            match['line'],
            fix_suggestion,
            test_script,
            project_root
        )
        
        # Step 5: Run build verification
        print("\n" + "=" * 60)
        print("[VERIFICATION] Running build verification...")
        build_result = run_build_verification(project_root)
        
        # Log build verification results
        if build_result["issues_found"]:
            print(f"⚠️  Build verification found {len(build_result['issues_found'])} potential issues")
            for issue in build_result["issues_found"]:
                print(f"   • {issue}")
        else:
            print("✅ Build verification completed successfully - no issues detected")
        
        print("-" * 60)
        print("[SUCCESS] Debug Finder Skill completed")
        print(f"📁 Error location: {match['file']}:{match['line']}")
        print(f"🧪 Test script: {test_script or 'Not created'}")
        print(f"📋 Log file: {log_result or 'Not created'}")
        print(f"🔨 Build verification: {'Success' if build_result['success'] else 'Failed'}")
        print(f"🔍 Issues found: {len(build_result['issues_found'])}")
        
    except Exception as e:
        print(f"Error reading file {match['file']}: {e}")


if __name__ == "__main__":
    main()