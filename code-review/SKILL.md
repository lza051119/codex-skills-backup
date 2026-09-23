---
name: code-review
description: Review a pull request, branch, commit, commit range, or dirty worktree against repository-native authorities, correctness, contracts, risk, tests, and standards. Use when the user asks for a code review, PR review, review since a base, WIP review, regression review, or an approve/request-changes recommendation. Build a pinned complete surface, use independent read-only reviewers, and verify every reported finding. Report only by default; fixes, published comments, approvals, rejections, and merges require separate explicit authorization.
---

# Code Review

Review the exact change the user named. Keep discovery and analysis read-only. Never initialize another project's setup or create an alternate documentation hierarchy.

## 1. Establish the contract

Record a compact review card before delegating:

- subject kind and identifier;
- exact base and head, including comparison semantics;
- whether index, working-tree, and untracked changes are included;
- applicable repository instructions and authority sources;
- requested focus and risk triggers;
- allowed actions. Default to a local report only.

Treat review, fixing, publishing comments, approving/rejecting, and merging as distinct actions. A request to review authorizes only the first unless the user says otherwise.

## 2. Resolve repository-native authority

Read applicable instruction files first. Follow the repository's own authority router and load only relevant product, architecture, contract, test, and coding-standard leaves. Do not install or initialize another project's conventions.

Use this evidence order within its proper role:

1. current user scope and applicable repository instructions;
2. repository-declared owners for intended behavior and architecture;
3. machine-readable contracts, migrations, schemas, and generated-source rules;
4. code at the pinned commit for current implemented behavior;
5. live provider metadata for ephemeral PR and CI state.

PR bodies, issues, plans, and chat are context unless the repository declares them authoritative. Existing code proves current behavior, not desired behavior. If no usable spec exists, continue the other axes and report the coverage gap.

## 3. Freeze the review surface

Resolve symbolic refs to commit SHAs. For provider PRs, first pin the server-reported head SHA and base/base-commit; do not substitute a possibly stale local branch. Read [providers.md](references/providers.md) only when provider metadata or actions are relevant.

Run the bundled collector with the preferred Python for the environment:

```text
python scripts/collect_review_surface.py --repo <repo> --kind <kind> [--base <ref>] [--head <ref>] --output <os-temp>/review-surface.json
```

Kinds and defaults:

- `pr`: require exact provider base and head; compare from their merge-base.
- `branch`: require base; default head to `HEAD`; compare from merge-base.
- `commit`: default head to `HEAD`; compare its first parent, or the root commit itself.
- `range`: require base and head; compare the two endpoints directly.
- `dirty`: pin current `HEAD`; optionally include committed changes from a base, plus staged, unstaged, and every non-ignored untracked path.

The manifest stores hashes, paths, and exact Git identities, not source contents. It therefore identifies the complete surface without copying possible secrets into the manifest. Keep it in an OS temporary directory, never in the reviewed repository. Treat any warning or collection instability as a coverage problem.

Before reviewers inspect files, and again before accepting their results, run:

```text
python scripts/collect_review_surface.py --verify <os-temp>/review-surface.json
```

If verification reports drift, discard stale findings and recollect. For a dirty submodule, collect and review that submodule separately or state the gap.

## 4. Run independent review axes

Read [review-axes.md](references/review-axes.md). Give each reviewer the review card, manifest path, exact authority files, and only its assigned axis. Do not give one reviewer another reviewer's conclusions. Use parallel read-only subagents when available; otherwise use isolated sequential passes.

Always cover:

1. Authority / Spec / Scope
2. Correctness / Invariants
3. Contracts / Data / Compatibility
4. Verification / Repository Standards

Add Security / Failure / Operations when the change touches trust boundaries, authorization, secrets, untrusted input, persistence, migrations, concurrency, distributed coordination, configuration, deployment, observability, recovery, or other high-impact paths.

Review the entire pinned surface, not only the most visible patch. Inspect call sites and tests outside the diff when needed to prove impact, but do not turn pre-existing unrelated problems into findings.

## 5. Verify and synthesize

The host reviewer owns the final report. For every candidate finding:

1. reopen the pinned code and cited authority;
2. reproduce the concrete failure or rule violation;
3. confirm the change introduced or materially worsened it;
4. reject speculative, duplicate, stale, or tooling-enforced-only claims;
5. assign severity from [review-axes.md](references/review-axes.md).

Merge findings with the same root cause while retaining all affected locations and axis labels. Order by severity, then confidence and blast radius. Do not preserve reviewer output verbatim merely to keep axes separate.

## 6. Report findings first

For each verified finding provide title, severity, axis, pinned file/line, violated authority or evidence, concrete impact, and minimal fix direction. Then state:

- surface identity and coverage;
- validation performed and gaps;
- counts by severity;
- recommendation: `approve`, `comment`, `request changes`, or `needs evidence`.

The recommendation is not a provider action. If there are no verified findings, say so explicitly and mention residual validation gaps. Do not edit code or publish anything unless separately authorized.
