# Execution protocol — git-narrator

This is the contract the executor agent follows. The planning skill writes plans
against it; the executor executes it **exactly and in order**. Deviating from a
gate is never an optimization — it is a defect.

## The one invariant

**The final tree must be byte-identical to the tree at the original HEAD.**
Every gate below exists to protect or verify that invariant. The executor never
edits file content — it only regroups the same changes into different commits.
If a gate failure tempts you to change code to make it pass, stop: the fix is
always moving files between slices, never editing them.

## Input contract

A valid plan (delivered in the spawn prompt) contains:

| Field | Meaning |
| --- | --- |
| `base` | Base branch name |
| `branch` | Branch being re-narrated |
| `expected_head` | SHA the branch must be at; abort on mismatch (drift since approval) |
| `build_cmd` | Command that compiles/checks the tree; empty means build gate degraded to the stated substitute |
| `test_cmd` + scoping syntax | How to run tests, and how to scope them to paths |
| `gate` | `build` \| `scoped` \| `full` |
| `slices[]` | Ordered: message (with `Stage:` trailer), complete file list |
| `pairs[]` | Reconstructions: path, `source_sha` (where the content lives in original history), add-position, remove-position, removal message |
| `push` | `true` → `--force-with-lease` at the end; `false` → local only |

**Fail fast on an incomplete plan:** the union of all slice file lists must
equal `git diff base...expected_head --name-only` exactly (pairs excluded —
their files are absent from the final diff by definition). Missing or extra
files → abort before touching anything, report which.

## Phase 0 — Sanity and baseline

1. `git status --porcelain` empty; current branch == `branch`;
   `git rev-parse HEAD` == `expected_head`. Any mismatch → abort, report, touch
   nothing.
2. Run the **precondition suite**: full `test_cmd` at the current HEAD. Red →
   abort and report the failures; re-narration of a red branch only relocates
   the redness. (This runs here, not in planning, so a failure costs planning
   time but never a half-rewritten branch.)
3. Create the backup: `git branch backup/narrate-<branch>-<yyyymmdd-HHMM> HEAD`.
   Every later step assumes this exists; verify it does.

## Phase 1 — Reconstruction

4. `git reset --soft $(git merge-base <base> HEAD)` — history gone, tree and
   index intact, everything staged.
5. `git restore --staged .` — clean slate for selective staging.
6. Per slice, in plan order:
   - If a pair's add-position is here: `git checkout <source_sha> -- <path>`
     then stage it. Content comes from history — never authored fresh.
   - `git add <the slice's files>`
   - `git commit` with the plan's message verbatim, trailers included.
   - If a pair's remove-position is here: `git rm <path>` and commit with the
     plan's removal message.
7. After the last slice: `git status --porcelain` must be empty. Leftover
   files mean phase 0's coverage check was bypassed — abort and restore.

**File-splitting (advanced, only when the plan explicitly demands it):**
interactive staging is unavailable; split by generating a patch and applying it
to the index — `git diff <merge-base> <expected_head> -- <file>` piped through
a hand-built partial patch into `git apply --cached`. Fragile; the plan must
justify why the file cannot live whole in the later slice.

## Phase 2 — Gates per commit

8. For each new commit, oldest first, in a **disposable worktree** (the user's
   working tree is never used for gate runs — later slices' files are sitting
   in it unstaged during reconstruction, and building it would test the wrong
   tree):

   ```
   git worktree add /tmp/narrate-gate <commit-sha>   # detached; legal even
   cd /tmp/narrate-gate                              # while the branch is
   <build_cmd>                                       # checked out elsewhere
   <test_cmd scoped to this commit's own tests>      # gate >= scoped
   <test_cmd for all tests committed so far>         # gate == full
   cd - && git worktree remove --force /tmp/narrate-gate
   ```

   Docs-only commits (intent slice, pair add/remove commits) pass the build
   gate trivially; run the build anyway if it is cheap, skip with a note if not.

9. **Gate failure = slicing error.** The tree is immutable, so the only lever
   is moving a file to an earlier slice. Read the error, identify the missing
   dependency (typical: a test fixture classified as support but imported by
   domain tests), move that file's assignment, then restart phase 1 from step 4
   with the amended plan. Cheap: reconstruction is seconds; the gates are the
   expensive part, and passed prefixes stay passed if their slices didn't
   change.
10. **Three amendment rounds maximum.** Not converging means two slices are
    genuinely interdependent: merge the failing commit with its predecessor
    (concatenate messages, keep both `Stage:` trailers) and re-gate. If even
    that stays red → abort and restore.

## Phase 3 — Verification and landing

11. `git diff backup/narrate-...  HEAD` — **must be empty.** This is the
    invariant made mechanical. Also verify `git status --porcelain` is empty.
    Any difference → abort and restore; report the diff.
12. If `push`: `git push --force-with-lease origin <branch>`. Never bare
    `--force`. If the lease fails, the remote moved since approval — do not
    retry with force; report and stop.
13. Report (this is the deliverable):
    - old → new commit mapping (`git log --oneline` of both, side by side),
    - gate results per commit, including amendment rounds used,
    - backup ref name and the exact restore command:
      `git reset --hard backup/narrate-<...>`,
    - pushed or local.

## Abort semantics

Abort means: `git reset --hard <backup ref>` (when phase ≥ 1 started), verify
HEAD == `expected_head` again, remove any leftover gate worktree
(`git worktree prune`), and report **what failed, what was restored, and that
the branch is exactly as before**. A silent partial state is the only
unacceptable outcome; a clean abort is a normal, successful run of the
protocol.
