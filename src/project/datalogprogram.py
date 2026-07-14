"""Representation for a Datalog program.

The module includes abstractions for the `Parameter`, `Predicate`, `Rule`,
and a `DatalogProgram`.
"""

from typing import Any, Literal

ParameterType = Literal["ID", "STRING"]
"""
Parameters can be either an ID naming a part of a relation or a string naming
a literal value.
"""


class Parameter:
    """Parameter class for all predicates.

    There are two types of parameters: ID and STRING. These correspond to their
    token counterparts.

    Attributes:
        value (str): The actual text for the parameter taken from the associated token.
        parameter_type (ParameterType): The type of the parameter: ID or STRING.
    """

    def __init__(self, value: str, parameter_type: ParameterType) -> None:
        self.value = value
        self.parameter_type = parameter_type

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Parameter):
            return False
        return (self.parameter_type == other.parameter_type) and (
            self.value == other.value
        )

    def __repr__(self) -> str:
        return (
            f"Parameter(value={self.value!r}, parameter_type={self.parameter_type!r})"
        )

    def is_id(self) -> bool:
        """True iff it is an ID parameter."""
        return "ID" == self.parameter_type

    def is_string(self) -> bool:
        """True iff it is a STRING parameter."""
        return "STRING" == self.parameter_type

    @staticmethod
    def id(value: str) -> "Parameter":
        """Create an ID parameter with value."""
        return Parameter(value, "ID")

    @staticmethod
    def string(value: str) -> "Parameter":
        """Create a STRING parameter with value."""
        return Parameter(value, "STRING")


class Predicate:
    """Predicate class for all datalog entities.

    The predicate is a general structure that is used for schemes, facts,
    rules, and queries. The only difference is in the type of parameters
    allowed in the predicates where rules and queries allow for
    both the ID and STRING parameters -- the former for parts of a relation
    and the later for literals while schemes only allow for IDs and facts
    only allow for STRINGs.

    Attributes:
        name (str): The name of the predicate.
        parameters (list[Parameter]): The parameter list.
    """

    def __init__(self, name: str, parameters: list[Parameter]) -> None:
        self.name = name
        self.parameters = parameters

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Predicate):
            return False
        return (self.name == other.name) and (self.parameters == other.parameters)

    def __repr__(self) -> str:
        return f"Predicate(name={self.name!r}, parameters={self.parameters!r})"

    def __str__(self) -> str:
        parameters: str = ",".join([i.value for i in self.parameters])
        return f"{self.name}({parameters})"

    def add_parameter(self, parameter: Parameter) -> None:
        """Add a parameter to the predicate.

        Helper function if the `__init__` doesn't provide parameters or a
        complete parameter list.

        Args:
            parameter: The parameter to add.
        """
        self.parameters.append(parameter)


class Rule:
    """Rule class consisting of a head and list of predicates.

    There are two components to a rule: the head predicate and then a list
    of predicates. The head predicate defines the resulting relation. The list
    of predicates define how tuples are generated for the relation.

    Attributes:
        head (Predicate): The head predicate.
        predicates (list[Predicate]): The list of predicates comprising this rule.
    """

    def __init__(self, head: Predicate, predicates: list[Predicate]) -> None:
        self.head = head
        self.predicates = predicates

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Rule):
            return False
        return (self.head == other.head) and (self.predicates == other.predicates)

    def __repr__(self) -> str:
        return f"Rule(head={self.head!r}, predicates={self.predicates!r})"

    def __str__(self) -> str:
        predicates = ",".join([str(i) for i in self.predicates])
        return f"{str(self.head)} :- {predicates}"


class DatalogProgram:
    """Class for a Datalog program.

    The `Datalog` program class holds all the schemes, rules, facts, and
    queries for the program.

    Attributes:
        schemes (list[Predicate]): The list of schemes as predicates.
        facts (list[Predicate]): The list of facts as predicates.
        rules (list[Rule]): The list of rules.
        queries (list[Predicate]): The list of queries as predicates.
    """

    def __init__(
        self,
        schemes: list[Predicate],
        facts: list[Predicate],
        rules: list[Rule],
        queries: list[Predicate],
    ):
        self.schemes = schemes
        self.facts = facts
        self.rules = rules
        self.queries = queries

    def __str__(self) -> str:
        """Returns the string representation of the program."""
        # initialize the output string and domain list
        output_string: str = ""
        domain: list[str] = []

        # add the schemes to the output string
        output_string += f"Schemes({len(self.schemes)}):\n"
        for scheme in self.schemes:
            output_string += f"  {scheme}\n"

        # add the facts to the output string and make the domain list
        output_string += f"Facts({len(self.facts)}):\n"
        for fact in self.facts:
            output_string += f"  {fact}.\n"

        # add the rules to the output string
        output_string += f"Rules({len(self.rules)}):\n"
        for rule in self.rules:
            output_string += f"  {rule}.\n"

        # add the queries to the output string
        output_string += f"Queries({len(self.queries)}):\n"
        for query in self.queries:
            output_string += f"  {query}?\n"

        # make the domain list
        for fact in self.facts:
            for parameter in fact.parameters:
                if parameter.value not in domain:
                    domain.append(parameter.value)

        # add the domain to the output string
        output_string += f"Domain({len(domain)}):"
        for value in sorted(domain):
            output_string += f"\n  {value}"

        return output_string

    def add_scheme(self, scheme: Predicate) -> None:
        """Add a scheme to the list of schemes."""
        self.schemes.append(scheme)

    def add_fact(self, fact: Predicate) -> None:
        """Add a fact to the list of facts."""
        self.facts.append(fact)

    def add_rule(self, rule: Rule) -> None:
        """Add rule to the list of rules."""
        self.rules.append(rule)

    def add_query(self, query: Predicate) -> None:
        """Add a query to the list of queries."""
        self.queries.append(query)
