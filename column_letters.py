def index_to_column_letters(index: int) -> str:
    """Convert a 0-based column index to Excel-style letters (A, B, ..., Z, AA, AB, ...).

    Args:
        index: Zero-based column index (0 => 'A').

    Returns:
        The Excel-style column label as a string.

    Raises:
        ValueError: If index is negative.
    """
    if not isinstance(index, int):
        raise TypeError("index must be an int")
    if index < 0:
        raise ValueError("index must be non-negative")

    # Excel-like base-26 with no zero digit: 0->A, 25->Z, 26->AA
    result = []
    n = index
    while True:
        n, rem = divmod(n, 26)
        result.append(chr(ord('A') + rem))
        if n == 0:
            break
        n -= 1  # Carry handling due to lack of zero digit in Excel columns
    return ''.join(reversed(result))

