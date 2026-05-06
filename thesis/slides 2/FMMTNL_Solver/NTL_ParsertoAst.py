from pyparsing import *
from NTL_Struct import *




# Grammar definitions
integer = pyparsing_common.integer
infinity = Literal("inf").setParseAction(lambda toks: float('inf'))

# Ensure second_element correctly combines integer and infinity
second_element = Or([integer, infinity])

# Define the content of a filled interval
interval_contents = integer + Suppress(',') + second_element
filled_interval = Suppress('[') + Group(interval_contents) + Suppress(']')
empty_interval = Suppress('[') + Suppress(']')

# Combine filled and empty intervals using Or operator
interval = filled_interval | empty_interval.setParseAction(lambda: [])


# Define interval structure precisely
#interval = Suppress('[') + Group(integer + Suppress(',') + second_element) + Suppress(']')
intervals = Suppress('{') + Group(delimitedList(interval)) + Suppress('}')

# Define norm types and structure for a norm
action = Word(alphas)
norm_type = oneOf("O F")
norm = Group(norm_type + action + intervals)

# Logical operators setup in infix notation
expr = infixNotation(norm, [
    (Literal("!"), 1, opAssoc.RIGHT),
    (Literal("&"), 2, opAssoc.RIGHT),
    (Literal("||"), 2, opAssoc.RIGHT),
    (Literal(";"), 2, opAssoc.RIGHT),
    (Literal(">>"), 2, opAssoc.RIGHT),
])
# Function to parse norms input
def parse_norms(input_string):
    try:
        results = expr.parseString(input_string, parseAll=True)
        return results[0]  # Return the root of the parsed structure
    except ParseException as pe:
        print("Parsing error:", str(pe))
        return None
    
def parse_norms2(input_string):
    try:
        results = expr.parseString(input_string, parseAll=True)
        return results.asList()  # Converts the parsed result to a list for better inspection
    except ParseException as pe:
        print("Parsing error:", str(pe))
        print("At char:", pe.loc, "in line:", pe.lineno)
        print("Input around error:", input_string[max(0, pe.loc-10):pe.loc+10])
        return None    


    
def build_ast_from_parsed(parsed_input):
    #print(parsed_input)
    """
    Recursively builds an AST from a parsed input.

    :param parsed_input: The output from pyparsing's parseString function.
    :return: A Norm or BinaryOperation object based on the parsed input.
    """
    if (parsed_input[0] in {'O', 'F'}):
        return Norm(parsed_input[0], parsed_input[2].asList(), parsed_input[1])
    elif parsed_input[0] == "!":
        return NotOperation(build_ast_from_parsed(parsed_input[1]))
    else:
        return BinaryOperation(build_ast_from_parsed(parsed_input[0]), parsed_input[1],build_ast_from_parsed(parsed_input[2]))

def process_input(input_string):
    parsed_input = parse_norms(input_string)
    if parsed_input:
        ast = build_ast_from_parsed(parsed_input)
        return ast
    return "Failed to parse the input."




