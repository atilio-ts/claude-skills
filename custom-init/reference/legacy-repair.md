# Legacy Repair

Older `/custom-init` versions wrote things the current one doesn't: tool lines in the
committed `.gitignore`, ignore files and MCP config at the repo root, tool data outside
`.vscode/`. Re-running `/custom-init` on such a repo must clean them up, not just add the
new setup next to them. Read this from `SKILL.md` Step 7a, after Step 7 has written the
exclude list — everything removed from `.gitignore` here is already hidden from there.

---

## Detect

```bash
OWNED='^/?(\.filestash|\.file-stash|\.code-review-graph|\.cachebro|graphify-out|\.mcp\.json|\.graphifyignore|\.code-review-graphignore)/?$'
echo "-- .gitignore lines:";   rg -n "$OWNED" .gitignore 2>/dev/null
echo "-- tracked files:";      git ls-files .code-review-graphignore .graphifyignore .mcp.json .claude .omp
echo "-- root leftovers:";     ls -d .code-review-graph .filestash .cachebro graphify-out .graphifyignore 2>/dev/null
echo "-- root .mcp.json:";     [ -f .mcp.json ] && [ ! -L .mcp.json ] && cat .mcp.json
echo "-- old docs layout:";    ls .vscode/*-CLAUDE.md 2>/dev/null
```

Each section with output is a finding. No output anywhere → nothing to repair, skip to
Step 7b.

## Repair

Present every finding with `AskUserQuestion` before acting — several of these change
committed files or delete local data, and the team will see the `.gitignore` diff.
Never commit; leave the changes for the user to review.

| Finding | Repair |
|---|---|
| Tool lines in `.gitignore` | Remove exactly those lines (below). If the file ends up empty, say so and let the user decide whether to delete it. Never touch other lines, `.vscode` included. |
| Tracked `.code-review-graphignore`, `.graphifyignore`, `.mcp.json`, `.claude`, `.omp` | `git rm --cached <path>` — untracks it and keeps the local file, which Step 7 now hides. Never plain `rm` or `git rm` without `--cached`. |
| `.code-review-graph/` at the root | Stale database from before `--data-dir`; the graph now lives in `.vscode/code-review-graph/`. Offer to delete it after Step 4 rebuilt the new one. |
| `.filestash/`, `.cachebro/`, `graphify-out/`, `.graphifyignore` | Data from tools no longer used (or from file-stash before `FILESTASH_DIR`). Offer to delete. |
| Real `.mcp.json` at the root | Show its servers. Entries for filestash or code-review-graph (now global) or houtini-lm (dropped) are obsolete. If nothing else remains, offer to delete the file. Otherwise offer to move it: `mv .mcp.json .vscode/.mcp.json && ln -s .vscode/.mcp.json .mcp.json`, with the obsolete entries removed. |
| `.vscode/<module>-CLAUDE.md` files | Nothing here — Step 6 runs `/claude-docs` in audit mode, which migrates them into `.vscode/docs/`. |

Remove the `.gitignore` lines with:

```bash
OWNED="$OWNED" awk '$0 !~ ENVIRON["OWNED"]' .gitignore > .gitignore.tmp && mv .gitignore.tmp .gitignore
```

Report each repair in the Step 8 summary, and each finding the user chose to keep.
