"""An option built from a set of values: the help names them and completion offers them."""

from typing import Literal

from ycli.cli.typedefs import known_values, values_option

Order = Literal["asc", "ascending", "desc"] | str


def test_the_known_values_come_from_the_definition():
    assert known_values(Order) == ("asc", "ascending", "desc")
    assert known_values(str) == ()


def test_the_option_names_the_values_and_completes_them():
    option = values_option(Order, "--order", help="Sort direction.")
    assert option.help == "Sort direction. One of: asc, ascending, desc."
    assert option.autocompletion("a") == ["asc", "ascending"]
    assert option.autocompletion("x") == []
