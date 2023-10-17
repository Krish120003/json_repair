def parse(string):
    pass


class TestParse:
    """
    Tests for json parsing.
    """

    def test_object(self):
        assert parse('{"a": 1}') == {"a": 1}
