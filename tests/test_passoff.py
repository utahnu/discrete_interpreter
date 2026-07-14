# type: ignore
import os

from project.project import project as compute

_TEST_ROOT_DIR = "./tests/resources/project-passoff/"


def _get_inputs(input_file: str, answer_file: str) -> tuple[str, str]:
    input = ""
    with open(input_file, "r") as f:
        input = f.read()
    answer = ""
    with open(answer_file, "r") as f:
        answer = f.read()
    return input, answer


def test_bucket_80_0():
    # given
    input_file, expected_file = ("input0.txt", "answer0.txt")
    test_dir = _TEST_ROOT_DIR + "80"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()


def test_bucket_80_1():
    # given
    input_file, expected_file = ("input1.txt", "answer1.txt")
    test_dir = _TEST_ROOT_DIR + "80"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()


def test_bucket_80_2():
    # given
    input_file, expected_file = ("input2.txt", "answer2.txt")
    test_dir = _TEST_ROOT_DIR + "80"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()


def test_bucket_80_3():
    # given
    input_file, expected_file = ("input3.txt", "answer3.txt")
    test_dir = _TEST_ROOT_DIR + "80"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()


def test_bucket_80_4():
    # given
    input_file, expected_file = ("input4.txt", "answer4.txt")
    test_dir = _TEST_ROOT_DIR + "80"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()


def test_bucket_80_5():
    # given
    input_file, expected_file = ("input5.txt", "answer5.txt")
    test_dir = _TEST_ROOT_DIR + "80"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()


def test_bucket_80_6():
    # given
    input_file, expected_file = ("input6.txt", "answer6.txt")
    test_dir = _TEST_ROOT_DIR + "80"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()


def test_bucket_80_7():
    # given
    input_file, expected_file = ("input7.txt", "answer7.txt")
    test_dir = _TEST_ROOT_DIR + "80"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()


def test_bucket_100_1():
    # given
    input_file, expected_file = ("input1.txt", "answer1.txt")
    test_dir = _TEST_ROOT_DIR + "100"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()


def test_bucket_100_2():
    # given
    input_file, expected_file = ("input2.txt", "answer2.txt")
    test_dir = _TEST_ROOT_DIR + "100"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()


def test_bucket_100_3():
    # given
    input_file, expected_file = ("input3.txt", "answer3.txt")
    test_dir = _TEST_ROOT_DIR + "100"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()


def test_bucket_100_5():
    # given
    input_file, expected_file = ("input5.txt", "answer5.txt")
    test_dir = _TEST_ROOT_DIR + "100"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()


def test_bucket_100_6():
    # given
    input_file, expected_file = ("input6.txt", "answer6.txt")
    test_dir = _TEST_ROOT_DIR + "100"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()


def test_bucket_100_7():
    # given
    input_file, expected_file = ("input7.txt", "answer7.txt")
    test_dir = _TEST_ROOT_DIR + "100"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()


def test_bucket_100_8():
    # given
    input_file, expected_file = ("input8.txt", "answer8.txt")
    test_dir = _TEST_ROOT_DIR + "100"
    input, expected = _get_inputs(
        os.path.join(test_dir, input_file), os.path.join(test_dir, expected_file)
    )

    # when
    answer = compute(input)

    # then
    assert expected.rstrip() == answer.rstrip()
