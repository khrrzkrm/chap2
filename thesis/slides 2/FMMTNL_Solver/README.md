# SMT Solving for Formulas in the Flat Monadic Metric Time Normative Logic:

This project's goal is to reason about the satisfiability of formulas in  FMMTNL 
Written in Python and using the Z3 solver, the tool computes a formula in the logic and checks weather it is satisfiable and returns the shortest trace in terms of number of events when it exists.


## Installation
Python 3.11.3 or above.

Z3 and Pyparsing libraries in python:
```
pip install z3-solver
pip install pyparsing

```
## Usage
1- Execute the satisfiability checker
```
python satcheck.py
```
2- Type a valid formula according to the syntax, such as:

```
O open {[0,7],[12,inf]} & (O Load {[3,27]} || F complain {[2,200]})
```

## Syntax :
Norm ::=  O Action IS  , F Action Is , Norm  & Norm, Norm  || Norm, ! Norm

Action ::=  String 

I ::= [Int,Int] , [Int,inf] $~~~~~~~~~~(Interval)$

Is ::= \{I, ..., I\} $~~~~~~~~~~\quad\quad(Interval Set )$

inf ($+\infty$)

&  (Conjunction) 

|| (disjunction)

! (Negation)

## More examples can be found in Examples file:

Paper example:
```
(O dag {[9,16]} || O dap {[9,inf]}) &  F dap {[12,24]} & F dag {[10,14]}
```
Ontic conflict example:
```
O read {[1,2]} & O write {[1,2]} & O erase {[1,2]}
```

Deontic conflict example:
```
O open {[4,6],[12,15]} & F open {[0,20]}
```
2 occurrences of the same action for 2 obligations on the same action:
```
O open {[4,6],[12,15]} & O open {[25,100]}
```

1 occurrence is enough for two obligations:
```
O open {[4,6],[12,15]} & O open {[0,25]}
```

Infinity intervals:
```
O open {[0,inf]} & F open {[2,inf]}
```

 Complex example:
 ```
(O read {[1,2]} || F write {[0,199]} || O erase {[0,8]} ) &  (F read {[0,16]} || O write {[100,250]} || F erase {[0,70]}) & (O read {[15,28]} || O write {[39,50],[78,100]} || O erase {[10,15]})
```


