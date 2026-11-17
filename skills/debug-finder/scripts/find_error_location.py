#!/usr/bin/env python3
"""
Find error location in codebase based on error message
"""

import os
import sys
import re
from pathlib import Path


def find_error_location(error_message, project_root):
    """
    Find the location of an error in the codebase based on the error message
    """
    print(f"[INFO] Searching for error in codebase: {error_message[:50]}...")
    
    # Define file extensions to search based on error type
    cpp_extensions = ['.cpp', '.h', '.hpp', '.cxx', '.cc']
    js_extensions = ['.js', '.ts', '.jsx', '.tsx']
    vue_extensions = ['.vue']
    frontend_extensions = js_extensions + vue_extensions
    
    # Determine likely file type based on error message
    is_cpp_error = any(keyword in error_message.lower() for keyword in 
                      ['error:', 'warning:', 'undefined reference', 'expected', 
                       'syntax error', 'identifier', 'undeclared', 'linker'])
    is_frontend_error = any(keyword in error_message.lower() for keyword in 
                           ['javascript', 'referenceerror', 'typeerror', 
                            'syntaxerror', 'unexpected token', 'is not defined'])
    
    extensions_to_search = []
    if is_cpp_error:
        extensions_to_search = cpp_extensions
        print("   [CPP] Detected C++ error, searching C++ files...")
    elif is_frontend_error:
        extensions_to_search = frontend_extensions
        print("   [FRONTEND] Detected frontend error, searching JS/Vue files...")
    else:
        # Search all relevant extensions
        extensions_to_search = cpp_extensions + frontend_extensions
        print("   [GENERIC] Generic error, searching all relevant files...")
    
    # Search for relevant files
    matches = []
    for ext in extensions_to_search:
        for root, dirs, files in os.walk(project_root):
            # Skip common directories that shouldn't be searched
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'build', 'dist']]
            
            for file in files:
                if file.endswith(ext):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            # Look for patterns in the error message
                            if is_cpp_error:
                                matches.extend(search_cpp_patterns(error_message, file_path, content))
                            elif is_frontend_error:
                                matches.extend(search_frontend_patterns(error_message, file_path, content))
                            else:
                                # Generic search
                                matches.extend(generic_search(error_message, file_path, content))
                    except Exception as e:
                        print(f"   Warning: Could not read {file_path}: {e}")
    
    # Return the most relevant matches
    return deduplicate_matches(matches)[:10]  # Limit to top 10 matches


def search_cpp_patterns(error_message, file_path, content):
    """Search for C++ specific error patterns"""
    matches = []
    
    # Look for undefined identifiers
    identifier_match = re.search(r"'([^']*)' was not declared in this scope|use of undeclared identifier '([^']*)'", error_message)
    if identifier_match:
        identifier = identifier_match.group(1) or identifier_match.group(2)
        if identifier:
            # Find where this identifier is used in the file
            for i, line in enumerate(content.split('\n'), 1):
                if identifier in line and not line.strip().startswith('//'):
                    matches.append({
                        'file': str(file_path),
                        'line': i,
                        'content': line.strip(),
                        'confidence': 'high'
                    })
    
    # Look for syntax errors
    if 'expected' in error_message and 'before' in error_message:
        # Parse what was expected and where
        expected_match = re.search(r"expected '([^']+)' before", error_message)
        if expected_match:
            expected_token = expected_match.group(1)
            # Find lines that might be missing the expected token
            for i, line in enumerate(content.split('\n'), 1):
                if expected_token in error_message and line.strip():
                    matches.append({
                        'file': str(file_path),
                        'line': i,
                        'content': line.strip(),
                        'confidence': 'medium'
                    })
    
    return matches


def search_frontend_patterns(error_message, file_path, content):
    """Search for frontend specific error patterns"""
    matches = []
    
    # Look for undefined variables
    var_match = re.search(r"'([^']+)' is not defined|Cannot access '([^']*)' before initialization", error_message)
    if var_match:
        var_name = var_match.group(1) or var_match.group(2)
        if var_name:
            for i, line in enumerate(content.split('\n'), 1):
                if var_name in line and not line.strip().startswith('//'):
                    matches.append({
                        'file': str(file_path),
                        'line': i,
                        'content': line.strip(),
                        'confidence': 'high'
                    })
    
    # Look for import/export issues
    if 'import' in error_message.lower() or 'export' in error_message.lower():
        for i, line in enumerate(content.split('\n'), 1):
            if ('import' in line or 'export' in line) and not line.strip().startswith('//'):
                matches.append({
                    'file': str(file_path),
                    'line': i,
                    'content': line.strip(),
                    'confidence': 'medium'
                })
    
    return matches


def generic_search(error_message, file_path, content):
    """Generic search for any error pattern"""
    matches = []
    
    # Just look for any occurrence of key terms from the error message
    # Extract potential keywords from error message
    keywords = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', error_message)
    # Filter out common words
    common_words = {'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'a', 'an', 'is', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'error', 'warning', 'failed', 'not', 'no', 'yes'}
    keywords = [kw for kw in keywords if len(kw) > 2 and kw.lower() not in common_words]
    
    for keyword in keywords[:5]:  # Limit to first 5 keywords to avoid too many matches
        for i, line in enumerate(content.split('\n'), 1):
            if keyword.lower() in line.lower() and not line.strip().startswith('//'):
                matches.append({
                    'file': str(file_path),
                    'line': i,
                    'content': line.strip(),
                    'confidence': 'low',
                    'matched_keyword': keyword
                })
    
    return matches


def deduplicate_matches(matches):
    """Remove duplicate matches based on file and line"""
    seen = set()
    unique_matches = []
    
    for match in matches:
        key = (match['file'], match['line'])
        if key not in seen:
            seen.add(key)
            unique_matches.append(match)
    
    return unique_matches


def main():
    if len(sys.argv) < 3:
        print("Usage: python find_error_location.py <error_message> <project_root>")
        sys.exit(1)
    
    error_message = sys.argv[1]
    project_root = sys.argv[2]
    
    matches = find_error_location(error_message, project_root)
    
    print(f"\nFound {len(matches)} potential matches:")
    for match in matches:
        print(f"  {match['file']}:{match['line']} [{match.get('confidence', 'unknown')}] - {match['content'][:80]}...")


if __name__ == "__main__":
    main()