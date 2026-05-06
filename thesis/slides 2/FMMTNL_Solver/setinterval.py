from z3 import *

# Define the Event type
Event = Datatype('Event')
Event.declare('mk_event', ('action', StringSort()), ('time_stamp', IntSort()))
Event = Event.create()

# Define the trace as an array of events indexed by integer
Trace = ArraySort(IntSort(), Event)
opt = Optimize()

# Function to parse user input according to specified format
def get_input():
    input_norms = []
    print("Enter your norms in the format 'O/F action {[t1_min,t1_max], [t2_min,t2_max], ...}'. Type 'end' to finish.")
    while True:
        inp = input("Enter norm (or 'end' to finish): ")
        if inp.lower() == "end":
            break
        try:
            op, action, intervals_str = inp.split(' ', 2)
            if op not in ['O', 'F']:
                raise ValueError("Invalid operator. Use 'O' or 'F'.")
            intervals_str = intervals_str.strip()[1:-1]  # Remove outer braces
            intervals = []
            for interval in intervals_str.split('], ['):
                t_min, t_max = map(int, interval.strip('[]').split(','))
                intervals.append((t_min, t_max))
            input_norms.append((op, action, intervals))
        except ValueError as e:
            print("Error in input format:", e)
            continue
    return input_norms

input_norms = get_input()

trace = Const('trace', Trace)
max_index = Int('max_index')
opt.add(max_index >= 0)  # Ensure at least one event exists

# Process norms for multiple intervals
for op, action, intervals in input_norms:
    if op == "O":
        obligation_found = False
        for i in range(2):
            event = Select(trace, i)
            is_action = Event.action(event) == StringVal(action)
            in_time_any = False
            for t_min, t_max in intervals:
                in_time = And(Event.time_stamp(event) >= t_min, Event.time_stamp(event) <= t_max)
                in_time_any = Or(in_time_any, in_time)
            obligation_found = Or(obligation_found, And(is_action, in_time_any))
            opt.add_soft(Implies(is_action, i <= max_index))
        opt.add(obligation_found)
    elif op == "F":
        for i in range(2):
            event = Select(trace, i)
            is_action = Event.action(event) == StringVal(action)
            not_in_time_all = True
            for t_min, t_max in intervals:
                in_time = And(Event.time_stamp(event) >= t_min, Event.time_stamp(event) <= t_max)
                not_in_time_all = And(not_in_time_all, Not(in_time))
            opt.add(Implies(is_action, not_in_time_all))

# Minimize the maximum index used in the trace
opt.minimize(max_index)
for c in opt.assertions():
        print(c)
# Solve and output the trace
if opt.check() == sat:
    m = opt.model()
    highest_index = m.evaluate(max_index).as_long()
    print("Satisfiable trace with minimum length:")
    for i in range(highest_index + 1):
        event = m.evaluate(Select(trace, i))
        action = m.evaluate(Event.action(event)).as_string()
        time_stamp = m.evaluate(Event.time_stamp(event)).as_long()
        if action != "":
            print(f"Event {i}: Action = {action}, Time Stamp = {time_stamp}")
else:
    print("No satisfiable trace exists.")
