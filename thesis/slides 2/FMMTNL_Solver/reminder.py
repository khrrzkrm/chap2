from z3 import *

class Reminder:
    def __init__(self, value):
        self.value = value
    
    @classmethod
    def int(cls, value):
        return cls(IntVal(value))

    @classmethod
    def arith(cls, expr):
        return cls(expr)

    @classmethod
    def top(cls):
        # Use BoolVal(True) to ensure the value is a Z3 boolean object
        return cls(BoolVal(True))
    @classmethod
    def min(cls, left, right):
        # Check if either is "top"
        if left.is_top():
            return right
        if right.is_top():
            return left
        # Proceed with normal minimum calculation
        left_val = left.value if isinstance(left, Reminder) else left
        right_val = right.value if isinstance(right, Reminder) else right
        return cls(If(left_val < right_val, left_val, right_val))

    @classmethod
    def max(cls, left, right):
        # Check if either is "top"
        if left.is_top() or right.is_top():
            return cls.top()
        # Proceed with normal maximum calculation
        left_val = left.value if isinstance(left, Reminder) else left
        right_val = right.value if isinstance(right, Reminder) else right
        return cls(If(left_val > right_val, left_val, right_val))

    def is_top(self):
        # Check if the value is a Z3 BoolRef and evaluates to True
        return isinstance(self.value, BoolRef) and is_true(self.value)
    
    def __repr__(self):
        return f"Reminder({self.value})"

def is_true(expr):
    # Simplify the expression and check if it's true
    return simplify(expr) == True

def reminder_to_z3(reminder):
    if not isinstance(reminder, Reminder):
        raise TypeError("reminder_to_z3 function expected a Reminder instance")
    return reminder.value