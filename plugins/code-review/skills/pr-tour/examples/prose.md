# Prose examples — narrative and reading order at three PR sizes

Format reference, not a template. Write the real tour in the user's language,
sized to the real diff. Diagrams are omitted here — see the per-type files.

## Small PR (2 files) — no diagram, no category labels, no group headers

> The change teaches `parseDuration()` in `lib/duration.ts` to accept `"1h30m"`
> compound strings; `cli/args.ts` just passes user input through to it, so the
> new format becomes available on the `--timeout` flag with no other wiring.
>
> **Reading order**
>
> 1. `lib/duration.ts` — first: the whole behavior change lives here. Look
>    at: the new tokenizer loop at `lib/duration.ts:41` — what happens with
>    `"90"` (no unit) decides backward compatibility.
> 2. `lib/duration.test.ts` — the promised behavior. Look at: is the no-unit
>    case pinned, or only the happy compound path?

## Medium PR (6 files, cohesive) — one group, labels earn their place

> Billing gains refunds. `billing/schema.ts` introduces the `Refund` record;
> `billing/refund.ts` (new) implements issuing against the gateway;
> `api/routes.ts` wires `POST /refunds` to it; `billing/charge.ts` only
> changes to tag receipts with a `refundable` flag the new code reads.
>
> **Reading order**
>
> 1. `billing/schema.ts` — [Contracts] — first: both new code paths consume
>    the `Refund` type. Look at: nullability of `Refund.reason`.
> 2. `billing/refund.ts` — [Core] — the substance. Look at: the idempotency
>    guard at `billing/refund.ts:58` — double-submit is the risk here.
> 3. `billing/charge.ts` — [Core] — small but load-bearing. Look at: the
>    `refundable` flag — is it ever true for zero-amount receipts?
> 4. `api/routes.ts` — [Wiring] — connects the dots. Look at: auth middleware
>    on the new route matches the other billing routes.
> 5. `billing/refund.test.ts` — [Tests] — the promise. Look at: idempotency
>    covered, or only single-submit?
> 6. `openapi.yaml` — [Generated] — skim: regenerated from routes.

## Large PR — independent groups, each with its own tour

Structure only (narratives shortened). Groups ordered most substantive first;
cross-cutting docs land in a final housekeeping group.

> ### Group 1 — async billing pipeline (7 files)
> Narrative… (+ diagram per the selector). **Reading order** 1–7…
>
> ### Group 2 — logger swap, mechanical (9 files)
> One-sentence narrative; no diagram — same one-line change in nine call
> sites. **Reading order**: read `lib/log.ts` first, then spot-check two call
> sites; the rest are identical.
>
> ### Group 3 — housekeeping
> `README.md`, `CHANGELOG.md` touch both groups above. Look at: does the
> README's new example match Group 1's final API?
