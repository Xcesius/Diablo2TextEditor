import pytest

from column_letters import index_to_column_letters


@pytest.mark.parametrize(
    "idx,expected",
    [
        (0, "A"),
        (1, "B"),
        (25, "Z"),
        (26, "AA"),
        (27, "AB"),
        (51, "AZ"),
        (52, "BA"),
        (701, "ZZ"),
        (702, "AAA"),
    ],
)
def test_index_to_column_letters(idx, expected):
    assert index_to_column_letters(idx) == expected


def test_index_to_column_letters_errors():
    with pytest.raises(ValueError):
        index_to_column_letters(-1)
    with pytest.raises(TypeError):
        index_to_column_letters(3.14)  # type: ignore[arg-type]

