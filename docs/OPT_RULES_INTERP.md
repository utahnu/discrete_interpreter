# Optimized Rule Evaluation


Example Input
```
Schemes:
Parent(p,c)
Sibling(a,b)
Ancestor(x,y)

Facts:
Parent('bob','ned').
Parent('jim','bob').
Sibling('sue','ned').

Rules:
Sibling(x,y):-Sibling(y,x).
Ancestor(x,y):-Ancestor(x,z),Parent(z,y).
Ancestor(x,y):-Parent(x,y).

Queries:
Ancestor(x,'ned')?
Sibling('ned','sue')?
```

Expected Output
```
Dependency Graph
R0:R0
R1:R1,R2
R2:

Rule Evaluation
Ancestor(x,y) :- Parent(x,y).
  x='bob', y='ned'
  x='jim', y='bob'
Ancestor(x,y) :- Ancestor(x,z),Parent(z,y).
  x='jim', y='ned'
Ancestor(x,y) :- Ancestor(x,z),Parent(z,y).
Sibling(x,y) :- Sibling(y,x).
  a='ned', b='sue'
Sibling(x,y) :- Sibling(y,x).

Query Evaluation
Ancestor(x,'ned')? Yes(2)
  x='bob'
  x='jim'
Sibling('ned','sue')? Yes(1)
```

The `Rule Evaluation` output is grouped by SCC but is not explicitly delineated in the output. In the example, there are three SCCs:
0. `Ancestor(x,y) :- Parent(x,y).` which is trivial and only needs to be evaluated once.
0. `Ancestor(x,y) :- Ancestor(x,z),Parent(z,y).` requiring two evaluations.
0. `Sibling(x,y) :- Sibling(y,x).` requiring two evaluations.
A _trivial SCC_ is one that has a single rule in it and there is no self-loop on that rule.

## Evaluating Rules

0. Build the dependency graph and the reverse dependency graph.
0. Run DFS-Forest on the reverse dependency graph to get the post-order.
0. Use the post-order for a DFS-Forest on the forward dependency graph to find the strongly connected components (SCCs).
0. Evaluate the rules in each component.

## Dependency Graph

Build the dependency graph for the rules in the Datalog program.

Assign a numeric identifier to each rule starting with zero. Assign the identifiers to the rules in the order the rules appear in the input. Use 0 for the first rule, 1 for the second rule, etc.

When outputting rule identifiers always precede the rule identifier with the letter R. For example, output the first rule as R0, the second rule as R1, etc. The preceding R is for decoration only and is not part of the identifier.

Make a node in the graph for every rule identifier. Don't add the same node to the graph more than once.

Make an edge in the graph for each rule dependency. Add an edge to the graph from node x to node y if the evaluation of x depends on the result of y. Rule A depends on rule B if any of the predicate names in the body of rule A is the same as the predicate name of the head of rule B. Don't add the same edge to the graph more than once.

Note that more than one rule may have the same predicate name in the head. This means that a single name in the body of a rule may cause a dependency on more than one rule.

Note also that a rule may depend on itself.

Consider the following rules as an example:
```
A(X,Y) :- B(X,Y), C(X,Y). # R0
B(X,Y) :- A(X,Y), D(X,Y). # R1
B(X,Y) :- B(Y,X).         # R2
E(X,Y) :- F(X,Y), G(X,Y). # R3
E(X,Y) :- E(X,Y), F(X,Y). # R4
```
The dependency graph as an adjacency list is:
```
R0: R1 R2
R1: R0
R2: R1 R2
R3:
R4: R3 R4
```

## Reverse Dependency Graph
Finding the strongly connected components (SCCs) of the dependency graph allows the rules to be grouped and ordered for improved evaluation. An algorithm for computing the SCCs is found in section 3.4.2 of Algorithms by Dasgupta, C. H. Papadimitriou, and U. V. Vazirani.

The first step of the algorithm is to build the reverse dependency graph. The reverse graph has the same nodes as the original dependency graph. The edges in the reverse graph are the same as the edges in the original graph except the direction of each edge is reversed.

The reverse dependency graph for the example from the previous section as an adjacency list is:
```
R0: R1
R1: R0 R2
R2: R0 R2
R3: R4
R4: R4
```

## DFS Forest
The next step of the SCC algorithm is to run DFS-Forest on the reverse dependency graph to obtain post-order numbers.

Run DFS-Forest on the reverse dependency graph. Create a post-order of node identifiers. When there is a choice of which node to visit next in the DFS-Forest, choose the node identifier that comes first numerically.

The post-order for the example from the previous section is: `R2, R1, R0, R4, R3`

## Finding the SCCs
The post-order from the DFS-Forest on the reverse graph gives the correct order to use for searching for SCCs in the original dependency graph. The order is used in reverse order.

The first SCC is found by running a depth-first search on the original dependency graph starting from the node last in the post-order. Any node visited during the DFS is part of the SCC.

For the example from the previous section, the search starts at node R3 and visits only node R3. The first SCC contains only node R3.

The process is repeated with the other nodes from the end of the post-order to the beginning.

The search for the second SCC starts at node R4 and visits only node R4. The second SCC contains only node R4.

The search for the next SCC starts at node R0 and visits nodes R0, R1, and R2. The SCC contains nodes R0, R1, and R2.

The process attempts to find additional SCCs starting with node R1 and then node R2. Since these nodes have already been visited, additional SCCs are not found.

Note that the visit markers used in the DFS-Forest must not be reset between the searches for each SCC.

## SCC Evaluation
For each SCC found in the previous step, run the rule evaluation process from the previous project on the subset of rules found in the SCC.

Evaluate the SCCs in the order they are found.

If an SCC contains only one rule and that rule does not depend on itself, the rule is only evaluated once.

If an SCC contains more than one rule, or a single rule that depends on itself, repeat the evaluation of the rules in the SCC until the evaluation reaches a fixed point.

When an SCC contains more than one rule, evaluate the rules in the SCC in the numeric order of the rule identifiers.
