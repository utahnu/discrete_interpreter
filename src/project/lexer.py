"""Turn a input string into a stream of tokens with lexical analysis.

The `lexer(input_string: str)` function is the entry point. It generates a
stream of tokens from the `input_string`.

Examples:

    >>> from project.lexer import lexer
    >>> input_string = ":\\n  \\n:"
    >>> for i in lexer(input_string):
    ...     print(i)
    ...
    (COLON,":",1)
    (COLON,":",3)
    (EOF,"",3)
"""

from typing import Iterator

from project.fsm import (
    Colon,
    ColonDash,
    Comma,
    Comment,
    Eof,
    Facts,
    FiniteStateMachine,
    Id,
    Left_Paren,
    Period,
    Q_Mark,
    Queries,
    Right_Paren,
    Rules,
    Schemes,
    String,
    WhiteSpace,
    run_fsm,
)
from project.token import Token, TokenType


def lexer(input_string: str) -> Iterator[Token]:
    """Produce a stream of tokens from a given input string.

    Pseudo-code:

    ```
    fsms: list[FiniteStateMachine] = [Colon(), Eof(), WhiteSpace()]
    hidden: list[TokenType] = ["WHITESPACE"]
    line_num: int = 1
    token: Token = Token.undefined("")
    while not _is_last_token(token):
        token = _get_token(input_string, fsms)
        token.line_num = line_num
        line_num = line_num + _get_new_lines(token.value)
        input_string = input_string.removeprefix(token.value)
        if token.token_type in hidden:
            continue
        yield token
    ```

    The `_get_token` function should return the token from the FSM that reads
    the most characters. In the case of two FSMs reading the same number of
    characters, the one that comes first in the list of FSMs, `fsms`, wins.
    Some care must be given to determining when the _last_ token has been
    generated and how to update the new `line_num` for the next token.

    Args:
        input_string: Input string for token generation.

    Yields:
        token: The current token resulting from the string.
    """
    fsms: list[FiniteStateMachine] = [
        Comma(),
        Period(),
        Q_Mark(),
        Left_Paren(),
        Right_Paren(),
        ColonDash(),
        Colon(),
        Schemes(),
        Facts(),
        Rules(),
        Queries(),
        Id(),
        String(),
        Comment(),
        Eof(),
        WhiteSpace(),
    ]  # noqa: F841
    hidden: set[TokenType] = {"WHITESPACE", "COMMENT"}  # noqa: F841

    def _get_max_token(input_string: str, fsms: list[FiniteStateMachine]) -> Token:
        max_token = Token.undefined("")  # type: Token
        max_characters_read = 0  # type: int

        # run each fsm on the input string
        for fsm in fsms:
            fsm_output = run_fsm(fsm, input_string)
            characters_read = fsm_output[0]
            if characters_read > max_characters_read:
                max_characters_read = characters_read
                max_token = fsm_output[1]

        # return the max token if an fsm read any characters
        if max_characters_read > 0:
            max_token.line_num = line_number
            return max_token

        # return an undefined token if no fsm read any characters
        else:
            undefined_token = Token.undefined(input_string[0])
            undefined_token.line_num = line_number
            return undefined_token

    line_number = 1
    current_token = Token.undefined("")  # type: Token
    token_list: list[Token] = []

    while current_token is None or current_token.token_type != "EOF":
        # get the next token
        current_token = _get_max_token(input_string, fsms)

        # slice off the prefix from the input string
        input_string = input_string[len(current_token.value) :]

        # update the line number
        line_number += current_token.value.count("\n")

        # add the token to the list if it is not whitespace
        if current_token.token_type not in hidden:
            token_list.append(current_token)
            if current_token.token_type == "UNDEFINED":
                break

    # return the list of tokens
    return iter(token_list)
