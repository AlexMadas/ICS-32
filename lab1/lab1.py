# lab1.py

# Starter code for lab 1 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.
# Please see the README in this repository for the requirements of this lab exercise

# Alex Madas
# madasa@uci.edu
# 39847840

def main():
    print("Welcome to ICS 32 PyCalc!\n")

    num1 = int(input("Enter your first operand: "))
    num2 = int(input("Enter your second operand: "))
    operator = input("Enter your desired operator (+, -, or x): ")

    match operator:
        case "+":
            result = num1 + num2
        case "-":
            result = num1 - num2
        case "x":
            result = num1 * num2
        case _:
            result = "Something Broke! :("
    print("\nThe result of your calculation is:", result)

if __name__ == "__main__":
    main()