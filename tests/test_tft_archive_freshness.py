"""Focused tests for TFT observation dates and the comp archive."""
from __future__ import annotations

import importlib.util
import importlib.machinery
import json
import sys
import tempfile
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "site_build"), str(ROOT / "src")]

# These tests never perform HTTP or render a site. Keep imports usable in the
# bundled, dependency-light Python runtime without replacing installed libs.
if importlib.util.find_spec("requests") is None:
    requests_stub = types.ModuleType("requests")
    requests_stub.__spec__ = importlib.machinery.ModuleSpec("requests", loader=None)
    sys.modules["requests"] = requests_stub
if importlib.util.find_spec("jinja2") is None:
    jinja2_stub = types.ModuleType("jinja2")
    jinja2_stub.Environment = type("Environment", (), {})
    jinja2_stub.FileSystemLoader = type("FileSystemLoader", (), {})
    sys.modules["jinja2"] = jinja2_stub
if importlib.util.find_spec("markupsafe") is None:
    markupsafe_stub = types.ModuleType("markupsafe")
    markupsafe_stub.Markup = str
    sys.modules["markupsafe"] = markupsafe_stub
if importlib.util.find_spec("dotenv") is None:
    dotenv_stub = types.ModuleType("dotenv")
    dotenv_stub.load_dotenv = lambda: None
    dotenv_stub.__spec__ = importlib.machinery.ModuleSpec("dotenv", loader=None)
    sys.modules["dotenv"] = dotenv_stub

import build_site
from tft_tracker import pipeline


def comp(key: str) -> dict:
    return {"key": key, "label": key, "tier": "A", "play_count": 20}


class ArchiveFreshnessTests(unittest.TestCase):
    def archive(self, comps: list[dict], previous: dict, observed_at: str | None = None):
        with patch.object(build_site, "load_comp_archive", return_value=previous):
            return build_site.build_hors_meta_comps(comps, observed_at=observed_at)

    def test_old_source_date_does_not_advance_to_site_build_date(self):
        class BuildClock:
            @classmethod
            def now(cls, tz=None):
                return datetime(2026, 9, 29, tzinfo=timezone.utc)

        with patch.object(build_site, "datetime", BuildClock):
            _, updated = self.archive([comp("old-source")], {}, "2026-09-22")

        self.assertEqual(updated["old-source"]["_last_seen"], "2026-09-22")

    def test_source_observation_date_sets_last_seen(self):
        previous = {"comp-a": {"_set": build_site.SET_LABEL, "_last_seen": "2026-09-10"}}
        _, updated = self.archive([comp("comp-a")], previous, "2026-09-22")

        self.assertEqual(updated["comp-a"]["_last_seen"], "2026-09-22")

    def test_missing_source_date_preserves_existing_archive_date(self):
        previous = {"comp-a": {"_set": build_site.SET_LABEL, "_last_seen": "2026-09-10"}}
        _, updated = self.archive([comp("comp-a")], previous)

        self.assertEqual(updated["comp-a"]["_last_seen"], "2026-09-10")

    def test_comp_leaving_live_list_keeps_its_historical_date(self):
        previous = {
            "comp-a": {
                **comp("comp-a"),
                "_set": build_site.SET_LABEL,
                "_last_seen": "2026-09-10",
            }
        }
        hors_meta, updated = self.archive([], previous)

        self.assertEqual(updated["comp-a"]["_last_seen"], "2026-09-10")
        self.assertEqual(hors_meta[0]["_last_seen"], "2026-09-10")

    def test_missing_source_and_history_do_not_invent_last_seen(self):
        _, updated = self.archive([comp("new-comp")], {})

        self.assertNotIn("_last_seen", updated["new-comp"])

    def test_from_cache_pipeline_output_does_not_claim_new_observation(self):
        class OfflineClient:
            request_count = 0

        class PipelineClock:
            @classmethod
            def now(cls, tz=None):
                return datetime(2026, 9, 29, 12, tzinfo=timezone.utc)

        match = {
            "metadata": {"match_id": "EUW1_cached"},
            "info": {"queueId": 1100, "tft_set_core_name": "TFT_TEST", "participants": []},
        }
        payload = {
            "total_matches": 1,
            "total_participants": 0,
            "comps": [],
            "regression": {},
        }

        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "tierlist.json"
            history_path = Path(tmp) / "comp_history.json"
            with (
                patch.object(pipeline, "RiotClient", return_value=OfflineClient()),
                patch.object(pipeline, "_load_matches_from_cache", return_value={"EUW": [match]}),
                patch.object(pipeline, "compute_full_payload", return_value=payload),
                patch.object(pipeline, "_append_comp_history"),
                patch.object(pipeline, "datetime", PipelineClock),
            ):
                pipeline.main([
                    "--from-cache", "--regions", "EUW", "--no-images", "--no-champions",
                    "--out", str(output_path), "--comp-history-out", str(history_path),
                ])

            written = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertIsNone(written["observed_at"])
        self.assertEqual(written["generated_at"], "2026-09-29T12:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
