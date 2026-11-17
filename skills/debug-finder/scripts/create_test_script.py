#!/usr/bin/env python3
"""
Create test script based on error and fix
"""

import os
import sys
from datetime import datetime
from pathlib import Path


def create_cpp_test(error_desc, fixed_file, fixed_line_num, project_root):
    """Create a C++ test for the fix"""
    test_content = f'''// Auto-generated test for fix in {fixed_file}:{fixed_line_num}
// Error description: {error_desc}

#include <iostream>
#include <cassert>
// Add other necessary includes

int main() {{
    std::cout << "Testing fix for: {error_desc[:50]}..." << std::endl;
    
    // Add specific test for the fixed issue
    // This is a template - customize based on the actual fix
    
    try {{
        // Insert code here that would have caused the original error
        // and should now work with the fix
        
        std::cout << "Test passed - error condition resolved!" << std::endl;
        return 0;
    }} catch (const std::exception& e) {{
        std::cerr << "Test failed: " << e.what() << std::endl;
        return 1;
    }}
}}
'''
    
    # Create test directory if it doesn't exist
    test_dir = Path(project_root) / "test"
    test_dir.mkdir(exist_ok=True)
    
    # Write test to the test directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_file = test_dir / f"cpp_test_{timestamp}.cpp"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    return str(test_file)


def create_js_test(error_desc, fixed_file, fixed_line_num, project_root):
    """Create a JavaScript test for the fix"""
    test_content = f'''// Auto-generated test for fix in {fixed_file}:{fixed_line_num}
// Error description: {error_desc}

console.log("Testing fix for:", "{error_desc[:50]}...");

try {{
    // Insert code here that would have caused the original error
    // and should now work with the fix
    
    // Example test - customize based on the actual fix
    console.log("Test passed - error condition resolved!");
}} catch (error) {{
    console.error("Test failed:", error.message);
    process.exit(1);
}}
'''

    # Create test directory if it doesn't exist
    test_dir = Path(project_root) / "test"
    test_dir.mkdir(exist_ok=True)
    
    # Write test to the test directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_file = test_dir / f"js_test_{timestamp}.js"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    return str(test_file)


def create_vue_test(error_desc, fixed_file, fixed_line_num, project_root):
    """Create a Vue component test for the fix"""
    test_content = f'''<!-- Auto-generated test for fix in {fixed_file}:{fixed_line_num} -->
<!-- Error description: {error_desc} -->

<template>
  <div id="app">
    <!-- Template that exercises the fixed functionality -->
    <div>{{{{ message }}}}</div>
  </div>
</template>

<script>
import {{ createApp }} from 'vue';

const App = {{
  data() {{
    return {{
      message: 'Test passed - error condition resolved!'
    }}
  }},
  mounted() {{
    console.log('Testing fix for: {error_desc[:50]}...');
    // Add specific test logic here
  }}
}};

createApp(App).mount('#app');
</script>

<style>
/* Add any necessary styles */
</style>
'''

    # Create test directory if it doesn't exist
    test_dir = Path(project_root) / "test"
    test_dir.mkdir(exist_ok=True)
    
    # Write test to the test directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_file = test_dir / f"vue_test_{timestamp}.vue"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    return str(test_file)


def create_test_script(error_description, fixed_file, fixed_line_num, project_root):
    """
    Create an appropriate test script based on the file type and error description
    """
    print(f"[TEST] Creating test script for fix in {fixed_file}:{fixed_line_num}")
    
    # Determine file type and create appropriate test
    if fixed_file.endswith('.cpp') or fixed_file.endswith('.h') or fixed_file.endswith('.hpp'):
        return create_cpp_test(error_description, fixed_file, fixed_line_num, project_root)
    elif fixed_file.endswith('.js') or fixed_file.endswith('.ts') or fixed_file.endswith('.jsx') or fixed_file.endswith('.tsx'):
        return create_js_test(error_description, fixed_file, fixed_line_num, project_root)
    elif fixed_file.endswith('.vue'):
        return create_vue_test(error_description, fixed_file, fixed_line_num, project_root)
    else:
        # Default to JS test if unsure
        return create_js_test(error_description, fixed_file, fixed_line_num, project_root)


def main():
    if len(sys.argv) < 5:
        print("Usage: python create_test_script.py <error_description> <fixed_file> <fixed_line_num> <project_root>")
        sys.exit(1)
    
    error_description = sys.argv[1]
    fixed_file = sys.argv[2]
    fixed_line_num = sys.argv[3]
    project_root = sys.argv[4]
    
    test_file = create_test_script(error_description, fixed_file, fixed_line_num, project_root)
    print(f"Test script created: {test_file}")


if __name__ == "__main__":
    main()