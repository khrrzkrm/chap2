class Interval:
    def __init__(self, tmin, tmax):
        # Validate tmax as either an integer or 'inf'
        if not (isinstance(tmax, int) or tmax == float('inf')):
            raise ValueError(f"Invalid tmax '{tmax}'. tmax must be an integer or 'inf'.")
        if tmax == 'inf':
            tmax = float('inf')
        # Validate tmin is less than or equal to tmax
        if not isinstance(tmin, int) or tmin > tmax:
            raise ValueError(f"Invalid interval with tmin {tmin} and tmax {tmax}. tmin must be an integer and tmin <= tmax.")
        self.tmin = tmin
        self.tmax = tmax
    def add(self, i):
        new_tmin = self.tmin + i
        # Handle infinity case
        if self.tmax == float('inf'):
            new_tmax = float('inf')
        else:
            new_tmax = self.tmax + i
        return Interval(new_tmin, new_tmax)
    def __repr__(self):
        tmax_display = '∞' if self.tmax == float('inf') else self.tmax
        return f"[{self.tmin}, {tmax_display}]"

class IntervalSet:
    def __init__(self, intervals):
        self.intervals = intervals
    def max_value(self):
        # Extracts the tmax from each interval and finds the maximum
        max_val = max(interval.tmax for interval in self.intervals)
        return max_val if max_val != float('inf') else '∞'
    def __repr__(self):
        return f"{{{', '.join(map(str, self.intervals))}}}"
    def add(self, i):
        # Add a value to all intervals in the set and return a new IntervalSet
        new_intervals = [interval.add(i) for interval in self.intervals]
        return IntervalSet(new_intervals)    

class Action:
    def __init__(self, action):
        self.action = action
    def __repr__(self):
        return self.action

class NotOperation:
    __match_args__ = ("operand",)
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"Not({self.operand})"

    def add(self, i):
        # Apply 'add' recursively to the operand if applicable
        if hasattr(self.operand, 'add'):
            return NotOperation(self.operand.add(i))
        return self

    def count_obligations(self):
        # Use the negate function to determine obligations in the negated form
        negated_formula = negate(self)
        return negated_formula.count_obligations() if hasattr(negated_formula, 'count_obligations') else 0

    def get_alphabet(self):
        # Delegate alphabet retrieval to the operand
        return self.operand.get_alphabet() if hasattr(self.operand, 'get_alphabet') else []

class Norm:
    def __init__(self, norm_type, interval_set, action):
        if norm_type not in {'O', 'F'}:
            raise ValueError(f"Invalid norm_type '{norm_type}'. Must be 'O' for Obligation or 'F' for Prohibition.")
        self.norm_type = norm_type
        self.interval_set = interval_set
        self.action = action
    def add(self, i):
        # Add a value to the intervals in the set and return a new Norm object
        new_interval_set = self.interval_set.add(i)
        return Norm(self.norm_type, new_interval_set, self.action)    
    def __repr__(self):
        return f"{self.norm_type} {self.interval_set} {self.action}"

class BinaryOperation:
    def __init__(self, left, operator, right):
        if operator not in {';', '||','&','>>'}:
            raise ValueError(f"Invalid operator '{operator}'. Operator must be ';' or '&' or '||' or '>>'.")
        self.left = left
        self.operator = operator
        self.right = right
    def add(self, i):
        new_left = self.left.add(i) if hasattr(self.left, 'add') else self.left + i
        new_right = self.right.add(i) if hasattr(self.right, 'add') else self.right + i
        return BinaryOperation(new_left, self.operator, new_right)
    def __repr__(self):
        return f"({self.left} {self.operator} {self.right})"
    
    def count_obligations(self):
        # Recursively count the number of obligations in the binary operation
        if isinstance(self.left, Norm) and self.left.norm_type == 'O':
            count_left = 1
        elif hasattr(self.left, 'count_obligations'):
            count_left = self.left.count_obligations()
        else:
            count_left = 0

        if isinstance(self.right, Norm) and self.right.norm_type == 'O':
            count_right = 1
        elif hasattr(self.right, 'count_obligations'):
            count_right = self.right.count_obligations()
        else:
            count_right = 0

        return count_left + count_right   

def negate(formula:BinaryOperation)-> BinaryOperation:
    match formula:
        case Norm(norm_type="O", action=action, interval_set=interval_set):
            return  Norm(norm_type="F", action=action, interval_set=interval_set)
        case Norm(norm_type="F", action=action, interval_set=interval_set):
            return  Norm(norm_type="O", action=action, interval_set=interval_set)
        case NotOperation(operand):
            print("Double Negation on:", operand)
            return operand 
        case BinaryOperation(left=left, operator=op, right=right):
                leftn=negate(left)
                rightn=negate(right)
                match op:
                    case("&"):
                        return BinaryOperation(leftn, "||", rightn)
                    case("||"):
                        return  BinaryOperation(leftn, "&", rightn)
                    case(";"):
                        return  BinaryOperation(leftn, "||", BinaryOperation(left, ";",rightn))
                    case(">>"):
                        return  BinaryOperation(leftn, ";", rightn)
                        
class LabeledFormula:
    def __init__(self, formula, label):
        self.formula = formula
        self.label = label

    def __repr__(self):
        return f"{self.formula} - Label: {self.label}"                    
def decompose_reparation(formula, path_label=""):
    if isinstance(formula, BinaryOperation):
        if formula.operator == '>>':
            # Decompose the left and right parts
            left_parts = decompose_reparation(formula.left, path_label)
            right_parts = decompose_reparation(formula.right, path_label)
            combined = []
            for left_part in left_parts:
                # Label for direct path includes the formula and 'no reparation'
                direct_label = f"no reparation + {left_part.formula}"
                combined.append(LabeledFormula(left_part.formula, direct_label))

                # Create paths with negation and include specific reparation label
                for right_part in right_parts:
                    combined_formula = BinaryOperation(negate(left_part.formula), ';', right_part.formula)
                    negation_label = f"reparation + {combined_formula}"
                    combined.append(LabeledFormula(combined_formula, negation_label))
            return combined
        else:
            # Recursively apply to both sides and combine results based on the operator
            left_parts = decompose_reparation(formula.left, path_label)
            right_parts = decompose_reparation(formula.right, path_label)
            results = []
            for left in left_parts:
                for right in right_parts:
                    combined_formula = BinaryOperation(left.formula, formula.operator, right.formula)
                    results.append(LabeledFormula(combined_formula, left.label + " and " + right.label))
            return results
    else:
        # Base case: return the formula itself with an initial label indicating no reparation
        initial_label = f"no reparation + {formula}"
        return [LabeledFormula(formula, initial_label)]
                       
def count_obligations(binary_op):
    if isinstance(binary_op, Norm):
        return 1 if binary_op.norm_type == 'O' else 0
    if isinstance(binary_op, NotOperation):
        return count_obligations(negate(binary_op.operand))
    elif isinstance(binary_op, BinaryOperation):
        left_count = count_obligations(binary_op.left)
        right_count = count_obligations(binary_op.right)
        return left_count + right_count
    else:
        return 0
    
def get_alphabet(binary_op) -> list[str]:
    def recursive_get_alphabet(op) -> set:
        if isinstance(op, Norm):
            return {op.action}  
        elif isinstance(op, BinaryOperation):
            left_alphabet = recursive_get_alphabet(op.left)
            right_alphabet = recursive_get_alphabet(op.right)
            return left_alphabet.union(right_alphabet)  # Union of sets merges them without duplicates
        else:
            return set()
    # Convert the set of actions to a list before returning
    return list(recursive_get_alphabet(binary_op))

def rewrite_rep(formula):
   match formula:
       case(BinaryOperation(left=left,operator=">>",right= right)):
           return BinaryOperation(left, "||", BinaryOperation(negate(left), ";", right))
def print_actions(self):
    actions = self.get_actions()
    for action in actions:
        print(action)
# Example usage of the AST classes
if __name__ == "__main__":
    # Define some actions
    action_a = Action("a")

    # Define some intervals
    interval1 = Interval(1, 3)
    interval2 = Interval(5, float('inf'))

    # Create interval sets
    interval_set1 = IntervalSet([interval1, interval2])

    # Create norms
    obligation = Norm("O", interval_set1, action_a)
    prohibition = Norm("F", interval_set1, action_a)

    # Create binary operations
    conjunction = BinaryOperation(obligation, '&', prohibition)
    disjunction = BinaryOperation(obligation, '||', prohibition)
    sequence =  BinaryOperation(obligation, ';', prohibition)
    reparation= BinaryOperation(obligation, '>>', prohibition)
    mixed    = BinaryOperation(conjunction ,'&',sequence)
    mixed2  = BinaryOperation(reparation ,'||',BinaryOperation(sequence, ';',reparation)) 

    # # Print the constructed expressions
    # print(obligation)
    # print(negate(obligation))# Output: O {[1, 3], [5, ∞]} a
    # print("second")
    # print(prohibition) 
    # print(negate(prohibition))# Output: F {[1, 3], [5, ∞]} a
    # print("third")
    # print(conjunction)
    # print(negate(conjunction))  # Output: (O {[1, 3], [5, ∞]} a & F {[1, 3], [5, ∞]} a)
    # print("fourth")
    # print(disjunction)
    # print(negate(disjunction))  # Output: (O {[1, 3], [5, ∞]} a || F {[1, 3], [5, ∞]} a)
    # print("fifth")
    # print(sequence)
    # print(negate(sequence))
    # print("sixth")
    # print(mixed)
    # print(negate(mixed))
    # print("reparation")
    # print(reparation)
    # print(rewrite_rep(reparation))
    # #print(negate(reparation))

# print("the formula is:")   
# print(mixed2)

# decomposed_formulas = decompose_reparation(mixed2)
# print("Decomposed Formulas:")
# for formula in decomposed_formulas:  
#     print(formula)
