# Datalog Rule Interpreter

Here is an example input to the interpreter.

```
Schemes:
  snap(S,N,A,P)
  csg(C,S,G)
  cn(C,N)
  ncg(N,C,G)

Facts:
  snap('12345','C. Brown','12 Apple St.','555-1234').
  snap('22222','P. Patty','56 Grape Blvd','555-9999').
  snap('33333','Snoopy','12 Apple St.','555-1234').
  csg('CS101','12345','A').
  csg('CS101','22222','B').
  csg('CS101','33333','C').
  csg('EE200','12345','B+').
  csg('EE200','22222','B').

Rules:
  cn(c,n) :- snap(S,n,A,P),csg(c,S,G).
  ncg(n,c,g) :- snap(S,n,A,P),csg(c,S,g).

Queries:
  cn('CS101',Name)?
  ncg('Snoopy',Course,Grade)?
```

This results in the following output:

```
Rule Evaluation
cn(c,n) :- snap(S,n,A,P),csg(c,S,G).
  C='CS101', N='C. Brown'
  C='CS101', N='P. Patty'
  C='CS101', N='Snoopy'
  C='EE200', N='C. Brown'
  C='EE200', N='P. Patty'
ncg(n,c,g) :- snap(S,n,A,P),csg(c,S,g).
  N='C. Brown', C='CS101', G='A'
  N='C. Brown', C='EE200', G='B+'
  N='P. Patty', C='CS101', G='B'
  N='P. Patty', C='EE200', G='B'
  N='Snoopy', C='CS101', G='C'
cn(c,n) :- snap(S,n,A,P),csg(c,S,G).
ncg(n,c,g) :- snap(S,n,A,P),csg(c,S,g).

Schemes populated after 2 passes through the Rules.

Query Evaluation
cn('CS101',Name)? Yes(3)
  Name='C. Brown'
  Name='P. Patty'
  Name='Snoopy'
ncg('Snoopy',Course,Grade)? Yes(1)
  Course='CS101', Grade='C'
```

The major steps or each described in their own file:
* [JOIN_ALGORITHM.md](./JOIN_ALGORITHM.md)
* [EVALUATE_RULE_ALGORITHM.md](./EVALUATE_RULE_ALGORITHM.md)
* [FIX_POINT_ALGORITHM.md](./FIX_POINT_ALGORITHM.md)

## Assumptions

We assume the following about the Datalog input:

1. The Datalog program is semantically correct and satisfies all def-use requirements.
1. The head of every rule will only contain variable names. No strings will be given in the head of any rule.
1. No two variable names in a rule head are the same. Each variable in a rule head is unique in that rule head.
1. Every variable name in the head of a rule will appear in at least one predicate in the body (right-hand side) of the rule.