import os
import re
from pathlib import Path


def indent_block(text, spaces=4):
    """Add indentation to each line of text."""
    lines = text.split('\n')
    result = []
    for i, line in enumerate(lines):
        if i == 0 and not line.strip():
            result.append(line)
        elif line.strip():
            result.append(' ' * spaces + line)
        else:
            result.append(line)
    return '\n'.join(result)


def convert_solution_file(filepath):
    """Convert a function-based solution to class-based."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract the day from path
    day_folder = filepath.parent.name
    day = day_folder.replace('day', '').lstrip('0')
    year = "2024"
    
    # Remove any if __name__ == "__main__" or if __name__ == '__main__' blocks
    content = re.sub(r'if __name__ == ["\']__main__["\']:.*', '', content, flags=re.DOTALL)
    
    # Extract docstring if exists
    docstring_match = re.match(r'^"""[\s\S]*?"""', content, re.MULTILINE)
    docstring = docstring_match.group(0) if docstring_match else f'"""\nAdvent of Code {year} - Day {day}\n"""'
    
    # Remove old docstring from content
    if docstring_match:
        content = content[docstring_match.end():].lstrip()
    
    # Extract imports
    imports = []
    import_pattern = r'^(import\s+.+|from\s+.+import\s+.+)$'
    for line in content.split('\n'):
        if re.match(import_pattern, line.strip()):
            imports.append(line)
        elif line.strip() and not line.strip().startswith('#'):
            if not line.strip().startswith('def '):
                break
    
    # Find ALL function definitions
    functions = []
    func_pattern = r'^def (\w+)\(([^)]*)\):(.*?)(?=^def |\Z)'
    matches = re.finditer(func_pattern, content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        func_name = match.group(1)
        func_params = match.group(2)
        func_body = match.group(3)
        functions.append((func_name, func_params, func_body))
    
    # Get all function names for replacement (excluding the main ones we're renaming)
    all_function_names = [name for name, _, _ in functions 
                         if name not in {'part_one', 'part_two', 'part1', 'part2', 'load_data', 'solve'}]
    
    # Start building the class
    class_content = f'{docstring}\n\n'
    
    if imports:
        class_content += '\n'.join(imports) + '\n\n'
    
    class_content += '\nclass Solution:\n'
    class_content += '    def __init__(self, data_file="data"):\n'
    class_content += '        self.data = self.load_data(data_file)\n'
    class_content += '    \n'
    
    # Categorize functions
    main_funcs = {'load_data', 'part_one', 'part1', 'part_two', 'part2', 'solve'}
    helper_funcs = []
    
    # Separate main functions from helpers
    main_func_dict = {}
    for func_name, func_params, func_body in functions:
        if func_name in main_funcs:
            main_func_dict[func_name] = (func_params, func_body)
        else:
            helper_funcs.append((func_name, func_params, func_body))
    
    # Add load_data method
    if 'load_data' in main_func_dict:
        params, func_body = main_func_dict['load_data']
        params = update_params(params)
        func_body = update_function_calls(func_body, all_function_names)
        func_body = indent_block(func_body, 4)
        class_content += f'    def load_data(self{", " + params if params else ""}):{func_body}\n'
    else:
        class_content += '    def load_data(self, filename):\n'
        class_content += '        """Load and parse the input data."""\n'
        class_content += '        with open(filename, \'r\') as f:\n'
        class_content += '            return f.read().strip()\n'
        class_content += '    \n'
    
    # Add part1 method
    part1_key = 'part1' if 'part1' in main_func_dict else ('part_one' if 'part_one' in main_func_dict else None)
    if part1_key:
        params, func_body = main_func_dict[part1_key]
        params = update_params(params)
        func_body = update_function_calls(func_body, all_function_names)
        func_body = indent_block(func_body, 4)
        class_content += f'    def part1(self{", " + params if params else ""}):{func_body}\n'
    else:
        class_content += '    def part1(self):\n'
        class_content += '        """Solve part 1 of the puzzle."""\n'
        class_content += '        # TODO: Implement part 1\n'
        class_content += '        return None\n'
        class_content += '    \n'
    
    # Add part2 method
    part2_key = 'part2' if 'part2' in main_func_dict else ('part_two' if 'part_two' in main_func_dict else None)
    if part2_key:
        params, func_body = main_func_dict[part2_key]
        params = update_params(params)
        func_body = update_function_calls(func_body, all_function_names)
        func_body = indent_block(func_body, 4)
        class_content += f'    def part2(self{", " + params if params else ""}):{func_body}\n'
    else:
        class_content += '    def part2(self):\n'
        class_content += '        """Solve part 2 of the puzzle."""\n'
        class_content += '        # TODO: Implement part 2\n'
        class_content += '        return None\n'
        class_content += '    \n'
    
    # Add all helper functions as methods
    for func_name, func_params, func_body in helper_funcs:
        params = update_params(func_params)
        func_body = update_function_calls(func_body, all_function_names)
        func_body = indent_block(func_body, 4)
        class_content += f'    def {func_name}(self{", " + params if params else ""}):{func_body}\n'
    
    # Add solve method
    if 'solve' in main_func_dict:
        params, func_body = main_func_dict['solve']
        params = update_params(params)
        func_body = update_function_calls(func_body, all_function_names)
        func_body = indent_block(func_body, 4)
        class_content += f'    def solve(self{", " + params if params else ""}):{func_body}\n'
    else:
        class_content += '    def solve(self):\n'
        class_content += '        """Run both parts and print results."""\n'
        class_content += f'        print(f"Day {day} Solutions:")\n'
        class_content += '        print(f"Part 1: {self.part1()}")\n'
        class_content += '        print(f"Part 2: {self.part2()}")\n'
        class_content += '\n\n'
    
    # Add main block (only one, our own)
    class_content += '\nif __name__ == "__main__":\n'
    class_content += '    solution = Solution()\n'
    class_content += '    solution.solve()\n'
    
    return class_content


def update_params(params):
    """Remove 'data' parameter if it exists, as it will be self.data."""
    if not params:
        return ""
    
    param_list = [p.strip() for p in params.split(',')]
    param_list = [p for p in param_list if p and not p.startswith('data')]
    
    return ', '.join(param_list)


def update_function_calls(func_body, all_function_names):
    """Update function calls and variable references to use self."""
    # First, rename part_one/part_two to part1/part2
    func_body = re.sub(r'(?<!self\.)(?<!\.)\bpart_one\(', 'part1(', func_body)
    func_body = re.sub(r'(?<!self\.)(?<!\.)\bpart_two\(', 'part2(', func_body)
    
    # Now add self. to part1, part2, and load_data
    func_body = re.sub(r'(?<!self\.)(?<!\.)\bpart1\(', 'self.part1(', func_body)
    func_body = re.sub(r'(?<!self\.)(?<!\.)\bpart2\(', 'self.part2(', func_body)
    func_body = re.sub(r'(?<!self\.)(?<!\.)\bload_data\(', 'self.load_data(', func_body)
    
    # Replace calls to ALL helper functions defined in the file
    for func_name in all_function_names:
        pattern = rf'(?<!self\.)(?<!\.)\b{func_name}\('
        replacement = f'self.{func_name}('
        func_body = re.sub(pattern, replacement, func_body)
    
    # Replace standalone 'data' references with 'self.data'
    func_body = re.sub(r'(?<!self\.)\bdata\b', 'self.data', func_body)
    
    return func_body


def process_current_directory():
    """Process all solution files in day folders in current directory."""
    day_folders = sorted([d for d in Path(".").iterdir() 
                         if d.is_dir() and d.name.startswith("day")])
    
    if not day_folders:
        print("No day## folders found in current directory")
        return
    
    converted_count = 0
    
    for day_folder in day_folders:
        backup_file = day_folder / "solution.py.bak"
        solution_file = day_folder / "solution.py"
        
        if backup_file.exists():
            print(f"Converting: {backup_file} -> {solution_file}")
            
            try:
                new_content = convert_solution_file(backup_file)
                
                with open(solution_file, 'w') as f:
                    f.write(new_content)
                
                print(f"  ✓ Converted successfully")
                converted_count += 1
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Skipping {day_folder}: No .bak file found")
    
    print(f"\n{'='*50}")
    print(f"Converted {converted_count} files from backups")
    print(f"\nBackup files (.bak) preserved")
    print(f"Review the changes and delete backups when satisfied")


if __name__ == "__main__":
    print("Converting solutions from .bak files...")
    print("="*50)
    process_current_directory()