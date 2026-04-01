---
name: sync-configuration
version: 1.0.0
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

---

## Repositorios y paths relevantes

| Repositorio | Path local | Remote |
|---|---|---|
| dev-setup | `~/Projects/Personal/dev-setup/` | `atilio-ts/dev-setup` |
| claude-skills | `~/Projects/Personal/claude-skills/` | `atilio-ts/claude-skills` |

Skills personales instalados en `~/.claude/skills/` como symlinks al repo
`claude-skills`. Las skills de terceros (gstack, fullstack-dev-skills, etc.)
NO se sincronizan — solo las del repo personal.

---

## Paso 1 — Sincronizar dev-setup

### 1.1 Comparar archivos

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

### 1.2 Reglas de sincronización para zshrc (CRÍTICAS)

El `zshrc` del repo usa **mise** como gestor de versiones (Node, Java, etc.).
El live puede tener variantes específicas de la máquina que NO deben copiarse
al repo:

**Ignorar siempre** (no copiar al repo, no son parte del baseline):
- Bloque `jenv` (`export PATH="$HOME/.jenv/bin:$PATH"` + `eval "$(jenv init -)"`)
- Bloque `fnm` (`eval "$(fnm env --use-on-cd --shell zsh)"`)
- Cualquier otro gestor de versiones alternativo a `mise`

**El repo siempre debe tener:**
- `eval "$($HOME/.local/bin/mise activate zsh)"` como gestor de versiones
- `$HOME/.bun/_bun` (ruta con variable, no absoluta)

Para el resto de diferencias (nuevas líneas, aliases, tools, etc.): aplicar
los cambios del live al repo.

### 1.3 Aplicar cambios

Para cada archivo con diferencias:
- Si son diferencias simples (orden de keys, trailing newlines): `cp` del live
- Si es `zshrc`: aplicar manualmente solo los cambios que no sean jenv/fnm/mise
- Nunca copiar credenciales, tokens o paths absolutos con username hardcodeado
  cuando exista una alternativa con `$HOME`

---

## Paso 2 — Sincronizar claude-skills

### 2.1 Skills en el repo personal

Los skills personales en `~/Projects/Personal/claude-skills/` son:
- `commit-message/`
- `estimate/`
- `user-story/`

`user-story` es un symlink desde `~/.claude/skills/user-story` al repo —
cualquier cambio en el skill ya está reflejado automáticamente.

Para `commit-message` y `estimate`, comparar:
- `~/.claude/skills/commit-message/SKILL.md` vs `~/Projects/Personal/claude-skills/commit-message/SKILL.md`
- `~/.claude/skills/estimate/SKILL.md` vs `~/Projects/Personal/claude-skills/estimate/SKILL.md`

Si hay diferencias, copiar desde `~/.claude/skills/` al repo.

### 2.2 Skills nuevos

Si hay skills en `~/.claude/skills/` que el usuario haya creado y que no sean
de terceros (gstack, fullstack-dev-skills, vercel, etc.), preguntar al usuario
si quiere agregarlos al repo antes de proceder.

---

## Paso 3 — Commit y push

Una vez aplicados los cambios en ambos repos, para cada repo con cambios:

1. Mostrar el `git diff --stat` antes de commitear
2. Hacer commit con mensaje descriptivo siguiendo Conventional Commits:
   - Tipo `chore(sync):` para sincronizaciones de rutina
   - Listar en el cuerpo qué archivos cambiaron y por qué
3. Push a `main`

Si un repo no tiene cambios, informarlo y no crear commit vacío.

---

## Paso 4 — Verificación final

Después del push, confirmar:
- Ambos repos están en sync con `origin/main`
- No quedaron diferencias inesperadas entre live y repo (re-ejecutar diffs clave)
- Reportar un resumen de qué se actualizó en cada repo