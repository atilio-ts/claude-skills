---
name: sync-configuration
version: 2.0.0
description: |
  Sincroniza el repositorio de dev-setup y el repositorio personal de skills
  de Claude con el estado actual de la máquina. Detecta diferencias, aplica
  los cambios correctos y hace commit + push de ambos repos.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# Sincronización de Configuración

Tu tarea es sincronizar dos repositorios personales con el estado actual de
la máquina:

- **dev-setup**: `~/Projects/Personal/dev-setup/`
- **claude-skills**: `~/Projects/Personal/claude-skills/`

**Principio clave**: el estado de esta máquina es la fuente de verdad.
Si hay diferencia entre el repo y el live, el repo es lo que hay que actualizar.

---

## Repositorios y paths relevantes

| Repositorio | Path local | Remote |
|---|---|---|
| dev-setup | `~/Projects/Personal/dev-setup/` | `atilio-ts/dev-setup` |
| claude-skills | `~/Projects/Personal/claude-skills/` | `atilio-ts/claude-skills` |

---

## Paso 1 — Comprobar completitud del repo (antes de comparar archivos)

Antes de hacer diffs, verificar que no haya directorios o archivos en `~/.claude/`
que no estén rastreados en el repo. Ejecutar:

```bash
ls ~/.claude/
ls ~/Projects/Personal/dev-setup/claude/
```

Directorios esperados en el repo bajo `claude/`:
- `agents/`, `hooks/`, `memory/`, `mcp-configs/`, `rules/`
- `CLAUDE.md`, `settings.json`, `statusline-command.sh`

Directorios de `~/.claude/` que NO se sincronizan (auto-generados o runtime):
- `backups/`, `cache/`, `commands/`, `debug/`, `ecc/`, `file-history/`
- `homunculus/`, `ide/`, `metrics/`, `paste-cache/`, `plans/`, `plugins/`
- `projects/`, `scripts/`, `session-env/`, `sessions/`, `shell-snapshots/`
- `skills/`, `statsig/`, `tasks/`, `telemetry/`, `todos/`
- `history.jsonl`, `marketplace.json`, `mcp-needs-auth-cache.json`
- `plugin.json`, `stats-cache.json`
- `hooks/hooks.json`, `hooks/README.md` (generados por ECC al instalar)

Si aparece un directorio en `~/.claude/` que no está en ninguna de las dos listas,
investigar si es custom y debe agregarse al repo.

Para **agentes** y **reglas**, comparar directorios completos:

```bash
diff -rq ~/.claude/agents/ ~/Projects/Personal/dev-setup/claude/agents/
diff -rq ~/.claude/rules/ ~/Projects/Personal/dev-setup/claude/rules/
```

Si hay diferencias, copiar el directorio completo desde live al repo:

```bash
cp -r ~/.claude/agents ~/Projects/Personal/dev-setup/claude/agents
cp -r ~/.claude/rules ~/Projects/Personal/dev-setup/claude/rules
```

---

## Paso 2 — Comparar archivos individuales

Ejecuta `diff` entre cada archivo del repo y su contraparte live:

| Repo | Live |
|---|---|
| `claude/CLAUDE.md` | `~/.claude/CLAUDE.md` |
| `claude/settings.json` | `~/.claude/settings.json` |
| `claude/statusline-command.sh` | `~/.claude/statusline-command.sh` |
| `claude/hooks/pre-bash.sh` | `~/.claude/hooks/pre-bash.sh` |
| `claude/hooks/pre-websearch.sh` | `~/.claude/hooks/pre-websearch.sh` |
| `shell/zshrc` | `~/.zshrc` |
| `shell/p10k.zsh` | `~/.p10k.zsh` |
| `git/gitconfig` | `~/.gitconfig` |
| `git/gitignore_global` | `~/.gitignore_global` |
| `vscode/settings.json` | `~/Library/Application Support/Code/User/settings.json` |
| `gh/config.yml` | `~/.config/gh/config.yml` |
| `atuin/config.toml` | `~/.config/atuin/config.toml` |
| `nvim/init.lua` | `~/.config/nvim/init.lua` |
| `nvim/lua/config/*.lua` | `~/.config/nvim/lua/config/*.lua` |

### Diffs que se pueden ignorar

- `gitconfig` — el campo `git-commit-alias` es un SHA auto-gestionado, ignorar
- `settings.json` — diferencias de orden de keys JSON sin cambio de contenido, ignorar
- `spicetify/` — `.DS_Store`, `CustomApps`, `Extensions`, `Themes` son datos runtime
- `launchagents/` — plists de Google Updater son auto-instalados, no gestionados

### Reglas para zshrc (CRÍTICAS)

El repo usa **mise** como gestor de versiones. El live puede tener variantes
específicas de la máquina que NO deben copiarse al repo:

**Ignorar siempre** (no son parte del baseline):
- Bloque `jenv` (`export PATH="$HOME/.jenv/bin:$PATH"` + `eval "$(jenv init -)"`)
- Bloque `fnm` (`eval "$(fnm env --use-on-cd --shell zsh)"`)
- Cualquier otro gestor de versiones alternativo a `mise`

**El repo siempre debe tener:**
- `eval "$($HOME/.local/bin/mise activate zsh)"` como gestor de versiones
- `$HOME/.bun/_bun` (ruta con variable, no absoluta)

### Reglas generales de sincronización

- Nunca copiar credenciales, tokens o paths absolutos con username hardcodeado
  cuando exista una alternativa con `$HOME`
- Si el diff es solo orden de keys o trailing newline, no actualizar

---

## Paso 3 — Sincronizar claude-skills

### 3.1 Skills en el repo personal

| Skill | Instalado como |
|---|---|
| `commit-message/` | directorio en `~/.claude/skills/` |
| `estimate/` | directorio en `~/.claude/skills/` |
| `user-story/` | symlink → repo |
| `sync-configuration/` | symlink → repo |
| `update-skills/` | symlink → repo |

Para `commit-message` y `estimate` (no son symlinks), comparar y copiar si difieren:

```bash
diff ~/.claude/skills/commit-message/SKILL.md ~/Projects/Personal/claude-skills/commit-message/SKILL.md
diff ~/.claude/skills/estimate/SKILL.md ~/Projects/Personal/claude-skills/estimate/SKILL.md
```

### 3.2 Skills nuevos

Listar todos los directorios reales (no symlinks) en `~/.claude/skills/`:

```bash
for f in ~/.claude/skills/*/; do
  [ -L "${f%/}" ] || echo "DIR  $(basename $f)"
done
```

Comparar contra lo que está en el repo. Si hay alguno que no sea de terceros
(gstack, ECC plugin skills, vercel, caveman), preguntar al usuario si quiere
agregarlo al repo.

Skills de terceros conocidos que NO se sincronizan:
- ECC plugin: backend-patterns, coding-standards, continuous-learning, continuous-learning-v2,
  frontend-patterns, frontend-slides, iterative-retrieval, java-coding-standards,
  springboot-patterns, springboot-tdd, springboot-verification, strategic-compact,
  tdd-workflow, verification-loop
- gstack (tiene node_modules, se instala via `claude plugins install gstack`)
- learned (directorio vacío, runtime de ECC)
- Symlinks a vercel-labs, caveman, find-skills (gestionados via `npx skills add`)

---

## Paso 4 — Commit y push

Para cada repo con cambios:

1. Mostrar `git diff --stat` antes de commitear
2. Commit con Conventional Commits:
   - `chore(sync):` para sincronizaciones de rutina
   - Listar en el cuerpo qué cambió y por qué
3. Push a `main`

Si un repo no tiene cambios, informarlo y no crear commit vacío.

---

## Paso 5 — Verificación final

Confirmar:
- Ambos repos están en sync con `origin/main`
- Re-ejecutar los diffs clave para verificar que no quedaron diferencias
- Reportar resumen de qué se actualizó en cada repo