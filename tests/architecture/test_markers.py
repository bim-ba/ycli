"""The form of a ``# violation(<rule>): <reason>`` marker (docs/conventions/resources.md §7)."""

import re

from tests.architecture.scanners import CONVENTION_RULES, SRC, malformed_markers


def test_a_violation_marker_is_well_formed():
    """Every marker in the package names a known rule and stands right above a line of code.

    Whether the code below really departs from the rule is the business of that rule's own
    check, where it has one (``arch-9``); for a rule without a scanner the reviewer reads it.
    """
    wrong = [
        f"{path.relative_to(SRC)}:{finding}"
        for path in sorted(SRC.rglob("*.py"))
        for finding in malformed_markers(path.read_text(encoding="utf-8"))
    ]
    assert wrong == []


def test_the_marker_form_check_bites():
    """Prove-it: a trailing marker, an unknown rule and a marker above nothing are reported."""
    source = (
        "# violation(naming): one object\n"
        "def logs_get(): ...\n"
        "x = 1  # violation(arch-9): trailing\n"
        "# violation(arch-9) no colon\n"
        "y = 2\n"
        "# violation(taste): not a rule\n"
        "z = 3\n"
        "# violation(arch-3): reads\n"
        "\n"
        "w = 4\n"
        "# violation(arch-1): at the end\n"
    )
    assert malformed_markers(source) == [
        "3: not `# violation(<rule>): <reason>` on a line of its own",
        "4: not `# violation(<rule>): <reason>` on a line of its own",
        "6: unknown rule 'taste'",
        "8: no line of code right below",
        "11: no line of code right below",
    ]


def test_the_rule_of_the_editor_names_the_rules_this_check_names():
    """The ast-grep rule `violation-marker-form` shows a wrong marker as it is typed.

    It reads the text of the comment; that a marker stands on a line of its own, right above
    code, is about lines and stays with the check above. Both name one set of rules.
    """
    rule = (SRC.parents[1] / ".ast-grep/rules/violation-marker-form.yml").read_text("utf-8")
    (named,) = re.findall(r"violation\\\(\((.+?)\)\\\): ", rule)
    assert set(named.split("|")) == {"arch-[1-9]", *CONVENTION_RULES}
