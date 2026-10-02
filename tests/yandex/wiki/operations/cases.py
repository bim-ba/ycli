"""Contract cases for Wiki ``/operations`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent

CASES = [
    Case(
        "wiki.operations.clone_get",
        args=("task-5201",),
        cli=["wiki", "operations", "clone-get", "task-5201"],
        mcp=("wiki_operations_clone_get", {"task_id": "task-5201"}),
        exchanges=[
            (
                Sent("GET", "operations/clone/task-5201"),
                Reply(json={"status": "success", "result": {"page": {"id": 5202, "slug": "c"}}}),
            )
        ],
    ),
    Case(
        "wiki.operations.gridclone_get",
        args=("task-5301",),
        cli=["wiki", "operations", "gridclone-get", "task-5301"],
        mcp=("wiki_operations_gridclone_get", {"task_id": "task-5301"}),
        exchanges=[
            (
                Sent("GET", "operations/clone_inline_grid/task-5301"),
                Reply(json={"status": "in_progress", "progress": {"percentage": 0.25}}),
            )
        ],
    ),
    # GET /operations/move/{task_id} (undocumented).
    Case(
        "wiki.operations.move_get",
        args=("task-5401",),
        cli=["wiki", "operations", "move-get", "task-5401"],
        mcp=("wiki_operations_move_get", {"task_id": "task-5401"}),
        exchanges=[
            (
                Sent("GET", "operations/move/task-5401"),
                Reply(json={"status": "success", "result": {"page_count": 4}}),
            )
        ],
    ),
]
