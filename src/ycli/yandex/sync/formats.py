"""How a file is laid out: a Markdown file with a header, or a YAML file."""

from pathlib import PurePosixPath
from typing import Any, Protocol

import yaml

from ycli.yandex.sync.document import KIND_KEY, Parts, UnreadableFile

_FENCE = "---"


class FileFormat(Protocol):
    """One layout of a file: how its text is taken apart and put together again."""

    suffix: str

    def read(self, path: PurePosixPath, text: str) -> Parts:
        """Take ``text`` apart; refuse it with its path and line if it is not such a file."""
        ...

    def write(self, parts: Parts) -> str:
        """Put ``parts`` together as the text of a file."""
        ...


class _Dumper(yaml.SafeDumper):
    """Writes a text of several lines as a block, so a change of one line is one line of a diff."""


def _text(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


_Dumper.add_representer(str, _text)


def _mapping(path: PurePosixPath, text: str, *, offset: int) -> Parts:
    """The keys of a YAML mapping as parts; ``offset`` is how many lines of the file precede it."""
    try:
        node = yaml.compose(text, Loader=yaml.SafeLoader)
        keys: Any = yaml.safe_load(text)
    except yaml.MarkedYAMLError as error:
        line = error.problem_mark.line if error.problem_mark else 0
        raise UnreadableFile(path, line + 1 + offset, str(error.problem)) from None
    if not isinstance(node, yaml.MappingNode):
        raise UnreadableFile(path, 1 + offset, "the keys of a file are a YAML mapping")
    lines = {key.value: key.start_mark.line + 1 + offset for key, _ in node.value}
    kind = keys.pop(KIND_KEY, None)
    if not isinstance(kind, str):
        line = lines.get(KIND_KEY, 1)
        raise UnreadableFile(path, line, f"no `{KIND_KEY}` key says what kind it is")
    return Parts(path, kind, keys, lines=lines)


def _dump(parts: Parts) -> str:
    keys = {KIND_KEY: parts.kind, **parts.keys}
    return yaml.dump(keys, Dumper=_Dumper, sort_keys=False, allow_unicode=True)


class YAMLFile:
    r"""A file that is one YAML mapping: ``ycli``, the link keys, then the content.

    Examples:
        >>> from pathlib import PurePosixPath
        >>> text = "ycli: tracker/trigger\nid: 16\nname: Assign on create\n"
        >>> parts = YAMLFile().read(PurePosixPath("tracker/queues/DE/triggers/16.yaml"), text)
        >>> parts.kind, dict(parts.keys)
        ('tracker/trigger', {'id': 16, 'name': 'Assign on create'})
        >>> YAMLFile().write(parts) == text
        True
    """

    suffix = ".yaml"

    def read(self, path: PurePosixPath, text: str) -> Parts:
        """Take a YAML file apart.

        Args:
            path: Where the file lies, for an error.
            text: What the file holds.

        Returns:
            Its kind and its keys.
        """
        return _mapping(path, text, offset=0)

    def write(self, parts: Parts) -> str:
        """Put a YAML file together.

        Args:
            parts: The kind and the keys.

        Returns:
            The text of the file.

        Raises:
            TypeError: The parts carry a text: a kind with a body is a Markdown file.
        """
        if parts.text is not None:
            raise TypeError(f"{parts.kind} has a body: it is written as Markdown, not YAML")
        return _dump(parts)


class MarkdownWithHeader:
    r"""A Markdown file whose first lines, between two ``---``, are a YAML mapping.

    Examples:
        >>> from pathlib import PurePosixPath
        >>> text = "---\nycli: wiki/page\nid: 4821\ntitle: Onboarding\n---\n# First day\n"
        >>> parts = MarkdownWithHeader().read(PurePosixPath("wiki/team/onboarding.md"), text)
        >>> parts.kind, dict(parts.keys), parts.text
        ('wiki/page', {'id': 4821, 'title': 'Onboarding'}, '# First day\n')
        >>> MarkdownWithHeader().write(parts) == text
        True
    """

    suffix = ".md"

    def read(self, path: PurePosixPath, text: str) -> Parts:
        """Take a Markdown file apart.

        Args:
            path: Where the file lies, for an error.
            text: What the file holds.

        Returns:
            Its kind, the keys of its header and the text under it.

        Raises:
            UnreadableFile: The file has no header, or the header is not closed.
        """
        first, _, rest = text.partition("\n")
        if first != _FENCE:
            raise UnreadableFile(path, 1, f"a Markdown file starts with a header: `{_FENCE}`")
        lines = rest.split("\n")
        if _FENCE not in lines:
            raise UnreadableFile(path, len(lines) + 1, f"the header is not closed: no `{_FENCE}`")
        closing = lines.index(_FENCE)
        header = _mapping(path, "\n".join(lines[:closing]), offset=1)
        body = "\n".join(lines[closing + 1 :])
        return Parts(path, header.kind, header.keys, body, header.lines)

    def write(self, parts: Parts) -> str:
        """Put a Markdown file together.

        Args:
            parts: The kind, the keys of the header and the text under it.

        Returns:
            The text of the file.
        """
        return f"{_FENCE}\n{_dump(parts)}{_FENCE}\n{parts.text or ''}"
