---
name: debug-finder
description: "Automates debugging by locating errors in C++ or frontend code, applying fixes, creating test scripts in ./test, and logging to ./logs. Use when encountering C++/frontend errors that need systematic debugging, code location, automated fixes, test creation, and fix logging. No summary documents created."
---

# Debug Finder Skill

Finds and fixes errors in C++ or frontend code based on error messages. Automates debugging by locating issues, applying fixes, creating tests, and logging results.

## Workflow

1. **Error Analysis**: Parses error messages to identify type and location
2. **Code Location**: Searches codebase for relevant files and sections
3. **Fix Application**: Applies appropriate fixes based on error type
4. **Test Creation**: Creates tests in ./test directory with timestamp-based naming
5. **Logging**: Saves detailed logs to ./logs as JSON files with timestamp naming
6. **Build Verification**: Automatically runs `npm run build` to verify the fix doesn't introduce new issues and logs the verification results

## When to Use
Use when encountering C++/frontend errors needing systematic debugging, code location, automated fixes, test creation, and fix logging.

## Input
- Complete error message
- Affected file path (if known)

## Output
- Error location
- Applied fix
- Test script in ./test
- Log in ./logs