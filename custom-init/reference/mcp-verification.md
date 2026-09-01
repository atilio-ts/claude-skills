# MCP Verification

Checks that filestash, code-review-graph, and houtini-lm are registered as global MCPs
and reachable, plus the `enableAllProjectMcpServers` setting that makes per-project MCPs
work without a `.claude/settings.local.json`. Read this from `SKILL.md` Step 2.

**Never modify `~/.claude.json` or `~/.claude/settings.json` automatically** — only print
instructions for the user in every case below.

---

## 2a — Check filestash in `~/.claude.json`

```bash
python3 -c "
import json, os
p = os.path.expanduser('~/.claude.json')
try:
    d = json.load(open(p))
    mcp = d.get('mcpServers', {})
    if 'filestash' in mcp:
        print('OK')
    else:
        print('MISSING')
except Exception as e:
    print(f'ERROR: {e}')
"
```

**If filestash is missing**, print this message and continue:

```
⚠  filestash MCP not found in ~/.claude.json.

Install globally and add manually:

  npm install -g @claude-code/filestash
  echo "$(npm prefix -g)/bin/filestash"   # copy this path

Then open ~/.claude.json and insert under "mcpServers":

  "filestash": {
    "command": "<path from above>",
    "args": ["serve"],
    "env": {
      "FILESTASH_DIR": ".vscode/file-stash"
    }
  }

Do NOT use npx — it is unreliable when the npx cache expires.
Restart Claude Code after editing.
```

**If present**, print: `✓ filestash MCP is configured globally`.

> Note: filestash (like any MCP server) only connects at session start. If a check like
> this one reports it missing mid-session even after the user says they just enabled it,
> that's expected — it needs a fresh session, not a re-check. Fall back to the built-in
> `Read` tool for that session rather than blocking on it.

## 2b — Check code-review-graph global MCP in `~/.claude.json`

code-review-graph is configured globally (not per-project) as a direct binary:

```bash
python3 -c "
import json, os
p = os.path.expanduser('~/.claude.json')
try:
    d = json.load(open(p))
    mcp = d.get('mcpServers', {})
    if 'code-review-graph' in mcp:
        print('OK')
    else:
        print('MISSING')
except Exception as e:
    print(f'ERROR: {e}')
"
```

Also verify the binary exists:

```bash
[ -f "/Users/atilio/.local/bin/code-review-graph" ] && echo "OK" || echo "MISSING"
```

**If missing**, print this message and continue:

```
⚠  code-review-graph global MCP not found.

Install and register globally:

  pipx install code-review-graph

Then add to ~/.claude.json under "mcpServers":

  "code-review-graph": {
    "command": "/Users/<username>/.local/bin/code-review-graph",
    "args": ["serve"]
  }

Restart Claude Code after editing.
```

**If present**, print: `✓ code-review-graph MCP is configured globally`.

## 2c — Check houtini-lm global MCP

houtini-lm is configured globally (not per-project) and connects Claude Code to the
local LLM running in LM Studio on `localhost:1234`. Check that it is registered and
using a direct binary path (not `npx -y`, which is unreliable):

```bash
claude mcp list 2>/dev/null | grep -i houtini
```

**If missing**, print this message and continue:

```
⚠  houtini-lm global MCP not found.

Install and register globally with a direct binary path:

  npm install -g @houtini/lm
  HOUTINI_BIN="$(npm prefix -g)/bin/houtini-lm"
  claude mcp add --scope user houtini-lm -- "$HOUTINI_BIN"

Then restart Claude Code.
```

**If present but using `npx`**, print this message — the registration should be updated
to use the installed binary for reliability:

```
⚠  houtini-lm is registered via npx — this can fail on slow networks or cold starts.

Re-register with the direct binary path:

  npm install -g @houtini/lm
  claude mcp remove houtini-lm
  HOUTINI_BIN="$(npm prefix -g)/bin/houtini-lm"
  claude mcp add --scope user houtini-lm -- "$HOUTINI_BIN"

Then restart Claude Code.
```

**If present with a direct binary path**, call `mcp__houtini-lm__discover` to verify
the local LLM server is reachable:

- If the tool returns `Status: ONLINE` → print: `✓ houtini-lm connected — <model name>`
- If it returns `Status: OFFLINE` → print:

```
⚠  houtini-lm is registered but LM Studio is not running.

Start LM Studio and load a model, then re-run /custom-init or verify manually
with: claude mcp list
```

Do NOT fail the setup — continue with the remaining steps.

## 2d — Check `enableAllProjectMcpServers` in `~/.claude/settings.json`

This setting auto-enables any `.mcp.json` found in a project root, without needing a
per-project `.claude/settings.local.json`.

```bash
python3 -c "
import json, os
p = os.path.expanduser('~/.claude/settings.json')
try:
    d = json.load(open(p))
    if d.get('enableAllProjectMcpServers'):
        print('OK')
    else:
        print('MISSING')
except Exception as e:
    print(f'ERROR: {e}')
"
```

**If missing**, print this message and continue:

```
⚠  enableAllProjectMcpServers not set in ~/.claude/settings.json.

Add it manually by opening ~/.claude/settings.json and inserting at the top level:

  "enableAllProjectMcpServers": true

Then restart Claude Code.
```

**If present**, print: `✓ enableAllProjectMcpServers is set globally`.

---

## Global MCPs never go in `.mcp.json`

filestash, code-review-graph, and houtini-lm are all global. **Never write any of them
into a project's `.mcp.json`.** The code-review-graph MCP server (`code-review-graph serve`)
resolves the database dynamically from `$PWD` at startup — by default that's
`.code-review-graph/`, but this machine builds into `.vscode/code-review-graph` via
`--data-dir` (Step 4b), which the server follows automatically through the same
`~/.code-review-graph/registry.json` lookup the CLI uses. If the database doesn't exist
yet (before first build), the server still starts but graph tools return empty results,
which is expected. houtini-lm connects to LM Studio the same way regardless of which
project you're in.

Only create `.mcp.json` if the specific project needs MCPs beyond these three global ones.
If no project-specific MCPs are needed, skip that file entirely, and do not create
`.claude/settings.local.json` or any `.claude/` folder in the project — the global
`enableAllProjectMcpServers: true` makes both unnecessary.