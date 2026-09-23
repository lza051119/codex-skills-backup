#!/usr/bin/env python3
"""Create or verify a read-only, content-free identity manifest for a Git review surface."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
GIT_DIFF_FLAGS = ["--binary", "--full-index", "--no-ext-diff", "--no-textconv"]


class SurfaceError(RuntimeError):
    pass


def run_git(repo: Path, args: Iterable[str], *, input_bytes: bytes | None = None) -> bytes:
    command = ["git", "-C", str(repo), *args]
    completed = subprocess.run(
        command,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise SurfaceError(f"git command failed ({' '.join(args)}): {detail}")
    return completed.stdout


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve_repo(path: str) -> Path:
    candidate = Path(path).resolve()
    root = run_git(candidate, ["rev-parse", "--show-toplevel"]).decode().strip()
    return Path(root).resolve()


def resolve_commit(repo: Path, ref: str, label: str) -> str:
    value = run_git(repo, ["rev-parse", "--verify", f"{ref}^{{commit}}"])
    resolved = value.decode().strip()
    if not resolved:
        raise SurfaceError(f"{label} did not resolve to a commit: {ref}")
    return resolved


def nul_paths(data: bytes) -> list[str]:
    return sorted(
        item.decode("utf-8", "surrogateescape")
        for item in data.split(b"\0")
        if item
    )


def patch_identity(patch: bytes, paths: list[str]) -> dict[str, Any]:
    return {
        "patch_sha256": sha256(patch),
        "patch_bytes": len(patch),
        "paths": paths,
    }


def normal_diff(repo: Path, start: str, end: str) -> dict[str, Any]:
    patch = run_git(repo, ["diff", *GIT_DIFF_FLAGS, start, end, "--"])
    paths = nul_paths(run_git(repo, ["diff", "--name-only", "-z", start, end, "--"]))
    commits = run_git(repo, ["rev-list", "--reverse", f"{start}..{end}"]).decode().splitlines()
    return {"from_sha": start, "to_sha": end, "commits": commits, **patch_identity(patch, paths)}


def root_commit_diff(repo: Path, commit: str) -> dict[str, Any]:
    patch = run_git(
        repo,
        ["diff-tree", "--root", "--no-commit-id", "-p", *GIT_DIFF_FLAGS, commit, "--"],
    )
    paths = nul_paths(
        run_git(repo, ["diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "-z", commit, "--"])
    )
    return {"from_sha": None, "to_sha": commit, "commits": [commit], **patch_identity(patch, paths)}


def status_mentions_submodule(status: bytes) -> bool:
    for record in status.split(b"\0"):
        if not record.startswith((b"1 ", b"2 ", b"u ")):
            continue
        fields = record.split(b" ", 3)
        if len(fields) >= 3 and fields[2].startswith(b"S"):
            return True
    return False


def committed_surface(
    repo: Path,
    kind: str,
    base_sha: str | None,
    head_sha: str,
    comparison: str,
) -> tuple[dict[str, Any] | None, str | None, str]:
    if kind == "commit":
        parents = run_git(repo, ["rev-list", "--parents", "-n", "1", head_sha]).decode().split()
        if len(parents) == 1:
            return root_commit_diff(repo, head_sha), None, "root"
        parent = parents[1]
        return normal_diff(repo, parent, head_sha), parent, "first-parent"

    if base_sha is None:
        return None, None, "none"

    if comparison == "merge-base":
        start = run_git(repo, ["merge-base", base_sha, head_sha]).decode().strip()
        if not start:
            raise SurfaceError("base and head have no merge-base")
    else:
        start = base_sha
    return normal_diff(repo, start, head_sha), start, comparison


def index_surface(repo: Path, head_sha: str) -> dict[str, Any]:
    patch = run_git(repo, ["diff", "--cached", *GIT_DIFF_FLAGS, head_sha, "--"])
    paths = nul_paths(run_git(repo, ["diff", "--cached", "--name-only", "-z", head_sha, "--"]))
    return {"from_sha": head_sha, "to": "index", **patch_identity(patch, paths)}


def worktree_surface(repo: Path) -> dict[str, Any]:
    patch = run_git(repo, ["diff", *GIT_DIFF_FLAGS, "--"])
    paths = nul_paths(run_git(repo, ["diff", "--name-only", "-z", "--"]))
    return {"from": "index", "to": "worktree", **patch_identity(patch, paths)}


def hash_untracked(repo: Path) -> list[dict[str, Any]]:
    paths = nul_paths(run_git(repo, ["ls-files", "--others", "--exclude-standard", "-z"]))
    records: list[dict[str, Any]] = []
    for relative in paths:
        path = repo / relative
        if path.is_symlink():
            target = os.readlink(path).encode("utf-8", "surrogateescape")
            records.append(
                {"path": relative, "kind": "symlink", "bytes": len(target), "sha256": sha256(target)}
            )
        elif path.is_file():
            digest = hashlib.sha256()
            size = 0
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    size += len(chunk)
                    digest.update(chunk)
            records.append(
                {"path": relative, "kind": "file", "bytes": size, "sha256": digest.hexdigest()}
            )
        else:
            records.append({"path": relative, "kind": "other", "bytes": None, "sha256": None})
    return records


def fingerprint(subject: dict[str, Any], surface: dict[str, Any]) -> str:
    identity = {
        "subject": {
            "kind": subject["kind"],
            "head_sha": subject["head_sha"],
            "base_sha": subject["base_sha"],
            "comparison_base_sha": subject["comparison_base_sha"],
            "comparison": subject["comparison"],
        },
        "surface": surface,
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return sha256(encoded)


def collect_once(
    repo: Path,
    kind: str,
    base_input: str | None,
    head_input: str,
    comparison: str,
) -> dict[str, Any]:
    head_sha = resolve_commit(repo, head_input, "head")
    base_sha = resolve_commit(repo, base_input, "base") if base_input else None

    if kind == "dirty":
        checked_out = resolve_commit(repo, "HEAD", "checked-out HEAD")
        if head_sha != checked_out:
            raise SurfaceError("dirty review head must be the currently checked-out HEAD")

    committed, comparison_base_sha, effective_comparison = committed_surface(
        repo, kind, base_sha, head_sha, comparison
    )
    subject = {
        "kind": kind,
        "repo_root": str(repo),
        "base_input": base_input,
        "base_sha": base_sha,
        "head_input": head_input,
        "head_sha": head_sha,
        "comparison_base_sha": comparison_base_sha,
        "comparison": effective_comparison,
    }
    surface: dict[str, Any] = {"committed": committed}
    warnings: list[str] = []

    if kind == "dirty":
        surface["index"] = index_surface(repo, head_sha)
        surface["worktree"] = worktree_surface(repo)
        surface["untracked"] = hash_untracked(repo)
        status = run_git(repo, ["status", "--porcelain=v2", "-z", "--untracked-files=all"])
        surface["status_sha256"] = sha256(status)
        surface["status_bytes"] = len(status)
        if status_mentions_submodule(status):
            warnings.append("submodule state is present; collect changed submodules separately")

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "collector": "collect_review_surface.py",
        "subject": subject,
        "surface": surface,
        "state_fingerprint": fingerprint(subject, surface),
        "warnings": warnings,
        "content_policy": "identity-only; source and patch contents are not embedded",
    }
    return manifest


def collect_stable(
    repo: Path,
    kind: str,
    base_input: str | None,
    head_input: str,
    comparison: str,
) -> dict[str, Any]:
    first = collect_once(repo, kind, base_input, head_input, comparison)
    if kind != "dirty":
        return first
    second = collect_once(repo, kind, base_input, head_input, comparison)
    if first["state_fingerprint"] != second["state_fingerprint"]:
        raise SurfaceError("review surface changed while it was being collected; retry when stable")
    return second


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SurfaceError(f"cannot read manifest: {exc}") from exc
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise SurfaceError(f"unsupported schema_version: {manifest.get('schema_version')!r}")
    return manifest


def write_manifest_outside_repo(repo: Path, output: Path, rendered: str) -> None:
    try:
        output.relative_to(repo)
    except ValueError:
        pass
    else:
        raise SurfaceError("--output must be outside the reviewed repository; use an OS temporary path")

    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
    except FileExistsError as exc:
        raise SurfaceError(f"refusing to overwrite existing manifest: {output}") from exc


def verify(path: Path) -> int:
    expected = load_manifest(path)
    subject = expected.get("subject", {})
    repo = resolve_repo(subject.get("repo_root", "."))
    kind = subject.get("kind")
    if kind not in {"pr", "branch", "commit", "range", "dirty"}:
        raise SurfaceError(f"unsupported manifest kind: {kind!r}")

    base = subject.get("base_sha")
    head = subject.get("head_sha")
    comparison = subject.get("comparison")
    if kind == "commit":
        comparison = "direct"
    elif comparison not in {"merge-base", "direct", "none"}:
        raise SurfaceError(f"unsupported comparison: {comparison!r}")

    actual = collect_stable(repo, kind, base, head, comparison)
    matched = actual["state_fingerprint"] == expected.get("state_fingerprint")
    result = {
        "matched": matched,
        "expected_fingerprint": expected.get("state_fingerprint"),
        "actual_fingerprint": actual["state_fingerprint"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if matched else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", metavar="MANIFEST", help="verify an existing manifest")
    parser.add_argument("--repo", default=".", help="path inside the Git repository")
    parser.add_argument("--kind", choices=["pr", "branch", "commit", "range", "dirty"])
    parser.add_argument("--base", help="base ref or exact commit")
    parser.add_argument("--head", default="HEAD", help="head ref or exact commit")
    parser.add_argument("--comparison", choices=["auto", "merge-base", "direct"], default="auto")
    parser.add_argument("--output", help="write JSON to this path; otherwise print it")
    args = parser.parse_args()
    if args.verify:
        return args
    if not args.kind:
        parser.error("--kind is required unless --verify is used")
    if args.kind in {"pr", "branch", "range"} and not args.base:
        parser.error(f"--base is required for --kind {args.kind}")
    return args


def main() -> int:
    args = parse_args()
    try:
        if args.verify:
            return verify(Path(args.verify).resolve())

        repo = resolve_repo(args.repo)
        if args.comparison == "auto":
            comparison = "direct" if args.kind == "range" else "merge-base"
        else:
            comparison = args.comparison
        if args.kind == "commit":
            comparison = "direct"
        manifest = collect_stable(repo, args.kind, args.base, args.head, comparison)
        rendered = json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
        if args.output:
            output = Path(args.output).resolve()
            write_manifest_outside_repo(repo, output, rendered)
        else:
            sys.stdout.write(rendered)
        return 0
    except SurfaceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
