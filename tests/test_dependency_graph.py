# type: ignore
"""Tests for the dependency graph and SCC computation"""

from project.datalogprogram import DatalogProgram, Parameter, Predicate, Rule
from project.interpreter import Interpreter

######################################################
##### TEST INTERPRETER GET_RULE_DEPENDENCY_GRAPH #####
######################################################


def test_get_rule_dependency_graph_simple_cycle():
    # given
    schemes = [Predicate("p", [Parameter.id("A")])]
    facts = []
    rules = [
        Rule(
            Predicate("p", [Parameter.id("X")]),
            [Predicate("p", [Parameter.id("X")])],
        )
    ]
    queries = []
    program = DatalogProgram(schemes, facts, rules, queries)
    interpreter = Interpreter(program)

    # when
    graph = interpreter.get_rule_dependency_graph()

    # then
    expected_graph = {0: [0]}  # rule 0 depends on itself
    assert graph == expected_graph


def test_get_rule_dependency_graph_double():
    # given
    schemes = [
        Predicate("A", [Parameter.id("B")]),
        Predicate("B", [Parameter.id("C")]),
        Predicate("C", [Parameter.id("X")]),
    ]
    facts = []
    rules = [
        Rule(
            Predicate("A", [Parameter.id("a")]),
            [Predicate("B", [Parameter.id("b")])],
        ),
        Rule(
            Predicate("B", [Parameter.id("b")]),
            [Predicate("C", [Parameter.id("c")])],
        ),
        Rule(
            Predicate("C", [Parameter.id("c")]),
            [Predicate("X", [Parameter.id("x")])],
        ),
    ]
    queries = []
    program = DatalogProgram(schemes, facts, rules, queries)
    interpreter = Interpreter(program)

    # when
    graph = interpreter.get_rule_dependency_graph()

    # then
    expected_graph = {0: [1], 1: [2], 2: []}
    assert graph == expected_graph


def test_get_rule_dependency_graph_no_dependencies():
    # given
    schemes = [Predicate("p", [Parameter.id("A")]), Predicate("q", [Parameter.id("B")])]
    facts = []
    rules = [
        Rule(
            Predicate("p", [Parameter.id("X")]),
            [Predicate("q", [Parameter.id("Y")])],
        ),
        Rule(
            Predicate("w", [Parameter.id("W")]),
            [Predicate("r", [Parameter.id("Z")])],
        ),
    ]
    queries = []
    program = DatalogProgram(schemes, facts, rules, queries)
    interpreter = Interpreter(program)

    # when
    graph = interpreter.get_rule_dependency_graph()

    # then
    expected_graph = {0: [], 1: []}  # no dependencies between rules
    assert graph == expected_graph


def test_get_rule_dependency_graph_complex():
    # given
    schemes = [
        Predicate("A", [Parameter.id("B")]),
        Predicate("B", [Parameter.id("C")]),
        Predicate("C", [Parameter.id("X")]),
        Predicate("D", [Parameter.id("Y")]),
    ]
    facts = []
    rules = [
        Rule(
            Predicate("A", [Parameter.id("a")]),
            [Predicate("B", [Parameter.id("b")])],
        ),
        Rule(
            Predicate("B", [Parameter.id("b")]),
            [Predicate("C", [Parameter.id("c")])],
        ),
        Rule(
            Predicate("C", [Parameter.id("c")]),
            [Predicate("A", [Parameter.id("a")]), Predicate("D", [Parameter.id("d")])],
        ),
        Rule(
            Predicate("D", [Parameter.id("d")]),
            [Predicate("B", [Parameter.id("b")])],
        ),
    ]
    queries = []
    program = DatalogProgram(schemes, facts, rules, queries)
    interpreter = Interpreter(program)

    # when
    graph = interpreter.get_rule_dependency_graph()

    # then
    expected_graph = {
        0: [1],  # Rule 0 depends on Rule 1
        1: [2],  # Rule 1 depends on Rule 2
        2: [0, 3],  # Rule 2 depends on Rule 0 and Rule 3
        3: [1],  # Rule 3 depends on Rule 1
    }
    assert graph == expected_graph


######################################################
######### TEST INTERPRETER GET_REVERSE_GRAPH #########
######################################################


def test_get_reverse_graph_simple_cycle():
    # given
    schemes = [Predicate("p", [Parameter.id("A")])]
    facts = []
    rules = []
    queries = []
    program = DatalogProgram(schemes, facts, rules, queries)
    interpreter = Interpreter(program)
    graph = {0: [0]}  # rule 0 depends on itself

    # when
    reverse_graph = interpreter.get_reverse_graph(graph)

    # then
    expected_reverse_graph = {0: [0]}  # rule 0 depends on itself
    assert reverse_graph == expected_reverse_graph


def test_get_reverse_graph_double():
    # given
    schemes = []
    facts = []
    rules = []
    queries = []
    program = DatalogProgram(schemes, facts, rules, queries)
    interpreter = Interpreter(program)
    graph = {0: [1], 1: [2], 2: []}

    # when
    reverse_graph = interpreter.get_reverse_graph(graph)

    # then
    expected_reverse_graph = {0: [], 1: [0], 2: [1]}
    assert reverse_graph == expected_reverse_graph


#####################################################
####### TEST INTERPRETER GET_POSTORDER_VECTOR #######
#####################################################


def test_get_post_order_vector():
    # given
    schemes = []
    facts = []
    rules = []
    queries = []
    program = DatalogProgram(schemes, facts, rules, queries)
    interpreter = Interpreter(program)
    graph = {0: [1], 1: [0], 2: [1], 3: [1]}

    # when
    post_order_vector = interpreter.get_post_order_vector(graph)

    # then
    expected_post_order_vector = [2, 3, 1, 0]
    assert post_order_vector == expected_post_order_vector


def test_get_post_order_vector_2():
    # given
    schemes = []
    facts = []
    rules = []
    queries = []
    program = DatalogProgram(schemes, facts, rules, queries)
    interpreter = Interpreter(program)
    graph = {0: [1, 2], 1: [0, 2], 2: [3, 4], 3: [2], 4: []}

    # when
    post_order_vector = interpreter.get_post_order_vector(graph)

    # then
    expected_post_order_vector = [1, 0, 3, 2, 4]
    assert post_order_vector == expected_post_order_vector


#####################################################
############# TEST INTERPRETER GET_SCCS #############
#####################################################


def test_get_sccs():
    # given
    schemes = []
    facts = []
    rules = []
    queries = []
    program = DatalogProgram(schemes, facts, rules, queries)
    interpreter = Interpreter(program)
    graph = {0: [1], 1: [2], 2: [0, 3], 3: [4], 4: [3, 5], 5: []}

    # when
    sccs = list(interpreter.get_sccs(graph))

    # then
    expected_sccs = [
        [5],
        [3, 4],
        [0, 1, 2],
    ]
    assert sccs == expected_sccs


def test_get_sccs_2():
    # given
    schemes = []
    facts = []
    rules = []
    queries = []
    program = DatalogProgram(schemes, facts, rules, queries)
    interpreter = Interpreter(program)
    graph = {0: [1, 2], 1: [0, 2], 2: [3, 4], 3: [2], 4: []}

    # when
    sccs = list(interpreter.get_sccs(graph))

    # then
    expected_sccs = [
        [4],
        [2, 3],
        [0, 1],
    ]
    assert sccs == expected_sccs
