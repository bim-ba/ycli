"""An option built from a set of values: the help names them and completion offers them."""

from typing import Literal

from ycli.cli.typedefs import known_values, values_argument, values_option

Order = Literal["asc", "ascending", "desc"] | str


def test_the_known_values_come_from_the_definition():
    assert known_values(Order) == ("asc", "ascending", "desc")
    assert known_values(str) == ()


def test_the_option_names_the_values_and_completes_them():
    option = values_option(Order, "--order", help="Sort direction.")
    assert option.help == "Sort direction. Known values: asc, ascending, desc."
    assert option.autocompletion("a") == ["asc", "ascending"]
    assert option.autocompletion("x") == []


def test_an_argument_names_the_values_and_completes_them():
    argument = values_argument(Order, metavar="ORDER", help="Sort direction.")
    assert argument.help == "Sort direction. Known values: asc, ascending, desc."
    assert argument.metavar == "ORDER"
    assert argument.autocompletion("d") == ["desc"]
