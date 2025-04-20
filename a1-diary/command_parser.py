# Starter code for assignment 1 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Alex Madas
# Madasa@uci.edu
# 39847840

import shlex

def parse_command(input_str):
    """  
    Parses a shell-like command string into its components.  

    Args:  
        input_str: Raw user input (e.g., "C 'my path' -n diary").  

    Returns:  
        Dictionary with:  
        - 'command': Uppercase command (e.g., 'C'),  
        - 'args': List of non-option arguments,  
        - 'options': Dictionary of options and their values,  
        - 'options_order': List to preserve option order.  
        Returns None if input is empty or invalid.  
    """  
    try:
        parts = shlex.split(input_str)
    except ValueError:
        return None
    
    if not parts:
        return None

    command = parts[0].upper()
    args = []
    options = {}
    options_order = []

    current_option = None

    for part in parts[1:]:
        if part.startswith('-'):
            current_option = part
            options[current_option] = None
            options_order.append(current_option)
        else:
            if current_option:
                options[current_option] = part
                current_option = None
            else:
                args.append(part)

    return {
        'command': command,
        'args': args,
        'options': options,
        'options_order': options_order
    }