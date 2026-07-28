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
