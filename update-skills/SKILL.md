---
name: update-skills
version: 1.0.0
description: |
  Update all installed Claude Code skills and plugins for this setup.
  Covers: vercel-labs skills (via npx skills CLI), caveman (via npx skills CLI),
  and Claude plugins (fullstack-dev-skills, everything-claude-code, coderabbit).
  Use when any skill feels outdated or after a new Claude Code release.
allowed-tools:
  - Bash
---

# Update Skills & Plugins

Update all installed skills and plugins for this Claude Code setup.

## Step 1 — Update Claude plugins

Run in the terminal (not via Bash tool — these are interactive CLI commands):

```bash
claude plugin update fullstack-dev-skills
claude plugin update everything-claude-code
claude plugin update coderabbit
```

## Step 2 — Update vercel-labs skills (via npx skills CLI)

These are installed in `~/.agents/skills/` and symlinked from `~/.claude/skills/`.

```bash
npx skills add vercel-labs/agent-skills -g -s vercel-react-best-practices
npx skills add vercel-labs/agent-skills -g -s vercel-composition-patterns
npx skills add vercel-labs/agent-skills -g -s vercel-react-native-skills
npx skills add vercel-labs/agent-skills -g -s web-design-guidelines
```

## Step 3 — Update caveman

```bash
npx skills add JuliusBrussee/caveman -g
```

## Step 4 — Verify symlinks are intact

After updating, verify no symlinks broke:

```bash
for f in ~/.claude/skills/*; do
  [ -L "$f" ] && [ ! -e "$f" ] && echo "BROKEN: $(basename $f)"
done
echo "symlink check done"
```

## Step 5 — Verify plugin skill counts

```bash
ls ~/.claude/plugins/cache/fullstack-dev-skills/fullstack-dev-skills/*/skills/ | wc -l
ls ~/.claude/plugins/cache/everything-claude-code/everything-claude-code/*/skills/ | wc -l
```

## Notes

- vercel-labs and caveman install to `~/.agents/skills/` — symlinks in `~/.claude/skills/` are permanent, no need to recreate them after updates
- Plugin updates may restore previously deleted skills — review after updating and re-delete if needed
- `find-skills` in `~/.agents/skills/` is part of the skills CLI itself, no manual update needed
- Skills installed via `npx skills add` do NOT show in `claude plugin list` — they are managed separately
- To check installed plugin versions: `cat ~/.claude/plugins/installed_plugins.json`

## Skills source map

| Skill | Source | Update method |
|-------|--------|---------------|
| vercel-react-best-practices | github.com/vercel-labs/agent-skills | npx skills add |
| vercel-composition-patterns | github.com/vercel-labs/agent-skills | npx skills add |
| vercel-react-native-skills | github.com/vercel-labs/agent-skills | npx skills add |
| web-design-guidelines | github.com/vercel-labs/agent-skills | npx skills add |
| caveman | github.com/JuliusBrussee/caveman | npx skills add |
| caveman-compress | github.com/JuliusBrussee/caveman | npx skills add |
| fullstack-dev-skills/* | Claude plugin marketplace | claude plugin update |
| everything-claude-code/* | Claude plugin marketplace | claude plugin update |
| coderabbit/* | Claude plugin marketplace | claude plugin update |