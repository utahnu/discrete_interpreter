"""Project 5 optimized rule and query interpreter for Datalog programs."""

from sys import argv
from typing import Iterator

from project.datalogprogram import DatalogProgram, Predicate, Rule
from project.interpreter import Interpreter
from project.lexer import lexer
from project.parser import UnexpectedTokenException, parse
from project.relation import Relation
from project.reporter import project_5_report
from project.token import Token


def project(input_string: str) -> str:
    """Interpret queries in the Datalog program input.

    The function creates the lexer and parser to turn the input string into
    a `DatalogProgram` instance. It then uses the interpreter to get the
    answers to each query in the Datalog program. The answers are formatted for output
    matching with an appropriate reporter interface.

    Returns:
        answer (str): The string representing the rule evaluation and the answers for
        each query in the given Datalog program or a parse failure.
    """
    token_iterator: Iterator[Token] = lexer(input_string)
    try:
        datalog_program: DatalogProgram = parse(token_iterator)
        interpreter: Interpreter = Interpreter(datalog_program)
        interpreter.eval_schemes()
        interpreter.eval_facts()
        dependency_graph = interpreter.get_rule_dependency_graph()

        rule_evals: list[tuple[Relation, Rule, Relation]] = [
            i for i in interpreter.eval_rules_optimized()
        ]
        query_evals: list[tuple[Predicate, Relation]] = [
            i for i in interpreter.eval_queries()
        ]
        answer: str = project_5_report(dependency_graph, rule_evals, query_evals)
        return answer
    except UnexpectedTokenException as e:
        return "Failure!\n  " + str(e.token)


def projectcli() -> None:
    """Answer queries in a Datalog program

    `projectcli` is only called from the command line in the integrated terminal.
    This function prints the results of each query in the Datalog program to the terminal.

    Args:
        argv (list[str]): Generated from the command line and needs to name the input file.

    Examples:

    ```
    $ cat prog.txt
    Schemes:
      f(a,b)
      g(c,d)
      r(e,f)

    Facts:
      f('1','2').
      f('4','3').
      g('3','2').
      r('3','5').

    Rules:
      r(E,F):-f(E,F).
      g(C,D):-f(C,X),r(X,D).

    Queries:
      g('4',B)?
      r(E,'3')?
      f(A,B)?
      g(A,B)?
      r(A,B)?

    $ project prog.txt
    Dependency Graph
    R0:
    R1:R0

    Rule Evaluation
    r(E,F) :- f(E,F).
      e='1', f='2'
      e='4', f='3'
    g(C,D) :- f(C,X),r(X,D).
      c='4', d='5'

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
      A='4', B='3'
    ```
    """
    if len(argv) == 2:
        input_file = argv[1]
        with open(input_file, "r") as f:
            input_string = f.read()
            result = project(input_string)
            print(result)
    else:
        print("usage: project <input file>")
