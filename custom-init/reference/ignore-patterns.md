# `.code-review-graphignore` Patterns

code-review-graph has native support for `.code-review-graphignore` (gitignore-style
patterns). It already excludes common noise by default (`node_modules`, `__pycache__`,
`.git`, `build`, `target`, `dist`, `out`, `venv`, lock files). This file adds
project-type-specific patterns that are NOT excluded by default, reducing extraction cost.
Read this from `SKILL.md` Step 3.

**This file should be committed** — it is project config, not machine-specific output.

---

## Check if it already exists

```bash
[ -f ".code-review-graphignore" ] && echo "EXISTS" || echo "MISSING"
```

If it already exists, skip the rest of this step.

## Write the universal block, then the language-specific block(s)

```bash
cat > .code-review-graphignore << 'EOF'
# ── Universal noise ──────────────────────────────────────────────────────────
# code-review-graph already skips: node_modules, __pycache__, .git, build,
# target, dist, out, venv, lock files. These extend that baseline.

# Tool output folders (machine-specific, no semantic value)
.code-review-graph/
.filestash/
temporary/

# IDE and OS noise
.idea/
.DS_Store
*.iml
EOF
```

Then append the block(s) matching the detected build system(s). For monorepos mixing
languages, append all relevant blocks.

**Java / Gradle or Maven:**
```bash
cat >> .code-review-graphignore << 'EOF'

# ── Java ─────────────────────────────────────────────────────────────────────
# Compiled bytecode
*.class
*.jar
*.war
*.ear

# Gradle caches and wrapper binaries
.gradle/
gradle/wrapper/gradle-wrapper.jar

# Vendored / local Maven repos (binary JARs, no source value)
local-maven/

# Generated source (OpenAPI codegen output, etc.)
build/gm/

# Test fixtures and generated test data (high volume, low semantic value)
src/test/resources/
**/test-data/
**/fixtures/
**/__snapshots__/
EOF
```

**Node.js / TypeScript:**
```bash
cat >> .code-review-graphignore << 'EOF'

# ── Node.js / TypeScript ─────────────────────────────────────────────────────
# Framework build output
.next/
.nuxt/
.svelte-kit/

# Test coverage reports and snapshots
coverage/
.nyc_output/
**/__snapshots__/
**/*.snap

# Type declaration caches
*.tsbuildinfo

# Test fixtures (data files, not logic)
**/fixtures/
**/test-data/
**/mocks/data/
EOF
```

**Python:**
```bash
cat >> .code-review-graphignore << 'EOF'

# ── Python ───────────────────────────────────────────────────────────────────
*.pyc
*.pyo
*.pyd
.Python
*.egg
*.egg-info/
dist/
htmlcov/
.coverage

# Test fixtures
**/fixtures/
**/test_data/
**/__snapshots__/
EOF
```

**Go:**
```bash
cat >> .code-review-graphignore << 'EOF'

# ── Go ───────────────────────────────────────────────────────────────────────
vendor/
*.test
*.out

# Test fixtures
**/testdata/
**/fixtures/
EOF
```

**Rust:**
```bash
cat >> .code-review-graphignore << 'EOF'

# ── Rust ─────────────────────────────────────────────────────────────────────
**/*.rs.bk

# Test fixtures
**/fixtures/
**/test_data/
EOF
```

> **Note on test source files** (`.java`, `.ts`, `.py`, etc.): test logic files are
> intentionally NOT ignored. They contain domain knowledge, reveal how the system is
> expected to behave, and produce high-value nodes in the graph. Only data/fixture files
> are excluded since they are high-volume with no architectural signal.

After writing, print the number of patterns added and confirm the file was created.