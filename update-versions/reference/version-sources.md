# Version sources and gotchas by ecosystem

Read only the sections for ecosystems present in the project. Every query filters out
pre-releases. Keep raw responses in a sandbox or scratchpad file and print only the
derived versions.

Shared pre-release filter for version lists:

```bash
rg -iv '(rc|alpha|beta|milestone|snapshot|preview|-m[0-9]|\.m[0-9]|cr[0-9]|ea)' | sort -V | tail -3
```

---

## Runtimes and LTS lines

- Java (Temurin): `https://api.adoptium.net/v3/info/available_releases` gives
  `most_recent_feature_release` and `available_lts_releases`. The latest patch of a line
  is in `https://api.adoptium.net/v3/assets/latest/<major>/hotspot?image_type=jdk&os=linux&architecture=x64`
  (`openjdk_version`, `release_name`).
- Node.js: `https://nodejs.org/dist/index.json` (`lts` field is the codename, or `false`).
- End of life of any line: `https://endoflife.date/api/<product>.json` (`eol`, `lts`,
  `latest`).
- A non-LTS feature release loses support within months. Flag it in the inventory.
  Only propose it when the user explicitly wants feature releases.

## Maven Central and Gradle

- Library: `https://repo1.maven.org/maven2/<group/as/path>/<artifact>/maven-metadata.xml`.
- Gradle plugin: `https://plugins.gradle.org/m2/<plugin/id/as/path>/<plugin.id>.gradle.plugin/maven-metadata.xml`.
- Gradle itself: `https://services.gradle.org/versions/current`. Runtime support matrix:
  `https://docs.gradle.org/current/userguide/compatibility.html`.
- Update the wrapper with `./gradlew wrapper --gradle-version <v>` and then
  `./gradlew wrapper` again. The second run regenerates the jar and the scripts with the
  new version. The regenerated `gradlew.bat` shows a large diff; keep its line endings
  as they were.
- Gradle 9.x deprecates implicit lookup of root properties from subprojects. Inside
  `subprojects {}` use `rootProject.libs...`.
- Coverage and formatter tools that Gradle applies with a default version (JaCoCo) still
  count. Pin them in the catalog with `toolVersion`.
- Tools that use compiler internals (palantir/google-java-format, Error Prone, NullAway,
  JaCoCo) can break on a new JDK even when Gradle and the framework support it. Check
  their issue trackers for the target JDK before proposing it.
- Spotless runs the formatter in the Gradle daemon JVM, not in the toolchain. Its build
  cache entries do not include the JVM version. Run spikes with `--no-build-cache`. If a
  cache was already poisoned, rerun the format tasks with `--rerun-tasks` on the good JDK.

### Spring Boot BOM

- Managed versions: `spring-boot-dependencies-<boot>.pom` on Maven Central (`<x.version>`
  properties). The next Boot release candidate's BOM shows what Boot plans to move to.
  That is a signal, not proof.
- System requirements (Java range, Gradle range):
  `https://docs.spring.io/spring-boot/system-requirements.html`.
- Override managed versions from the catalog, inside `subprojects`, after
  `apply plugin: 'io.spring.dependency-management'`:
  `ext['flyway.version'] = rootProject.libs.versions.flyway.get()`. Confirm each override
  with `dependencyInsight`.
- Cross-coupled families (Jackson databind and annotations, Spring Framework, Security,
  Micrometer) can break when only one side moves. Prove each override in the spike and
  try the next older line when the spike fails.

## npm

- `npm view <pkg> dist-tags --json` (`latest` is the stable tag) and
  `npm view <pkg> versions --json` for the full list.
- Pin exact versions (no `^` or `~`) when the rule asks for exact versions, and update
  the lockfile with the package manager the project uses.
- Check `engines` and peer dependencies of every major.

## PyPI

- `https://pypi.org/pypi/<pkg>/json`: `info.version` is the latest stable. `releases`
  holds the full list; filter pre-releases.
- Check `requires_python` against the project's runtime.

## Container images

- Docker Hub:
  `https://hub.docker.com/v2/repositories/<namespace>/<repo>/tags?page_size=100&name=<prefix>`.
  Use `library` as the namespace for official images. The `name` filter matches
  substrings (`27` also matches `11.0.27_6`) and results are paginated. Query narrow
  prefixes (`18.6`, `25.0.`) or follow `next` before you call a version the latest.
- quay.io: `https://quay.io/api/v1/repository/<namespace>/<repo>/tag/?limit=100&onlyActiveTags=true`.
- GHCR and others: the project's GitHub releases plus a `docker pull` of the exact tag.
- Pick the tag with a patch that matches the variant in use (`18.6-alpine`,
  `25.0.5_8-jre-alpine`, `v3.7.18`). Confirm with `docker pull` when the registry is
  reachable.

### Databases in containers

- PostgreSQL 18+ images mount data at `/var/lib/postgresql` (not
  `/var/lib/postgresql/data`). A data directory from an older major does not start with
  the new binary. It needs `pg_dump`/restore or `pg_upgrade`. Before changing the tag,
  list containers and volumes (`docker ps -a`, `docker volume ls`). Never delete them
  without the user's confirmation.
- With `cap_drop: ALL`, the PostgreSQL 18 entrypoint fails with
  `chmod: ... Operation not permitted` unless it gets enough capabilities to fix
  ownership. Test the hardened service once before relying on it.
- Migration tools (Flyway, Liquibase): keep the CLI image and the embedded library
  aligned. Run the CLI against a history table written by the library (`info`) as a
  check.

## GitHub Actions

- Releases: `gh api repos/<owner>/<repo>/releases --jq '[.[]|select(.prerelease==false and .draft==false)|.tag_name]|.[0:5]'`.
- Pin `@vX.Y.Z`, never `@vX`. Read the release notes of every major in between: Node
  runtime bumps, removed or renamed inputs, changed defaults, new terms of use. For
  example, `gradle/actions` v6 moved caching to a proprietary component, and
  `cache-provider: basic` keeps it MIT.
- Runner labels: `actions/runner-images` README. `*-latest` breaks the rule; use the
  newest GA label (`ubuntu-26.04`), not one marked beta or preview. The per-image readme
  lists Docker, Compose and preinstalled runtimes.
- `setup-java` / `setup-node`: pin the runtime version with patch (`'25.0.5'`), matching
  the container images.
- CI cannot run without a push. Validate with a YAML parse and with
  `rg -n '@v[0-9]+$|latest' .github`.

## Dependency bots

- Dependabot or Renovate configs usually pin nothing. Confirm that every ecosystem now
  pinned exactly (docker, docker-compose, github-actions, gradle, npm, pip) is covered.
  Report a gap; do not add new ecosystems unasked.
