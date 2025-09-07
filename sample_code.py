#!/usr/bin/env python3
"""
Sample Python file with various issues for testing ReviewRabbit.
This file intentionally contains bugs, security issues, and code quality problems.
"""

import os
import subprocess
import random
from typing import List

# Security issues
password = "admin123"  # Hardcoded password
api_key = "sk-1234567890abcdef"  # Hardcoded API key

def unsafe_sql_query(user_id):
    """Example of SQL injection vulnerability."""
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query

def unsafe_command_execution(filename):
    """Example of command injection vulnerability."""
    os.system(f"cat {filename}")  # Unsafe command execution

def unsafe_file_access(path):
    """Example of path traversal vulnerability."""
    with open(f"../{path}", "r") as f:  # Path traversal
        return f.read()

# Code quality issues
def very_long_function():
    """This function is too long and has too many parameters."""
    # Simulating a very long function
    for i in range(100):
        if i % 2 == 0:
            if i % 4 == 0:
                if i % 8 == 0:
                    if i % 16 == 0:
                        print(f"Complex nested condition: {i}")
    
    # More code...
    data = []
    for j in range(50):
        data.append(j * 2)
    
    # Even more code...
    result = []
    for k in range(25):
        result.append(data[k] + k)
    
    return result

def function_with_too_many_parameters(a, b, c, d, e, f, g, h, i, j, k):
    """Function with too many parameters."""
    return a + b + c + d + e + f + g + h + i + j + k

def function_with_bare_except():
    """Function with bare except clause."""
    try:
        result = 10 / 0
    except:  # Bare except clause
        pass

def unused_import_example():
    """Function that doesn't use all imports."""
    # random is imported but not used in this function
    return "Hello World"

def insecure_random_usage():
    """Example of insecure random number generation."""
    return random.randint(1, 100)  # Should use secrets module for crypto

def resource_leak_example():
    """Example of potential resource leak."""
    f = open("temp.txt", "w")  # File not closed properly
    f.write("data")
    # Missing f.close()

def null_pointer_example(obj):
    """Example of potential null pointer issue."""
    if obj is None:
        return obj.some_method()  # Calling method on None

def infinite_loop_example():
    """Example of potential infinite loop."""
    while True:  # No break condition
        print("Infinite loop")

# TODO: Fix this function
# FIXME: This needs refactoring
# HACK: Temporary solution

class ComplexClass:
    """A class with high complexity."""
    
    def __init__(self):
        self.data = []
    
    def complex_method(self, x):
        """Method with high cyclomatic complexity."""
        if x > 0:
            if x > 10:
                if x > 100:
                    if x > 1000:
                        return "very large"
                    else:
                        return "large"
                else:
                    return "medium"
            else:
                return "small"
        else:
            if x < -10:
                if x < -100:
                    return "very negative"
                else:
                    return "negative"
            else:
                return "zero or small negative"

def main():
    """Main function with various issues."""
    # Test the functions
    unsafe_sql_query("1 OR 1=1")  # SQL injection test
    unsafe_command_execution("file.txt; rm -rf /")  # Command injection test
    unsafe_file_access("../../../etc/passwd")  # Path traversal test
    
    very_long_function()
    function_with_too_many_parameters(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    function_with_bare_except()
    unused_import_example()
    insecure_random_usage()
    resource_leak_example()
    null_pointer_example(None)
    # infinite_loop_example()  # Commented out to prevent actual infinite loop
    
    obj = ComplexClass()
    print(obj.complex_method(150))

if __name__ == "__main__":
    main()
