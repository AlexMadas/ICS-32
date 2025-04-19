# Starter code for assignment 1 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Alex Madas
# Madasa@uci.edu
# 39847840

import shlex

def parse_command():
    parts = shlex.split(input("> ")) 
   # print()
   # print(parts[0])  
   # print(parts[1])  
   # print(parts[2])
   # print(parts[3])

    return parts[0], parts[1], parts[2], parts[3]

command, input_1, option, input_2 = parse_command()
print(f'Command: {command} Input1: {input_1} Option: {option} Input2: {input_2}')