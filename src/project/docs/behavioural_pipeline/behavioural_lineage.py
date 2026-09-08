"""Same figure as behavioural_grains.py."""

from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parent / "behavioural_grains.py"), run_name="__main__")
