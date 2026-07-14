# type: ignore
import pytest

from project.datalogprogram import Parameter, Predicate, Rule
from project.relation import Relation
from project.reporter import (
    project_4_report,
    project_5_report,
    query_report,
    rule_report,
)

input_literals_no = (
    Predicate("SK", [Parameter.string("'c'"), Parameter.string("'c'")]),
    Relation(("X", "Y"), set()),
)
expect_literals_no = "SK('c','c')? No"


input_literals_yes = (
    Predicate("SK", [Parameter.string("'b'"), Parameter.string("'c'")]),
    Relation(("X", "Y"), set([("'b'", "'c'")])),
)
expect_literals_yes = "SK('b','c')? Yes(1)"


input_mixed_no = (
    Predicate("SK", [Parameter.id("A"), Parameter.string("'c'")]),
    Relation(("A",), set()),
)
expect_mixed_no = "SK(A,'c')? No"


input_mixed_yes = (
    Predicate("SK", [Parameter.id("A"), Parameter.string("'c'")]),
    Relation(("A",), set([("'a'",), ("'b'",)])),
)
expect_mixed_yes = """SK(A,'c')? Yes(2)
  A='a'
  A='b'"""

input_id_yes = (
    Predicate("SK", [Parameter.id("A"), Parameter.string("B")]),
    Relation(("A", "B"), set([("'a'", "'b'"), ("'a'", "'c'"), ("'b'", "'c'")])),
)
expect_id_yes = """SK(A,B)? Yes(3)
  A='a', B='b'
  A='a', B='c'
  A='b', B='c'"""


@pytest.mark.parametrize(
    argnames=("input", "expect"),
    argvalues=(
        (input_literals_no, expect_literals_no),
        (input_literals_yes, expect_literals_yes),
        (input_mixed_no, expect_mixed_no),
        (input_mixed_yes, expect_mixed_yes),
        (input_id_yes, expect_id_yes),
    ),
    ids=[
        "literals_no",
        "literals_yes",
        "mixed_no",
        "mixed_yes",
        "id_yes",
    ],
)
def test_given_query_reporter_when_str_then_match_expect(input, expect):
    # given
    # input, expect
    query, answer = input

    # when
    answer = query_report(query, answer)

    # then
    assert expect == answer


def test_given_iterator_when_reporting_then_match_expect():
    # given
    answers = [
        input_literals_no,
        input_literals_yes,
        input_mixed_no,
        input_mixed_yes,
        input_id_yes,
    ]
    expect = f"{expect_literals_no}\n{expect_literals_yes}\n{expect_mixed_no}\n{expect_mixed_yes}\n{expect_id_yes}"

    # when
    answer = "\n".join([query_report(i, j) for i, j in answers])

    # then
    assert expect == answer


init_f_tuples = {("'1'", "'2'"), ("'4'", "'3'")}
init_g_tuples = {("'3'", "'2'")}
init_r_tuples = {("'3'", "'5'")}


def test_given_eval_rule_iterator_value_when_rule_report_then_expected():
    # given
    before = Relation(["e", "f"], init_r_tuples)
    rule = Rule(
        Predicate("r", [Parameter.id("E"), Parameter.id("F")]),
        [Predicate("f", [Parameter.id("E"), Parameter.id("F")])],
    )
    after = Relation(["e", "f"], init_r_tuples.union(init_f_tuples))
    expect = """r(E,F) :- f(E,F).
  e='1', f='2'
  e='4', f='3'"""

    # when
    answer = rule_report(before, rule, after)

    # then
    assert expect == answer


def test_given_num_rules_rule_evals_query_evals_when_project_4_report_then_expected():
    # given
    rule_0 = Rule(
        Predicate("r", [Parameter.id("E"), Parameter.id("F")]),
        [Predicate("f", [Parameter.id("E"), Parameter.id("F")])],
    )
    rule_1 = Rule(
        Predicate("g", [Parameter.id("C"), Parameter.id("D")]),
        [
            Predicate("f", [Parameter.id("C"), Parameter.id("X")]),
            Predicate("r", [Parameter.id("X"), Parameter.id("D")]),
        ],
    )
    query_0 = Predicate("g", [Parameter.string("'4'"), Parameter.id("B")])
    query_1 = Predicate("r", [Parameter.id("E"), Parameter.string("'3'")])
    query_2 = Predicate("f", [Parameter.id("A"), Parameter.id("B")])
    query_3 = Predicate("g", [Parameter.id("A"), Parameter.id("B")])
    query_4 = Predicate("r", [Parameter.id("A"), Parameter.id("B")])

    rule_evals = [
        (
            Relation(["e", "f"], init_r_tuples),
            rule_0,
            Relation(["e", "f"], init_r_tuples.union(init_f_tuples)),
        ),
        (
            Relation(["c", "d"], init_g_tuples),
            rule_1,
            Relation(["c", "d"], init_g_tuples.union({("'4'", "'5'")})),
        ),
        (
            Relation(["e", "f"], init_r_tuples.union(init_f_tuples)),
            rule_0,
            Relation(["e", "f"], init_r_tuples.union(init_f_tuples)),
        ),
        (
            Relation(["c", "d"], init_g_tuples.union({("'4'", "'5'")})),
            rule_1,
            Relation(["c", "d"], init_g_tuples.union({("'4'", "'5'")})),
        ),
    ]

    query_evals = [
        (query_0, Relation(["B"], {("'5'",)})),
        (query_1, Relation(["E"], {("'4'",)})),
        (query_2, Relation(["A", "B"], {("'1'", "'2'"), ("'4'", "'3'")})),
        (query_3, Relation(["A", "B"], {("'3'", "'2'"), ("'4'", "'5'")})),
        (
            query_4,
            Relation(["A", "B"], {("'1'", "'2'"), ("'3'", "'5'"), ("'4'", "'3'")}),
        ),
    ]

    expect = """Rule Evaluation
r(E,F) :- f(E,F).
  e='1', f='2'
  e='4', f='3'
g(C,D) :- f(C,X),r(X,D).
  c='4', d='5'
r(E,F) :- f(E,F).
g(C,D) :- f(C,X),r(X,D).

Schemes populated after 2 passes through the Rules.

Query Evaluation
g('4',B)? Yes(1)
  B='5'
r(E,'3')? Yes(1)
  E='4'
f(A,B)? Yes(2)
  A='1', B='2'
  A='4', B='3'
g(A,B)? Yes(2)
  A='3', B='2'
  A='4', B='5'
r(A,B)? Yes(3)
  A='1', B='2'
  A='3', B='5'
  A='4', B='3'"""

    # when
    answer = project_4_report(2, rule_evals, query_evals)

    # then
    assert expect == answer


def test_given_dependency_graph_rule_evals_query_evals_when_project_5_report_then_expected():
    # given
    dependency_graph = {0: [], 1: [2], 2: [0, 1]}
    rule_0 = Rule(
        Predicate("r", [Parameter.id("E"), Parameter.id("F")]),
        [Predicate("f", [Parameter.id("E"), Parameter.id("F")])],
    )
    rule_1 = Rule(
        Predicate("r", [Parameter.id("X"), Parameter.id("Y")]),
        [
            Predicate("g", [Parameter.id("X"), Parameter.id("R")]),
            Predicate("f", [Parameter.id("Y"), Parameter.id("S")]),
        ],
    )
    rule_2 = Rule(
        Predicate("g", [Parameter.id("C"), Parameter.id("D")]),
        [
            Predicate("f", [Parameter.id("C"), Parameter.id("X")]),
            Predicate("r", [Parameter.id("X"), Parameter.id("D")]),
        ],
    )
    query_0 = Predicate("g", [Parameter.string("'4'"), Parameter.id("B")])
    query_1 = Predicate("r", [Parameter.id("E"), Parameter.string("'3'")])
    query_2 = Predicate("f", [Parameter.id("A"), Parameter.id("B")])
    query_3 = Predicate("g", [Parameter.id("A"), Parameter.id("B")])
    query_4 = Predicate("r", [Parameter.id("A"), Parameter.id("B")])

    rule_evals = [
        (
            Relation(["e", "f"], init_r_tuples),
            rule_0,
            Relation(["e", "f"], init_r_tuples.union(init_f_tuples)),
        ),
        (
            Relation(["e", "f"], init_r_tuples.union(init_f_tuples)),
            rule_1,
            Relation(
                ["e", "f"],
                init_r_tuples.union(init_f_tuples).union(
                    {("'3'", "'1'"), ("'3'", "'4'")}
                ),
            ),
        ),
        (
            Relation(["c", "d"], init_g_tuples),
            rule_2,
            Relation(
                ["c", "d"],
                init_g_tuples.union({("'4'", "'1'"), ("'4'", "'4'"), ("'4'", "'5'")}),
            ),
        ),
        (
            Relation(
                ["e", "f"],
                init_r_tuples.union(init_f_tuples).union(
                    {("'3'", "'1'"), ("'3'", "'4'")}
                ),
            ),
            rule_1,
            Relation(
                ["e", "f"],
                init_r_tuples.union(init_f_tuples).union(
                    {("'3'", "'1'"), ("'3'", "'4'"), ("'4'", "'1'"), ("'4'", "'4'")}
                ),
            ),
        ),
        (
            Relation(
                ["c", "d"],
                init_g_tuples.union({("'4'", "'1'"), ("'4'", "'4'"), ("'4'", "'5'")}),
            ),
            rule_2,
            Relation(
                ["c", "d"],
                init_g_tuples.union({("'4'", "'1'"), ("'4'", "'4'"), ("'4'", "'5'")}),
            ),
        ),
        (
            Relation(
                ["e", "f"],
                init_r_tuples.union(init_f_tuples).union(
                    {("'3'", "'1'"), ("'3'", "'4'"), ("'4'", "'1'"), ("'4'", "'4'")}
                ),
            ),
            rule_1,
            Relation(
                ["e", "f"],
                init_r_tuples.union(init_f_tuples).union(
                    {("'3'", "'1'"), ("'3'", "'4'"), ("'4'", "'1'"), ("'4'", "'4'")}
                ),
            ),
        ),
        (
            Relation(
                ["c", "d"],
                init_g_tuples.union({("'4'", "'1'"), ("'4'", "'4'"), ("'4'", "'5'")}),
            ),
            rule_2,
            Relation(
                ["c", "d"],
                init_g_tuples.union({("'4'", "'1'"), ("'4'", "'4'"), ("'4'", "'5'")}),
            ),
        ),
    ]

    query_evals = [
        (query_0, Relation(["B"], {("'1'",), ("'4'",), ("'5'",)})),
        (query_1, Relation(["E"], {("'4'",)})),
        (query_2, Relation(["A", "B"], {("'1'", "'2'"), ("'4'", "'3'")})),
        (
            query_3,
            Relation(
                ["A", "B"],
                {("'3'", "'2'"), ("'4'", "'1'"), ("'4'", "'4'"), ("'4'", "'5'")},
            ),
        ),
        (
            query_4,
            Relation(
                ["A", "B"],
                {
                    ("'1'", "'2'"),
                    ("'3'", "'1'"),
                    ("'3'", "'4'"),
                    ("'3'", "'5'"),
                    ("'4'", "'1'"),
                    ("'4'", "'3'"),
                    ("'4'", "'4'"),
                },
            ),
        ),
    ]

    expect = """Dependency Graph
R0:
R1:R2
R2:R0,R1

Rule Evaluation
r(E,F) :- f(E,F).
  e='1', f='2'
  e='4', f='3'
r(X,Y) :- g(X,R),f(Y,S).
  e='3', f='1'
  e='3', f='4'
g(C,D) :- f(C,X),r(X,D).
  c='4', d='1'
  c='4', d='4'
  c='4', d='5'
r(X,Y) :- g(X,R),f(Y,S).
  e='4', f='1'
  e='4', f='4'
g(C,D) :- f(C,X),r(X,D).
r(X,Y) :- g(X,R),f(Y,S).
g(C,D) :- f(C,X),r(X,D).

Query Evaluation
g('4',B)? Yes(3)
  B='1'
  B='4'
  B='5'
r(E,'3')? Yes(1)
  E='4'
f(A,B)? Yes(2)
  A='1', B='2'
  A='4', B='3'
g(A,B)? Yes(4)
  A='3', B='2'
  A='4', B='1'
  A='4', B='4'
  A='4', B='5'
r(A,B)? Yes(7)
  A='1', B='2'
  A='3', B='1'
  A='3', B='4'
  A='3', B='5'
  A='4', B='1'
  A='4', B='3'
  A='4', B='4'"""

    # when
    answer = project_5_report(dependency_graph, rule_evals, query_evals)

    # then
    assert expect == answer
