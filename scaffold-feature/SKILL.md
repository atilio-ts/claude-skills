---
name: personal:scaffold-feature
version: 1.0.0
description: |
  Scaffolds a new application feature (I<Name>/impl pair) or external integration port
  (I<Noun>Contract/adapter pair) for a Spring Boot Clean Architecture project built on
  the api-projectbase-spring template (api/application/domain/infrastructure Gradle
  modules, CleanArchBeanRegistry classpath-scanning DI, no Spring annotations in
  domain/application, ArchUnit-enforced layering). Detects the project's base package
  automatically so the same skill works unmodified across sibling OCA modernization
  repos (oca.backofficenexito, oca.backofficeaudit, and future ones like FileBus/RPO).
  Use when starting a new feature or integration port in one of these repos.
trigger: /scaffold-feature
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
---

# /scaffold-feature

Generates the minimal, compilable file scaffolding for a new business feature or a new
external integration port in a Spring Boot Clean Architecture project that follows the
`api-projectbase-spring` template. Never invents business logic — only file structure,
packages, and imports.

## Usage

```
/scaffold-feature feature GetSystemParameter
/scaffold-feature port Sherlog
```

---

## Step 1 — Confirm this project actually uses this template

Before doing anything, check all three:

```bash
grep -E "include 'modules:(api|application|domain|infrastructure)'" settings.gradle
grep -rl CleanArchBeanRegistry modules/infrastructure/ 2>/dev/null
```

- `settings.gradle` declares the four modules (`api`, `application`, `domain`,
  `infrastructure`).
- `CleanArchBeanRegistry` (or an equivalently-named `BeanDefinitionRegistryPostProcessor`)
  exists under `modules/infrastructure/.../config/`.

If either check comes back empty, **stop and tell the user this skill doesn't apply
here** — it's specific to this template's DI mechanism, not a generic Spring Boot
scaffolder.

## Step 2 — Detect the base package

```bash
BASE_PKG_PATH=$(find modules/domain/src/main/java -mindepth 3 -maxdepth 3 -type d | head -1 | sed 's|modules/domain/src/main/java/||')
BASE_PACKAGE=$(echo "$BASE_PKG_PATH" | tr '/' '.')
```

This resolves to e.g. `uy.oca.backofficenexito` in `oca.backofficenexito`, or
`uy.oca.backofficeaudit` in `oca.backofficeaudit` — use `$BASE_PACKAGE` /
`$BASE_PKG_PATH` everywhere below. **Never hardcode a package name**, even though the
examples in this file use `uy.oca.backofficenexito` for concreteness.

## Step 3 — Consult before writing anything

Real naming and behavior decisions don't come from this skill — they come from context
it cannot see on its own. Before generating a single file:

1. Check whether the project has its own local subagents for this
   (`ls .claude/agents/ .vscode/.claude/agents/ 2>/dev/null`). If a precedent-project
   agent exists (something like `audit-expert` — a sibling project that already
   implemented something similar), consult it first: a working precedent beats
   inventing a new variant. If a legacy-system agent exists (something like
   `nexito-legacy-expert`), consult it for the real behavior this feature/port needs to
   preserve.
2. Read the project's own architecture docs if present (`.vscode/CLAUDE.md` and its
   module deep-dives, any `docs/*-clean-architecture.md`, `error-handling.md`) — they
   document the *current, verified* state of this project's conventions. If they
   disagree with this skill on a naming detail, trust the project's own docs over this
   file.
3. If the project tracks compatibility deviations from a legacy system it's replacing
   (a `COMPATIBILITY_NOTES.md` or similar), remember to flag whether this feature needs
   an entry there once its real behavior is implemented.

This skill does not assume a fixed list of agents or docs — check what actually exists
in the current project rather than assuming the names above are present.

## Step 4 — Decide: feature or port?

| | Business feature | External integration port |
|---|---|---|
| When | Internal logic, invoked by a controller or another feature | Talks to an external system (HTTP, direct DB, SDK) |
| Naming | Verb+noun (`GetSystemParameter`, `CreateActivityRecord`) | Noun of the external system (`Sherlog`, `Rpo`, `MerchantIdp`) |
| Interface package | `application.feature.<camelCaseName>` | `application.contract` |
| Impl package | `application.feature.<camelCaseName>.impl` | `infrastructure.contract.impl` |

Both `application.feature` and `application.contract` (plus `infrastructure.contract.impl`
for port adapters) are scanned automatically by `CleanArchBeanRegistry` at startup.
**Never add `@Service`/`@Component`** — no class in `domain` or `application` carries
Spring annotations; this is an ArchUnit-enforced rule in every project this skill targets.

## Step 5a — Generate a business feature

Real example already in `oca.backofficenexito` — match this exact shape, not this
content:

```java
// application/feature/validateApi/IValidateAPI.java
package uy.oca.backofficenexito.application.feature.validateApi;

public interface IValidateAPI {
    void checkApiKey(String givenApiKey);
}
```

```java
// application/feature/validateApi/impl/ValidateAPIImpl.java
package uy.oca.backofficenexito.application.feature.validateApi.impl;

import uy.oca.backofficenexito.application.feature.validateApi.IValidateAPI;

public class ValidateAPIImpl implements IValidateAPI {
    @Override
    public void checkApiKey(String givenApiKey) {
        // TODO: implement — see Step 3 before writing the real logic
        throw new UnsupportedOperationException("not yet implemented");
    }
}
```

Create, using `$BASE_PKG_PATH`/`$BASE_PACKAGE` from Step 2:

- `modules/application/src/main/java/$BASE_PKG_PATH/application/feature/<camelCaseName>/I<Name>.java`
- `modules/application/src/main/java/$BASE_PKG_PATH/application/feature/<camelCaseName>/impl/<Name>Impl.java`

## Step 5b — Generate an integration port

Same mechanism, two files:

- `modules/application/src/main/java/$BASE_PKG_PATH/application/contract/I<Name>Contract.java`
  — interface only. Don't invent method signatures; leave a `// TODO: define contract —
  see Step 3` comment and one placeholder method if the real shape isn't known yet.
- `modules/infrastructure/src/main/java/$BASE_PKG_PATH/infrastructure/contract/impl/<Name>ContractImpl.java`
  — adapter with a minimal constructor; every method throws
  `UnsupportedOperationException` until implemented.

## Step 6 — Domain model (only if the feature/port needs one)

`modules/domain/src/main/java/$BASE_PKG_PATH/domain/model/<Name>Model.java` — **immutable
record**, no framework annotations at all. ArchUnit rule verified in every project this
skill targets: any class named `*Model` must live in `domain.model`, and no class in
`domain` may end in `Exception` (business exceptions live in `application.exception`
instead — see the project's own `error-handling.md` if it has one).

## Step 7 — HTTP controller (only if the feature is exposed over HTTP)

`modules/api/src/main/java/$BASE_PKG_PATH/api/controller/v1/<Name>Controller.java` —
standard Spring MVC `@RestController` (`@RequestMapping`/`@GetMapping`/etc.). If the
legacy system being modernized used a spec-first router (e.g.
`org.resthub.web.springmvc.router`) instead of Spring MVC annotations, **that convention
has already been abandoned in the modernization** — don't replicate it, use standard
annotations.

## Step 8 — Verify

After generating files:

```bash
./gradlew :modules:api:compileJava   # or the most specific module touched
./gradlew test --tests "*CleanArchTest*"
```

If `CleanArchTest` fails, it means a file landed in the wrong package — move the file,
don't loosen the ArchUnit rule to make it pass.

---

## Never invent

- Never invent method signatures, parameters, or real business logic — every generated
  implementation method must compile but throw `UnsupportedOperationException` with a
  `// TODO` comment until the real logic is written (ideally after Step 3's consultation).
- Never hardcode the base package — always detect it (Step 2), even though this file's
  examples use `uy.oca.backofficenexito` for concreteness.
- If Step 1 doesn't confirm the project uses this template, say so explicitly and
  generate nothing — this skill is specific to this DI/layering convention, not a
  generic Spring Boot scaffolder.

## Final output

Report, without narrating the process:

- The 2 (or 3, if a domain model was needed) files created, with full paths.
- The detected base package.
- The result of compiling + running `CleanArchTest` (green, or which file landed in the
  wrong package).
- One reminder line: "check whether this needs a `COMPATIBILITY_NOTES.md` entry" — only
  if the project actually has that file.
