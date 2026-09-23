# Handoff: <topic>

- Created: <YYYY-MM-DD HH:mm:ss offset>
- Previous snapshot: <repository-relative link, absolute non-repository path, or none>
- Ownership: <sending session> -> <receiving session or next session>
- State: <implementation incomplete | verification pending | blocked>
- Owning worktree: <absolute path>
- Branch: <branch or none with reason>
- PR: <URL and exact PR head, or none with reason>
- Base fingerprint: <merge-base or other fixed base SHA>
- Head fingerprint: <HEAD SHA>
- Working-tree fingerprint: <hash of HEAD + staged patch + unstaged patch + scoped untracked path/content hashes>

> This snapshot is disposable working memory. It is not product, architecture, implementation, review, CI, or verification authority.

## TL;DR

- <what is already complete>
- <what remains unproved or incomplete>
- <the main current constraint>

## Authority pointers

- Repository instructions: <AGENTS.md path>
- Navigation entry: <docs/README.md or repository equivalent>
- Product or specification authority: <path/URL + section>
- Architecture or decision authority: <path/URL + section>
- Candidate or change surface: <PR URL / commit / diff anchor>
- Verification evidence: <exact report path/URL, or none>

## Captured transient state

Observed at `<capture time>`; refresh all live state before relying on it.

- Working-tree status:

  ```text
  <exact git status --short output, or clean>
  ```

- Committed change summary: <link or concise scope>
- Staged state: <concise scope or none>
- Staged diff hash: <algorithm:value or none>
- Unstaged state: <concise scope or none>
- Unstaged diff hash: <algorithm:value or none>
- Scoped untracked files: <paths or none>
- Scoped untracked hash: <algorithm:value or none>
- Last local validation: `<exact command>` -> <pass | fail | not run>
- PR/CI state: <captured observation; must be refreshed>

## Decision delta

- <only decisions added or changed since Previous snapshot; write none if no delta>
- <mark every decision not yet reconciled into its authority as provisional>

Do not reproduce the conversation transcript or duplicate existing artifacts.

## Validity and invalidation

This snapshot becomes invalid if any of the following occurs:

- branch, base, head, PR scope, or authoritative specification differs from the fingerprints above;
- the worktree contains changes of unknown ownership;
- the sending session resumes mutation without transferring ownership back;
- a newer successor snapshot exists;
- the PR is merged or closed, or the task is completed, abandoned, or re-scoped.

## Boundaries

- Authorized scope: <what the receiving session may do>
- Explicitly not authorized: <commit/push/merge/deploy/rebase/cleanup or other actions not granted>
- Sensitive material: none included; use <credential source/setup reference> if access is needed.
- This file does not prove CI status, approval, Candidate verification, or current implementation behavior.

## Next action

<Exactly one bounded action. Start by validating the fingerprints if this is a receiving session.>

## Cleanup

After the task is merged, closed, or explicitly abandoned and durable facts are reconciled, remove this snapshot and its predecessor chain under the repository's normal cleanup rules. Branch and worktree cleanup remain separate actions requiring their own authorization and safety checks.
