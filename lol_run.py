#!/usr/bin/env python
"""Entry point: `py lol_run.py [options]`. See src/tft_tracker/lol_pipeline.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from tft_tracker.lol_pipeline import main  # noqa: E402

if __name__ == "__main__":
    main()
