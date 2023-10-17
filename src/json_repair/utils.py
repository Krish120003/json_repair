import re


def is_whitespace(char: str) -> bool:
    """
    Check if a character is a whitespace or escape character.

    Args:
        char (str): The character to check.

    Returns:
        bool: True if the character is a whitespace or escape character, False otherwise.
    """
    return char == " " or char == "\n" or char == "\t" or char == "\r"


def is_special_whitespace(char: str) -> bool:
    """
    Determines if a given character is a special whitespace character.

    Args:
        char (str): The character to check.

    Returns:
        bool: True if the character is a special whitespace character, False otherwise.
    """
    unicode_char = ord(char)
    return (
        unicode_char == 160
        or (unicode_char >= 8192 and unicode_char <= 8202)
        or unicode_char == 8239
        or unicode_char == 8287
        or unicode_char == 12288
    )


def is_quote(char: str) -> bool:
    """Given a character, determine if it is a variation of unicode quotes.

    Args:
        char (str): The character to check.

    Returns:
        bool: True if the character is a quote, False otherwise.
    """
    return (
        char == '"'
        or char == "“"
        or char == "”"
        or char == "‘"
        or char == "’"
        or char == "'"
        or char == "`"
        or char == "´"
    )


def is_end_quote(char: str) -> bool:
    """Given a character, determine if it is a variation of unicode end quotes.

    Args:
        char (str): The character to check.

    Returns:
        bool: True if the character is an end quote, False otherwise.
    """
    return char == '"' or char == "”" or char == "’" or char == "'"


def is_start_of_value(char: str) -> bool:
    """
    Check if a character is the start of a JSON value.

    Args:
        char (str): The character to check.

    Returns:
        bool: True if the character is the start of a JSON value, False otherwise.
    """
    regex_start_of_value = re.compile(r"^[[{\w-]$")
    return (regex_start_of_value.match(char) is not None) or (char and is_quote(char))
