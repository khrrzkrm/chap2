from z3 import *
from NTL_Struct import *
from reminder import *

# Define the event datatypefrom z3 import *
import random
from NTL_Struct import Norm, BinaryOperation
Event = Datatype('Event')
Event.declare('mk_event', ('action', StringSort()), ('time_stamp', IntSort()))
Event = Event.create()
Trace = ArraySort(IntSort(), Event)
# Declare the array with fixed length
trace = Array('trace', IntSort(), Event)





def z3_solver_tight(formula:BinaryOperation,number:int,rem:Reminder)-> (z3.Solver,Int,Reminder):
    num_events = number
    remin=reminder_to_z3(rem)
    match formula:
        case Norm(norm_type="O", action=action, interval_set=interval_set):
            sol=Solver()
            x=random.randint(1, 2)
            label='pt'+str(x)+action
            #label= 'j'
            i= Int(label)
            if not formula.interval_set:  # Check if the interval set is empty
                print("No satisfiable trace exists: Empty set of interval on Obligation")  
                sol.add(BoolVal(False))
                return sol
            else:
                event_i= Select(trace, i)
                tarction=Event.action(event_i)
                ttime=Event.time_stamp(event_i)
                timed_constraints= Solver()
                for [t_min,t_max] in formula.interval_set:
                    if (t_max==float('inf')):
                        timed_constraints.add(ttime>=t_min+remin) 
                    else:
                        timed_constraints.add(And(ttime>=t_min+remin,ttime<=t_max+remin ))
            if len(timed_constraints.assertions()) != 1:
                timed_constraints= Or(timed_constraints.assertions())
            else:
                timed_constraints= timed_constraints.assertions()[0]
            clauses = []
            for x in range(0,num_events):
                clauses.append(And(i==x,tarction==action,timed_constraints))
            sol.add(Or(clauses))
            remin = Reminder.arith(If(tarction == formula.action, ttime, IntVal(-1)))
            # if len(sol.assertions()) != 1:
            #     sol=And(Or(sol.assertions()))
            # else: 
            #     sol=And(sol.assertions()[0])

        case Norm(norm_type="F", action=action, interval_set=interval_set) if  formula.interval_set:
            print("hero")
            sol=Solver()
            x=random.randint(1, 2)
            label='pt'+str(x)+action
            i= Int(label)
            event_i= Select(trace, i)
            tarction=Event.action(event_i)
            ttime=Event.time_stamp(event_i)
            timed_constraints= Solver()
            clauses=[]
            for [t_min,t_max] in formula.interval_set:
                if (t_max==float('inf')):
                    clauses.append(ttime>=t_min+remin)
                    # timed_constraints.add(ttime>=t_min+remin) 
                else:
                    clauses.append(And(ttime +remin>=t_min,ttime<=t_max+remin))
                    # timed_constraints.add(And(ttime +remin>=t_min,ttime<=t_max+remin ))
            if len(clauses) > 1:
                sol.add(ForAll([i], Implies(timed_constraints, tarction != action)))
                print("wer")
                # sol.add(ForAll([i], Implies(Or(clauses), And(i <= num_events, tarction != action))))
            elif len(clauses)==1:
                timed_constraints,=clauses
                print("we are here")
                sol.add(ForAll([i], Implies(timed_constraints, tarction != action)))
                # sol.add(ForAll([i], Implies(timed_constraints, And(i <= num_events, tarction != action))))
            x,supp=formula.interval_set[-1]
            if supp == float('inf'):
                remin=Reminder.top()
            else:
                v = Reminder.int(supp)
                remin = Reminder.arith(remin + v.value)
                
        case BinaryOperation(left=left, operator=op, right=right):
            sol_l,n,rem_l = z3_solver_tight(left,number,rem)
            if op == "&":
                sol_r,n,rem_r = z3_solver_tight(right,number,rem)
                sol=Solver()
                sol= sol_l
                combine_solvers_and(sol, sol_r)
                remin=Reminder.max(rem_l,rem_r)
            elif op == "||":
                sol_l,n,rem_l = z3_solver_tight(left,number,rem)
                print(rem_l)
                sol=Solver()
                sol_r,n,rem_r = z3_solver_tight(right,number,rem)
                print(rem_r)
                if not rem_l.is_top() and not rem_r.is_top():
                    sol=Solver()
                    sol_r,n,rem_r = z3_solver_tight(right,number,rem)
                    combine_solvers_or(sol, sol_l, sol_r)
                    remin=remin=Reminder.max(rem_r,rem_l)
                elif rem_l.is_top():
                    sol = sol_r
                    remin = rem_r
                elif rem_r.is_top():
                    sol = sol_l
                    remin=rem_l   
        case _:
            print("Unsupported formula type", file=sys.stderr)
    return sol,num_events,remin


def z3_solver(formula:BinaryOperation,number:int,rem:Reminder)-> (z3.Solver,Int,Reminder):
    num_events = number
    remin=reminder_to_z3(rem)
    trace = Const('trace', Trace)
    print(type(formula))
    match formula:
        case Norm(norm_type="O", action=action, interval_set=interval_set):
            sol=Solver()
            x=random.randint(1, 2)
            label='pt'+str(x)+action
            #label= 'j'
            i= Int(label)
            if not formula.interval_set:  # Check if the interval set is empty
                print("No satisfiable trace exists: Empty set of interval on Obligation")  
                sol.add(BoolVal(False))
                return sol
            else:
                event_i= Select(trace, i)
                #event_condition = event_i.isValid 
                tarction=Event.action(event_i)
                ttime=Event.time_stamp(event_i)
                timed_constraints= Solver()
                for [t_min,t_max] in formula.interval_set:
                    if (t_max==float('inf')):
                        timed_constraints.add(ttime>=t_min+remin) 
                    else:
                        timed_constraints.add(And(ttime>=t_min+remin,ttime<=t_max+remin ))
            if len(timed_constraints.assertions()) != 1:
                timed_constraints= Or(timed_constraints.assertions())
            else:
                timed_constraints= timed_constraints.assertions()[0]
            clauses = []
            for x in range(0,num_events):
                clauses.append(And(i==x,tarction==action,timed_constraints))
            sol.add(Or(clauses))
            remin = Reminder.arith(If(tarction == formula.action, ttime, IntVal(-1)))

        case Norm(norm_type="F", action=action, interval_set=interval_set) if  formula.interval_set:
            sol=Solver()
            x=random.randint(1, 2)
            label='pt'+str(x)+action
            i= Int(label)
            event_i= Select(trace, i)
            tarction=Event.action(event_i)
            ttime=Event.time_stamp(event_i)
            timed_constraints= Solver()
            clauses=[]
            for [t_min,t_max] in formula.interval_set:
                if (t_max==float('inf')):
                    clauses.append(ttime>=t_min+remin)
                    # timed_constraints.add(ttime>=t_min+remin) 
                else:
                    clauses.append(And(ttime +remin>=t_min,ttime<=t_max+remin))
                    # timed_constraints.add(And(ttime +remin>=t_min,ttime<=t_max+remin ))
            if len(clauses) > 1:
                sol.add(ForAll([i], Implies(Or(clauses), And(i <= num_events, tarction != action))))
            elif len(clauses)==1:
                timed_constraints,=clauses
                sol.add(ForAll([i], Implies(timed_constraints, And(i <= num_events, tarction != action))))
            x,supp=formula.interval_set[-1]
            if supp == float('inf'):
                remin=Reminder.top()
            else:
                v = Reminder.int(supp)
                remin = Reminder.arith(remin + v.value)
              
        case NotOperation(operand):
            # Initialize a new solver
            sol = Solver()
    
            # Process the operand using the solver
            # operand_sol, n, rem = z3_solver(operand, number, rem)
    
            # Negate the assertions of the operand's solver using Z3's Not
            # negated_constraints = [Not(assertion) for assertion in operand_sol.assertions()]
            negated = negate(operand)
            print(negated)
            print(type(negated))
            # Add the negated constraints to the solver
            #sol.add(negated_constraints)
            print(operand)
            return z3_solver(negated, number, rem)
    
    # Return the updated solver, event count, and reminder
            return sol, n, rem  
         
        case BinaryOperation(left=left, operator=op, right=right):
            sol_l,n,rem_l = z3_solver(left,number,rem)
            if op == "&":
                sol_r,n,rem_r = z3_solver(right,number,rem)
                sol=Solver()
                sol= sol_l
                combine_solvers_and(sol, sol_r)
                remin=Reminder.max(rem_l,rem_r)
            elif op == "||":
                sol=Solver()
                sol_r,n,rem_r = z3_solver(right,number,rem)
                remin=Reminder.min(rem_l,rem_r)
                combine_solvers_or(sol, sol_l, sol_r)
                
            elif op == ";":
                sol_t,n,rem_t = z3_solver_tight(left,number,rem)
                if rem_t.is_top():
                    print("formula unsat, sequence with infinite duration prohibition")
                    sys.exit("Stopping execution: Formula unsatisfiable due to 'top' condition.")
                else:
                    sol=Solver()
                    sol_r,n,rem_r = z3_solver(right,number,rem_t)
                    sol=sol_t
                    combine_solvers_and(sol, sol_r)
                    remin= rem_r  
            elif op == ">>":   
                rewrite= rewrite_rep(formula)
                sol,n,remin = z3_solver(rewrite,number,rem)  
            else:
                print("Operator Not handeled yet",file=sys.stderr)     
        case _:
            print("Unsupported formula type a x", file=sys.stderr)
    # num_events= Int('num_events')
    # sol.add(num_events==number)
    # timestamps = [Event.time_stamp(Select(trace, i)) for i in range(number)]
    # sol.add(Distinct(timestamps))
    for i in range(number-1):
        sol.add(Event.time_stamp(Select(trace, i)) >=0)
    for i in range(number - 1):
        sol.add(Event.time_stamp(Select(trace, i)) < Event.time_stamp(Select(trace, i + 1)))
    return sol,num_events,remin
        
def combine_solvers_and(left_solver, right_solver):
    for constraint in right_solver.assertions():
        left_solver.add(constraint)
                     
def combine_solvers_or(main_solver, left_solver, right_solver):
    # Create a new intermediate solver to hold combined OR conditions
    or_solver = Solver()
    lefts= left_solver.assertions()
    rights= right_solver.assertions()
    or_solver.add(Or(And(lefts), And(rights)))
    for constraint in or_solver.assertions():
        main_solver.add(constraint)

def synthetize(formula:BinaryOperation) -> ():
    for x in range(0,(count_obligations(formula)+1)):
        temp_sol=Solver()
        r = Reminder.int(0)
        temp_sol,x,z=z3_solver(formula,x,r)
        for c in temp_sol.assertions(): 
            print(c)
        if temp_sol.check() == sat:
            m = temp_sol.model()
            event0 = Select(trace, 0)
            if(not m.evaluate(Event.action(event0)).as_string()):
               print("empty trace satisfies the formula")
            else:   
                print("Satisfiable trace with minimum length:")
                print(x)
                for i in range(x):
                    event = Select(trace, i)
                    action = m.evaluate(Event.action(event)).as_string()
                    time_stamp = m.evaluate(Event.time_stamp(event)).as_long()
                    print(f"Event {i}: Action = {action}, Time Stamp = {time_stamp}")
            return
        else:
            temp_sol.reset()
            print("adding one more")
            
    if temp_sol.check() == unsat:
        core=temp_sol.unsat_core()
        print(type(core))
        for c in core:
            print(len(c))
    print("No satisfiable trace exists.")
    
def multisynthetize(formula:BinaryOperation) -> ():
    print(formula)
    for x in decompose_reparation(formula):
        print(x.label)
        synthetize(x.formula)
        
       