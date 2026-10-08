#!/usr/bin/env bash
# Launch a Cursor cloud agent on the demo repo and wait for the PR link.
# Needs: CURSOR_API_KEY (env), jq, curl.
# Usage: scripts/launch_cursor_agent.sh https://github.com/<you>/credit-watch-demo [branch]
# Request shape verified against Cursor's Cloud Agents API docs (Oct 2026):
#   POST /v1/agents  {prompt:{text}, repos:[{url,startingRef}], autoCreatePR}
#   GET  /v1/agents/{id}/runs/{runId}  -> status, git.branches[].prUrl
set -euo pipefail
REPO_URL="${1:?repo url, e.g. https://github.com/<you>/credit-watch-demo}"
BRANCH="${2:-main}"
: "${CURSOR_API_KEY:?set CURSOR_API_KEY first}"
API=https://api.cursor.com/v1
PROMPT="Implement the scout package exactly per docs/specs/SPEC-001-signal-scout.md. Follow AGENTS.md and the repo rules and skills. Run pytest -m 'not live' and scripts/pure_check.py until both pass, then open a PR (do not merge). Include the PURE self-review in the PR description."
BODY=$(jq -n --arg p "$PROMPT" --arg u "$REPO_URL" --arg b "$BRANCH" \
  '{prompt:{text:$p}, repos:[{url:$u, startingRef:$b}], autoCreatePR:true}')
RESP=$(curl -sS -u "$CURSOR_API_KEY:" -H 'Content-Type: application/json' -d "$BODY" "$API/agents")
echo "$RESP" | jq .
AGENT=$(echo "$RESP" | jq -r '.agent.id // empty')
RUN=$(echo "$RESP" | jq -r '.run.id // empty')
[ -z "$AGENT" ] || [ -z "$RUN" ] && { echo "Launch failed: no agent/run id (check key, repo access, JSON above)"; exit 1; }
echo "Agent $AGENT started. Watch it live at https://cursor.com/agents"
for _ in $(seq 1 180); do
  R=$(curl -sS -u "$CURSOR_API_KEY:" "$API/agents/$AGENT/runs/$RUN")
  ST=$(echo "$R" | jq -r '.status // .run.status // "UNKNOWN"')
  echo "$(date +%H:%M:%S) status: $ST"
  case "$ST" in
    FINISHED) echo "$R" | jq -r '[.. | .prUrl? // empty] | unique | .[]' | sed 's/^/PR: /'; exit 0 ;;
    ERROR|CANCELLED|EXPIRED) echo "$R" | jq .; exit 1 ;;
  esac
  sleep 10
done
echo "Timed out waiting; check https://cursor.com/agents"; exit 1
