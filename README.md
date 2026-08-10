# claude-tookit

Marketplace de plugins para [Claude Code](https://code.claude.com/docs). Um único
repositório que guarda vários plugins — cada um com qualquer combinação de
skills, agents, commands, hooks e MCP servers.

## Instalar

```
/plugin marketplace add jr-jesse123/claude-tookit
/plugin install code-review@jr-claude-toolkit
/plugin install devops-tools@jr-claude-toolkit
```

Depois de instalado, tudo fica sob o namespace do plugin:
`/code-review:quick-review`, `/devops-tools:deploy-check`, `@devops-tools:...`.
O prefixo é obrigatório e não dá para remover.

Para atualizar quando este repo mudar:

```
/plugin marketplace update jr-claude-toolkit
```

### Auto-instalação neste repo

Este repositório consome os próprios plugins: `.claude/settings.json` registra o
marketplace via `extraKnownMarketplaces` e habilita todos os plugins via
`enabledPlugins`. Ao abrir o repo no Claude Code e confiar na pasta, ele
oferece instalar o marketplace e os plugins automaticamente — sem rodar
`/plugin install` na mão.

Nota: mesmo aqui os plugins rodam da cópia em `~/.claude/plugins/cache`, não
desta pasta (veja [Desenvolver localmente](#desenvolver-localmente) para iterar
sem reinstalar).

## Plugins

### `code-review`

| Componente | Nome | O que faz |
| --- | --- | --- |
| skill | `/code-review:quick-review` | Revisa as mudanças não commitadas: correção, edge cases, sobras de debug, contratos quebrados, testes faltando. |
| skill | `/code-review:pr-tour` | Tour guiado de um PR ou branch antes de revisar: narrativa de como as mudanças se conectam (com diagramas Mermaid quando ajudam, inclusive múltiplos cortes/zooms), grupos independentes separados, e ordem de leitura com o motivo da posição e o foco de cada arquivo. Não aponta bugs — orienta. |
| skill | `/code-review:plan-tour` | O espelho do `pr-tour` no tempo: aterra um plano de implementação no código real *antes* de codar. Explora o terreno que o plano toca, narra como funciona hoje e como o plano o transforma, pinta o delta prospectivo em Mermaid (existente esmaecido, ⊕ para o que vai nascer, ⊖ para o que vai sair — um ou mais diagramas, cada um respondendo uma pergunta diferente, como no `pr-tour`), e reporta discrepâncias factuais plano-vs-código ("o plano assume X; o código mostra Y", sempre com citação) mais as perguntas que o plano deixou em aberto. Não planeja nem implementa — orienta. |
| agent | `code-review:security-reviewer` | Subagente que audita injection, authn/authz, segredos, path traversal, desserialização e cripto. Só lê — nunca edita. |

Os dois tours compartilham as convenções de pintura (o `plan-tour` lê os
`examples/` do `pr-tour` dentro do plugin) e fecham um ciclo: o `plan-tour`
pinta o delta *prometido* e, depois da implementação, o `pr-tour` pinta o
delta *entregue* — dá para comparar os dois no fim. Fluxo típico:
plano → `plan-tour` → (ajusta o plano se houver discrepância) →
implementação → `pr-tour`.

### `model-router`

| Componente | Nome | O que faz |
| --- | --- | --- |
| skill | `/model-router:choose-model` | Roteia **uma tarefa atômica**: recomenda o modelo, o effort e a forma de execução mais baratos que dão conta dela, entre os provedores aceitos (Anthropic e OpenAI). Aplica a rubrica compartilhada (5 dimensões → tier abstrato) e deixa cada policy de provedor nomear o candidato. Quando detecta que a forma honesta é multi-modelo (scouts paralelos, advisor+implementer, agent team, workflow orquestrado), não chuta: emite o sinal e encaminha para a `plan-execution`. Pesquisa online opcional (`--research`) quando policy e log não cobrem o caso. |
| skill | `/model-router:plan-execution` | A pergunta invertida: **decompõe primeiro, roteia depois**. Para tarefa grande ou heterogênea demais para rotear como unidade, corta em 2–7 partes atômicas (cada uma com prompt executável, oráculo próprio e dependências explícitas), aplica a mesma rubrica **por parte**, e monta o shape de execução (scouts, advisor+implementer, agent team, workflow, pipeline em estágios) com caps de fan-out nomeados. Se a tarefa é atômica, devolve para a `choose-model` em uma linha — o gate é que a decomposição precisa se pagar. |
| skill | `/model-router:log-calibration` | Invocada ao fim da tarefa (ou de cada parte de um plano): preenche os outcomes a partir da sessão, confirma com você e faz append no log via script validado — o único caminho de escrita do plugin. |
| referência | `reference/routing-core.md` | O núcleo compartilhado pelas duas skills de roteamento: hard overrides, rubrica de 5 dimensões, regra de decisão → tier, thresholds do log, desempate cross-provider e regra de effort. Não nomeia modelos. |
| referência | `reference/policies/anthropic.md`, `reference/policies/openai.md` | Uma policy por provedor: mapeamento de tiers, escada de effort, preços, categorias, notas de execução. Carregadas por progressive disclosure — só as dos provedores aceitos entram no contexto. |
| referência | `reference/calibration.md` | Schema do log de calibração e regras de threshold — o único comparador cross-provider que o plugin confia. |

Provedores aceitos vêm de `--providers=` no argumento ou de
`.claude/model-router.json` no projeto (default: só `anthropic`). Para mudar
roteamento, edite a policy do provedor — as skills contêm apenas procedimento,
sem critérios de modelo duplicados; a rubrica vive uma vez só em
`routing-core.md`.

Os advisors só recomendam; nunca executam (`Edit`/`Write` em
`disallowed-tools`). O log em `.claude/model-calibration.jsonl` acumula
evidência real por categoria e provedor (partes de um plano logam sob o slug
próprio), e passa por cima da policy quando 3 entradas apontam na mesma
direção.

### `git-narrator`

| Componente | Nome | O que faz |
| --- | --- | --- |
| skill | `/git-narrator:narrate` | **Fase 1 — planejamento.** Analisa a branch, fatia as mudanças (docs de intenção → domínio+testes → suporte+testes → wiring+E2E), detecta explorações add→remove e pergunta o destino de cada uma (ADR, par reconstruído, ou descartar). Apresenta o plano e só delega após aprovação. |
| skill | `/git-narrator:narrate-wip` | **Modo forward.** Num ponto de pausa, transforma a working tree suja em 1–3 commits semânticos em vez de `git add -A && commit -m wip`. Mesmos eixos de fatiamento e trailers `Stage:`, gate de build opcional em worktree descartável. Sem rewrite, sem force-push — seguro em branch com PR em review. Arquivos podem ficar de fora de propósito (lista explícita no plano). |
| agent | `git-narrator:executor` | **Fase 2 — execução.** Roda o protocolo: backup ref, `reset --soft`, staging fatiado, gate de build/testes por commit, e a verificação de que a árvore final é byte-idêntica. Sem `Edit`/`Write`. |
| referência | `execution-protocol.md` | O contrato dos gates, compartilhado pelas duas fases. |
| referência | `reference/narration-core.md` | O bloco comum às duas skills — descoberta de build/testes, eixos de fatiamento, trailers, gate em worktree, semântica de gate vermelho. Cada skill guarda só os próprios deltas. |

Três decisões de desenho que valem conhecer antes de usar:

- **Reconstrói, não rebaseia.** `reset --soft` até a merge-base e recommit fatiado. Sem conflitos por construção, e o invariante fica verificável: `git diff <backup> HEAD` tem que ser vazio, ou aborta.
- **Todo commit compila.** Testes viajam junto com o código que testam — separar quebraria `git bisect`, que é justamente quem consome esse histórico. Gate configurável: `build` (padrão), `scoped`, `full`.
- **Gate vermelho é erro de fatiamento, não de código.** A árvore é imutável; a única correção é mover arquivo entre fatias. Até 3 rodadas, depois funde os dois commits.

Aborto sempre restaura do backup ref, e o relatório traz o comando de restore mesmo quando dá certo.

O `narrate-wip` complementa (não substitui) o `narrate` final: ordem de
descoberta não é ordem de leitura, e explorações só revelam o destino no fim.
Mas commits forward já chegam atômicos e rotulados por `Stage:`, então a
narração pré-merge vira principalmente reordenação — e como só faz `add` +
`commit`, tudo é reversível com um `git reset --soft` (comando incluído no
relatório).

### `comment-curator`

| Componente | Nome | O que faz |
| --- | --- | --- |
| skill | `/comment-curator:curate` | Revisa o ciclo de vida dos comentários — no diff atual (default) ou num arquivo/pasta que você passar. Três vereditos: **stale** (contradiz o código — corrige ou remove, sempre com citação da contradição), **delete** (ruído: narração, código comentado, artefatos de sessão LLM), **keep** (restrições que o código não consegue expressar). Nada é editado antes de você aprovar a tabela de vereditos. |

Regras que valem conhecer: na dúvida, mantém (delete errado perde conhecimento;
keep errado custa uma linha); doc comments de API pública são contrato e nunca
saem por redundância; headers de licença, pragmas e arquivos gerados são
intocáveis; em modo caminho, comentário humano antigo tem prior de manutenção
(`git log -L` distingue origem humana de LLM). Depois de editar, auto-diff
confirma que só linhas de comentário mudaram, e o build do projeto (se
descobrível) confirma que nada funcional saiu junto.

### `sessions`

| Componente | Nome | O que faz |
| --- | --- | --- |
| skill | `/sessions:name` | Destila a sessão atual num nome curto e buscável (kebab-case, 2–5 palavras) que funciona como handle de retomada — `claude --resume <nome>` sem aspas — e entrega o comando `/rename` pronto para colar. |

Decisões de desenho que valem conhecer:

- **Claude não renomeia sozinho.** Não existe ferramenta para isso; `/rename` só
  funciona digitado pelo usuário. A skill nunca finge que renomeou — o
  entregável é o nome + o comando pronto.
- **O nome carrega só o que o picker não mostra.** O picker de `/resume` já
  exibe branch, caminho do projeto e recência — então o nome não repete nada
  disso e gasta as palavras em **intenção + objeto** (o objetivo da sessão, não
  o passo atual).
- **Formas por tipo de sessão** (feature, bug, pesquisa, review, rotina) e
  banimento de palavras vazias (`fix`, `wip`, `stuff`…), com o termo
  distintivo na frente para sobreviver a truncamento e busca por prefixo.

### `output-styler`

| Componente | Nome | O que faz |
| --- | --- | --- |
| skill | `/output-styler:restyle` | Reescreve o último output (ou um texto/arquivo apontado) em um ou mais estilos nomeados, lado a lado, para comparação: `bluf` (resposta primeiro — BLUF/Minto), `plain` (linguagem simples — ISO 24495-1), `docs` (documentação de desenvolvedor — Google/Microsoft), `ste` (técnico controlado — ASD-STE100), `eli5` (só palavras comuns + uma analogia) e `visual` (Mermaid/tabelas). `all` gera todos; `--score` anexa métricas de legibilidade; `--help` mostra o catálogo e não reescreve nada. |
| referência | `styles/*.md` | Um arquivo por estilo (regras + exemplo antes/depois), carregado por progressive disclosure — só os estilos pedidos entram no contexto. |
| referência | `help.md` | Catálogo de decisão do `--help`: quando cada estilo compensa, o que ele custa, e o mesmo texto renderizado nos seis. Lido só quando `--help` aparece. |
| output style | `Visual` (ative em `/config` → *Output style*) | Registro permanente de conversa: o Claude passa a se comunicar visualmente por padrão — Mermaid/tabelas quando o conteúdo é estrutura, fluxo, estado ou comparação; prosa para o que figura não alcança (e para resposta factual simples — diagrama decorativo é proibido). Mesma disciplina dos tours do `code-review`: cada diagrama responde uma pergunta nomeada, nós ancorados em arquivos/símbolos reais. |

Estilo de reescrita e output style são criaturas diferentes: os `styles/*.md`
são regras de *reescrita sob demanda* (comparação, um texto por vez); o
componente em `output-styles/` é system prompt — muda como o Claude *fala*,
persistente por projeto ou usuário. Só ganha porte nativo o estilo com tese
conversacional genuína (hoje: `visual`); os demais continuam disponíveis no
`restyle`, e vencer comparações repetidamente é o critério para o próximo
porte.

Invariantes que valem conhecer: os *fatos* são congelados — restyle muda forma,
nunca conteúdo, e cortes forçados pelo estilo viram uma linha *Omitted:* em vez
de sumirem em silêncio. O alvo fica fixado no texto original entre invocações
(comparar estilos exige a mesma base). Quando você declara um vencedor, a skill
oferece o mecanismo certo: `outputStyle` no `.claude/settings.json` do projeto
se o vencedor tem porte nativo (hoje: `visual`), ou uma linha no `CLAUDE.md`
para os demais — é assim que o experimento vira o estilo padrão daquele
repositório.

### `devops-tools`

| Componente | Nome | O que faz |
| --- | --- | --- |
| skill | `/devops-tools:deploy-check` | Checklist pré-deploy: árvore limpa, sincronizada com a base, testes e linters, migrations, env vars novas, mudanças de infra. |
| command | `/devops-tools:changelog` | Gera a seção de changelog a partir dos commits desde a última tag. |
| hook | `PreToolUse` em `Bash` | Escala para confirmação do usuário comandos destrutivos (`terraform destroy`, `kubectl delete`, `DROP TABLE`, force push, `rm -rf`…). Nunca bloqueia sozinho — só tira do modo auto-aprovar. |

O hook está em [`plugins/devops-tools/scripts/guard-destructive-commands.py`](plugins/devops-tools/scripts/guard-destructive-commands.py).
Edite a lista `RULES` para ajustar ao seu ambiente.

## Estrutura do repositório

```
claude-tookit/
├── .claude-plugin/
│   └── marketplace.json              # catálogo: lista todos os plugins do repo
├── plugins/
│   ├── code-review/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/quick-review/SKILL.md
│   │   ├── skills/pr-tour/
│   │   │   ├── SKILL.md
│   │   │   └── examples/            # few-shot por tipo de diagrama + prosa, via ${CLAUDE_SKILL_DIR}
│   │   ├── skills/plan-tour/
│   │   │   ├── SKILL.md             # delta prospectivo: reusa os examples do pr-tour via ${CLAUDE_PLUGIN_ROOT}
│   │   │   └── examples/prospective.md
│   │   └── agents/security-reviewer.md
│   ├── model-router/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── reference/               # compartilhado pelas skills, via ${CLAUDE_PLUGIN_ROOT}
│   │   │   ├── routing-core.md      # rubrica, tiers, desempate, thresholds — sem modelos
│   │   │   ├── policies/            # uma por provedor, progressive disclosure
│   │   │   │   ├── anthropic.md
│   │   │   │   └── openai.md
│   │   │   ├── calibration.md
│   │   │   └── calibration.example.jsonl
│   │   ├── skills/choose-model/SKILL.md    # roteia tarefa atômica; multi-modelo → encaminha
│   │   ├── skills/plan-execution/SKILL.md  # decompõe primeiro, roteia cada parte depois
│   │   └── skills/log-calibration/
│   │       ├── SKILL.md
│   │       └── log-calibration.py   # único caminho de escrita (append-only)
│   ├── git-narrator/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── reference/narration-core.md  # bloco comum às duas skills
│   │   ├── skills/narrate/
│   │   │   ├── SKILL.md             # fase 1: análise e plano
│   │   │   └── execution-protocol.md
│   │   ├── skills/narrate-wip/SKILL.md  # modo forward: commits semânticos do WIP
│   │   └── agents/executor.md       # fase 2: execução mecânica
│   ├── comment-curator/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/curate/SKILL.md
│   ├── sessions/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/name/SKILL.md
│   ├── output-styler/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── output-styles/visual.md  # registro visual permanente (ative em /config → Output style)
│   │   └── skills/restyle/
│   │       ├── SKILL.md
│   │       ├── help.md              # catálogo do --help (só entra em contexto com --help)
│   │       └── styles/              # um por estilo, lidos via ${CLAUDE_SKILL_DIR}
│   └── devops-tools/
│       ├── .claude-plugin/plugin.json
│       ├── skills/deploy-check/SKILL.md
│       ├── commands/changelog.md
│       ├── hooks/hooks.json
│       ├── scripts/guard-destructive-commands.py
│       └── .mcp.json.example
├── scripts/validate-marketplace.mjs  # validação local e no CI
├── scripts/validate-diagrams.mjs     # valida os diagramas mermaid dos plugins
└── .github/workflows/validate.yml
```

Nenhuma pasta dentro de um plugin é obrigatória. Um plugin pode ter só uma skill,
só um hook, ou os cinco tipos de componente.

## Adicionar um plugin novo

1. Crie `plugins/<nome>/` com os componentes que quiser:

   | Pasta | Conteúdo | Vira |
   | --- | --- | --- |
   | `skills/<nome>/SKILL.md` | markdown com frontmatter | `/<plugin>:<nome>` |
   | `commands/<nome>.md` | markdown "solto" (mesma coisa que skill, sem pasta) | `/<plugin>:<nome>` |
   | `agents/<nome>.md` | frontmatter com `name` + `description` | subagente `<plugin>:<nome>` |
   | `hooks/hooks.json` | matchers de evento | roda automaticamente |
   | `.mcp.json` | servidores MCP | ferramentas MCP |

2. Crie `plugins/<nome>/.claude-plugin/plugin.json`. Só `name` é obrigatório.

3. Adicione a entrada em `.claude-plugin/marketplace.json`:

   ```json
   {
     "name": "meu-plugin",
     "source": "./plugins/meu-plugin",
     "description": "O que ele faz",
     "category": "utilities"
   }
   ```

4. Rode `node scripts/validate-marketplace.mjs` antes de commitar.

## Desenvolver localmente

Plugins são **copiados** para `~/.claude/plugins/cache` na instalação — não rodam
a partir desta pasta. Para iterar sem publicar:

```
/plugin marketplace add ./caminho/para/claude-tookit
/plugin install devops-tools@jr-claude-toolkit
```

Mudanças em `SKILL.md` valem na hora. Mudanças em `hooks/`, `agents/`,
`.mcp.json` e `plugin.json` exigem `/reload-plugins` ou reinstalar o plugin.

Se você tiver a CLI à mão, `claude plugin validate ./plugins/<nome> --strict`
complementa o validador deste repo (ele checa frontmatter contra o schema real).

## Validação

```
node scripts/validate-marketplace.mjs
node scripts/validate-diagrams.mjs
```

Sem dependências, Node 18+. Rodam no CI a cada push ([`validate.yml`](.github/workflows/validate.yml)).
O `validate-diagrams.mjs` valida todo bloco de código `mermaid` sob `plugins/`
(inclusive indentado ou em blockquote) em duas
camadas: sintaxe pelo parser oficial do Mermaid (via
`npx @zabaca/mermaid-validate`, pulado com aviso se `npx` faltar ou com
`--no-npx`) e checagens estruturais que o parser não faz — índice de
`linkStyle` dentro do número de arestas e `class`/`:::` apontando para
`classDef` declarado.
Verifica:

- `marketplace.json` — JSON válido, `name` kebab-case e não reservado, `owner.name`, nomes de plugin únicos;
- toda `source` relativa aponta para um diretório que existe, sem `../`;
- cada `plugin.json` — `name` kebab-case, tipos corretos, caminhos de componente dentro do plugin;
- cada skill tem `SKILL.md` com `description`; cada agent tem `name` + `description` e não usa campos proibidos (`hooks`, `mcpServers`, `permissionMode`);
- `hooks.json` — scripts referenciados existem, são executáveis e usam `${CLAUDE_PLUGIN_ROOT}`;
- diretórios em `plugins/` que ficaram de fora do catálogo.

## Pegadinhas

- **Sem `../`.** Um plugin não pode referenciar arquivos fora da própria pasta.
  Para código compartilhado, duplique ou use symlink.
- **`${CLAUDE_PLUGIN_ROOT}` em todo caminho** dentro de hooks e `.mcp.json`.
  Caminho relativo à raiz do projeto quebra, porque o plugin roda do cache.
- **Nome de marketplace é único por usuário.** Adicionar outro marketplace com
  `name: "jr-claude-toolkit"` sobrescreve este.
- **`version` está omitido de propósito** nos `plugin.json` daqui. Sem ele, o
  Claude Code usa o SHA do commit — todo commit vira uma versão nova e o
  auto-update funciona sozinho. Se um dia quiser releases fixos, adicione
  `"version": "1.0.0"` e faça o bump manualmente a cada mudança.
- **Nomes reservados.** `anthropic-*`, `claude-*-plugins`, `agent-skills` e
  parecidos são bloqueados para marketplaces de terceiros — o validador checa.

## Docs

- [Plugins](https://code.claude.com/docs/en/plugins.md)
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces.md)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference.md)
- [Skills](https://code.claude.com/docs/en/skills.md)
- [Hooks](https://code.claude.com/docs/en/hooks.md)

## Licença

MIT
