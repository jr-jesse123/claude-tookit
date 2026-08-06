# eli5 — Simple words, one good analogy

Explain it with only the words everyone knows — the spirit of xkcd's *Thing
Explainer* (ten hundred most common words) and Simple English Wikipedia. The
reader is smart but has zero background. The trap to avoid: dumbing down the
*facts*. Simplify the words, keep the truth.

## Rules

1. **Common words only.** If a ten-year-old wouldn't know the word, replace
   it or explain it in the same breath: "a cache (a place where the computer
   keeps answers it already worked out)". Name unavoidable technical terms
   once, so the reader can recognize them later — then use the plain version.
2. **One sustained analogy** for the central mechanism, chosen for structural
   match, and kept for the whole text. Never mix metaphors — a cache that is
   a "notebook" in paragraph one cannot become a "warehouse" in paragraph
   three.
3. **Short sentences.** Aim under 15 words. One idea each.
4. **Make numbers tangible**: "about as long as a blink", "one in every
   thousand", not "~300ms" or "0.1%".
5. **Cause before effect**, in order: "Because A happens, B happens. That is
   why C."
6. **Say what the simple version leaves out.** Analogies leak; end with one
   line — *This leaves out: …* — naming the real complications that didn't
   fit.
7. No condescension: no "it's really simple!", no exclamation-mark
   enthusiasm. Respect the reader; simplify the language, not the tone.

## Before

> The cache employs an LRU eviction policy: upon reaching capacity, the
> least-recently-accessed entries are evicted to accommodate new insertions,
> which keeps the hot working set resident.

## After

> The cache is like a small desk where the computer keeps the papers it uses
> most. The desk has limited space. When it is full and a new paper arrives,
> the computer removes the paper it has not touched for the longest time.
> This way, the papers it uses all the time stay within reach.
>
> *This leaves out: how the computer tracks which paper was used last, and
> that some caches use different removal rules.*
