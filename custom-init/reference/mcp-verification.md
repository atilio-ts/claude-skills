# MCP Verification

Checks that filestash and code-review-graph are registered as global MCPs
and reachable. Read this from `SKILL.md` Step 2.

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

## Global MCPs never go in `.mcp.json`

filestash and code-review-graph are both global. **Never write any of them
into a project's `.mcp.json`.** The code-review-graph MCP server (`code-review-graph serve`)
resolves the database dynamically from `$PWD` at startup — by default that's
`.code-review-graph/`, but this machine builds into `.vscode/code-review-graph` via
`--data-dir` (Step 4b), which the server follows automatically through the same
`~/.code-review-graph/registry.json` lookup the CLI uses. If the database doesn't exist
yet (before first build), the server still starts but graph tools return empty results,
which is expected.

Only create `.mcp.json` if the specific project needs MCPs beyond these two global ones.
If no project-specific MCPs are needed, skip that file entirely, and do not create
`.claude/settings.local.json` or any `.claude/` folder in the project. Claude Code asks for approval
the first time it sees a project-scoped MCP.