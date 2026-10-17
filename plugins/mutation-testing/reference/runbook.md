# Stryker.NET runbook (unit-only, incremental, ephemeral)

Follow the skill's eligibility gates BEFORE installing tooling or executing
tests. Names like Foo.UnitTests are not proof: inspect base classes, fixtures,
test setup and CI commands. A negative filter that only excludes known E2E
tests does not establish that the remainder is safe.

## Scope

Inspect working, index and committed branch changes; include untracked files.
A --base ref or --since does **not** identify task ownership. --since alone
is insufficient because changes to tests can mark unrelated mutants changed.

Stryker accepts positive selectors with character spans:

    -m "Services/OrderService.cs{100..340}"

For an existing large file, first identify the complete affected C# method
or similar declaration with syntax inspection. Do not guess its boundaries.
Convert its verified 1-based inclusive line range using the helper:

    python3 "$CLAUDE_PLUGIN_ROOT/scripts/line-span.py" \
      --project-root /path/to/ProductionProject \
      --file /path/to/ProductionProject/Services/OrderService.cs \
      --start-line 12 --end-line 44

The helper produces a project-relative selector with UTF-16 code-unit
character offsets and preserves CRLF. It does not parse C#. For multiple
methods on one line, use Roslyn/source TextSpan or skip instead of mutating
unrelated code. For entirely new files, a positive whole-file selector is
acceptable.

## Baseline (only verified existing unit tests)

For an inspected dedicated unit project:

    dotnet test /path/to/App.UnitTests/App.UnitTests.csproj

For an inspected mixed test project with verified positive unit category:

    dotnet test /path/to/Tests.csproj --filter "TestCategory=Unit"

Require passing tests and a nonzero executed count. Apply the exact filter
in Stryker. The test-case-filter feature depends on runner support; some
Microsoft Testing Platform runners, notably xUnit v3/TUnit variants, lack a
compatible --filter option. If filtering cannot be guaranteed, skip.

No integration test is eligible in v1, including SQLite-in-memory and
WebApplicationFactory integration tests. External DB, network, container,
cloud and E2E tests are forbidden even for the baseline.

## Temporary installation

Create a unique scratch directory outside the repository.

    # Bash
    scratch="$(mktemp -d)"
    dotnet --list-sdks
    dotnet --list-runtimes
    dotnet tool install dotnet-stryker --tool-path "$scratch/tools" --version "5.*"

    # PowerShell
    $scratch = Join-Path ([IO.Path]::GetTempPath()) ([IO.Path]::GetRandomFileName())
    New-Item -ItemType Directory -Path $scratch | Out-Null
    dotnet --list-sdks
    dotnet --list-runtimes
    dotnet tool install dotnet-stryker --tool-path (Join-Path $scratch "tools") --version "5.*"

Only use Stryker 5.x with .NET 10 runtime; use a compatible 4.x version when
only .NET 8 runtime is present, or skip. Stryker's runtime requirement
does not change the production project's target framework.

Do not install Stryker into a project-local manifest. .NET 10 may create one
automatically if --tool-path is omitted. A compatible existing Stryker may
be reused when its version/invocation is verified.

## Temporary config, explicit selection

Write the following to an absolute file such as scratch/config.json,
**not** to the repository. Change the project name and selector to approved
values; the project option names a referenced production csproj filename.

    {
      "stryker-config": {
        "project": "App.csproj",
        "mutate": ["Services/OrderService.cs{100..340}"],
        "reporters": ["json", "progress"],
        "mutation-level": "Standard",
        "concurrency": 2,
        "break-on-initial-test-failure": true
      }
    }

For a vetted mixed suite add the key and its proven allowlist expression:

    "test-case-filter": "TestCategory=Unit"

Execute from the selected test-project directory:

    # Bash
    "$scratch/tools/dotnet-stryker" --config-file "$scratch/config.json" \
      --output "$scratch/results" --skip-version-check

    # PowerShell
    & (Join-Path $scratch "tools/dotnet-stryker.exe") `
      --config-file (Join-Path $scratch "config.json") `
      --output (Join-Path $scratch "results") --skip-version-check

Default operation is one production project via one verified eligible
test project. For a multi-target or .NET Framework project you may need
an explicit target-framework or solution option. For 1 production project
and N eligible unit-test projects Stryker supports multiple --test-project
arguments while running from the production project; never add an
unverified project.

Always use explicit --config-file so a pre-existing repository config
cannot silently select extra tests, mutations or dashboard uploads.
The --output option moves Stryker logs/reports, but normal builds can
still create obj/bin and NuGet caches.

## Results and cleanup

Inspect JSON reports by mutant status and source path/range, not just the
aggregate score. A mismatch in scope invalidates the run. A no-mutants
report, failing initial tests, or unfilterable mixed suite is not a pass.
Do not upload results to a hosted dashboard.

After reading the report, delete only the scratch directory created by
the current invocation, and verify Git status against the pre-run inventory.
Never use git clean, reset, stash, stage or commit. Preserve legitimate
source/test edits and all pre-existing files.

Sources: https://stryker-mutator.io/docs/stryker-net/configuration/
https://stryker-mutator.io/docs/stryker-net/migration-guide/
https://learn.microsoft.com/dotnet/core/tools/dotnet-tool-install
