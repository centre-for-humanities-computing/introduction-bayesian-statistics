"""Derive the exercise notebooks from the solution notebooks (and optionally execute them).

The solution notebooks in notebooks/solutions/ are the single source of truth.
Exercise cells are tagged `solution`; in the exercise version their content is
replaced by the cell's `scaffold` metadata (or a default placeholder), and all
outputs are cleared.

    uv run python notebooks/build_notebooks.py            # regenerate exercise notebooks
    uv run python notebooks/build_notebooks.py --execute  # run solutions first, then regenerate

To mark a cell as an exercise in Jupyter: add the tag `solution` to the cell, and
optionally a `scaffold` entry in its metadata with the starter code/text.
"""

import argparse
from pathlib import Path

import nbformat

HERE = Path(__file__).resolve().parent
SOLUTIONS = HERE / "solutions"
TAG = "solution"
DEFAULT_SCAFFOLD = {"code": "# ✏️ Your code here", "markdown": "✏️ **Your answer:** …"}


def execute(path: Path, timeout: int = 900) -> None:
    from nbclient import NotebookClient

    nb = nbformat.read(path, as_version=4)
    NotebookClient(
        nb,
        timeout=timeout,
        kernel_name="python3",
        resources={"metadata": {"path": str(path.parent)}},
    ).execute()
    nbformat.write(nb, path)
    print(f"executed {path.relative_to(HERE.parent)}")


def make_exercise(src: Path) -> Path:
    nb = nbformat.read(src, as_version=4)
    for cell in nb.cells:
        tags = cell.metadata.get("tags", [])
        if TAG in tags:
            cell.source = cell.metadata.get(
                "scaffold", DEFAULT_SCAFFOLD[cell.cell_type]
            )
            cell.metadata.pop("scaffold", None)
            tags.remove(TAG)
            if not tags:
                cell.metadata.pop("tags")
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
    first = nb.cells[0]
    first.source = (
        first.source.replace(" (solutions)", "")
        .replace("notebooks/solutions/", "notebooks/")
        .replace("_solutions.ipynb", ".ipynb")
    )
    out = HERE / src.name.replace("_solutions", "")
    nbformat.write(nb, out)
    print(f"wrote     {out.relative_to(HERE.parent)}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--execute", action="store_true", help="execute the solution notebooks first"
    )
    args = parser.parse_args()
    for src in sorted(SOLUTIONS.glob("*_solutions.ipynb")):
        if args.execute:
            execute(src)
        make_exercise(src)


if __name__ == "__main__":
    main()
