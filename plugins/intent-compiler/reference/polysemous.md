# Terms that do not compress

A shipped prior, not evidence. These are terms whose intension is *not* fixed
even though they look catalogued — each evokes two or more strong frames, so
anchoring on one without a disambiguator scores **frame precision ≤ 1** and
usually lands in Expanded or Trimmed.

This file is to `compile` what a provider policy is to `choose-model`: a
starting prior that the project lexicon overrides once it has three entries
(see `compression-core.md` → **Lexicon thresholds**). When a term here proves
unambiguous *in your codebase* — because the surrounding vocabulary pins it —
the log says so and the log wins.

## The overloaded set

| Term | Competing frames | What pins it |
| --- | --- | --- |
| **agent** | (a) LLM tool-using loop; (b) actor/daemon process; (c) HTTP user-agent; (d) principal–agent in economics | Name the loop, the protocol, or the runtime |
| **service** | (a) DDD domain/application service; (b) deployable microservice; (c) systemd unit; (d) DI-injectable class | Name the layer or the deployment unit |
| **context** | (a) LLM context window; (b) DDD bounded context; (c) Go `context.Context` cancellation; (d) React context; (e) execution context | Almost always needs its qualifier kept |
| **event** | (a) domain event — a fact, past tense, immutable; (b) UI/DOM event; (c) message or command in transit | "domain event" or "integration event", never bare |
| **actor** | (a) actor model (Erlang/Akka/Orleans); (b) UML actor in a use case; (c) security principal | Name the mailbox or the diagram |
| **saga** | (a) long-running distributed transaction with compensation; (b) redux-saga side-effect middleware | Name compensation, or name the library |
| **projection** | (a) event-sourcing read model; (b) relational projection (choosing columns); (c) geometric/linear-algebra projection | "read model" is the unambiguous synonym |
| **aggregate** | (a) DDD aggregate root and consistency boundary; (b) SQL aggregate function; (c) MongoDB aggregation pipeline | "aggregate root" pins (a) |
| **repository** | (a) PoEAA/DDD repository pattern; (b) git repository; (c) package repository | Name the collection abstraction, or say "git repo" |
| **model** | (a) ML model; (b) MVC model; (c) domain model; (d) data model/schema | Qualify always |
| **policy** | (a) authorization policy; (b) retry/resilience policy; (c) DDD policy — a reaction to an event | Name what it decides |
| **transaction** | (a) database ACID transaction; (b) business transaction / unit of work; (c) blockchain tx | Name the boundary that holds it |
| **stream** | (a) event stream / log; (b) byte stream (IO); (c) Java `Stream` / LINQ-style pipeline | Name what flows |
| **middleware** | (a) request-pipeline component; (b) enterprise integration middleware / ESB | Name the pipeline |
| **handler**, **manager**, **processor**, **provider** | No frame at all — these are suffixes, not concepts | Nothing pins them; describe the behaviour |

## Terms whose meaning drifted

Canonicity is a moving target. For these, the catalogue and the model's
codebook may disagree about *which era* you mean, which is a miscompression
the score will not catch — canonicity looks high, precision looks high, and
the model still expands to the wrong decade.

| Term | The drift |
| --- | --- |
| **serverless** | FaaS-only (≈2015) → any managed-scaling runtime, containers included |
| **agent** / **agentic** | Autonomous software agent (classical AI) → LLM tool-use loop (post-2023) |
| **RAG** | Retrieve-then-stuff-the-prompt → an umbrella for retrieval-shaped architectures generally |
| **microservice** | Independently deployable bounded context → any HTTP service, however coupled |
| **reactive** | Reactive Streams / back-pressure → anything event-driven |
| **prompt engineering** | Wording tricks → context construction and evaluation |

When you need an era-specific meaning, pin it with a date, a spec, or an
implementation ("serverless as in Lambda-style per-request billing"). That is
a trim, and it is still cheaper than describing the whole thing.

## Terms that compress exceptionally well

The other end, worth knowing because these are where the technique pays. What
they share: a catalogue entry with a fixed intension, one dominant sense, and
enough training mass to be reliably in the codebook.

- Catalogued patterns with unambiguous names: `event sourcing`, `circuit
  breaker`, `strangler fig`, `outbox pattern`, `idempotency key`,
  `optimistic concurrency`, `write-ahead log`, `bulkhead`, `sidecar`.
- Standards and specs: any RFC by number, `RFC 7807 problem details`,
  `semantic versioning`, `ISO 8601`, `JWT`, `OAuth 2.0 authorization code
  flow with PKCE`.
- Named algorithms and guarantees: `consistent hashing`, `CRDT`,
  `read-your-writes consistency`, `serializable isolation`, `write skew`,
  `exponential backoff with jitter`.
- Named refactorings (Fowler's catalogue): `extract method`, `introduce
  parameter object`, `replace conditional with polymorphism`.

The tell they share: you can ask "what does X imply?" and get the same list
back twice. That is what a fixed intension looks like from the outside, and it
is the cheapest canonicity test available — see `compile` step 3.
