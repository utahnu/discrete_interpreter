# type: ignore
import pytest

from project.relation import IncompatibleOperandError, Relation


def test_given_empty_relation_when_add_tuple_then_tuple_in_relation():
    # given
    header = ("a", "b", "c")
    relation = Relation(header, set())
    input = ("'1'", "'2'", "'3'")

    # when
    relation.add_tuple(input)

    # then
    assert 1 == len(relation.set_of_tuples)
    assert input in relation.set_of_tuples


def test_given_relation_when_str_then_match_expected():
    # given
    header = ("a", "b", "c")
    set_of_tuples = set([("'1'", "'2'", "'3'"), ("'1'", "'3'", "'5'")])
    relation = Relation(header, set_of_tuples)

    expected = """+-----+-----+-----+
|  a  |  b  |  c  |
+-----+-----+-----+
| '1' | '2' | '3' |
| '1' | '3' | '5' |
+-----+-----+-----+"""

    # when
    answer = str(relation)

    # then
    assert expected == answer


def test_given_relation_and_wrong_size_when_add_tuple_then_exception():
    # given
    relation = Relation(("a", "b", "c"), set())

    # when
    with pytest.raises(IncompatibleOperandError) as exception:
        relation.add_tuple(("1", "2"))

    # then
    assert (
        "Error: ('1', '2') is not compatible with header ['a', 'b', 'c'] in Relation.add_tuple"
        == str(exception.value)
    )


def test_given_relation_when_add_tuple_then_added():
    # given
    relation = Relation(("a", "b", "c"), set())

    # when
    relation.add_tuple(("1", "2", "3"))

    # then
    assert ("1", "2", "3") in relation.set_of_tuples


def test_given_mismatched_header_and_tuple_when_construct_then_exception():
    # given
    header = ("a", "b", "c")
    set_of_tuples = set([("1", "2")])

    # when
    with pytest.raises(IncompatibleOperandError) as exception:
        _ = Relation(header, set_of_tuples)

    # then
    assert (
        "Error: ('1', '2') is not compatible with header ['a', 'b', 'c'] in Relation.add_tuple"
        == str(exception.value)
    )


def test_given_set_that_is_not_over_tuples_when_construct_then_exception():
    # given
    header = "a"
    set_of_tuples = set(["1"])

    # when
    with pytest.raises(IncompatibleOperandError) as exception:
        _ = Relation(header, set_of_tuples)

    # then
    assert (
        "Error: 1 is not type compatible with Relation.RelationTuple in Relation.add_tuple"
        == str(exception.value)
    )


def test_given_set_that_is_tuples_but_not_str_when_construct_then_exception():
    # given
    header = ("a", "b")
    set_of_tuples = set([("1", 2)])

    # when
    with pytest.raises(IncompatibleOperandError) as exception:
        _ = Relation(header, set_of_tuples)

    # then
    assert (
        "Error: ('1', 2) is not type compatible with Relation.RelationTuple in Relation.add_tuple"
        == str(exception.value)
    )


def test_given_mismatched_relations_when_difference_then_exception():
    # given
    left = Relation(("a", "b", "c"), set())
    right = Relation(("a", "b"), set())

    # when
    with pytest.raises(IncompatibleOperandError) as exception:
        left.difference(right)

    # then
    assert (
        "Error: headers ['a', 'b', 'c'] and ['a', 'b'] are not compatible in Relation.difference"
        == str(exception.value)
    )


def test_given_matched_relations_when_difference_then_difference():
    # given
    left = Relation(("a", "b", "c"), set([("1", "2", "3"), ("2", "4", "6")]))
    right = Relation(("a", "b", "c"), set([("2", "4", "6")]))
    expected = Relation(("a", "b", "c"), set([("1", "2", "3")]))

    # when
    answer = left.difference(right)

    # then
    assert expected == answer


def test_union_raises_when_headers_differ() -> None:
    # given
    P = Relation(["bart", "lisa"], {("h", "1"), ("m", "2")})
    W = Relation(["bart", "maggie"], {("f", "3")})  # header differs in second column

    # when
    # then
    with pytest.raises(IncompatibleOperandError):
        P.union(W)


@pytest.mark.parametrize(
    argnames=("hdr, rows1, rows2, expected_rows"),
    argvalues=(
        # Disjoint
        (
            ["A", "B"],
            {("1", "a"), ("2", "b")},
            {("3", "c")},
            {("1", "a"), ("2", "b"), ("3", "c")},
        ),
        # Overlap (duplicates should be removed by set semantics)
        (
            ["A", "B"],
            {("1", "a"), ("2", "b")},
            {("2", "b"), ("3", "c")},
            {("1", "a"), ("2", "b"), ("3", "c")},
        ),
        # Left empty
        (["A", "B"], set(), {("1", "a")}, {("1", "a")}),
        # Right empty
        (["A", "B"], {("1", "a")}, set(), {("1", "a")}),
        # Idempotent: R ∪ R = R
        (
            ["A", "B"],
            {("10", "x"), ("11", "y")},
            {("10", "x"), ("11", "y")},
            {("10", "x"), ("11", "y")},
        ),
    ),
    ids=("Disjoint", "Overlap", "Left Empty", "Right Empty", "Idempotent"),
)
def test_union_basic_cases(hdr, rows1, rows2, expected_rows):
    # given
    r1 = Relation(hdr, rows1)
    r2 = Relation(hdr, rows2)
    expected = Relation(hdr, expected_rows)

    # when
    answer = r1.union(r2)

    # then
    assert expected == answer


def test_given_bad_col_when_project_then_raise() -> None:
    # given
    r = Relation(["A", "B"], {("x", "1")})
    project_hdr = ["Z"]

    # when
    # then
    with pytest.raises(IncompatibleOperandError):
        r.project(project_hdr)


@pytest.mark.parametrize(
    argnames=("hdr, rows, project_hdr, expected_rows"),
    argvalues=(
        # Disjoint
        (
            ["A", "B"],
            set(),
            ["A"],
            set(),
        ),
        # Two Columns
        (
            ["A", "B"],
            {("x", "1"), ("y", "2")},
            ["A"],
            {("x",), ("y",)},
        ),
        # Two Columns with Duplicates
        (
            ["A", "B"],
            {("x", "1"), ("x", "2")},
            ["A"],
            {("x",)},
        ),
        # Three Columns
        (
            ["A", "B", "C"],
            {("x1", "1", "True"), ("y", "2", "False")},
            ["B"],
            {("1",), ("2",)},
        ),
        # Three Columns with Two Adjacent
        (
            ["A", "B", "C"],
            {
                ("x", "1", "True"),
                ("y", "2", "False"),
                ("x", "1", "False"),
            },
            ["A", "B"],
            {("x", "1"), ("y", "2")},
        ),
        # Three Columns with Two Not Adjacent
        (
            ["A", "B", "C"],
            {
                ("x", "1", "True"),
                ("y", "2", "False"),
                ("x", "9", "True"),
            },
            ["A", "C"],
            {("x", "True"), ("y", "False")},
        ),
    ),
    ids=(
        "Empty",
        "Two Cols",
        "Two Cols with Dups",
        "Three Cols",
        "Three Cols with Two Adj",
        "Three Cols with Two Not Adj",
    ),
)
def test_project_basic_cases(hdr, rows, project_hdr, expected_rows):
    # given
    r = Relation(hdr, rows)
    expected = Relation(project_hdr, expected_rows)

    # when
    answer = r.project(project_hdr)

    # then
    assert expected == answer


#######################################################################
################################ HW 14 ################################
#######################################################################


@pytest.mark.parametrize(
    "hdr,rows,expected_rows,src,col",
    [
        # operand is the empty relation
        (
            ["A", "B"],
            set(),
            set(),
            "A",
            "B",
        ),
        # relation has more than 2 attributes
        (
            ["A", "B", "C"],
            {("1", "2", "5"), ("3", "3", "6")},
            {("3", "3", "6")},
            "A",
            "B",
        ),
        # answer is the empty set
        (
            ["A", "B"],
            {("1", "a"), ("2", "b"), ("3", "c")},
            set(),
            "A",
            "B",
        ),
        # all rows match
        (
            ["A", "B"],
            {("1", "1"), ("2", "2")},
            {("1", "1"), ("2", "2")},
            "A",
            "B",
        ),
        # 1 row matches
        (
            ["A", "B"],
            {("1", "1"), ("3", "b"), ("4", "c")},
            {("1", "1")},
            "A",
            "B",
        ),
    ],
)
def test_select_eq_col(hdr, rows, expected_rows, src, col):
    # given
    r = Relation(hdr, rows)
    expected = Relation(hdr, expected_rows)

    # when
    answer = r.select_eq_col(src, col)

    # then
    assert expected == answer


def test_negative_select_eq_col_when_first_column_does_not_exist() -> None:
    # given
    r = Relation(["A", "B"], {("1", "f"), ("2", "a"), ("3", "b")})

    # when
    # then
    with pytest.raises(IncompatibleOperandError):
        r.select_eq_col("C", "B")  # column C does not exist


def test_negative_select_eq_col_when_second_column_does_not_exist() -> None:
    # given
    r = Relation(["A", "B"], {("1", "f"), ("2", "a"), ("3", "b")})

    # when
    # then
    with pytest.raises(IncompatibleOperandError):
        r.select_eq_col("A", "C")  # column C does not exist


@pytest.mark.parametrize(
    "hdr,rows,expected_rows",
    [
        # operand is the empty relation
        (
            ["A", "B"],
            set(),
            set(),
        ),
        # relation has more than 2 attributes
        (
            ["A", "B", "C"],
            {("a", "a", "x"), ("a", "b", "y"), ("f", "c", "z")},
            {("f", "c", "z")},
        ),
        # result is the empty relation
        (
            ["A", "B"],
            {("a", "1"), ("b", "2")},
            set(),
        ),
        # 1 row matches
        (
            ["A", "B"],
            {("x", "1"), ("f", "2"), ("z", "3")},
            {("f", "2")},
        ),
    ],
)
def test_select_eq_lit(hdr, rows, expected_rows):
    # given
    r = Relation(hdr, rows)
    expected = Relation(hdr, expected_rows)

    # when
    answer = r.select_eq_lit("A", "f")

    # then
    assert expected == answer


def test_negative_select_eq_lit_when_select_wrong_column() -> None:
    # given
    r = Relation(["A", "B"], {("1", "f"), ("2", "a"), ("3", "b")})
    negative_expected = Relation(["A", "B"], {("1", "f")})

    # when
    answer = r.select_eq_lit("B", "f")

    # then
    assert answer == negative_expected


def test_negative_select_eq_lit_when_column_does_not_exist() -> None:
    # given
    r = Relation(["A", "B"], {("1", "f"), ("2", "a"), ("3", "b")})

    # when
    # then
    with pytest.raises(IncompatibleOperandError):
        r.select_eq_lit("C", "f")  # column C does not exist


@pytest.mark.parametrize(
    "hdr,rows,expected_hdr,expected_rows,rename_to",
    [
        # rename A to Z
        (
            ["A", "B"],
            {("1", "a"), ("2", "b"), ("3", "c")},
            ["Z", "B"],
            {("1", "a"), ("2", "b"), ("3", "c")},
            ["Z", "B"],
        ),
        # rename with more than 2 columns
        (
            ["A", "B", "C"],
            {("1", "a", "x"), ("2", "b", "y"), ("3", "c", "z")},
            ["Z", "B", "C"],
            {("1", "a", "x"), ("2", "b", "y"), ("3", "c", "z")},
            ["Z", "B", "C"],
        ),
        # rename middle column
        (
            ["A", "B", "C"],
            {("1", "a", "x"), ("2", "b", "y"), ("3", "c", "z")},
            ["A", "Z", "C"],
            {("1", "a", "x"), ("2", "b", "y"), ("3", "c", "z")},
            ["A", "Z", "C"],
        ),
        # rename last column
        (
            ["A", "B", "C"],
            {("1", "a", "x"), ("2", "b", "y"), ("3", "c", "z")},
            ["A", "B", "Z"],
            {("1", "a", "x"), ("2", "b", "y"), ("3", "c", "z")},
            ["A", "B", "Z"],
        ),
    ],
)
def test_rename(hdr, rows, expected_hdr, expected_rows, rename_to):
    # given
    r = Relation(hdr, rows)
    expected = Relation(expected_hdr, expected_rows)

    # when
    answer = r.rename(rename_to)

    # then
    assert expected == answer


def test_negative_rename_when_length_mismatch() -> None:
    # given
    r = Relation(["A", "B"], {("1", "a"), ("2", "b"), ("3", "c")})

    # when
    # then
    with pytest.raises(IncompatibleOperandError):
        r.rename(["Z"])  # length mismatch


# def test_negative_rename_when_duplicate_names() -> None:
#     # given
#     r = Relation(["A", "B"], {("1", "a"), ("2", "b")})

#     # when
#     # then
#     with pytest.raises(IncompatibleOperandError):
#         r.rename(["Z", "Z"])  # duplicate names


@pytest.mark.parametrize(
    "hdr,rows,expected_hdr,expected_rows,reorder_to",
    [
        # reorder AB to BA
        (
            ["A", "B"],
            {("1", "a"), ("2", "b")},
            ["B", "A"],
            {("a", "1"), ("b", "2")},
            ["B", "A"],
        ),
        # reorder with more than 2 columns
        (
            ["A", "B", "C"],
            {("1", "a", "x"), ("2", "b", "y"), ("3", "c", "z")},
            ["C", "A", "B"],
            {("x", "1", "a"), ("y", "2", "b"), ("z", "3", "c")},
            ["C", "A", "B"],
        ),
        # reorder the empty relation
        (
            ["A", "B"],
            set(),
            ["B", "A"],
            set(),
            ["B", "A"],
        ),
    ],
)
def test_reorder(hdr, rows, expected_hdr, expected_rows, reorder_to):
    # given
    r = Relation(hdr, rows)
    expected = Relation(expected_hdr, expected_rows)

    # when
    answer = r.reorder(reorder_to)

    # then
    assert expected == answer


def test_negative_reorder_when_length_mismatch() -> None:
    # given
    r = Relation(["A", "B"], {("1", "a"), ("2", "b")})

    # when
    # then
    with pytest.raises(IncompatibleOperandError):
        r.reorder(["C", "A", "B", "D"])  # length mismatch
