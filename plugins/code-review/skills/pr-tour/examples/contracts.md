# Contracts examples — promise delta, compatibility verdict, blast radius

Format reference, not a template. The section appears only when the diff
introduces, changes, or removes a promise other code relies on; write the
real entries in the user's language, sized to the real contract. Every
entry moves promise → verdict → radius; what varies by kind is who counts
as a consumer — an implementor (interfaces), a subscriber (events), a
caller (endpoints), old data (schemas). A new contract has no before and
its verdict names the commitment; a removed one has no after and is
breaking by definition.

## Type contract — widened union (typed language)

> - `Invoice.status` · `src/billing/schema.ts:12` — union widened:
>   `"open" | "paid"` → `"open" | "paid" | "refunded"`. Additive for
>   producers; breaking for exhaustive consumers. Bound by it:
>   `billing/report.ts:88` (exhaustive switch, updated here),
>   `export/csv.ts:31` (exhaustive switch, **not in this diff**),
>   `api/serialize.ts:57` (pass-through, unaffected). Rows persisted
>   before the deploy never carry `"refunded"` — old readers need no
>   backfill.

## Interface contract — new member

> - `PaymentGateway.refund()` · `src/payments/gateway.ts:9` — member
>   added: `refund(receipt: Receipt): Promise<void>`. Reads as additive
>   in the diff; breaking for every implementor. Bound by it:
>   `payments/stripe.ts:120` (implemented here), `payments/mock.ts:44`
>   (implemented here) — no other `implements PaymentGateway` in the
>   repo.

## Event contract — repurposed field

> - `order.updated` payload · `src/events/order.ts:23` — field
>   repurposed: `total` (int, cents) → `total` (decimal string).
>   Breaking for every subscriber — nothing type-checks across the
>   queue. Bound by it: `analytics/ingest.ts:71` (updated here),
>   `email/receipt.ts:35` (**not in this diff**). Messages published
>   before the deploy still carry the int payload — subscribers see both
>   shapes during rollout.

## New contract — endpoint introduced (⊕, no before)

> - `GET /invoices/:id/refunds` · `api/routes.ts:102` — ⊕ new endpoint:
>   returns `Refund[]` (200), 404 for unknown invoice, auth middleware
>   matching the other billing routes. New promise: public API surface
>   grows — response shape is committed once external clients appear.
>   Consumers wired in this diff: `web/refund-list.tsx:33`; none outside
>   the diff yet, so this is the cheapest moment to reshape it.

## Endpoint contract — narrowed request

> - `POST /refunds` · `api/routes.ts:88` — request narrowed: `reason`
>   optional → required (422 without it). No schema file changed — the
>   narrowing lives in the validator at `api/validate.ts:31`. Breaking
>   for callers that omit `reason`: `web/checkout.tsx:210` (updated
>   here); mobile clients ship on their own cadence — cannot be verified
>   from this repo.

"Not in this diff" is a fact of the terrain, not a finding — the review
verdict belongs to `/code-review:quick-review`.
