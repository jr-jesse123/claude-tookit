# Example — a detour handoff

A format reference for step 4 of the `detour` skill, not a template: size the
real handoff to the real subject. The repo, paths and counts below are
illustrative. The facts about EF Core are real, for the version named. A real
handoff is written in the language the user is speaking. This one is in
English so it can serve as a reference for any language.

---

````markdown
# Detour: change tracking in EF Core (ef-change-tracking)

## For you, the destination agent

The person you are talking to is reviewing a pull request in an
order-management API (.NET 8, EF Core 8.0.11, SQL Server). They got stuck
on `AsNoTracking` and on what EF Core does, or fails to do, when entities
are changed and saved. Their goal is to go back to the PR able to decide
whether moving the order loader to `AsNoTracking` is safe.

You know this person and how they learn. This brief covers *what* to
cover and *when they are done*, not *how* to teach it.

- In scope: the base concepts below, how EF Core 8 models them, and the
  repo excerpts in this brief.
- Out of scope: the rest of the project, and judging the PR. Both happen
  back in the repo.
- When examples help, take them from *Project context*. The person will
  meet these same entities again in the code.
- They are done when they can answer the *Exit questions* in their own
  words. Then help them fill in the *Return note* at the end, which they
  will paste back into the repo session.

Markers: `seen` means the source was opened and says it; `inferred` means
a conclusion drawn from what was opened.

## Project context

- **What it is:** a back-office API where operators create, edit and
  approve customer orders. ASP.NET Core with MediatR handlers, EF Core over
  SQL Server. (`README.md`, `src/Orders.Api/Program.cs:14`, seen)
- **Where the subject lives:** the order-approval flow. `POST
  /orders/{id}/approve` reaches `ApproveOrderHandler`. The handler loads
  the order through `OrderRepository`, checks the approval rules, sets
  `Status = Approved` and saves. (`src/Orders.Application/Approve/ApproveOrderHandler.cs:21-47`, seen)
- **Entities:**
  - `Order`: aggregate root, with `Status` and `ApprovedBy`, owns its
    `OrderLine`s.
  - `OrderLine`: product, quantity, price.
  - `RowVersion`: a SQL Server `rowversion` column on `Order`.
  (`src/Orders.Domain/Order.cs:8-40`, seen)
- **Constraint that matters here:** several operators edit the same order
  at once. The `RowVersion` exists so that the second writer gets a
  conflict instead of silently overwriting the first.
  (`docs/adr/0007-optimistic-concurrency.md`, seen)

## Where it showed up

The PR changes the loader used by the approval flow:

```csharp
// src/Orders.Infrastructure/OrderRepository.cs:31 (after the PR)
public Task<Order?> GetForEditAsync(Guid id, CancellationToken ct) =>
    _db.Orders.AsNoTracking()          // ⊕ added in this PR
        .Include(o => o.Lines)
        .SingleOrDefaultAsync(o => o.Id == id, ct);
```

```csharp
// src/Orders.Application/Approve/ApproveOrderHandler.cs:41 (unchanged)
order.Approve(cmd.OperatorId);         // sets Status and ApprovedBy
await _db.SaveChangesAsync(ct);
```

**Decision waiting:** whether this change is safe for the approval flow,
and what else would have to change with it.

## Base concepts (in dependency order)

1. **Unit of work.** A session collects every change made during one
   business operation and writes them together, in one transaction, at the
   end. The application changes objects; the session works out which SQL
   to send. Other names: session, persistence context.
2. **Change tracking.** To know what changed, the unit of work has to
   remember what each loaded object looked like when it was loaded. There
   are two broad ways to do this:
   - *snapshot*: keep a copy of the original values, and compare against
     it when saving;
   - *notification*: each object reports its own changes.
   An object the unit of work is not tracking is invisible to it, and
   changes to that object are never saved.
3. **Identity map.** Within one unit of work, a given database row is
   represented by at most one object. Loading the same row twice returns
   the same instance.
4. **Optimistic concurrency.** Writers do not take locks. Each write checks
   that the row is still at the version the writer read, and fails if not.
   This needs the version value *from the time of the read* to reach the
   `UPDATE ... WHERE`.

*Assumed known:* ORMs mapping classes to tables; transactions; SQL
`UPDATE ... WHERE`.

## How EF Core 8.0.11 models them

| Concept | EF Core construct | What it guarantees | Default | Where it departs from the general idea | Source |
| --- | --- | --- | --- | --- | --- |
| Unit of work | `DbContext` + `SaveChanges` | All tracked changes are saved in one transaction. | One context per request in ASP.NET Core (scoped DI). | It is not tied to a transaction until `SaveChanges`: reads in between run outside it. | learn.microsoft.com/ef/core/saving/transactions (seen) |
| Change tracking | `ChangeTracker`, snapshot by default | Changes to *tracked* entities are detected on `SaveChanges` (`DetectChanges`). | Queries track (`QueryTrackingBehavior.TrackAll`). | Tracking is a per-query choice: `AsNoTracking()` returns entities that the context never sees. | learn.microsoft.com/ef/core/querying/tracking (seen) |
| Re-attaching | `Update()`, `Attach()`, `Entry().State` | Makes a detached entity tracked again. | — | `Update()` marks *every* property modified, so the UPDATE writes the whole row. | learn.microsoft.com/ef/core/change-tracking/explicit-tracking (seen) |
| Identity map | identity resolution | Tracking queries return one instance per key. | On for tracking queries. | No-tracking queries do *not* resolve identity, unless `AsNoTrackingWithIdentityResolution()` is used. | learn.microsoft.com/ef/core/querying/tracking#identity-resolution (seen) |
| Optimistic concurrency | `[Timestamp]` / `IsRowVersion()` | The original token value goes into `WHERE`. If 0 rows are affected, EF throws `DbUpdateConcurrencyException`. | — | The "original" value is whatever the tracked entry holds. After `Update()` on a detached entity, that is the value the entity carries. | learn.microsoft.com/ef/core/saving/concurrency (seen) |

## How this repo uses it

- **Default tracking is on.** The context does not change
  `QueryTrackingBehavior`. (`src/Orders.Infrastructure/OrdersDbContext.cs:12`, seen)
- **Read path:** 37 queries go through `ReadOnlyOrderQueries`, and all of
  them use `AsNoTracking()`. They feed GET endpoints only.
  (`src/Orders.Infrastructure/ReadOnlyOrderQueries.cs:18`, seen; the count
  is from grep)
- **Write path:** handlers load through `OrderRepository`, change the
  aggregate, and call `SaveChangesAsync`. No handler calls `Update()` or
  `Attach()`. (grep across `src/Orders.Application`, seen)
- **Concurrency:** `Order.RowVersion` is configured with `IsRowVersion()`.
  (`src/Orders.Infrastructure/Config/OrderConfig.cs:22`, seen)
- **Unusual use:** after this PR, `GetForEditAsync` is the only method
  named `...ForEdit` that does not track. (inferred, from the naming
  pattern in `OrderRepository.cs`)

## Exit questions

1. In `ApproveOrderHandler.cs:41`, the order now comes from a no-tracking
   query and `SaveChangesAsync` runs right after `Approve(...)`. What is
   written to the database, and why?
2. Suppose the fix is to call `_db.Update(order)` before saving. What does
   the `UPDATE` statement contain, and what does that mean for the order
   lines loaded through `Include`?
3. Two operators approve the same order at the same moment, with that fix
   in place. Does the `RowVersion` still protect them? What has to be true
   about the `order` instance for it to work?
4. The PR description says it was done "for performance". On the approval
   flow, which loads one order with its lines, where does the cost of
   tracking actually come from?

## Sources

- EF Core 8 docs at learn.microsoft.com/ef/core/:
  - `querying/tracking`
  - `change-tracking/explicit-tracking`
  - `saving/concurrency`
  - `saving/transactions`
- Repo files quoted above, at the PR head commit.

## Return note

Fill this in together, then paste it back into the repo session with
`/knowledge:detour --return`.

```
# Return: change tracking in EF Core (ef-change-tracking)
- In my words: <the idea, 3–5 lines>
- Exit answers: Q1 → … / Q2 → … / Q3 → … / Q4 → …
- What I now assume about this code: <statements to check>
- Still fuzzy: <what is left>
```
````
