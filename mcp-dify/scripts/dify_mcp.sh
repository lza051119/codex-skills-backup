#!/usr/bin/env bash
# mcp-dify — call Dify apps/workflows exposed as MCP servers, straight from the shell.
#
# Config (override via environment):
#   DIFY_MCP_URL    Streamable-HTTP MCP endpoint (the URL ending in /mcp)
#   DIFY_MCP_TOKEN  Bearer token set on the Dify MCP endpoint ("" if you left it empty)
#
# Usage:
#   dify_mcp.sh list
#   dify_mcp.sh call <tool> '<json-args>'      # inline args (ASCII-safe)
#   dify_mcp.sh call <tool> @args.json         # args from a UTF-8 file (use for 中文 on Windows)
#
# MCP is stateful: every call does initialize -> notifications/initialized -> the request,
# carrying the Mcp-Session-Id header returned by initialize.
set -eu

URL="${DIFY_MCP_URL:-https://4xi3pntg77m2wf59.ai-plugin.io/mcp}"
TOKEN="${DIFY_MCP_TOKEN:-sk-mytoken123}"

CT='Content-Type: application/json'
AC='Accept: application/json, text/event-stream'
AUTH="Authorization: Bearer ${TOKEN}"

# initialize the MCP session; print the Mcp-Session-Id from the response headers
init_session() {
  curl -sS -D - -o /dev/null -X POST "$URL" -H "$CT" -H "$AC" -H "$AUTH" \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"dify-mcp-sh","version":"1"}}}' \
    | tr -d '\r' | awk -F': ' 'tolower($1)=="mcp-session-id"{print $2}'
}

# POST a JSON-RPC body (literal string, or @file) on an established session
post() { # $1=session  $2=data-or-@file
  curl -sS -X POST "$URL" -H "$CT" -H "$AC" -H "$AUTH" -H "Mcp-Session-Id: $1" --data-binary "$2"
}

require_session() {
  [ -n "${1:-}" ] || {
    echo "ERROR: no MCP session id returned — check DIFY_MCP_URL / DIFY_MCP_TOKEN (auth or URL is wrong)" >&2
    exit 1
  }
}

case "${1:-help}" in
  list)
    sid=$(init_session); require_session "$sid"
    post "$sid" '{"jsonrpc":"2.0","method":"notifications/initialized"}' >/dev/null
    post "$sid" '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'; echo
    ;;
  call)
    tool="${2:?usage: call <tool> '<json-args>'  |  call <tool> @args.json}"
    if [ "$#" -ge 3 ]; then raw="$3"; else raw='{}'; fi
    # @file -> read UTF-8 file; otherwise treat as literal JSON
    if [ "${raw#@}" != "$raw" ]; then args=$(cat "${raw#@}"); else args="$raw"; fi
    sid=$(init_session); require_session "$sid"
    post "$sid" '{"jsonrpc":"2.0","method":"notifications/initialized"}' >/dev/null
    tmp=$(mktemp)
    printf '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"%s","arguments":%s}}' "$tool" "$args" > "$tmp"
    post "$sid" "@$tmp"; echo
    rm -f "$tmp"
    ;;
  *)
    echo "usage: $(basename "$0") list | call <tool> '<json-args>' | call <tool> @args.json"
    ;;
esac
