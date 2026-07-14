# Evaluate Rule Algorithm

Add rule evaluation to the query interpreter from the last project. The major steps of the interpreter are:

1. Process the schemes 
1. Process the facts 
1. Evaluate the rules
1. Evaluate the queries 

Evaluate each rule using relational algebra operations as follows:

1. **Evaluate the predicates on the right-hand side of the rule:**

    For each predicate on the right-hand side of a rule, evaluate the predicate in the same way you evaluated the queries in the last project (using select, project, and rename operations). Each predicate should produce a single relation as an intermediate result. If there are $n$ predicates on the right-hand side of a rule, there should be $n$ intermediate results. If you are careful, you can use the `eval_queries` function you wrote in Project 3 to perform this task.

2. **Join the relations that result:**

    If there are two or more predicates on the right-hand side of a rule, join the intermediate results to form the single result for Step 2. Thus, if $p1$, $p2$, and $p3$ are the intermediate results from Step 1, join them $(p1\ \ \mathtt{|\times|}\ \ p2\ \ \mathtt{|\times|}\ \ p3)$ into a single relation.

    If there is a single predicate on the right hand side of the rule, use the single intermediate result from Step 1 as the result for Step 2.

3. **Project the columns that appear in the head predicate:**

    The predicates in the body of a rule may have variables that are not used in the head of the rule.  Use a project operation on the result from Step 2 to remove the columns that don't appear in the head of the rule and to reorder the columns to match the order in the head.

4. **Reorder the columns of the relation to produce the order in the head predicate:**
    The variables in the head predicate may appear in a different order than the columns of the relation produced in the previous step

5. **Rename the relation to make it union-compatible:**

    Rename the relation that results from Step 3 to make it union compatible with the relation that matches the head of the rule. Rename each attribute in the result from Step 3 to the attribute name found in the corresponding position in the relation that matches the head of the rule.

6. **Union with the relation in the database:**

    Union the result from Step 4 with the relation in the database whose name matches the name of the head of the rule.

Evaluate the rules in the order they are given in the input file.
