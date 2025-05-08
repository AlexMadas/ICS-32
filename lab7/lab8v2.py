# lab8v2.py

# Starter code for lab 8 in ICS 32
# Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Alex Madas
# madasa
# 39847840


from abc import ABC, abstractmethod
import random


class Appetite:
    LOW = 3
    MEDIUM = 4
    HIGH = 5


class Dog(ABC):
    def __init__(self, name, age):
        self._name = name
        self._age = age
        self.hunger_clock = 0

    @abstractmethod
    def breed(self):
        pass

    @abstractmethod
    def appetite(self):
        pass

    def name(self):
        return self._name

    def age(self):
        return self._age

    def hungry(self):
        """
        Check if the dog is hungry based on hunger_clock and appetite.
        If hunger_clock exceeds appetite, randomly return True or False.
        Otherwise, increment hunger_clock and return False.
        """
        if self.hunger_clock > self.appetite():
            return bool(random.getrandbits(1))
        else:
            self.hunger_clock += 1
            return False

    def feed(self):
        """Reset hunger_clock to 0."""
        self.hunger_clock = 0


class GermanShepherd(Dog):
    def breed(self):
        return "German Shepherd"

    def appetite(self):
        return Appetite.MEDIUM


class Bulldog(Dog):
    def breed(self):
        return "Bulldog"

    def appetite(self):
        return Appetite.LOW


class Labrador(Dog):
    def breed(self):
        return "Labrador"

    def appetite(self):
        return Appetite.HIGH


def select_dog():
    while True:
        print("Choose your dog breed:")
        print("1. German Shepherd")
        print("2. Bulldog")
        print("3. Labrador")
        breed = input("Enter your choice: ").strip()

        if breed not in ("1", "2", "3"):
            print("Invalid selection. Please enter 1, 2, or 3.")
            continue

        name = input("Enter your dog's name: ").strip()

        try:
            age = int(input("Enter your dog's age (number): ").strip())
        except ValueError:
            print("Invalid age. Please enter a valid number.")
            continue

        return create_dog_by_breed(breed, name, age)


def create_dog_by_breed(breed, name, age):
    if breed == "1":
        return GermanShepherd(name, age)
    elif breed == "2":
        return Bulldog(name, age)
    elif breed == "3":
        return Labrador(name, age)


def main():
    dog = select_dog()

    while True:
        is_hungry = dog.hungry()
        h_text = "is hungry!" if is_hungry else "is not hungry."
        print(f"Your {dog.breed()}, {dog.name()} {h_text}")

        feed = input(f"Would you like to try feeding {dog.name()}? (y/n/q): ").strip().lower()

        if feed == "y":
            if is_hungry:
                dog.feed()
                print(f"{dog.name()} happily eats the food!")
            else:
                print(f"{dog.name()} is not hungry right now.")
        elif feed == "n":
            continue
        elif feed == "q":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 'y', 'n', or 'q'.")


if __name__ == "__main__":
    main()