# docs — Developer documentation (Google / Microsoft style)

The content reads like a page from well-maintained product docs: second
person, present tense, task-oriented, crisp but conversational. Anchored in
the Google developer documentation style guide and the Microsoft Writing
Style Guide.

## Rules

1. **Second person, present tense**: "You configure X" / "The server returns
   Y" — not "we will configure", not "X will be returned".
2. **Task-oriented structure.** Anything the reader *does* becomes a numbered
   procedure: one action per step, imperative verb first, expected result
   stated when it isn't obvious ("Run `make test`. All 42 tests pass.").
3. **Explain why before how** when introducing a concept — one short paragraph
   of purpose, then the procedure.
4. **Headings in sentence case, stating the task or fact**: "Configure the
   cache", "How invalidation works".
5. **Formatting conventions**: identifiers, flags, filenames in `code font`;
   commands in fenced blocks; UI elements in **bold**; descriptive link text
   (never "click here").
6. **Callouts sparingly**: one *Note* or *Warning* per section at most, only
   for things that break or surprise.
7. **One term per concept**, used consistently — no elegant variation between
   "endpoint", "route", and "URL" for the same thing.
8. Friendly is fine, chatty is not: no filler ("simply", "just", "obviously"),
   no exclamation marks.

## Before

> So basically you'll just want to get caching going — we made a config file
> for that (cache.yml) and once it's been edited by you the server should
> obviously be restarted, and then everything will be way faster!

## After

> ## Enable the cache
>
> Caching stores rendered responses so repeated requests skip the render
> step.
>
> 1. Open `cache.yml` and set `enabled: true`.
> 2. Restart the server: `bin/server restart`.
>
> The server now serves repeated requests from the cache. To verify, check
> for `HIT` in the `X-Cache` response header.
