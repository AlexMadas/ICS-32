#lab2.py

# Starter code for lab 2 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.
# Please see the README in this repository for the requirements of this lab exercise

# NAME
# EMAIL
# STUDENT ID

def add(a, b):
    return  a + b

def sub(a, b):
    return  a - b

def div(a, b):
    return  a / b

def mul(a, b):
    return  a * b

def run():
    a = input("Enter left operand: ")
    b = input("Enter right operand: ")
    operator = input("What type of calculation would you like to perform (+, -, x, /)? ")
    
    r = 0
    try:
        if operator == "+":
            r = add(int(a),int(b))
        elif operator == "-":
            r = sub(int(a),int(b))
        elif operator == "x":
            r = mul(int(a),int(b))
        elif operator == "/":
            r = div(int(a),int(b))
        else:
            r = "Unable to perform the desired calculation, please try again."
    except ZeroDivisionError:
        print("Error: Cannot divide by 0")
        run()
    except ValueError:
        print("Error: Invalid value")
        run()

    print(r)
    
    if input("Run another calculation (y/n)? ") == "y":
        run()


if __name__ == "__main__":
    print("Welcome to PyCalc!")
    run()
