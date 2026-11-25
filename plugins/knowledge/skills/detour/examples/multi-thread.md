# Example: a detour with several threads

A format reference for the *several subjects at once* case of the `detour`
skill. It shows only the parts that differ from the single-thread handoff in
`handoff.md`: the interview record across threads, the shared concepts, one
block per thread, *how they connect*, and the targets that cross threads.
The other sections keep the same shape as in `handoff.md`.

The repo, paths and counts are illustrative. The general behavior of
MediatR pipeline behaviors, EF Core transactions and a transactional outbox
is real.

---

````markdown
# Detour: saving, transactions and the outbox (approve-flow-persistence)

## For you, the destination agent
(Same shape as the single-thread preamble.) The person got stuck on "where
the transaction actually starts and ends, and why the message to billing
isn't sent from the handler". There are three threads, and the confusion is
mostly in how they fit together.

## Where the person stands

This is their own account, from the interview in the repo session. It is
not an assessment.

- **EF Core `SaveChanges`:** `clear`. "I know it writes the tracked
  changes."
- **`TransactionBehavior` (MediatR pipeline):** `blurry in this repo's
  usage`. "I know MediatR handlers. I didn't know something runs around
  them." They predicted that `SaveChangesAsync` in the handler commits.
- **Outbox:** `new`. "Why not just publish to the bus in the handler?"
- **Neighboring knowledge:** "Middleware in ASP.NET Core, I know well."

## Shared concepts (in dependency order)
1. **Transaction boundary.** A set of writes either all commit or all roll
   back. Who opens the transaction decides what is inside it.
   (Threads 1 and 2.)
2. **Decorator / pipeline.** Code that runs around a call without that
   call knowing. (Thread 2.)
3. **Dual write.** Writing to a database and to a message broker cannot be
   one atomic action. Either one can succeed while the other fails.
   (Threads 2 and 3.)
4. **Transactional outbox, at-least-once delivery.** The message is stored
   in the same database transaction as the business change. A separate
   process publishes it later, and may publish it more than once.
   (Thread 3.)

*Assumed known:* unit of work, message brokers.

## Thread 1: EF Core 8.0.11, `SaveChanges` inside an outer transaction
(Mapping table as in `handoff.md`, short: when a transaction is already
open on the connection, `SaveChanges` writes inside it, and nothing is
committed until that outer transaction commits.)

## Thread 2: MediatR 12.2, `TransactionBehavior`
- **Construct:** `IPipelineBehavior<TRequest, TResponse>` wraps every
  handler, like middleware wraps an endpoint. This is the bridge the
  person mentioned.
- **This repo:** `src/Orders.Application/Behaviors/TransactionBehavior.cs:19`
  opens a transaction and calls `next()`. It commits when `next()`
  returns, and rolls back on an exception. It is registered for every
  command. (`Program.cs:33`, seen)

## Thread 3: the outbox in this repo
- `OutboxMessage` rows are added to the same `DbContext` by
  `OrderApproved` handling. (`src/Orders.Infrastructure/Outbox/OutboxWriter.cs:12`, seen)
- `OutboxDispatcher`, a hosted service, polls the table and publishes.
  It marks a row sent only after the publish succeeds.
  (`src/Orders.Infrastructure/Outbox/OutboxDispatcher.cs:40-58`, seen)

## How they connect

At runtime, `POST /orders/{id}/approve` runs in this order:

1. `TransactionBehavior` opens the transaction (thread 2).
2. The handler changes the order, and the outbox row is added (thread 3).
3. `SaveChangesAsync` writes both rows inside the open transaction
   (thread 1). Nothing is visible to other connections yet.
4. `TransactionBehavior` commits when the handler returns.
5. Later, out of the request, `OutboxDispatcher` reads the row and
   publishes it.

The person's blur sits between steps 3 and 4.

## What must be understood
1. **Why `SaveChangesAsync` in the handler is not the commit.** This is
   their prediction. The commit is step 4, in `TransactionBehavior.cs:27`.
   (Threads 1 and 2.)
2. **Why there is no publish in the handler.** Publishing there is a dual
   write. If the commit at step 4 fails, billing hears about an approval
   that never happened. (Threads 2 and 3.)
3. **Why billing may receive the same message twice, and why that is
   accepted.** The dispatcher publishes first and marks the row second
   (`OutboxDispatcher.cs:52`): at-least-once delivery. (Thread 3.)
````
