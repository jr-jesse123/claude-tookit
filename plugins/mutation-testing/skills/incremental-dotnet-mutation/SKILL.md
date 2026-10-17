---
name: incremental-dotnet-mutation
description: Incremental Stryker.NET mutation testing for code newly written or modified during a .NET task, with existing, independently verified unit tests only. Bootstrap temporary Stryker tooling when no repo setup exists. Skip without unit tests; never execute integration, E2E or externally dependent tests.
argument-hint: "[--base REF] [--validate | --improve]"
---

# Incremental .NET mutation testing

Evaluate how effectively **existing unit tests** catch regressions in C# code
changed by the current task. This skill does not mandate repository-wide
mutation testing or adoption of permanent tooling. Read
${CLAUDE_PLUGIN_ROOT}/reference/runbook.md before invoking Stryker.

## Hard gates

1. **Existing unit-test infrastructure.** Find a test project and relevant,
   runnable tests already in the repository. Do not create a new test project
   or introduce a runner just to enable mutation testing.
2. **Unit tests only.** Exclude ALL integration and E2E suites, including
   integration tests that run entirely in-memory (v1 policy). Exclude any tests
   touching real DBs, external services, network, containers or browsers.
   Mocks and pure fakes within unit tests are fine.
3. **Prove test eligibility.** Names are hints, not evidence. Inspect test
   bodies, shared fixtures, base classes, setup/teardown, project settings
   and CI. Mixed suites require a verified positive unit-only filter that
   *both* the selected test runner and Stryker honor. If classification or
   filter support is uncertain, skip. Never run the whole mixed suite.
4. **Mutate only task-owned production behavior.** A file-level selector is
   allowed for entirely new files. In existing files select verified changed
   method/constructor/property/local-function spans. If the scope cannot be
   resolved reliably, skip it; never fall back to mutating the whole legacy
   file or project. Do not use --since as the sole scope guard: changed test
   files can widen its selection.
5. **No permanent mutation infrastructure.** Do not add or edit
   stryker-config.json, tool manifests, csproj dependencies, CI jobs, ignore
   comments, or other mutation-testing infrastructure in the target repo.
   Use a fresh temporary config and tool installation outside the worktree.
6. **Preserve workspace.** No git clean, reset, stash, stage or commit. Remove
   only temporary files positively identified as created by this run.
7. **Never fake a pass.** No tests, failing baseline, unsupported runner,
   unknown side effects, zero mutants, and tool failure are different from
   successful validation.

## Modes

- **--validate:** inspect and report; do not edit production or test files.
- **--improve (default):** improve relevant unit cases *in an existing eligible
  project*, then rerun. Maximum two improvement rounds. Never modify correct
  production code simply to kill mutants.
- **--base REF:** optional comparison ref; it does not prove task ownership.

No automatic Git staging, commits, hooks or CI adoption in either mode.

## 1 — Resolve the owned diff

Prefer a pre-task snapshot/explicit touched-declarations record from the
current session. Otherwise inspect git status, unstaged/staged diffs,
untracked C# files, and branch diff against the merge-base if applicable.
Explain when pre-existing changes cannot be distinguished from this task.

Identify changed source projects and the enclosing declarations. Choose
complete method-level spans for modified C# files: inspecting syntax, use
Roslyn if ambiguity exists. The line-span helper maps **known 1-based
declaration line boundaries** to UTF-16 character positions, but cannot
discover declarations; see runbook. New files can be selected in full.
When multiple declarations share lines or syntax is ambiguous, obtain
precise syntax spans or skip. Renames and removed methods may not have
corresponding executable mutants; disclose that instead of broadening scope.

## 2 — Prove eligible existing unit tests

Trace production project references to test projects; inspect concrete tests
relevant to the changed behavior. Review transitive fixtures and setup.
A dedicated, inspected unit-only project may be used without a filter.
A mixed project is eligible only with an explicit positive allowlist/filter
verified against both dotnet test and Stryker's runner; some MTP runners
(including particular xUnit v3/TUnit configurations) cannot support
test-case-filter. Never silently drop the filter.

If no verified unit tests relevant to the changed code are found, or the
target repo has only integration/E2E tests, **stop as Skipped** before
installing Stryker. No new test project.

## 3 — Verify the unmutated baseline

Run only approved unit tests, with the same filter planned for Stryker.
Require a passing result and a nonzero executed-test count. If the baseline
fails, no tests run, or the runner cannot honor the selection: stop and
report the obstacle. Do not expand test selection.

## 4 — Prepare disposable Stryker

Determine SDK and runtime availability first. Stryker.NET 5 needs .NET 10
runtime; Stryker.NET 4 needs .NET 8 runtime. Use an already installed
compatible tool when verified, or install a compatible version using
dotnet tool install --tool-path into a unique temporary directory **outside**
the repository. Never install a local tool without --tool-path.

Write a temporary Stryker config outside the repo with: exact production
project, positive mutate file/span selectors, only eligible test project(s)
and, for a mixed suite, its proven filter. Reporters must be local JSON
and optionally progress, with no dashboard. Use --config-file to prevent
implicit repository config from expanding the scope. Keep --output external.

## 5 — Execute and evaluate

Run from the selected test-project directory. Use Standard mutation level,
modest concurrency and no mandatory score threshold unless user requested
one. Before believing the score, inspect the JSON report to ensure the tool
actually mutated **only** approved declarations. Stop if it widened scope.

Separate Killed, Survived, NoCoverage, Timeout, Ignored and CompileError;
an empty set of mutants is **no evidence**, not 100%. In --improve mode,
strengthen unit tests for meaningful surviving behavioral differences
without assertions tied to implementation trivia; keep changes confined to
the existing unit-test project. Re-run the selected baseline and mutations.
Equivalent mutants remain explicitly unresolved.

## 6 — Cleanup and report

Read results first, then remove only the scratch files this run created.
Inspect final git status against the initial inventory. Stryker can still
produce normal bin/obj output and NuGet caches; do not assume --output
prevents that. Do not delete anything pre-existing. Do not stage/commit.

Report one outcome: **Validated**, **Surviving gaps**, **Skipped** or
**Failed**. Include task scope, verified unit-test projects/filter and
baseline count, generated mutant totals by status, important survivors,
test changes, skipped/unsupported areas, and evidence of cleanup. State
that no mutation-specific infrastructure was committed.

Review ${CLAUDE_PLUGIN_ROOT}/tests/acceptance.md for boundary cases.
