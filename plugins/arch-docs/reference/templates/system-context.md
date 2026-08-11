# System context (C4 level 1)

Who uses the system and what it depends on. One diagram, one question.

Arrow labels are mandatory and carry the interaction kind:
`sync:` request/response · `event:` publish/subscribe · `data:` batch or
replication · `dep:` build-time dependency · `deploy:` deployment relation.

```mermaid
flowchart LR
  user["Person: <primary role>"]
  admin["Person: <secondary role>"]
  sys["<System name>"]
  ext1["External: <dependency, e.g. payment gateway>"]
  ext2["External: <dependency, e.g. identity provider>"]

  user -->|"sync: uses via <channel>"| sys
  admin -->|"sync: operates via <channel>"| sys
  sys -->|"sync: <protocol> — <what for>"| ext1
  sys -->|"event: <topic> — <what for>"| ext2
```

<!-- Replace every placeholder with the real name before committing — a
     committed diagram with generic nodes is a defect. Delete nodes that do
     not exist; add the ones that do. -->
