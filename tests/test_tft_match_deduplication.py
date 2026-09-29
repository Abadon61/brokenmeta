"""Synthetic tests for regional Riot match aggregation (no API calls)."""
from __future__ import annotations

import sys
import importlib.util
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# The aggregation tests are offline. The bundled Python runtime used by some
# contributors may not have the repository's HTTP/.env requirements installed;
# provide import-only stubs in that case (none of their methods are called).
if importlib.util.find_spec("requests") is None:
    sys.modules["requests"] = types.ModuleType("requests")
if importlib.util.find_spec("dotenv") is None:
    dotenv_stub = types.ModuleType("dotenv")
    dotenv_stub.load_dotenv = lambda: None
    sys.modules["dotenv"] = dotenv_stub

from tft_tracker.collector import BracketSample, collect_bracket
from tft_tracker.pipeline import _aggregate_bracket_samples, compute_full_payload


def make_match(match_id: str, puuid: str = "player-1") -> dict:
    return {
        "metadata": {"match_id": match_id},
        "info": {
            "queueId": 1100,
            "tft_set_core_name": "TFT_TEST",
            "participants": [{
                "puuid": puuid,
                "placement": 1,
                "traits": [],
                "units": [],
            }],
        },
    }


def sample(region: str, tier: str, matches: list[dict], *, fallback: bool = False) -> BracketSample:
    return BracketSample(
        region=region,
        tier=tier,
        source_tier="DIAMOND" if fallback else tier,
        source_division="I" if fallback else None,
        used_fallback=fallback,
        matches=matches,
    )


class MatchDeduplicationTests(unittest.TestCase):
    def aggregate(self, samples: list[BracketSample], regions=None, tiers=None):
        return _aggregate_bracket_samples(
            samples,
            regions or list(dict.fromkeys(item.region for item in samples)),
            tiers or list(dict.fromkeys(item.tier for item in samples)),
        )

    def test_same_match_discovered_in_two_brackets_is_aggregated_once(self):
        match = make_match("EUW1_shared")
        all_matches, by_region, by_tier, _ = self.aggregate([
            sample("EUW", "DIAMOND", [match]),
            sample("EUW", "MASTER", [match]),
        ])

        self.assertEqual([m["metadata"]["match_id"] for m in all_matches], ["EUW1_shared"])
        self.assertEqual(len(by_region["EUW"]), 1)
        # The match has no rank in match-v1 and came from conflicting brackets.
        self.assertEqual(by_tier["DIAMOND"], [])
        self.assertEqual(by_tier["MASTER"], [])

    def test_same_match_discovered_in_three_brackets_is_aggregated_once(self):
        match = make_match("EUW1_three")
        all_matches, by_region, _, _ = self.aggregate([
            sample("EUW", "DIAMOND", [match]),
            sample("EUW", "MASTER", [match]),
            sample("EUW", "GRANDMASTER", [match]),
        ])

        self.assertEqual(len(all_matches), 1)
        self.assertEqual(len(by_region["EUW"]), 1)

    def test_apex_fallback_retains_diamond_source_and_is_not_apex_rank_data(self):
        proxy_match = make_match("EUW1_proxy")

        class FakeRiotClient:
            def get_apex_league(self, platform, tier):
                return {"entries": []}

            def get_league_entries(self, platform, tier, division, page=1):
                self.requested_fallback = (platform, tier, division)
                return [{"puuid": "diamond-player"}]

            def get_match_ids_by_puuid(self, regional, puuid, count):
                return ["EUW1_proxy"]

            def get_match(self, regional, match_id):
                return proxy_match

        client = FakeRiotClient()
        apex_sample = collect_bracket(client, "EUW", "CHALLENGER")
        self.assertEqual(client.requested_fallback, ("euw1", "DIAMOND", "I"))
        self.assertTrue(apex_sample.used_fallback)
        self.assertEqual((apex_sample.source_tier, apex_sample.source_division), ("DIAMOND", "I"))
        self.assertEqual(apex_sample.matches, [proxy_match])

        all_matches, by_region, by_tier, counts = self.aggregate([
            sample("EUW", "MASTER", [proxy_match], fallback=True),
            sample("EUW", "GRANDMASTER", [proxy_match], fallback=True),
            sample("EUW", "CHALLENGER", [proxy_match], fallback=True),
        ])

        self.assertEqual(len(all_matches), 1)
        self.assertEqual(len(by_region["EUW"]), 1)
        self.assertTrue(all(tier_matches == [] for tier_matches in by_tier.values()))
        self.assertEqual(counts[0]["matches_assigned_to_rank_bucket"], 0)

    def test_diamond_match_repeated_by_apex_fallback_stays_diamond_only(self):
        shared_match = make_match("EUW1_diamond_and_fallback")

        class FakeRiotClient:
            def get_apex_league(self, platform, tier):
                return {"entries": []}

            def get_league_entries(self, platform, tier, division, page=1):
                return [{"puuid": "diamond-player"}]

            def get_match_ids_by_puuid(self, regional, puuid, count):
                return ["EUW1_diamond_and_fallback"]

            def get_match(self, regional, match_id):
                return shared_match

        fallback_sample = collect_bracket(FakeRiotClient(), "EUW", "MASTER")
        diamond_sample = sample("EUW", "DIAMOND", [shared_match])
        all_matches, by_region, by_tier, _ = self.aggregate(
            [diamond_sample, fallback_sample],
            regions=["EUW"],
            tiers=["DIAMOND", "MASTER"],
        )

        self.assertEqual(len(all_matches), 1)
        self.assertEqual(len(by_region["EUW"]), 1)
        self.assertEqual(by_tier["DIAMOND"], [shared_match])
        self.assertEqual(by_tier["MASTER"], [])
        self.assertTrue(fallback_sample.used_fallback)
        self.assertEqual(fallback_sample.source_tier, "DIAMOND")
        self.assertEqual(fallback_sample.source_division, "I")
        self.assertIn("used DIAMOND I as a high-elo proxy", fallback_sample.fallback_note)

    def test_same_match_id_in_different_regions_remains_one_per_region(self):
        all_matches, by_region, _, _ = self.aggregate([
            sample("NA", "DIAMOND", [make_match("NA1_same")]),
            sample("BR", "DIAMOND", [make_match("NA1_same")]),
        ])

        self.assertEqual(len(all_matches), 2)
        self.assertEqual(len(by_region["NA"]), 1)
        self.assertEqual(len(by_region["BR"]), 1)

    def test_distinct_match_ids_with_same_players_are_both_kept(self):
        all_matches, by_region, by_tier, _ = self.aggregate([
            sample("EUW", "DIAMOND", [make_match("EUW1_first", "same-player")]),
            sample("EUW", "DIAMOND", [make_match("EUW1_second", "same-player")]),
        ])

        self.assertEqual(len(all_matches), 2)
        self.assertEqual(len(by_region["EUW"]), 2)
        self.assertEqual(len(by_tier["DIAMOND"]), 2)

    def test_aggregated_population_has_no_duplicate_ids_before_statistics(self):
        repeated = make_match("EUW1_repeat")
        samples = [
            sample("EUW", "DIAMOND", [repeated, make_match("EUW1_other")]),
            sample("EUW", "DIAMOND", [repeated]),
        ]
        all_matches, by_region, by_tier, _ = self.aggregate(samples)

        for population in (all_matches, by_region["EUW"], by_tier["DIAMOND"]):
            ids = [match["metadata"]["match_id"] for match in population]
            self.assertEqual(len(ids), len(set(ids)))
        payload = compute_full_payload(
            all_matches,
            want_matchups=False,
            want_champions=False,
            image_map={},
        )
        self.assertEqual(payload["total_matches"], 2)
        self.assertEqual(payload["total_participants"], 2)


if __name__ == "__main__":
    unittest.main()
