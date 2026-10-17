# Acceptance cases — incremental-dotnet-mutation

| Situation | Expected behavior |
| --- | --- |
| No test project | Skip before preparing Stryker; no tests project created. |
| Only E2E or integration tests | Skip; no baseline executed. |
| Integration test runs entirely in memory | Skip: not supported in v1. |
| UnitTests-named project starts Docker in a fixture | Reject; names are not proof. |
| Mixed suite, category unknown | Skip instead of running everything. |
| Mixed suite, proven positive Unit filter supported by both runners | Baseline and Stryker must use identical filtered set. |
| Mixed suite, MTP runner does not support test-case-filter | Skip. |
| Dedicated safe unit tests, no Stryker installed | Tool and config live outside repo; perform scoped run. |
| Only .NET 8 runtime | Compatible Stryker 4.x or skip; no blind 5.x install. |
| One changed method in large existing class | Mutate declaration span only; no file-wide fallback. |
| Entirely new .cs file | Exact file-level selector allowed. |
| Only tests changed; production unchanged | Skip, do not widen via --since. |
| Diff contains unrelated pre-existing user changes | Declare uncertainty, restrict or skip. |
| Unit baseline fails or discovers zero tests | Stop without reporting pass. |
| Report generated zero mutants | Report absence of evidence, not 100% score. |
| Survivor equivalent to original behavior | Explain; no brittle assertion just to kill. |
| --improve with existing eligible test project | Add/strengthen unit cases in that project only. |
| Running Stryker generates build artifacts | Preserve pre-existing files; cleanup only verified new scratch artifacts. |
| Interrupted or failed execution | Report failure; never git clean/reset/stash/commit. |
