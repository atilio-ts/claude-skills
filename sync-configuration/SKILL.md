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

Para **memory**, comparar el contenido del directorio:

```bash
diff -rq ~/.claude/memory/ ~/Projects/Personal/dev-setup/claude/memory/
```

Los archivos de memoria que se rastrean son `MEMORY.md` y los archivos de feedback/user
globales (`feedback_cachebro.md`, `user_profile.md`). Si hay nuevos archivos de feedback
relevantes para cualquier máquina (no específicos a un proyecto), agregarlos al repo.

Directorios de `~/.claude/` que NO se sincronizan (auto-generados o runtime):
- `backups/`, `cache/`, `commands/`, `debug/`, `ecc/`, `file-history/`
- `homunculus/`, `ide/`, `metrics/`, `paste-cache/`, `plans/`, `plugins/`
- `projects/`, `session-env/`, `sessions/`, `shell-snapshots/`
- `skills/`, `statsig/`, `tasks/`, `telemetry/`, `todos/`
- `scripts/` — generado por `setup.sh` con paths absolutos específicos de la máquina
  (ej: `graphify-start.sh` usa el path de pipx del usuario activo)
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
| `nvim/lua/plugins/example.lua` | `~/.config/nvim/lua/plugins/example.lua` |

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

## Paso 2.5 — Verificar DEV_SETUP.md

`DEV_SETUP.md` documenta el entorno completo para reproducirlo en una máquina nueva.
Hay que mantenerlo al día con el estado real de la máquina. Verificar:

### Fecha

Actualizar el campo `Last updated:` al día de hoy si se hicieron cambios.

### Formulas de Homebrew

Comparar la lista documentada en DEV_SETUP.md con lo que está instalado:

```bash
brew list --formula | sort
```

Diferencias frecuentes a detectar:
- **Herramienta removida**: eliminarla de la lista de formulas y de la tabla de tools
- **Herramienta nueva**: agregarla en orden alfabético en la lista de formulas y en la tabla si es una CLI tool
- **Cambio de versión de Python** (`python@3.13` → `python@3.14`): actualizar la lista Y la línea de PATH en el ejemplo de `.zshrc`

### zshrc

Comparar el bloque de `.zshrc` documentado en DEV_SETUP.md con el live `~/.zshrc`.
Diferencias frecuentes:
- Líneas de `eval "$(tool init ...)"` para herramientas que ya no están instaladas
- PATH de Python desactualizado

### Herramientas instaladas via pipx

```bash
pipx list
```

Las herramientas de pipx se documentan en la subsección **"Python tools — pipx"**
dentro de la sección "Terminal Tools & Aliases" de DEV_SETUP.md. Si hay nuevas,
agregarlas a la tabla con nombre, versión y comando de instalación.

> Nota: el package de pip puede diferir del nombre del comando (ej: `pipx install graphifyy`
> instala el comando `graphify`).

### Known gaps del Brewfile

La nota de "Known gaps" al inicio de la sección Homebrew debe reflejar solo los packages
que realmente están instalados pero que `brew bundle dump` omite. Actualizar si cambia.

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