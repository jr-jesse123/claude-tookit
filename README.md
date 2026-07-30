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

## Plugins

### `code-review`

| Componente | Nome | O que faz |
| --- | --- | --- |
| skill | `/code-review:quick-review` | Revisa as mudanças não commitadas: correção, edge cases, sobras de debug, contratos quebrados, testes faltando. |
| agent | `code-review:security-reviewer` | Subagente que audita injection, authn/authz, segredos, path traversal, desserialização e cripto. Só lê — nunca edita. |

### `model-router`

| Componente | Nome | O que faz |
| --- | --- | --- |
| skill | `/model-router:choose-model` | Recomenda o modelo, o `--effort` e a forma de execução mais baratos que dão conta da tarefa. Pontua 5 dimensões (novidade, horizonte, força do oráculo, blast radius, escala de contexto) e aplica uma regra de decisão explícita. |
| referência | `model-policy.md` | Fonte única da política: papéis dos modelos, escada de effort, roteamento por categoria, overrides de risco, formato do log de calibração. |

A skill lê a política via `${CLAUDE_SKILL_DIR}` — para mudar roteamento, edite só
[`model-policy.md`](plugins/model-router/skills/choose-model/model-policy.md). A skill
contém apenas o procedimento, sem critérios de modelo duplicados.

Só recomenda; nunca executa (`Edit`/`Write` estão em `disallowed-tools`).

### `git-narrator`

| Componente | Nome | O que faz |
| --- | --- | --- |
| skill | `/git-narrator:narrate` | **Fase 1 — planejamento.** Analisa a branch, fatia as mudanças (docs de intenção → domínio+testes → suporte+testes → wiring+E2E), detecta explorações add→remove e pergunta o destino de cada uma (ADR, par reconstruído, ou descartar). Apresenta o plano e só delega após aprovação. |
| agent | `git-narrator:executor` | **Fase 2 — execução.** Roda o protocolo: backup ref, `reset --soft`, staging fatiado, gate de build/testes por commit, e a verificação de que a árvore final é byte-idêntica. Sem `Edit`/`Write`. |
| referência | `execution-protocol.md` | O contrato dos gates, compartilhado pelas duas fases. |

Três decisões de desenho que valem conhecer antes de usar:

- **Reconstrói, não rebaseia.** `reset --soft` até a merge-base e recommit fatiado. Sem conflitos por construção, e o invariante fica verificável: `git diff <backup> HEAD` tem que ser vazio, ou aborta.
- **Todo commit compila.** Testes viajam junto com o código que testam — separar quebraria `git bisect`, que é justamente quem consome esse histórico. Gate configurável: `build` (padrão), `scoped`, `full`.
- **Gate vermelho é erro de fatiamento, não de código.** A árvore é imutável; a única correção é mover arquivo entre fatias. Até 3 rodadas, depois funde os dois commits.

Aborto sempre restaura do backup ref, e o relatório traz o comando de restore mesmo quando dá certo.

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
│   │   └── agents/security-reviewer.md
│   ├── model-router/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/choose-model/
│   │       ├── SKILL.md
│   │       ├── model-policy.md      # arquivo de apoio, lido via ${CLAUDE_SKILL_DIR}
│   │       └── calibration.example.jsonl
│   ├── git-narrator/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/narrate/
│   │   │   ├── SKILL.md             # fase 1: análise e plano
│   │   │   └── execution-protocol.md
│   │   └── agents/executor.md       # fase 2: execução mecânica
│   ├── comment-curator/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/curate/SKILL.md
│   └── devops-tools/
│       ├── .claude-plugin/plugin.json
│       ├── skills/deploy-check/SKILL.md
│       ├── commands/changelog.md
│       ├── hooks/hooks.json
│       ├── scripts/guard-destructive-commands.py
│       └── .mcp.json.example
├── scripts/validate-marketplace.mjs  # validação local e no CI
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
```

Sem dependências, Node 18+. Roda no CI a cada push ([`validate.yml`](.github/workflows/validate.yml)).
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
