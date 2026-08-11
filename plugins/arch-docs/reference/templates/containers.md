# Containers (C4 level 2)

What runs, what stores data, and what talks to what — with protocols and
responsibilities. Same mandatory arrow-label vocabulary as the context
diagram (`sync:` / `event:` / `data:` / `dep:` / `deploy:`).

```mermaid
flowchart TB
  user["Person: <primary role>"]

  subgraph sys["<System name>"]
    web["Container: web app — <responsibility>"]
    api["Container: API service — <responsibility>"]
    db[("Container: PostgreSQL — system of record")]
    broker["Container: message broker — <topics/queues>"]
    worker["Container: worker — <responsibility>"]
  end

  ext["External: <dependency>"]

  user -->|"sync: HTTPS"| web
  web -->|"sync: REST/JSON"| api
  api -->|"sync: SQL"| db
  api -->|"event: publishes <topic>"| broker
  broker -->|"event: delivers <topic>"| worker
  worker -->|"sync: REST — <what for>"| ext
```

<!-- Keep responsibilities to a phrase per container; anything longer belongs
     in overview.md or an ADR. In highly dynamic topologies, prefer pointing
     at tracing/APM for the interaction map and keep only the stable
     boundaries here (see right-sizing: durability ordering). -->
