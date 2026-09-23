# Conditional provider guidance

Read this file only for a provider-backed pull request or when the user separately authorizes a provider action. Repository-specific instructions override these examples.

## Provider-neutral rules

- Pin the server-reported head commit before analysis. Record the PR number/URL, base branch, base/base-commit, head branch, head SHA, state, and current CI state.
- Treat branch names and CI status as mutable. Use exact SHAs in the review surface and refresh live state before the final report.
- Fetching for inspection may update local remote-tracking data; never checkout over a dirty worktree. Prefer a clean review worktree or fetch exact refs without switching.
- Reading metadata is part of review. Posting comments, resolving threads, approving, rejecting, closing, or merging changes external state and needs separate explicit authorization.
- Never place access tokens, cookies, authorization headers, credential files, or environment dumps in a manifest, prompt, report, or command line.

## Forgejo/Gitea with `tea` 0.15

Use the repository's configured login. Do not supply a token on the command line.

Pin exact base and head commits through the read-only API helper:

```text
tea api 'repos/{owner}/{repo}/pulls/<number>' --repo <owner/repo-or-local-path>
```

Read `base.ref`, `base.sha`, `head.ref`, `head.sha`, `state`, `mergeable`, and the PR URL from that JSON. Pass `base.sha` and `head.sha` to the surface collector. If either object is absent locally, fetch the advertised head repository/ref without switching branches, then verify the fetched SHA equals the API value; if it does not, refresh the API response and restart. The higher-level `tea pr --fields head` value is a branch name in 0.15, not a commit SHA.

Read a compact human-facing summary and CI field when useful:

```text
tea pr <number> --repo <owner/repo-or-local-path> --fields index,state,url,title,base,base-commit,head,mergeable,ci --output json
```

List candidates when the PR number is unknown:

```text
tea pr list --repo <owner/repo-or-local-path> --state all --fields index,state,url,title,base,base-commit,head,updated,ci --output json
```

Read existing inline review comments when they are part of the requested scope:

```text
tea pr review-comments <number> --repo <owner/repo-or-local-path> --fields id,path,line,body,reviewer,resolver,created,updated,url --output json
```

`tea pr approve`, `tea pr reject`, `tea pr review`, `tea pr reply`, `tea pr resolve`, `tea pr close`, and `tea pr merge` are mutating actions. Do not invoke them during report-only review. If the user later authorizes one, refresh PR head and CI first and ensure the reviewed manifest still matches that head.
