# type: ignore

from project.datalogprogram import DatalogProgram, Parameter, Predicate, Rule
from project.interpreter import Interpreter

schemes = [
    Predicate(
        "student",
        [Parameter.id("N"), Parameter.id("I"), Parameter.id("A"), Parameter.id("M")],
    ),
    Predicate("WhoMajor", [Parameter.id("N"), Parameter.id("M")]),
]
facts = [
    Predicate(
        "student",
        [
            Parameter.string("'Roosevelt'"),
            Parameter.string("'51'"),
            Parameter.string("'10 Main'"),
            Parameter.string("'Econ'"),
        ],
    ),
    Predicate(
        "student",
        [
            Parameter.string("'Reagan'"),
            Parameter.string("'52'"),
            Parameter.string("'11 Maple'"),
            Parameter.string("'Econ'"),
        ],
    ),
    Predicate(
        "student",
        [
            Parameter.string("'G.W.Bush'"),
            Parameter.string("'53'"),
            Parameter.string("'12 Ashton'"),
            Parameter.string("'AgriSci'"),
        ],
    ),
    Predicate(
        "student",
        [
            Parameter.string("'Clinton'"),
            Parameter.string("'54'"),
            Parameter.string("''"),
            Parameter.string("'Lying'"),
        ],
    ),
]
rules = []
queries = [
    Predicate(
        "WhoMajor",
        [
            Parameter.string("'Roosevelt'"),
            Parameter.id("N"),
        ],
    ),
    Predicate(
        "WhoMajor",
        [
            Parameter.id("M"),
            Parameter.string("'Econ'"),
        ],
    ),
    Predicate(
        "WhoMajor",
        [
            Parameter.string("'George Washington'"),
            Parameter.string("'PoliSci'"),
        ],
    ),
    Predicate(
        "WhoMajor",
        [
            Parameter.string("'Abraham Lincoln'"),
            Parameter.string("'Law'"),
        ],
    ),
    Predicate(
        "student",
        [
            Parameter.string("'John Adams'"),
            Parameter.id("I"),
            Parameter.id("A"),
            Parameter.id("M"),
        ],
    ),
]
program = DatalogProgram(schemes, facts, rules, queries)
expected_relation_tuples = {
    ("'Roosevelt'", "'51'", "'10 Main'", "'Econ'"),
    ("'Reagan'", "'52'", "'11 Maple'", "'Econ'"),
    ("'G.W.Bush'", "'53'", "'12 Ashton'", "'AgriSci'"),
    ("'Clinton'", "'54'", "''", "'Lying'"),
}


def test_interpreter_eval_schemes_and_facts():
    # given
    interpreter = Interpreter(program)

    # when
    interpreter.eval_schemes()
    interpreter.eval_facts()

    # then
    assert len(interpreter.database) == 2
    assert "student" in interpreter.database
    assert "WhoMajor" in interpreter.database
    assert interpreter.database["student"].set_of_tuples == expected_relation_tuples
    assert len(interpreter.database["WhoMajor"].set_of_tuples) == 0


############################
#### TEST EVAL_RULES #####
############################
def test_eval_rules_single_step_isolated():
    """Test a single evaluation step from eval_rules without running to fixpoint.

    Program:
        Schemes: p(A), q(A)
        Facts: p('a')
        Rule: q(X) :- p(X)

    The generator returned by `eval_rules()` should yield a triple where the
    `before` relation for `q` is empty and the `after` relation contains the
    newly derived tuple `('a',)`. The interpreter's database should also be
    updated with the new tuple after the yielded evaluation.
    """
    schemes = [
        Predicate("p", [Parameter.id("A")]),
        Predicate("q", [Parameter.id("A")]),
    ]
    facts = [Predicate("p", [Parameter.string("a")])]
    rules = [
        Rule(
            Predicate("q", [Parameter.id("X")]),
            [Predicate("p", [Parameter.id("X")])],
        )
    ]

    prog = DatalogProgram(schemes, facts, rules, [])
    interp = Interpreter(prog)
    interp.eval_schemes()
    interp.eval_facts()

    gen = interp.eval_rules()
    # Only inspect the first yielded evaluation (do not exhaust to fixpoint)
    before_rel, rule_obj, after_rel = next(gen)

    # before relation for q should be empty
    assert before_rel.set_of_tuples == set()

    # the rule yielded should be the one we created
    assert rule_obj == rules[0]

    # after relation should contain the derived tuple and interpreter DB updated
    assert after_rel.set_of_tuples == {("a",)}
    assert interp.database["q"].set_of_tuples == {("a",)}


def test_eval_rules_hw_case_1():
    """Test Goal: Ensure the algorithm handles rules with only one body predicate
    and that projection removes unused attributes and reorders columns if needed.

    Program:
        Schemes: snap(S,N,A,P), address(P,A)
        Facts: snap("123", "bob", "123 brigham square", "555-1234")
        Rule: address(P,A) :- snap(S,N,A,P)
    """
    schemes = [
        Predicate(
            "snap",
            [
                Parameter.id("S"),
                Parameter.id("N"),
                Parameter.id("A"),
                Parameter.id("P"),
            ],
        ),
        Predicate("address", [Parameter.id("P"), Parameter.id("A")]),
    ]
    facts = [
        Predicate(
            "snap",
            [
                Parameter.string("123"),
                Parameter.string("bob"),
                Parameter.string("123 brigham square"),
                Parameter.string("555-1234"),
            ],
        )
    ]
    rules = [
        Rule(
            Predicate("address", [Parameter.id("P"), Parameter.id("A")]),
            [
                Predicate(
                    "snap",
                    [
                        Parameter.id("S"),
                        Parameter.id("N"),
                        Parameter.id("A"),
                        Parameter.id("P"),
                    ],
                )
            ],
        )
    ]
    queries = []

    prog = DatalogProgram(schemes, facts, rules, queries)
    interp = Interpreter(prog)

    interp.eval_schemes()
    interp.eval_facts()
    interp.eval_queries()

    before, rule_object, after = next(interp.eval_rules())

    assert before.set_of_tuples == set()
    assert rule_object == rules[0]
    assert after.set_of_tuples == {("555-1234", "123 brigham square")}
    assert interp.database["address"].set_of_tuples == {
        ("555-1234", "123 brigham square")
    }


def test_eval_rules_hw_case_2():
    """Test Goal: Confirm that the natural join correctly matches tuples on the
    shared variable (S) and merges the resulting attributes.
    Program:
        Schemes: snap(S,N,A,P), cn(C,N), csg(C,S,G)
        Facts: snap("123", "bob", "123 brigham square", "555-1234"),
               csg("CS111", "123", "A")
        Rule: cn(C, N) :- snap(S, N, A, P), csg(C, S, G)
    """
    schemes = [
        Predicate(
            "snap",
            [
                Parameter.id("S"),
                Parameter.id("N"),
                Parameter.id("A"),
                Parameter.id("P"),
            ],
        ),
        Predicate("cn", [Parameter.id("C"), Parameter.id("N")]),
        Predicate("csg", [Parameter.id("C"), Parameter.id("S"), Parameter.id("G")]),
    ]
    facts = [
        Predicate(
            "snap",
            [
                Parameter.string("123"),
                Parameter.string("bob"),
                Parameter.string("123 brigham square"),
                Parameter.string("555-1234"),
            ],
        ),
        Predicate(
            "csg",
            [Parameter.string("CS111"), Parameter.string("123"), Parameter.string("A")],
        ),
    ]
    rules = [
        Rule(
            Predicate("cn", [Parameter.id("C"), Parameter.id("N")]),
            [
                Predicate(
                    "snap",
                    [
                        Parameter.id("S"),
                        Parameter.id("N"),
                        Parameter.id("A"),
                        Parameter.id("P"),
                    ],
                ),
                Predicate(
                    "csg", [Parameter.id("C"), Parameter.id("S"), Parameter.id("G")]
                ),
            ],
        )
    ]
    queries = []

    prog = DatalogProgram(schemes, facts, rules, queries)
    interp = Interpreter(prog)

    interp.eval_schemes()
    interp.eval_facts()
    interp.eval_queries()

    before, rule_object, after = next(interp.eval_rules())

    assert before.set_of_tuples == set()
    assert rule_object == rules[0]
    assert after.set_of_tuples == {("CS111", "bob")}
    assert interp.database["cn"].set_of_tuples == {("CS111", "bob")}


def test_eval_rules_hw_case_3():
    """Test Goal: Ensure that the interpreter performs a selection
    (select_eq_lit) before projecting and renaming.

    Program:
        Schemes: snap(S,N,A,P), phone(N,P)
        Facts: snap("123", "bob", "123 brigham square", "555-1234"),
               snap("234", "joe", "234 brigham square", "444-1234")
        Rule: phone(N, P) :- snap(S, N, A, '555-1234')
    """
    schemes = [
        Predicate(
            "snap",
            [
                Parameter.id("S"),
                Parameter.id("N"),
                Parameter.id("A"),
                Parameter.id("P"),
            ],
        ),
        Predicate("cn", [Parameter.id("C"), Parameter.id("N")]),
        Predicate("phone", [Parameter.id("N"), Parameter.id("P")]),
    ]
    facts = [
        Predicate(
            "snap",
            [
                Parameter.string("123"),
                Parameter.string("bob"),
                Parameter.string("123 brigham square"),
                Parameter.string("555-1234"),
            ],
        ),
    ]
    rules = [
        Rule(
            Predicate("phone", [Parameter.id("N"), Parameter.id("P")]),
            [
                Predicate(
                    "snap",
                    [
                        Parameter.id("S"),
                        Parameter.id("N"),
                        Parameter.id("A"),
                        Parameter.id("P"),
                    ],
                )
            ],
        )
    ]
    queries = []

    prog = DatalogProgram(schemes, facts, rules, queries)
    interp = Interpreter(prog)

    interp.eval_schemes()
    interp.eval_facts()
    interp.eval_queries()

    before, rule_object, after = next(interp.eval_rules())

    assert before.set_of_tuples == set()
    assert rule_object == rules[0]
    assert after.set_of_tuples == {("bob", "555-1234")}
    assert interp.database["phone"].set_of_tuples == {("bob", "555-1234")}


def test_eval_rules_hw_case_4():
    """Test Goal: Verify that projection removes unnecessary attributes
    (like C) while preserving the correct column order.

    Program:
        Schemes: students(S,G), csg(C,S,G)
        Facts: csg("CS111", "123", "A")
        Rule: phone(N, P) :- snap(S, N, A, '555-1234')
    """
    schemes = [
        Predicate("students", [Parameter.id("S"), Parameter.id("G")]),
        Predicate("csg", [Parameter.id("C"), Parameter.id("S"), Parameter.id("G")]),
    ]
    facts = [
        Predicate(
            "csg",
            [Parameter.string("CS111"), Parameter.string("123"), Parameter.string("A")],
        ),
    ]
    rules = [
        Rule(
            Predicate("students", [Parameter.id("S"), Parameter.id("G")]),
            [
                Predicate(
                    "csg", [Parameter.id("C"), Parameter.id("S"), Parameter.id("G")]
                )
            ],
        )
    ]
    queries = []

    prog = DatalogProgram(schemes, facts, rules, queries)
    interp = Interpreter(prog)

    interp.eval_schemes()
    interp.eval_facts()
    interp.eval_queries()

    before, rule_object, after = next(interp.eval_rules())

    assert before.set_of_tuples == set()
    assert rule_object == rules[0]
    assert after.set_of_tuples == {("123", "A")}
    assert interp.database["students"].set_of_tuples == {("123", "A")}


def test_eval_rules_hw_case_5():
    """Test Goal: Ensure that the resulting relation’s columns are
    reordered to match the head predicate, not the body predicate.

    Program:
        Schemes: csg(C, S, G), gs(G, S)
        Facts: csg("CS111", "123", "A")
        Rule:  gs(G, S) :- csg(C, S, G)
    """
    schemes = [
        Predicate("csg", [Parameter.id("C"), Parameter.id("S"), Parameter.id("G")]),
        Predicate("gs", [Parameter.id("G"), Parameter.id("S")]),
    ]
    facts = [
        Predicate(
            "csg",
            [Parameter.string("CS111"), Parameter.string("123"), Parameter.string("A")],
        ),
    ]
    rules = [
        Rule(
            Predicate("gs", [Parameter.id("G"), Parameter.id("S")]),
            [
                Predicate(
                    "csg", [Parameter.id("C"), Parameter.id("S"), Parameter.id("G")]
                )
            ],
        )
    ]
    queries = []

    prog = DatalogProgram(schemes, facts, rules, queries)
    interp = Interpreter(prog)

    interp.eval_schemes()
    interp.eval_facts()
    interp.eval_queries()

    before, rule_object, after = next(interp.eval_rules())

    assert before.set_of_tuples == set()
    assert rule_object == rules[0]
    assert after.set_of_tuples == {("A", "123")}
    assert interp.database["gs"].set_of_tuples == {("A", "123")}


def test_eval_rules_hw_case_6():
    """Test Goal: Ensure that the select operation is performed before the
    join, and that the joined relation correctly merges the filtered tuples.

    Program:
        Schemes: snap(S, N, A, P), csg(C, S, G), cnFilter(C, N)
        Facts: snap("123", "bob", "123 brigham square", "555-1234"),
               snap("234", "joe", "234 brigham square", "444-1234"),
               csg("CS111", "123", "A"),
               csg("CS110", "234", "B")
        Rule:  cnFilter(C, N) :- snap(S, N, A, '555-1234'), csg(C, S, G).
    """
    schemes = [
        Predicate(
            "snap",
            [
                Parameter.id("S"),
                Parameter.id("N"),
                Parameter.id("A"),
                Parameter.id("P"),
            ],
        ),
        Predicate("csg", [Parameter.id("C"), Parameter.id("S"), Parameter.id("G")]),
        Predicate("cnFilter", [Parameter.id("C"), Parameter.id("N")]),
    ]
    facts = [
        Predicate(
            "snap",
            [
                Parameter.string("123"),
                Parameter.string("bob"),
                Parameter.string("123 brigham square"),
                Parameter.string("555-1234"),
            ],
        ),
        Predicate(
            "snap",
            [
                Parameter.string("234"),
                Parameter.string("joe"),
                Parameter.string("234 brigham square"),
                Parameter.string("444-1234"),
            ],
        ),
        Predicate(
            "csg",
            [Parameter.string("CS111"), Parameter.string("123"), Parameter.string("A")],
        ),
        Predicate(
            "csg",
            [Parameter.string("CS110"), Parameter.string("234"), Parameter.string("B")],
        ),
    ]
    rules = [
        Rule(
            Predicate("cnFilter", [Parameter.id("C"), Parameter.id("N")]),
            [
                Predicate(
                    "snap",
                    [
                        Parameter.id("S"),
                        Parameter.id("N"),
                        Parameter.id("A"),
                        Parameter.string("555-1234"),
                    ],
                ),
                Predicate(
                    "csg", [Parameter.id("C"), Parameter.id("S"), Parameter.id("G")]
                ),
            ],
        )
    ]
    queries = []

    prog = DatalogProgram(schemes, facts, rules, queries)
    interp = Interpreter(prog)

    interp.eval_schemes()
    interp.eval_facts()
    interp.eval_queries()

    before, rule_object, after = next(interp.eval_rules())

    assert before.set_of_tuples == set()
    assert rule_object == rules[0]
    assert after.set_of_tuples == {("CS111", "bob")}
    assert interp.database["cnFilter"].set_of_tuples == {("CS111", "bob")}
