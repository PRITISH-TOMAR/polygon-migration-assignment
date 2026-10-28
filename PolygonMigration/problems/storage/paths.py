"""
Single source of truth for how test-case files are named in storage.

    test_cases/{problem_id}/{test_number}      # input
    test_cases/{problem_id}/{test_number}.a    # expected output

Test numbers are zero-padded to two digits (01, 02, ...), matching the
naming used by the original Azure implementation.
"""


def problem_prefix(problem_id):
    """Returns the folder prefix holding all files for a problem."""
    return f"test_cases/{problem_id}/"


def test_input_key(problem_id, test_number):
    """Returns the object key for a test case's input file."""
    return f"{problem_prefix(problem_id)}{test_number:02d}"


def test_output_key(problem_id, test_number):
    """Returns the object key for a test case's expected output file."""
    return f"{test_input_key(problem_id, test_number)}.a"


def checker_key(problem_id, filename):
    """Returns the object key for a custom checker file (source or binary)."""
    return f"{problem_prefix(problem_id)}{filename}"
