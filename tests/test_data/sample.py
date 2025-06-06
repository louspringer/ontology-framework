class Person:
    """A simple class representing a person."""
    def __init__(self, name: str, age: int):
        """
        Initializes a Person object.

        Args:
            name: The name of the person.
            age: The age of the person.
        """
        self.name = name
        self.age = age

    def greet(self) -> str:
        """Returns a greeting message."""
        return f"Hello, my name is {self.name} and I am {self.age} years old."

class Employee(Person):
    """A class representing an employee, inheriting from Person."""
    def __init__(self, name: str, age: int, employee_id: str):
        """
        Initializes an Employee object.

        Args:
            name: The name of the employee.
            age: The age of the employee.
            employee_id: The ID of the employee.
        """
        super().__init__(name, age)
        self.employee_id = employee_id

    def get_details(self) -> str:
        """Returns employee details."""
        return f"Employee ID: {self.employee_id}, Name: {self.name}, Age: {self.age}"

def standalone_function(param1: int, param2: str) -> bool:
    """A standalone function for testing."""
    if param1 > 0 and len(param2) > 0:
        return True
    return False
