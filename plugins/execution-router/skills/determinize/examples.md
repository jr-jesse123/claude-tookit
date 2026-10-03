# Worked extraction contracts

All task facts below are hypothetical supplied inputs. No implementation or
tests have run. Use the case matching the current uncertainty.

## Mixed task: exact reconciliation plus explanation

**Input.** Each day reconcile two complete JSON arrays of posted payments and
explain discrepancies. The supplied contract says IDs are unique case-sensitive
strings, each amount is an integer number of cents, all rows are USD, and each
array is an immutable snapshot for the same interval. C1: report every missing
ID and amount mismatch with both original values. C2: explain likely business
causes without presenting hypotheses as confirmed facts. K1: retain every
source row and make no payment changes. Hundreds of daily batches justify a
reusable exact comparison; explanations remain case-specific.

**Status:** `proposed-extraction`.

**Exact portion and mechanism.** Parse both arrays, validate the supplied schema
and uniqueness constraints, index by exact ID, compare key sets and integer
amounts. Return source-linked missing-left, missing-right, and differing-amount
records. Preserve originals; deterministic ID ordering only affects display.
On duplicate IDs, invalid amounts, a non-USD row or mismatched snapshot scope,
reject the batch for resolution rather than choosing a row or silently rounding.
Keep both original arrays available to the explanation stage, not only totals.

**Oracle.** C1 is a set relation over exact IDs and integer equality, established
by the supplied reconciliation contract. Fixtures with independently enumerated
expected differences cover empty arrays, zero/negative cents, amount mismatch,
missing IDs on both sides and reordered rows. Require a representation that can
hold every permitted integer exactly; a representation that rounds two unequal
large amounts to the same value is a counterexample. Tests of JSON validity
alone do not prove C1. These are validation requirements, not passing results.

| Criterion or constraint | Exact obligation | Semantic residual |
| --- | --- | --- |
| C1 | Enumerate all set/equality differences with original values | None within validated domain |
| C2 | Supply source-linked differences and originals | Investigate/explain causes; distinguish hypotheses from facts |
| K1 | Preserve rows; read-only comparison | Preserve the same no-payment-changes constraint during investigation |

**Residual and recomposition.** Given the difference records and both snapshots,
explain potential causes, identify additional evidence needed, and state which
causes remain unconfirmed. Present the exhaustive difference list alongside
those explanations. Do not infer that a missing row means fraud or failed payment.

**Economics and work remaining.** Recurring identical comparison semantics support
the setup and fixture cost; changing the supplied ID or currency rules would
require reevaluation. Implement/validate the comparator, collect valid snapshots,
execute comparison, then perform the generative explanation and assemble the
report. None of that work has been performed by this design.

## No extraction: a deterministic keyword rule loses meaning

**Input.** Decide whether a complaint proves a refund is owed. C1: apply the
customer's actual refund policy and exceptions. C2: preserve quoted context.
The complaint is supplied but the refund policy is missing. A suggested keyword
rule would refund any text containing "broken".

**Status:** `no-extraction`. **Exact portion:** none.

The keyword rule executes deterministically but cannot satisfy C1. "The item
wasn't broken; I ordered the wrong color" is a counterexample to that rule,
not a new refund policy. Quoting text exactly does not resolve eligibility and
has no supplied payoff as a separately modeled extraction. A schema validator
would prove output shape, not policy compliance.

| Criterion | Exact obligation | Semantic residual |
| --- | --- | --- |
| C1 | None | Obtain applicable policy and judge eligibility with exceptions |
| C2 | None | Preserve the complaint's quoted context |

**Residual:** the entire original task, unchanged, with the absent policy named.
**Recomposition:** no extracted result exists. **Economics:** there is no supported
semantics-preserving candidate to fund. **Work remaining:** acquire the policy,
resolve eligibility, preserve source context. Suggest a generative handoff; do
not investigate the policy merely to justify this extraction.

## No extraction: technically feasible, uneconomic

**Input.** For one short, irregular note, produce a polished narrative summary
and include a verbatim list of its three supplied IDs. C1: preserve the note's
meaning. C2: copy all three IDs exactly. The user states this is a one-off, the
IDs are already listed explicitly, and no new guarantee is required.

**Status:** `no-extraction`. **Exact portion:** none. Copying known IDs can be
exact, but introducing a parser, interface and separate assembly step adds work
without a supported benefit. Stop before designing it.

| Criterion | Exact obligation | Semantic residual |
| --- | --- | --- |
| C1 | None | Summarize faithfully |
| C2 | None | Include the supplied IDs verbatim as part of the original task |

**Residual:** the original summary task including exact copying, unchanged.
Residual work need not be purely generative: rejecting decomposition does not
erase its small exact obligations. **Work remaining:** produce and verify the
summary with the original criteria. **Next step:** a generative handoff for the
whole task.

## Already exact: an empty semantic residual still leaves execution

**Input.** Verify that a supplied byte buffer equals a known reference buffer.
C1: equality means identical length and every byte equal. K1: do not modify
either buffer. A trusted byte-equality routine and this exact oracle are already
supplied; the user asks whether a new transformation is useful.

**Status:** `already-exact`. The existing routine covers C1 and K1. Inputs are
the two unchanged buffers; output is a boolean. Invalid/unavailable buffers
must produce an input error, not equality. The oracle compares length and bytes
against the supplied definition. Boundary cases include empty, equal and
same-length unequal buffers; different bytes with a colliding hash invalidate
substituting hash equality as an exact proof.

| Criterion or constraint | Exact obligation | Semantic residual |
| --- | --- | --- |
| C1 | Existing exact byte comparison | None |
| K1 | Read-only access to both buffers | None |

**Economics:** no new modeling or framework is justified. **Semantic residual:**
none, because the supplied contract covers all obligations. **Recomposition:**
report the routine's actual boolean result. **Work remaining:** obtain the valid
buffers, run the routine and verify/report the result. Equality has not been
established by this planning response. **Next step:** direct exact execution by
the caller; no model-router or Jev call.
