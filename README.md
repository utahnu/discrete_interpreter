# Discrete Datalog Interpreter

An interpreter for Datalog programs implemented in Python. The interpreter parses Datalog source (schemes, facts, rules, and queries), stores relations in memory, evaluates rules using relational-algebra operations, and answers queries. The project includes an optimized rule-evaluation mode that groups rules by strongly connected components (SCCs) of the rule-dependency graph.

## Summary
- **Language:** Python
- **Python requirement:** >= 3.11
- **Package name:** `project` (see `pyproject.toml`)

## Features
- Full Datalog parsing pipeline (`lexer` + `parser`).
- Relational-algebra implementation (`Relation`) with `select`, `project`, `join`, `rename`, `union`, `difference`.
- Rule evaluation until fixed point and an SCC-optimized evaluator.
- Simple CLI entrypoint and a programmatic API.

## Quick Install

Create and activate a virtual environment, then install the package with development extras:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --editable ".[dev]"
```

## Usage

CLI (after install):

```bash
project path/to/program.txt
```

Programmatic:

```python
from project import project
with open('prog.txt') as f:
    output = project(f.read())
    print(output)
```

`project.project(input_string)` returns the textual output produced by the program (dependency graph, rule evaluation trace, and query answers) or a parse failure message.

## Input format

A Datalog program is split into four named sections (order shown is expected):
- `Schemes:` — relation headers using IDs (e.g. `parent(A,B)`).
- `Facts:` — facts are tuples of STRING literals terminated with `.` (e.g. `parent('alice','bob').`).
- `Rules:` — rules have a head and a body separated with `:-` (e.g. `ancestor(X,Y):-parent(X,Y).`).
- `Queries:` — predicates to query ending with `?`.

Example input:

```text
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
```

Expected behavior: the CLI prints the rule dependency graph, rule evaluation trace, and query evaluation results formatted by the reporter.

## Example output (excerpt)

The CLI produces a human-friendly report similar to the example in `src/project/project.py`'s `projectcli()` docstring: a dependency graph, Rule Evaluation blocks, and Query Evaluation blocks with `Yes(n)` counts and bindings.

## Project structure
- `src/project/` — core implementation
  - `datalogprogram.py` — AST-like domain types: `Parameter`, `Predicate`, `Rule`, `DatalogProgram` ([file link](src/project/datalogprogram.py))
  - `interpreter.py` — `Interpreter` class, rule evaluation, SCC optimization ([file link](src/project/interpreter.py))
  - `relation.py` — in-memory relation implementation and relational algebra
  - `parser.py`, `lexer.py`, `token.py` — parsing pipeline
  - `project.py` — public entrypoints: `project()` and `projectcli()` ([file link](src/project/project.py))
- `tests/` — unit tests and resource programs
- `pyproject.toml` — packaging and tool configuration

## Key APIs
- `project.project(input_string: str) -> str` — parse and evaluate a Datalog program text and return formatted output.
- `Interpreter` — main class for evaluation. Important methods:
  - `eval_schemes()` — create empty relations for schemes.
  - `eval_facts()` — populate relations with facts.
  - `eval_rules()` and `eval_rules_optimized()` — evaluate rules, returning iterators that yield `(before_relation, rule, after_relation)` tuples for traceability.
  - `eval_queries()` — evaluate queries and return `(query_predicate, result_relation)` tuples.

## Development & Testing

- Run tests:

```bash
pytest
```

- Type checks:

```bash
mypy src tests
```

- Linting / formatting: configured via `pyproject.toml` (see `ruff`, `pre-commit`).

