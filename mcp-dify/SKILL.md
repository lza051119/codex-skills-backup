---
name: mcp-dify
description: Run Dify workflows/apps that are published as MCP servers, straight from the shell. Use when the user wants to invoke a Dify app — summarize tech news, analyze text/sentiment, OCR a card, run any Dify workflow — and get its result back. Can list the available Dify tools and call any of them by name with JSON arguments.
---

# mcp-dify

Calls Dify apps/workflows that have been exposed as MCP servers (via Dify's "MCP Server"
plugin endpoints), from the shell. No Dify SDK is required — the bundled script speaks the
MCP JSON-RPC handshake over HTTP with plain `curl`.

This is a **knowledge-layer skill**: it just runs `curl` through the shell tool. It is NOT
governed by any AgentHub lease / capability control (shell calls bypass that by design). If
you need governance, use the Service-command version of this bridge instead.

## Configuration

The bundled script `scripts/dify_mcp.sh` reads two values. Defaults are baked in for the
`科技新闻摘要` app; override with environment variables to point at a different Dify app.

| Env var | Meaning | Default |
|---|---|---|
| `DIFY_MCP_URL` | The Streamable-HTTP MCP endpoint (the URL ending in `/mcp`) | the `科技新闻摘要` endpoint |
| `DIFY_MCP_TOKEN` | Bearer token set on that endpoint (use `""` if you left it empty) | `sk-mytoken123` |

To add another Dify app: in Dify open the **MCP Server** plugin → API 端点 → `+` → create a new
endpoint pointing at that app → copy its `/mcp` URL → run this script with `DIFY_MCP_URL` set
to that URL.

## Usage

Run the bundled script with the shell/Bash tool. Paths are relative to **this skill's
directory** — use the absolute skill directory path the harness gives you.

**List the available tools** (names + input schemas):

```bash
bash scripts/dify_mcp.sh list
```

**Call a tool** — `arguments` must match that tool's input schema (for chat apps include `query`):

```bash
bash scripts/dify_mcp.sh call tech_news_summary '{"query":"today AI news"}'
```

**Non-ASCII (中文) arguments**: inline Chinese can be mangled by the shell's encoding (notably
Git Bash on Windows). Write the arguments JSON to a UTF-8 file and pass it with a leading `@`:

```bash
# args.json (UTF-8):  {"query":"今天的AI新闻"}
bash scripts/dify_mcp.sh call tech_news_summary @args.json
```

## Output

Returns the raw MCP JSON-RPC result. The model's answer is under `result.content[0].text`
(JSON-escaped Unicode). For human-readable output pipe through a JSON tool, e.g.:

```bash
bash scripts/dify_mcp.sh call tech_news_summary '{"query":"hi"}' | python -m json.tool
```

## Notes

- Treat the MCP URL + token like an API key. Don't commit a real production token to a shared
  repo — keep it in `DIFY_MCP_TOKEN` instead of the script default.
- Portable: this folder works as-is in **Claude Code** too — drop it into
  `~/.claude/skills/mcp-dify/` and the same `list` / `call` commands work.
- The default endpoint requires the token `sk-mytoken123`. If you cleared the token on the
  Dify endpoint, set `DIFY_MCP_TOKEN=""`.
