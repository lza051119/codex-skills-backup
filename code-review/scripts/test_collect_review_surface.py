#!/usr/bin/env python3
"""Self-contained tests for collect_review_surface.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("collect_review_surface.py")


def run(command: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=check)


def git(repo: Path, *args: str) -> str:
    return run(["git", *args], cwd=repo).stdout.strip()


class CollectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Review Test")
        git(self.repo, "config", "user.email", "review@example.invalid")
        (self.repo / "base.txt").write_text("base\n", encoding="utf-8")
        git(self.repo, "add", "base.txt")
        git(self.repo, "commit", "-q", "-m", "base")
        self.base = git(self.repo, "rev-parse", "HEAD")

        (self.repo / "committed.txt").write_text("committed\n", encoding="utf-8")
        git(self.repo, "add", "committed.txt")
        git(self.repo, "commit", "-q", "-m", "head")
        self.head = git(self.repo, "rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def collect(self, *args: str) -> dict:
        completed = run([sys.executable, str(SCRIPT), "--repo", str(self.repo), *args])
        return json.loads(completed.stdout)

    def test_range_pins_exact_endpoints(self) -> None:
        manifest = self.collect("--kind", "range", "--base", self.base, "--head", self.head)
        self.assertEqual(manifest["subject"]["base_sha"], self.base)
        self.assertEqual(manifest["subject"]["head_sha"], self.head)
        self.assertEqual(manifest["subject"]["comparison"], "direct")
        self.assertEqual(manifest["surface"]["committed"]["paths"], ["committed.txt"])
        self.assertEqual(manifest["surface"]["committed"]["commits"], [self.head])
        self.assertNotIn("patch", manifest["surface"]["committed"])

    def test_pr_and_branch_use_merge_base(self) -> None:
        for kind in ("pr", "branch"):
            with self.subTest(kind=kind):
                manifest = self.collect("--kind", kind, "--base", self.base, "--head", self.head)
                self.assertEqual(manifest["subject"]["comparison"], "merge-base")
                self.assertEqual(manifest["subject"]["comparison_base_sha"], self.base)
                self.assertEqual(manifest["surface"]["committed"]["paths"], ["committed.txt"])

    def test_commit_uses_first_parent(self) -> None:
        manifest = self.collect("--kind", "commit", "--head", self.head)
        self.assertEqual(manifest["subject"]["comparison"], "first-parent")
        self.assertEqual(manifest["subject"]["comparison_base_sha"], self.base)
        self.assertEqual(manifest["surface"]["committed"]["paths"], ["committed.txt"])

    def test_root_commit_is_reviewable(self) -> None:
        manifest = self.collect("--kind", "commit", "--head", self.base)
        self.assertEqual(manifest["subject"]["comparison"], "root")
        self.assertIsNone(manifest["subject"]["comparison_base_sha"])
        self.assertEqual(manifest["surface"]["committed"]["paths"], ["base.txt"])

    def test_output_inside_repo_is_rejected(self) -> None:
        output = self.repo / "surface.json"
        completed = run(
            [
                sys.executable,
                str(SCRIPT),
                "--repo",
                str(self.repo),
                "--kind",
                "commit",
                "--head",
                self.head,
                "--output",
                str(output),
            ],
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("outside the reviewed repository", completed.stderr)
        self.assertFalse(output.exists())

    def test_dirty_covers_and_detects_drift(self) -> None:
        (self.repo / "staged.txt").write_text("staged\n", encoding="utf-8")
        git(self.repo, "add", "staged.txt")
        (self.repo / "base.txt").write_text("changed\n", encoding="utf-8")
        (self.repo / "untracked.txt").write_text("untracked\n", encoding="utf-8")

        manifest_path = Path(self.temp.name) / "surface.json"
        run(
            [
                sys.executable,
                str(SCRIPT),
                "--repo",
                str(self.repo),
                "--kind",
                "dirty",
                "--base",
                self.base,
                "--output",
                str(manifest_path),
            ]
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["surface"]["index"]["paths"], ["staged.txt"])
        self.assertEqual(manifest["surface"]["worktree"]["paths"], ["base.txt"])
        self.assertEqual([item["path"] for item in manifest["surface"]["untracked"]], ["untracked.txt"])
        self.assertNotIn("untracked\\n", manifest_path.read_text(encoding="utf-8"))

        exact = run([sys.executable, str(SCRIPT), "--verify", str(manifest_path)], check=False)
        self.assertEqual(exact.returncode, 0, exact.stderr)
        self.assertTrue(json.loads(exact.stdout)["matched"])

        (self.repo / "untracked.txt").write_text("drifted\n", encoding="utf-8")
        drifted = run([sys.executable, str(SCRIPT), "--verify", str(manifest_path)], check=False)
        self.assertEqual(drifted.returncode, 1, drifted.stderr)
        self.assertFalse(json.loads(drifted.stdout)["matched"])


if __name__ == "__main__":
    unittest.main()
