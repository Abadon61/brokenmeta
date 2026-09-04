#!/usr/bin/env python
"""Entry point: `py run.py [options]`. See src/tft_tracker/pipeline.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from tft_tracker.pipeline import main  # noqa: E402

if __name__ == "__main__":
    main()
