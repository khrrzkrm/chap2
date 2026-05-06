import unittest
from reminder import *
from NTL_ParsertoAst import *
from z3_precise import *
from NTL_Struct import BinaryOperation
def main():
    # Ask the user for input
    input_string = input("Enter a formula from FMMTNL: ")
    parsed = process_input(input_string)
    print(type(parsed))
    synthetize(parsed)
if __name__ == "__main__":
    main()
    