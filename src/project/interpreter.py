"""Interpreter for Datalog programs.

Provides an interpreter interface for interpreting Datalog
programs using relational algebra.
"""

from copy import deepcopy
from typing import Iterator

from project.datalogprogram import DatalogProgram, Predicate, Rule
from project.relation import Relation


class Interpreter:
    """Interpreter class for Datalog.

    Defines the interface, and a place for the implementation, for interpreting
    Datalog programs. The interpreter must be implemented using relational algebra,
    so new attributes must be added to track the named relations in the Datalog
    program during the lifetime of the interpreter.

    Attributes:
        datalog (DatalogProgram): The Datalog program to interpret.
    """

    def __init__(self, datalog: DatalogProgram) -> None:
        self.datalog = datalog
        self.database: dict[str, Relation] = dict()

    def eval_schemes(self) -> None:
        """Evaluate the schemes in the Datalog program.

        Create, and store in the interpreter, a relation for each scheme
        in the Datalog program. The _name_ of the scheme must be stored
        separate from the relation since the `Relation` type has no name
        attribute.
        """
        for scheme in self.datalog.schemes:
            header = [parameter.value for parameter in scheme.parameters]
            self.database[scheme.name] = Relation(deepcopy(header), set())

    def eval_facts(self) -> None:
        """Evaluate the facts in the Datalog program.

        Create, and store in the appropriate relation belonging to the
        interpreter, a tuple for each fact in the Datalog program.
        """
        for fact in self.datalog.facts:
            tuple_ = tuple(parameter.value for parameter in fact.parameters)
            self.database[fact.name].add_tuple(tuple_)

    def eval_queries(self) -> Iterator[tuple[Predicate, Relation]]:
        """Yield each query and resulting relation from evaluation."

        For each query in the Datalog program, evaluate the query to get a
        resulting relation that is the answer to the query, and then yield
        the resulting `(query, relation)` tuple.

        Returns:
            out (tuple[Predicate, Relation]): An iterator to a tuple where the
            first element is the predicate for the query and the second element
            is the relation for the answer.
        """
        out: list[tuple[Predicate, Relation]] = []
        for query in self.datalog.queries:
            relation = self.database[query.name]
            # select operations
            for index, parameter in enumerate(query.parameters):
                if parameter.is_string():
                    relation = relation.select_eq_lit(
                        self.database[query.name].header[index], parameter.value
                    )
                if parameter.is_id():
                    for index2, parameter in enumerate(query.parameters):
                        if (
                            parameter.is_id()
                            and index2 != index
                            and parameter.value == query.parameters[index].value
                        ):
                            relation = relation.select_eq_col(
                                self.database[query.name].header[index],
                                self.database[query.name].header[index2],
                            )
            project_to: list[str] = []
            rename_to: list[str] = []
            # project and rename columns
            for index, parameter in enumerate(query.parameters):
                if parameter.is_id() and parameter.value not in rename_to:
                    project_to.append(self.database[query.name].header[index])
                    rename_to.append(parameter.value)
            relation = relation.project(project_to)
            relation = relation.rename(rename_to)
            out.append((query, relation))
        return iter(out)

    def eval_rules(self) -> Iterator[tuple[Relation, Rule, Relation]]:
        """Yield each _before_ relation, rule, and _after_ relation from evaluation.

        For each rule in the Datalog program, yield as a tuple the relation associated
        with the rule before evaluating the rule one time, the rule itself, and then
        the resulting relation after evaluating the rule one time. This process
        should repeat until the associated relations stop changing.
        All the generated facts should be stored in the appropriate relation
        in the interpreter.

        For example, given `rule_a` for relation `A`, `rule_b` for
        relation `B`, and that it takes three evaluations to see no change, then
        `eval_rules` should:

            yield((A_0, rule_a, A_1))
            yield((B_0, rule_b, B_1))
            yield((A_1, rule_a, A_2))
            yield((B_1, rule_b, B_2))
            yield((A_2, rule_a, A_3))
            yield((B_2, rule_b, B_3))

        Here `A_0` is the initial relation for `A`, `A_1` is the relation after evaluating
        `rule_a` on `A_0` etc. The same for `B`. The iteration stops because `A_2 == A_3` and
        `B_2 == B_3`.

        Returns:
            out (Iterator[tuple[Relation, Rule, Relation]]): An iterator to a tuple where the
                first element is the relation before rule evaluation, the second element is
                the rule associated with the relation, and the third element is the relation
                resulting from the rule evaluation.
        """
        out: list[tuple[Relation, Rule, Relation]] = []

        while True:
            any_added_in_pass = False

            for rule in self.datalog.rules:
                intermediates: list[Relation] = []
                for predicate in rule.predicates:
                    relation = deepcopy(self.database[predicate.name])

                    # select operations
                    for index, parameter in enumerate(predicate.parameters):
                        if parameter.is_string():
                            relation = relation.select_eq_lit(
                                relation.header[index], parameter.value
                            )
                    for i, p_i in enumerate(predicate.parameters):
                        if not p_i.is_id():
                            continue
                        for j, p_j in enumerate(predicate.parameters):
                            if i == j:
                                continue
                            if p_j.is_id() and p_j.value == p_i.value:
                                relation = relation.select_eq_col(
                                    relation.header[i], relation.header[j]
                                )

                    # project and rename
                    project_to: list[str] = []
                    rename_to: list[str] = []
                    for index, parameter in enumerate(predicate.parameters):
                        if parameter.is_id() and parameter.value not in rename_to:
                            project_to.append(relation.header[index])
                            rename_to.append(parameter.value)

                    relation = relation.project(project_to)
                    relation = relation.rename(rename_to)
                    intermediates.append(relation)

                # join all intermediate relations
                if len(intermediates) == 0:
                    joined = Relation([], set())
                else:
                    joined = intermediates[0]
                    for other in intermediates[1:]:
                        joined = joined.join(other)

                head = rule.head
                head_vars = [p.value for p in head.parameters]

                # take snapshot before update
                before = deepcopy(self.database[head.name])

                # project the columns that appear in the head predicate
                if all(v in joined.header for v in head_vars):
                    produced = joined.project(head_vars)
                else:
                    produced = Relation(head_vars, set())

                # rename to makek union compatible
                target_header = deepcopy(self.database[head.name].header)
                to_add = produced.rename(target_header)

                # union the produced tuples with the existing relation
                unioned = self.database[head.name].union(to_add)

                # detect additions by difference
                diff = unioned.difference(self.database[head.name])
                if len(diff.set_of_tuples) > 0:
                    any_added_in_pass = True

                # commit the unioned relation back into the database
                self.database[head.name] = unioned

                after = deepcopy(self.database[head.name])
                out.append((before, rule, after))

            if not any_added_in_pass:
                break

        return iter(out)

    def eval_rules_optimized(self) -> Iterator[tuple[Relation, Rule, Relation]]:
        """Yield each _before_ relation, rule, and _after_ relation from optimized evaluation.

        This function is the same as the `eval_rules` function only it groups rules by strongly
        connected components (SCC) in the dependency graph from the rules in the Datalog
        program. So given the first SCC is with `rule_a` for relation `A`, `rule_b` for
        relation `B`, that takes three evaluations to see no change, and the second SCC with
        `rule_c for relation C that takes two evaluations to see no change, then
        `eval_rules_opt` should:

            yield((A_0, rule_a, A_1))
            yield((B_0, rule_b, B_1))
            yield((A_1, rule_a, A_2))
            yield((B_1, rule_b, B_2))
            yield((A_2, rule_a, A_3))
            yield((B_2, rule_b, B_3))
            yield((C_0, rule_c, C_1))
            yield((C_1, rule_c, C_2))

        Here `A_0` is the initial relation for `A`, `A_1` is the relation after evaluating
        `rule_a` on `A_0` etc. The same for `B` and `C`. The iteration on the first SCC stops
        because `A_2 == A_3` and `B_2 == B_3`. After the iteration for the second SCC starts
        and stops after two iterations when `C_1 == C_2`.

        Returns:
            out (Iterator[tuple[Relation, Rule, Relation]]): An iterator to a tuple where the
                first element is the relation before rule evaluation, the second element is the
                rule associated with the relation, and the third element is the relation resulting
                from the rule evaluation.
        """
        out: list[tuple[Relation, Rule, Relation]] = []

        # Build a map of rule numbers to rule objects
        rule_idx_to_rule: dict[int, Rule] = {
            i: rule for i, rule in enumerate(self.datalog.rules)
        }

        # Copy rules in database to avoid modifying the original rules
        _rules = deepcopy(self.datalog.rules)

        # get the dependency graph
        rule_graph = self.get_rule_dependency_graph()
        sccs = self.get_sccs(rule_graph)
        for scc in sccs:
            _rule_list = [rule_idx_to_rule[i] for i in scc]

            # eval rules only once if it's a single rule unless has self-dependency
            if len(_rule_list) == 1:
                idx = scc[0]
                # if the rule depends on itself
                if idx in rule_graph.get(idx, []):
                    # evaluate this single-rule SCC until fixed point
                    self.datalog.rules = _rule_list
                    out.extend(self.eval_rules())
                    continue

                rule = _rule_list[0]
                intermediates: list[Relation] = []
                for predicate in rule.predicates:
                    relation = deepcopy(self.database[predicate.name])

                    # select operations
                    for index, parameter in enumerate(predicate.parameters):
                        if parameter.is_string():
                            relation = relation.select_eq_lit(
                                relation.header[index], parameter.value
                            )
                    for i, p_i in enumerate(predicate.parameters):
                        if not p_i.is_id():
                            continue
                        for j, p_j in enumerate(predicate.parameters):
                            if i == j:
                                continue
                            if p_j.is_id() and p_j.value == p_i.value:
                                relation = relation.select_eq_col(
                                    relation.header[i], relation.header[j]
                                )

                    # project and rename
                    project_to: list[str] = []
                    rename_to: list[str] = []
                    for index, parameter in enumerate(predicate.parameters):
                        if parameter.is_id() and parameter.value not in rename_to:
                            project_to.append(relation.header[index])
                            rename_to.append(parameter.value)

                    relation = relation.project(project_to)
                    relation = relation.rename(rename_to)
                    intermediates.append(relation)

                # join all intermediate relations
                if len(intermediates) == 0:
                    joined = Relation([], set())
                else:
                    joined = intermediates[0]
                    for other in intermediates[1:]:
                        joined = joined.join(other)

                head = rule.head
                head_vars = [p.value for p in head.parameters]

                # take snapshot before update
                before = deepcopy(self.database[head.name])

                # project the columns that appear in the head predicate
                if all(v in joined.header for v in head_vars):
                    produced = joined.project(head_vars)
                else:
                    produced = Relation(head_vars, set())

                # rename to makek union compatible
                target_header = deepcopy(self.database[head.name].header)
                to_add = produced.rename(target_header)

                # union the produced tuples with the existing relation
                unioned = self.database[head.name].union(to_add)

                # commit the unioned relation back into the database
                self.database[head.name] = unioned

                after = deepcopy(self.database[head.name])
                out.append((before, rule, after))

            # eval rules multiple times for SCCs with more than one rule
            else:
                self.datalog.rules = _rule_list
                out.extend(self.eval_rules())

        # Restore original rules
        self.datalog.rules = _rules

        return iter(out)

    def get_rule_dependency_graph(self) -> dict[int, list[int]]:
        """Return the rule dependency graph.

        Computes and returns the graph formed by dependencies between rules.
        The graph is used to compute strongly connected components of rules
        for optimized rule evaluation.

        Rules are zero-indexed so the first rule in the Datalog program is `0`,
        the second rules is `1`, etc. A return of `{0 : [0, 1], 1 : [2]}`
        means that `0` has edges to `0` and `1`, and `1` has an edge to `2`.

        Returns:
            out: A map with an entry for each rule and the associated rules connected to it.
        """
        # Build a map from predicate name to list of rule indices that produce that predicate
        head_name_to_rule_idxs: dict[str, list[int]] = {}
        for idx, rule in enumerate(self.datalog.rules):
            head_name = rule.head.name
            head_name_to_rule_idxs.setdefault(head_name, []).append(idx)

        graph: dict[int, list[int]] = {}
        # For each rule, find dependencies by checking each body predicate name
        for idx, rule in enumerate(self.datalog.rules):
            deps: list[int] = []
            for predicate in rule.predicates:
                name = predicate.name
                if name in head_name_to_rule_idxs:
                    for j in head_name_to_rule_idxs[name]:
                        deps.append(j)
            # Deduplicate and produce deterministic ordering (ascending)
            graph[idx] = sorted(set(deps))

        return graph

    def get_reverse_graph(self, graph: dict[int, list[int]]) -> dict[int, list[int]]:
        """
        Reverse all edges in the input dependency graph.
        Returns a new adjacency list where edge directions are reversed.
        """
        # Initialize reverse graph with all nodes present and empty adjacency lists
        reverse_graph: dict[int, list[int]] = {node: [] for node in graph.keys()}

        # For each edge u -> v in the original graph, add edge v -> u in reverse
        for src, dests in graph.items():
            for dst in dests:
                # Ensure destination exists as a node in reverse_graph
                if dst not in reverse_graph:
                    reverse_graph[dst] = []
                # Avoid duplicate entries
                if src not in reverse_graph[dst]:
                    reverse_graph[dst].append(src)

        return reverse_graph

    def get_post_order_vector(self, graph: dict[int, list[int]]) -> list[int]:
        """
        Perform DFS on the graph and return the postorder list.
        Each rule index appears once in the order it finishes.
        """
        # For computing SCCs using Kosaraju's algorithm the tests expect the
        # post-order to be derived from a DFS on the reversed graph. Build the
        # reversed graph and perform a standard DFS to collect finish order.
        rev = self.get_reverse_graph(graph)

        post_order: list[int] = []
        visited: set[int] = set()

        def dfs(node: int) -> None:
            visited.add(node)
            for neighbor in rev.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
            post_order.append(node)

        for node in graph:
            if node not in visited:
                dfs(node)

        return post_order

    def get_sccs(self, graph: dict[int, list[int]]) -> Iterator[list[int]]:
        """
        Identify strongly connected components (SCCs) in the dependency graph.
        Returns an iterator of SCCs, where each SCC is a list of rule indices.
        """
        # Kosaraju's algorithm:
        # 1. Compute postorder on the original graph.
        post_order = self.get_post_order_vector(graph)

        # 2. Reverse the graph.
        self.get_reverse_graph(graph)

        # 3. Do DFS on reversed graph in order of decreasing postorder
        visited: set[int] = set()

        # The tests expect `get_post_order_vector` to produce a postorder
        # derived from a DFS on the reversed graph. Therefore the second pass
        # of Kosaraju's algorithm should perform DFS on the original graph
        # in the order of decreasing finish times. Use `graph` here.
        def dfs_collect(node: int, collection: list[int]) -> None:
            visited.add(node)
            collection.append(node)
            for nbr in graph.get(node, []):
                if nbr not in visited:
                    dfs_collect(nbr, collection)

        # post_order has nodes in the order they finished; we need decreasing finish time
        for node in reversed(post_order):
            if node not in visited:
                comp: list[int] = []
                dfs_collect(node, comp)
                comp.sort()
                yield comp
