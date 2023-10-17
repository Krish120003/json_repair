from .utils import is_special_whitespace, is_start_of_value, is_whitespace, is_quote


class ParserError(Exception):
    def __init__(self, message: str, position: int):
        self.message = message
        self.position = position

    def __str__(self):
        return f"ParserError: {self.message} at position {self.position}"


class Parser:
    def __init__(self, json_string: str):
        self.input_json = json_string
        self.output = ""
        self.i = 0

    def _get(self, offset=0):
        try:
            return self.input_json[self.i + offset]
        except IndexError:
            raise ParserError("Unexpected end of input", self.i + offset)

    def repair(self) -> str:
        raise NotImplementedError

    def parse_value(self) -> bool:
        """
        Parses a JSON value from the input stream into the instance's output.

        Returns:
            bool: True if a JSON value was successfully parsed, False otherwise.
        """
        self.parse_whitespace_and_comments()

        processed = any(
            [
                self.parse_object(),
                self.parse_array(),
                self.parse_string(),
                self.parse_number(),
                self.parse_keyword(),
                self.parse_unquoted_string(),
            ]
        )
        self.parse_whitespace_and_comments()
        return processed

    def parse_whitespace_and_comments(self) -> bool:
        start = self.i

        changed = self.parse_whitespace()
        while True:
            changed = self.parse_comment()
            if changed:
                self.parse_whitespace()
            if not changed:
                break

        return self.i > start

    def parse_whitespace(self) -> bool:
        whitespace = ""

        while normal := is_whitespace(self._get()) or is_special_whitespace(
            self._get()
        ):
            if normal:
                whitespace += self._get()

            else:
                # repair: special whitespace with normal whitespace
                whitespace += " "

            self.i += 1

        if whitespace:
            self.output += whitespace
            return True

        return False

    def parse_comment(self) -> bool:
        # find a block comment
        # i.e. /* comment */

        if self._get() == "/" and self._get(1) == "*":
            while not (self._get() == "*" and self._get(1) == "/"):
                self.i += 1
            self.i += 2

            return True

        # find a line comment
        # i.e. // comment
        if self._get() == "/" and self._get(1) == "/":
            while self._get() != "\n":
                self.i += 1

            return True

        return False

    def parse_object(self) -> bool:
        if self._get() != "{":
            return False

        self.output += "{"
        self.i += 1
        self.parse_whitespace_and_comments()

        initial = True
        while self._get() != "}" and self.i < len(self.input_json):
            if not initial:
                processed_comma = self.parse_character(",")
                if not processed_comma:
                    # repair: missing comma
                    self._insert_before_last_whitespace(",")
                    pass

                self.parse_whitespace_and_comments()
            else:
                processed_comma = True
                initial = False

            processed_key = self.parse_string() or self.parse_unquoted_string()
            if not processed_key:
                if self._get() in "{[]}" or (self.i >= len(self.input_json)):
                    # repair: trailing comma
                    self._strip_last_occurrence(",")
                else:
                    raise ParserError(
                        "Expected string or unquoted string for Object key", self.i
                    )
                break

            self.parse_whitespace_and_comments()

            processed_colon = self.parse_character(":")
            if not processed_colon:
                if is_start_of_value(self._get()):
                    # repair: missing colon
                    self._insert_before_last_whitespace(":")

                else:
                    raise ParserError("Expected colon after Object key", self.i)

            processed_value = self.parse_value()
            if not processed_value:
                if processed_colon:
                    # repair: missing value
                    self.output += "null"
                else:
                    raise ParserError("Expected colon after Object key", self.i)

        if self._get() == "}":
            self.output += "}"
            self.i += 1
        else:
            self._insert_before_last_whitespace("}")

        return True

    def parse_character(self, char: str) -> bool:
        if self._get() != char:
            return False

        self.output += self._get()
        self.i += 1
        return True

    def parse_string(self, stop_at_delimiter=False) -> bool:
        if self._get() != "/":
            return False
        self.i += 1
        if is_quote(self._get()):
            # TODO
            pass

    def parse_number(self) -> bool:
        raise NotImplementedError

    def parse_array(self) -> bool:
        raise NotImplementedError

    def parse_keyword(self) -> bool:
        raise NotImplementedError

    def parse_unquoted_string(self) -> bool:
        raise NotImplementedError

    def _insert_before_last_whitespace(self, to_insert: str) -> None:
        index = len(self.output)

        if not is_whitespace(self.output[index - 1]):
            # no trailing whitespaces
            self.output += to_insert

        while is_whitespace(self.output[index - 1]):
            index -= 1

        self.output = self.output[:index] + to_insert + self.output[index:]

    def _strip_last_occurrence(self, to_strip: str) -> None:
        index = self.output.rfind(to_strip)
        if index == -1:
            return

        self.output = self.output[:index] + self.output[index + len(to_strip) :]
