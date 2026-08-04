"""Execute the publication notebook and save a rendered copy."""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_ROOT = Path(__file__).resolve().parent
SOURCE = ANALYSIS_ROOT / "notebooks/01_eeg_publication_analysis.ipynb"
OUTPUT = (
    ANALYSIS_ROOT
    / "outputs/reports/01_eeg_publication_analysis.executed.ipynb"
)


def main() -> None:
    notebook = nbformat.read(SOURCE, as_version=4)
    notebook.metadata.kernelspec = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook.metadata.language_info = {
        "name": "python",
        "version": "3",
    }
    client = NotebookClient(
        notebook,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(REPOSITORY_ROOT)}},
    )
    client.execute(cwd=str(REPOSITORY_ROOT))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, OUTPUT)
    print(f"Executed notebook successfully; wrote {OUTPUT}")


if __name__ == "__main__":
    main()
