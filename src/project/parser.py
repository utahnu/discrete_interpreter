"""Parser for Datalog programs.

Provides the parser and error interface for when parsing fails for Datalog
programs.
"""

from typing import Iterator

from project.datalogprogram import DatalogProgram, Parameter, Predicate, Rule
from project.token import Token, TokenType


class UnexpectedTokenException(Exception):
    """Class for parsing errors.

    A parse error is when the actual token does not have the correct type
    according to the state of the parser. In other words, the parser is
    expecting a specific token type but the actual token at that point does
    not match the expected type.

    Attributes:
        expected_type (TokenType): The type that was expected in the parse.
        token (Token): The actual token that was encountered.
    """

    def __init__(
        self,
        expected_type: TokenType | str,
        token: Token,
        message: str = "A parse error occurred due to an unexpected token",
    ) -> None:
        super().__init__(message)
        self.expected_type = expected_type
        self.token = token


class TokenStream:
    """Class for managing the token iterator from the lexer.

    A `TokenStream` is a wrapper for the `Iterator[Token]` from the lexer that
    provides core functions for parsing -- `match` and `advance` -- along with an
    additional function for checking if the current token has a type that
    belongs to a set of types -- useful for checking FIRST and FOLLOW sets -- and
    a way to get tho value from the current token.

    Attributes:
        token_iterator (Iterator[Token]): A token iterator.
        token (Token): The current token.
    """

    def __init__(self, token_iterator: Iterator[Token]) -> None:
        self._token_iterator = token_iterator
        self.advance()

    def __repr__(self) -> str:
        return f"TokenStream(token={self.token!r}, _token_iterator={self._token_iterator!r})"

    def advance(self) -> None:
        """Advances the iterator and updates the token.

        The last token in the iterator is stuttered meaning that it is repeated
        on every subsequent call.

        **WARNING**: `advance` side-effects the `token` and `token_iterator`.
        This side-effect means that the previous token is gone and cannot be
        recovered. There is no deep-copy for a `TokenStream`, so it's a _use
        once_ object. That is fine for parsing.
        """
        try:
            self.token = next(self._token_iterator)
        except StopIteration:
            pass

    def match(self, expected_type: TokenType) -> None:
        """Return if token matches expected type.

        `match` returns iff the expected type matches the current taken. If
        ever the token type does not match the expected type, it raises an exception
        indicating a match failure. The exception includes the expected token
        type and the token that did not match.

        Args:
            expected_type (TokenType): The expected token type in the stream for a successful match.

        Raises:
            error (UnexpectedTokenException): Error if the type of the current token does not match.
        """
        if self.token.token_type != expected_type:
            raise UnexpectedTokenException(expected_type, self.token)

    def member_of(self, token_types: set[TokenType]) -> bool:
        """Returns true iff the current token type is in the specified type.

        `member_of` is a way to determine if the type of the current token is
        in a set of token types. It is especially useful for checking membership
        in FIRST and FOLLOW sets when implementing a table driven parser.
        The FIRST and FOLLOW sets are used to determine which alternative to use
        in a grammar rule with alternatives.

        Args:
            token_types: A set of token types.

        Returns:
            out: True iff the current token type is in the set of token types.
        """
        return self.token.token_type in token_types

    def value(self) -> str:
        """Return the value attribute of the current token."""
        return self.token.value


##############################################################################
################## functions for each grammar rule ###########################
##############################################################################
def schemeList(token: TokenStream) -> list[Predicate]:
    first_set: set[TokenType] = {"ID"}
    follow_set: set[TokenType] = {"FACTS"}
    _schemelist = []

    if token.member_of(first_set):
        _schemelist.append(scheme(token))
        _schemelist.extend(schemeList(token))
    elif token.member_of(follow_set):
        return _schemelist
    else:
        raise UnexpectedTokenException("ID or FACTS", token.token)
    return _schemelist


def factList(token: TokenStream) -> list[Predicate]:
    first_set: set[TokenType] = {"ID"}
    follow_set: set[TokenType] = {"RULES"}
    _factlist = []

    if token.member_of(first_set):
        _factlist.append(fact(token))
        _factlist.extend(factList(token))
    elif token.member_of(follow_set):
        return _factlist
    else:
        raise UnexpectedTokenException("ID or FACTS", token.token)
    return _factlist


def ruleList(token: TokenStream) -> list[Rule]:
    first_set: set[TokenType] = {"ID"}
    follow_set: set[TokenType] = {"QUERIES"}
    _rulelist = []

    if token.member_of(first_set):
        _rulelist.append(rule(token))
        _rulelist.extend(ruleList(token))
    elif token.member_of(follow_set):
        return _rulelist
    else:
        raise UnexpectedTokenException("ID or QUERIES", token.token)
    return _rulelist


def queryList(token: TokenStream) -> list[Predicate]:
    first_set: set[TokenType] = {"ID"}
    follow_set: set[TokenType] = {"EOF"}
    _querylist = []

    if token.member_of(first_set):
        _querylist.append(query(token))
        _querylist.extend(queryList(token))
    elif token.member_of(follow_set):
        return _querylist
    else:
        raise UnexpectedTokenException("ID or EOF", token.token)
    return _querylist


def scheme(token: TokenStream) -> Predicate:
    token.match("ID")
    head_id = token.value()
    token.advance()
    token.match("LEFT_PAREN")
    token.advance()
    token.match("ID")
    _scheme: Predicate = Predicate(head_id, [Parameter(token.value(), "ID")])
    token.advance()
    _idList = idList(token)
    for id in _idList:
        _scheme.add_parameter(id)
    token.match("RIGHT_PAREN")
    token.advance()
    return _scheme


def fact(token: TokenStream) -> Predicate:
    # first_set = {"ID"}
    token.match("ID")
    head_id = token.value()
    token.advance()
    token.match("LEFT_PAREN")
    token.advance()
    token.match("STRING")
    _fact: Predicate = Predicate(head_id, [Parameter(token.value(), "STRING")])
    token.advance()
    _stringList = stringList(token)
    for string in _stringList:
        _fact.add_parameter(string)
    token.match("RIGHT_PAREN")
    token.advance()
    token.match("PERIOD")
    token.advance()
    return _fact


def rule(token: TokenStream) -> Rule:
    # first_set = {"ID"}
    _headPredicate: Predicate = headPredicate(token)
    token.match("COLON_DASH")
    token.advance()
    _predicates: list[Predicate] = []
    _predicates.append(predicate(token))
    _predicates.extend(predicateList(token))
    _rule: Rule = Rule(_headPredicate, _predicates)
    token.match("PERIOD")
    token.advance()
    return _rule


def query(token: TokenStream) -> Predicate:
    # first_set = {"ID"}
    _query: Predicate = predicate(token)
    token.match("Q_MARK")
    token.advance()
    return _query


def headPredicate(token: TokenStream) -> Predicate:
    # first_set = {"ID"}
    token.match("ID")
    _name = token.value()
    token.advance()
    token.match("LEFT_PAREN")
    token.advance()
    token.match("ID")
    _parameters: list[Parameter] = [Parameter(token.value(), "ID")]
    token.advance()
    _parameters.extend(idList(token))
    token.match("RIGHT_PAREN")
    token.advance()
    return Predicate(_name, _parameters)


def predicate(token: TokenStream) -> Predicate:
    # first_set = {"ID"}
    token.match("ID")
    _name = token.value()
    token.advance()
    token.match("LEFT_PAREN")
    token.advance()
    _predicate = Predicate(_name, [parameter(token)])
    _parameters: list[Parameter] = parameterList(token)
    for i in _parameters:
        _predicate.add_parameter(i)
    token.match("RIGHT_PAREN")
    token.advance()
    return _predicate


def predicateList(token: TokenStream) -> list[Predicate]:
    first_set: set[TokenType] = {"COMMA"}
    follow_set: set[TokenType] = {"PERIOD"}
    _predicatelist = []

    if token.member_of(first_set):
        token.match("COMMA")
        token.advance()
        _predicatelist.append(predicate(token))
        _predicatelist.extend(predicateList(token))
    elif token.member_of(follow_set):
        return _predicatelist
    else:
        raise UnexpectedTokenException("COMMA or PERIOD", token.token)
    return _predicatelist


def parameterList(token: TokenStream) -> list[Parameter]:
    first_set: set[TokenType] = {"COMMA"}
    follow_set: set[TokenType] = {"RIGHT_PAREN"}
    _parameterlist = []

    if token.member_of(first_set):
        token.match("COMMA")
        token.advance()
        _parameterlist.append(parameter(token))
        _parameterlist.extend(parameterList(token))
    elif token.member_of(follow_set):
        return _parameterlist
    else:
        raise UnexpectedTokenException("COMMA or RIGHT_PAREN", token.token)
    return _parameterlist


def stringList(token: TokenStream) -> list[Parameter]:
    first_set: set[TokenType] = {"COMMA"}
    follow_set: set[TokenType] = {"RIGHT_PAREN"}
    _stringlist = []

    if token.member_of(first_set):
        token.match("COMMA")
        token.advance()
        token.match("STRING")
        _stringlist.append(Parameter(token.value(), "STRING"))
        token.advance()
        _stringlist.extend(stringList(token))
    elif token.member_of(follow_set):
        return _stringlist
    else:
        raise UnexpectedTokenException("COMMA or RIGHT_PAREN", token.token)
    return _stringlist


def idList(token: TokenStream) -> list[Parameter]:
    first_set: set[TokenType] = {"COMMA"}
    follow_set: set[TokenType] = {"RIGHT_PAREN"}
    _idlist = []

    if token.member_of(first_set):
        token.match("COMMA")
        token.advance()
        token.match("ID")
        _idlist.append(Parameter(token.value(), "ID"))
        token.advance()
        _idlist.extend(idList(token))
    elif token.member_of(follow_set):
        return _idlist
    else:
        raise UnexpectedTokenException("COMMA or RIGHT_PAREN", token.token)
    return _idlist


def parameter(token: TokenStream) -> Parameter:
    first_set: set[TokenType] = {"STRING", "ID"}
    _parameter: Parameter

    if token.member_of(first_set):
        if token.token.token_type == "STRING":
            _parameter = Parameter(token.value(), "STRING")
        elif token.token.token_type == "ID":
            _parameter = Parameter(token.value(), "ID")
        token.advance()
        assert _parameter is not None
        return _parameter
    else:
        raise UnexpectedTokenException("STRING or ID", token.token)


def datalog_program(token: TokenStream) -> DatalogProgram:
    """Top-level grammar rule for a Datalog program.

    The function directly matches its associated grammar rule by matching
    on keywords and collecting returns from other non-terminal rules to
    build an instance of a `DatalogProgram`.

    Pseudo-code:
    ```
    token.match('SCHEMES')
    token.advance()
    token.match('COLON')
    token.advance()

    schemes: list[Predicate] = [scheme(token)]
    schemes.extend(scheme_list(token))

    # Other matches, advances, and rules for the rest of a Datalog Program

    return DatalogProgram(schemes, facts, rules, queries)
    ```

    Args:
        token (TokenStream]): A token stream.

    Returns:
        program (DatalogProgram): The Datalog program from the parse.
    """
    # instantiate the datalog program
    datalog_program: DatalogProgram = DatalogProgram([], [], [], [])

    # SCHEMES:
    token.match("SCHEMES")
    token.advance()
    token.match("COLON")
    token.advance()
    # schemes list
    schemes: list[Predicate] = [scheme(token)]
    schemes.extend(schemeList(token))
    # add schemes to datalog program
    for i in schemes:
        datalog_program.add_scheme(i)

    # FACTS:
    token.match("FACTS")
    token.advance()
    token.match("COLON")
    token.advance()
    # facts list (may be empty)
    facts: list[Predicate] = factList(token)
    # add facts to datalog program
    for i in facts:
        datalog_program.add_fact(i)

    # RULES:
    token.match("RULES")
    token.advance()
    token.match("COLON")
    token.advance()
    # rules list (may be empty)
    rules: list[Rule] = ruleList(token)
    for rule in rules:
        datalog_program.add_rule(rule)

    # QUERIES:
    token.match("QUERIES")
    token.advance()
    token.match("COLON")
    token.advance()
    # queries list
    queries: list[Predicate] = [query(token)]
    queries.extend(queryList(token))
    # add queries to datalog program
    for i in queries:
        datalog_program.add_query(i)

    # find EOF
    token.match("EOF")
    token.advance()

    return datalog_program


def parse(token_iterator: Iterator[Token]) -> DatalogProgram:
    """Parse a datalog program.

    A convenience function that avoids having to create an instance of the
    `TokenStream`

    Args:
        token_iterator (Iterator[Token]): A token iterator.

    Returns:

        program (DatalogProgram): The Datalog program from the parse.
    """
    token: TokenStream = TokenStream(token_iterator)
    return datalog_program(token)
