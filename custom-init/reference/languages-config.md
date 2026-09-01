# `.vscode/code-review-graph/languages.toml`

code-review-graph only parses `.md` files as markdown if a custom language grammar is
registered for that extension (requires code-review-graph 2.3.6+). Without it, `.vscode/`
project docs are never turned into graph nodes even when they're visible to the file
collector. Read this from `SKILL.md` Step 3b.

**Unlike `.code-review-graphignore`, this file is NOT committed.** It lives under
`.vscode/`, which is gitignored wholesale in these repos — so it's machine-local, same as
`.vscode/CLAUDE.md` and the rest of the project docs. That's the whole point of putting
it there: no `.code-review-graph` line needed in `.gitignore`, at the cost of this config
not syncing to teammates via git. `/custom-init` recreates it on any machine that runs it;
the global fallback (below) also covers machines that haven't run `/custom-init` for this
project at all.

> This machine also carries a **global fallback** at
> `~/.claude/code-review-graph/languages.toml` (same content), applied only when a repo
> has no local file of its own — see `dev-setup/code-review-graph/patch_global_languages.py`.
> The repo-local override path itself (`.vscode/code-review-graph/languages.toml` instead
> of the default `<repo_root>/.code-review-graph/languages.toml`) is a separate patch,
> `dev-setup/code-review-graph/patch_config_path.py`. Still write the repo-local copy
> here: it makes the config explicit, committed, and portable to any machine that doesn't
> have these patches applied.

## Check if it already exists

```bash
[ -f ".vscode/code-review-graph/languages.toml" ] && echo "EXISTS" || echo "MISSING"
```

If it already exists, skip the rest of this step.

## Write it

```bash
mkdir -p .vscode/code-review-graph
cat > .vscode/code-review-graph/languages.toml << 'EOF'
[languages.markdown]
extensions = [".md"]
grammar = "markdown"
class_node_types = ["section"]
name_field = ["inline"]
EOF
```

After writing, confirm the file was created.
