# type: ignore
import pytest

from project.relation import Relation


@pytest.mark.parametrize(
    argnames=(
        "r1_header, r1_tuples, r2_header, r2_tuples, expected_header, expected_tuples"
    ),
    argvalues=(
        # simple case with no common attributes
        (
            ["A", "B"],
            {("1", "2"), ("3", "4")},
            ["C", "D"],
            {("5", "6"), ("7", "8")},
            ["A", "B", "C", "D"],
            {
                ("1", "2", "5", "6"),
                ("1", "2", "7", "8"),
                ("3", "4", "5", "6"),
                ("3", "4", "7", "8"),
            },
        ),
        # all header attributes match in same order
        (
            ["char", "int"],
            {("a", "1"), ("b", "2"), ("c", "3"), ("d", "4")},
            ["char", "int"],
            {("f", "3"), ("b", "2"), ("b", "3"), ("d", "4")},
            ["char", "int"],
            {("b", "2"), ("d", "4")},
        ),
        # all header attributes match in different order
        (
            ["int", "char"],
            {("1", "a"), ("2", "b"), ("3", "c"), ("4", "d")},
            ["char", "int"],
            {("f", "3"), ("b", "2"), ("b", "3"), ("d", "4")},
            ["int", "char"],
            {("2", "b"), ("4", "d")},
        ),
        # all header attributes different
        (
            ["char", "int"],
            {("a", "1"), ("b", "2")},
            ["X", "Y"],
            {("x", "red"), ("y", "blue")},
            ["char", "int", "X", "Y"],
            {
                ("a", "1", "x", "red"),
                ("a", "1", "y", "blue"),
                ("b", "2", "x", "red"),
                ("b", "2", "y", "blue"),
            },
        ),
        # headers with one common attribute
        (
            ["id", "name", "dept"],
            {("1", "Alice", "HR"), ("2", "Bob", "IT")},
            ["dept", "location"],
            {("HR", "Building A"), ("IT", "Building B")},
            ["id", "name", "dept", "location"],
            {("1", "Alice", "HR", "Building A"), ("2", "Bob", "IT", "Building B")},
        ),
        # headers with multiple common attributes
        (
            ["A", "B", "C"],
            {("a", "b", "c"), ("d", "e", "f")},
            ["B", "C", "D"],
            {("b", "c", "x"), ("e", "f", "y")},
            ["A", "B", "C", "D"],
            {("a", "b", "c", "x"), ("d", "e", "f", "y")},
        ),
        # headers with multiple common attributes in different order
        (
            ["C", "A", "B"],
            {("c", "a", "b"), ("f", "d", "e")},
            ["B", "C", "D"],
            {("b", "c", "x"), ("e", "f", "y")},
            ["C", "A", "B", "D"],
            {("c", "a", "b", "x"), ("f", "d", "e", "y")},
        ),
    ),
    ids=(
        "simple case with no common attributes",
        "all header attributes match in same order",
        "all header attributes match in different order",
        "all header attributes different",
        "headers with one common attribute",
        "headers with multiple common attributes",
        "headers with multiple common attributes in different order",
    ),
)
def test_join_all_cases(
    r1_header, r1_tuples, r2_header, r2_tuples, expected_header, expected_tuples
):
    # given
    r1 = Relation(r1_header, r1_tuples)
    r2 = Relation(r2_header, r2_tuples)
    expected = Relation(expected_header, expected_tuples)

    # when
    result = r1.join(r2)

    # then
    assert result == expected
