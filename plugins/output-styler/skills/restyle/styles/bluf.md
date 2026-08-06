# bluf — Bottom Line Up Front / Minto Pyramid

The reader is an executive with 30 seconds. The answer comes first; everything
after it exists to let them stop reading as early as possible without being
wrong. Anchored in the US Army's BLUF doctrine and Barbara Minto's Pyramid
Principle (answer → grouped arguments → data).

## Rules

1. **Open with the bottom line**: 1–3 sentences stating the conclusion,
   recommendation, or key fact. Not the topic, not the context — the answer.
   A reader who stops here must still act correctly.
2. **Then the supporting arguments, grouped.** 2–4 groups, each headed by a
   *claim* ("Migration is safe to run in place"), never a topic label
   ("Migration"). Groups don't overlap; together they cover the bottom line.
3. **Data and detail last** — or referenced ("numbers in the table below")
   instead of inlined. Raw evidence never interrupts the argument.
4. **Every paragraph passes the "so what" test.** If removing it doesn't
   weaken the bottom line, remove it.
5. **Risks and caveats are part of the bottom line, not the fine print.** If
   there is a dealbreaker condition, it appears in the first block.
6. Prefer prose headlines over decoration: bold claim lines beat generic
   headers.

## Before

> We analyzed the three caching options. Redis offers persistence and rich
> data types, and our team has used it before. Memcached is simpler and
> slightly faster for pure key-value loads. DynamoDB DAX would integrate with
> our existing tables but locks us into AWS. After weighing operational cost,
> team familiarity, and the fact that we need pub/sub for invalidation
> anyway, Redis seems like the best fit.

## After

> **Use Redis.** It is the only option that covers cache *and* the pub/sub
> invalidation we already need, and the team has operated it before.
>
> **Why not the alternatives:** Memcached wins ~5% on raw key-value speed but
> would force a second system for pub/sub. DAX integrates with our tables but
> couples us to AWS with no invalidation story.
>
> *Omitted: per-option latency figures — available on request.*
