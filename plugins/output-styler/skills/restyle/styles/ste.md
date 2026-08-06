# ste — Controlled technical writing (ASD-STE100)

The style of aviation maintenance manuals: writing so constrained that a
tired, non-native reader executing a dangerous procedure cannot misread it.
Anchored in ASD-STE100 (issue 9, 2025: 53 writing rules + a dictionary of
~900 approved words, one meaning each). The full dictionary is
English-specific; what transfers to any language is the rule set below plus
the discipline of *one term, one meaning, everywhere*.

## Rules

1. **Sentence limits**: ≤ 20 words in procedures, ≤ 25 in descriptions. One
   topic per sentence. One instruction per sentence.
2. **Active voice, always.** Instructions in the imperative: "Remove the
   cover", never "the cover should be removed".
3. **One word = one meaning.** Pick one term per concept at the start and
   never vary it. Do not use one word in two senses ("close the file" vs
   "close to the limit" — pick another word for one of them).
4. **Simple verb forms only**: imperative, present, past. No gerund chains,
   no perfect tenses, no modal stacking ("might have been being processed").
5. **Conditions before instructions**: "If the pressure is more than 3 bar,
   open the valve" — the reader must know the condition before they act.
6. **Warnings come first**, on their own line, before the step they protect.
7. **Sequences become numbered steps**; do not bury order in prose ("after
   doing X, but before Y, ...").
8. **Keep the articles** ("Close the valve", not telegraphic "Close valve").
9. **Noun clusters ≤ 3 words**: break "database connection pool timeout
   configuration" apart with prepositions.
10. **No idioms, no metaphors, no humor.** Literal language only.

## Before

> Having verified connectivity, migration can be initiated, though it should
> be kept in mind that interrupting it while the schema's being altered might
> potentially leave the database in a state which could prove problematic.

## After

> WARNING: Do not stop the migration while it changes the schema. A stopped
> migration can cause damage to the database.
>
> 1. Make sure that the database connection is active.
> 2. Start the migration.
