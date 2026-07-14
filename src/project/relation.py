"""Relation type for interpreting Datalog."""

from copy import deepcopy
from typing import Any

from tabulate import tabulate


class IncompatibleOperandError(Exception):
    """Type for relational algebra operand errors."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


RelationTuple = tuple[str, ...]
"""Defines a type for tuples in the relation. Here the tuple can be any number of strings."""


class Relation:
    """Relation class for relational algebra.

    The interface for the class is complete meaning that it defines all the
    needed attributes and relation operations to implement the Datalog interpreter.
    It is expected that additional internal functions are to be added in support
    of the published public interface. No additional attributes should be needed.

    Attributes:
        header (list[str]): The relation header.
        set_of_tuples (set[RelationTuple]): The tuples belonging to the relation.
    """

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Relation):
            return False
        return self.header == other.header and self.set_of_tuples == other.set_of_tuples

    def __init__(self, header: list[str], set_of_tuples: set[RelationTuple]) -> None:
        """Initialize a new relation.

        The `RelationTuple` type is not mutable, so it is not necessary to make
        new copies when initializing a new relation. The list for the header and
        the set of tuples are mutable, so here new instances are created.
        """
        self.header = list(header)
        self.set_of_tuples: set[RelationTuple] = set()
        for i in set_of_tuples:
            self.add_tuple(i)

    def __repr__(self) -> str:
        return f"Relation(header={self.header!r}, set_of_tuples={self.set_of_tuples!r})"

    def __str__(self) -> str:
        """Return the relation as a string.

        A `set` type in Python is not sorted, and indeed, the order of elements
        in the set though defined by the hash of each tuple is non-deterministic
        from machine to machine and run to run. Here the tuples in the set are
        sorted so that the string representation is always deterministic.

        Returns:
            value (str): The relation as a string.
        """
        sorted_tuples = sorted(self.set_of_tuples)
        value: str = tabulate(iter(sorted_tuples), self.header, tablefmt="pretty")
        return value

    def add_tuple(self, r: RelationTuple) -> None:
        """Add a new tuple to the relation.

        Raises:
            error (IncompatibleOperandError): Error if the length of the tuple doesn't
                match the header or if the thing being added isn't a tuple of strings.
        """
        if len(self.header) != len(r):
            raise IncompatibleOperandError(
                f"Error: {r} is not compatible with header {self.header} in Relation.add_tuple"
            )
        if not isinstance(r, tuple) or any(not isinstance(i, str) for i in r):
            raise IncompatibleOperandError(
                f"Error: {r} is not type compatible with Relation.RelationTuple in Relation.add_tuple"
            )
        self.set_of_tuples.add(r)

    def difference(self, right_operand: "Relation") -> "Relation":
        """The difference between this relation and another.

        The left operand is this relation (self) and the right operand
        is provided in the function call. The headers must be the same.

        Returns:
            r (Relation): A new relation that is self - right_operand.
        Raises:
            error (IncompatibleOperandError): Error if the headers are not the same.
        """
        if self.header != right_operand.header:
            raise IncompatibleOperandError(
                f"Error: headers {self.header} and {right_operand.header} are not compatible in Relation.difference"
            )
        r = Relation(
            self.header,
            self.set_of_tuples.difference(right_operand.set_of_tuples),
        )
        return r

    def intersection(self, right_operand: "Relation") -> "Relation":
        """The intersection between this relation and another.

        The left operand is this relation (self) and the right operand
        is provided in the function call. The headers must agree.

        Returns:
            r (Relation): A new relation that is self intersect with right_operand.
        Raises:
            error (IncompatibleOperandError): Error if the headers are not the same.
        """
        if self.header != right_operand.header:
            raise IncompatibleOperandError(
                f"Error: headers {self.header} and {right_operand.header} are not compatible in Relation.intersection"
            )
        r = Relation(
            self.header,
            self.set_of_tuples.intersection(right_operand.set_of_tuples),
        )
        return r

    def join(self, right_operand: "Relation") -> "Relation":
        """The natural join between this relation and another.

        The left operand is this relation (self) and the right operand
        is provided in the function call.

        Returns:
            r (Relation): A new relation that is self natural join with right_operand.
        """
        new_header = deepcopy(self.header)
        right_indices = []
        for i, attribute in enumerate(right_operand.header):
            if attribute not in self.header:
                new_header.append(attribute)
            else:
                right_indices.append(i)

        new_tuples = set()
        for t1 in self.set_of_tuples:
            for t2 in right_operand.set_of_tuples:
                joinable = True
                for index in right_indices:
                    attribute = right_operand.header[index]
                    if t1[self.header.index(attribute)] != t2[index]:
                        joinable = False
                        break

                if joinable:
                    new_tuple = list(t1)
                    for i, value in enumerate(t2):
                        if right_operand.header[i] not in self.header:
                            new_tuple.append(value)
                    new_tuples.add(tuple(new_tuple))

        return Relation(new_header, new_tuples)

    def project(self, to: list[str]) -> "Relation":
        """The projection of this relation to a new header.

        The names in `to` must refer to existing names in the header. The final relation must only
        include entries in each tuple belonging to those named in `to` and must appear in each tuple
        in the order they appear in `to`. The final header should match `to` in the new relation.

        Returns:
            r (Relation): A new relation that is this relation projected to `to`.
        Raises:
            error (IncompatibleOperandError): Error if `to` names something not in this relation's header.
        """
        if not all(attr in self.header for attr in to):
            raise IncompatibleOperandError(
                f"Error: new header {to} has names not compatible with header {self.header} in Relation.project"
            )
        new_header = deepcopy(to)
        # Preserve the order specified in `to` by retrieving indices in that order.
        header_indices = [self.header.index(attribute) for attribute in to]
        new_tuples = set()
        for t in self.set_of_tuples:
            new_tuples.add(tuple(t[i] for i in header_indices))
        r = Relation(
            new_header,
            new_tuples,
        )
        return r

    def rename(self, to: list[str]) -> "Relation":
        """The rename of this relation to a new header.

        The length of `to` must match the current header. The new resulting relation
        should match this current relation with the exception of the new header. The
        header in the new relation should be `to`.

        Returns:
            r (Relation): A new relation that is this relation renamed to `to`.
        Raises:
            error (IncompatibleOperandError): Error if the length of `to` doesn't
            match the length of the header in this relation.
        """
        if len(to) != len(self.header):
            raise IncompatibleOperandError(
                f"Error: header length {len(self.header)} and new header length {len(to)} are not compatible in Relation.rename"
            )
        r = Relation(
            to,
            self.set_of_tuples,
        )
        return r

    def reorder(self, to: list[str]) -> "Relation":
        """The reorder of this relation to a new order on the header.

        The length of `to` must match the length of the header. And the names in
        `to` must match the names in the header albeit in the same or different order.
        The tuples in the final relation are the tuples in the current relation
        reordered to match the order in `to`. The header for the final relation should
        also match `to`.

        Returns:
            r (Relation): A new relation that is this relation with the header and tuples reordered to `to`.
        Raises:
            error (IncompatibleOperandError): Error if `to` has more entries than what is in this relation's header or has an name that is not in this relation's header.
        """
        if not all(attr in self.header for attr in to):
            raise IncompatibleOperandError(
                f"Error: new header {to} has names not compatible with header {self.header} in Relation.reorder"
            )
        if len(to) != len(self.header):
            raise IncompatibleOperandError(
                f"Error: header length {len(self.header)} and new header length {len(to)} are not compatible in Relation.reorder"
            )
        new_header = deepcopy(to)
        header_indices = []
        for attribute in new_header:
            header_indices.append(self.header.index(attribute))
        new_tuples = set()
        for t in self.set_of_tuples:
            new_tuples.add(tuple(t[i] for i in header_indices))
        r = Relation(
            new_header,
            new_tuples,
        )
        return r

    def select_eq_col(self, src: str, col: str) -> "Relation":
        """The select of this relation where the `src` entry equals the `col` entry.

        The `src` and `col` must be known in the header. The new resulting relation
        should only include tuples where the value for `src` is equal to the value
        for `col`. The header in the new relation is the same as in this relation.

        Returns:
            r (Relation): A new relation with tuples from this relation that agree
                on values for `src` and `col`.
        Raises:
            error (IncompatibleOperandError): Error if `src` or
            `col` are not found in the header.
        """
        if src not in self.header or col not in self.header:
            raise IncompatibleOperandError(
                f"Error: columns {src} and/or {col} are not compatible with header {self.header} in Relation.select_eq_col"
            )
        src_index = self.header.index(src)
        col_index = self.header.index(col)
        new_tuples = set()
        for t in self.set_of_tuples:
            if t[src_index] == t[col_index]:
                new_tuples.add(t)
        r = Relation(
            self.header,
            new_tuples,
        )
        return r

    def select_eq_lit(self, src: str, lit: str) -> "Relation":
        """The select of this relation where the `src` entry equals `lit`.

        The `src` must be known in the header. The new resulting relation
        should only include tuples where the value for `src` is equal to `lit`.
        The header in the new relation is the same as in this relation.

        Returns:
            r (Relation): A new relation with tuples from this relation where the
                values for `src` is `lit`.
        Raises:
            error (IncompatibleOperandError): Error if `src` is not found in the header.
        """
        if src not in self.header:
            raise IncompatibleOperandError(
                f"Error: column {src} is not compatible with header {self.header} in Relation.select_eq_lit"
            )
        src_index = self.header.index(src)
        new_tuples = set()
        for t in self.set_of_tuples:
            if t[src_index] == lit:
                new_tuples.add(t)
        r = Relation(
            self.header,
            new_tuples,
        )
        return r

    def union(self, right_operand: "Relation") -> "Relation":
        """The union of this relation and another.

        The left operand is this relation (self) and the right operand
        is provided in the function call. The headers must agree.

        Returns:
            r (Relation): A new relation that is self union with right_operand.
        Raises:
            error (IncompatibleOperandError): Error if the headers are not the same.
        """

        if self.header != right_operand.header:
            raise IncompatibleOperandError(
                f"Error: headers {self.header} and {right_operand.header} are not compatible in Relation.union"
            )
        r = Relation(
            self.header,
            self.set_of_tuples.union(right_operand.set_of_tuples),
        )
        return r
