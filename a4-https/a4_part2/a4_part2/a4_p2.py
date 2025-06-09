# Alex Madas
# Madasa
# 39847840


from abc import ABC, abstractmethod
import random,enum
import time

class Appetite:
    LOW = 3
    MEDIUM = 4
    HIGH = 5

class Dog(ABC):
    def __init__(self, name, age, appetite) -> None:
        self.hunger_clock = 0
        self._name = name
        self._age = age 
        self.appetite = appetite

    @abstractmethod
    def breed(self):
        pass
    
    def name(self):
        return self._name
    
    def age(self):
        return self._age

    def hungry(self, on_hungry: callable):
        """
        Periodically checks if hunger_clock > appetite.
        If so, randomly decides hunger and, when hungry, calls on_hungry(self).
        Then resets hunger_clock; otherwise increments it.
        """
        while True:
            if self.hunger_clock > self.appetite:
                # randomly decide if truly hungry
                if bool(random.getrandbits(1)):
                    on_hungry(self)
                else:
                    # if not hungry this round, just bump the clock
                    self.hunger_clock += 1
            else:
                self.hunger_clock += 1

            time.sleep(3)  # check every 3 seconds

    def feed(self):
        """
        Feeds the dog. Hunger clock is reset
        """
        self.hunger_clock = 0

class GermanShepherd(Dog):
    def __init__(self, name, age):
        super().__init__(name, age, appetite=Appetite.MEDIUM)

    def breed(self):
        return "German Shepherd"

class GoldenRetriever(Dog):
    def __init__(self, name, age):
        super().__init__(name, age, appetite=Appetite.MEDIUM)

    def breed(self):
        return "Golden Retriever"

class AnatolianShepherd(Dog):
    def __init__(self, name, age):
        super().__init__(name, age, appetite=Appetite.MEDIUM)

    def breed(self):
        return "Anatolian Shepherd"
    

if __name__ == '__main__':
    dog = None
    breed = input("What breed of dog would you like to care for? \n\n 1. German Shepherd \n 2. Golden Retriever \n 3. Anatolian Shepherd \n: ")
    name = input("What would you like to name your dog? ")
    age = input("How old would you like your dog to be? ")
    age = int(age)
    if breed == "1":
        dog = GermanShepherd(name, age)
    elif breed == "2":
        dog = GoldenRetriever(name, age)
    elif breed == "3":
        dog = AnatolianShepherd(name, age)
    else:
        print("I didn't understand your entry, please run again.")

    def feed_dog(d: Dog):
                print(f"Your {d.breed()}, {d.name()} is hungry; feeding now!")
                d.feed()

    print(f"Starting hunger monitor for your {dog.breed()}, {dog.name()}...")
    dog.hungry(feed_dog)