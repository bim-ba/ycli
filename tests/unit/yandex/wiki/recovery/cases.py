"""Contract cases for Wiki ``/recovery_tokens`` (see tests/contract/)."""

from tests.contract import Case, Reply, Sent

TOKEN = "recovery-token-1"

CASES = [
    Case(
        "wiki.recovery.recover",
        args=(TOKEN,),
        cli=["wiki", "recovery", "recover", TOKEN],
        mcp=("wiki_recovery_recover", {"token": TOKEN}),
        exchanges=[
            (
                Sent("POST", f"recovery_tokens/{TOKEN}/recover"),
                Reply(json={"id": 5101, "slug": "eng/restored", "pages_count": 3}),
            )
        ],
    ),
]
