# Tooling Catalog

Stack signal → plugin, MCP, or skill worth recommending. This step only prints
recommendations and the commands to apply them; it never installs, enables, or writes
config itself.

---

## Check what's already active

```bash
claude plugin list 2>/dev/null
claude mcp list 2>/dev/null
```

Drop anything already installed and enabled from the recommendation list. Mention it in
the summary as "already active" instead.

## Language servers (by signal file)

Language-server plugins only start for matching file types, so `--scope user` is safe and
keeps every config file out of the repo.

| Signal | Plugin |
|---|---|
| `package.json` with `typescript` or a `tsconfig.json` | `typescript-lsp@claude-plugins-official` |
| `gradlew`, `pom.xml`, `build.gradle(.kts)` with Java sources | `jdtls-lsp@claude-plugins-official` |
| Kotlin sources (`*.kt`) | `kotlin-lsp@claude-plugins-official` |
| `pyproject.toml`, `requirements.txt` | `pyright-lsp@claude-plugins-official` |
| `go.mod` | `gopls-lsp@claude-plugins-official` |
| `Cargo.toml` | `rust-analyzer-lsp@claude-plugins-official` |
| `*.csproj`, `*.sln` | `csharp-lsp@claude-plugins-official` |
| `composer.json` | `php-lsp@claude-plugins-official` |
| `Gemfile` | `ruby-lsp@claude-plugins-official` |
| `Package.swift` | `swift-lsp@claude-plugins-official` |
| `CMakeLists.txt`, C/C++ sources | `clangd-lsp@claude-plugins-official` |

```bash
claude plugin install <plugin> --scope user
```

## Other plugins (by signal)

| Signal | Plugin | Why |
|---|---|---|
| OpenAPI spec (`openapi.y*ml`, `swagger.json`) or an HTTP API module | `postman@claude-plugins-official` | Mocking, contract tests, collections from the spec |
| `terraform/` or `*.tf` | `terraform@claude-plugins-official` | Provider and module docs |
| Browser UI (React/Vue/Angular app, e2e tests) | `playwright@claude-plugins-official` | Driving the app in a browser |

## Project MCPs

Only when the project needs an MCP the global ones (filestash, code-review-graph) don't
cover — a project database, an internal service. Never guess server names or connection
strings: ask the user which service and how it's reached.

Keep the file inside `.vscode/` and link it from the root, where both Claude Code and omp
look for it. The root link is covered by `.git/info/exclude` (Step 7):

```bash
# write .vscode/.mcp.json with {"mcpServers": {...}}, then:
ln -s .vscode/.mcp.json .mcp.json
```

## Skills

Personal skills are global and need nothing per project. Recommend a project skill
(`/new-skill`, written into `.vscode/.claude/skills/`) only when Step 1 found a repeated,
project-specific workflow — a scaffold for a new endpoint following the project's layers,
a migration procedure. Name the workflow and the evidence; don't create the skill here.

## Output format

```
Recommended for this project:
  typescript-lsp  — tsconfig.json found        → claude plugin install typescript-lsp@claude-plugins-official --scope user
  postman         — openapi.yaml found         → claude plugin install postman@claude-plugins-official --scope user
Already active: context-mode, coderabbit
```

If nothing applies, print `No stack-specific tooling to recommend.`
