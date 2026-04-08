# Mapa da Infraestrutura — agency-gateway

Última atualização: 2026-03-27 (rev. migração)

---

## Estado real por ferramenta

| Ferramenta | Papel | Status | Conexão atual | Próximo passo |
|---|---|---|---|---|
| **Git local** | versionamento | ✅ ativo | repo inicializado | conectar remote (ver docs/github-setup.md) |
| **GitHub** | fonte de verdade | ⚠️ parcial | `.github/` existe, remote ausente | criar repo + push inicial |
| **dashboard v2** | gestão de runs | ✅ ativo | `localhost:8766`, JSON em disco | — operacional |
| **vault/** | memória operacional | ✅ ativo | dentro do repo | — estrutura OK |
| **Claude Code** | executor técnico principal | ✅ ativo | lê/edita/roda no repo | — |
| **VS Code** | ambiente técnico / review | ✅ presumido | mesmo diretório | confirmar workspace apontando pra raiz |
| **Obsidian** | visualização do vault | ⚠️ não confirmado | vault/ está no path correto | abrir vault/ no Obsidian se usar |
| **Antigravity** | Gemini Flash/Pro — tarefas auxiliares | ⚠️ não integrado ao código | disponível como ferramenta externa | usar manualmente para tarefas de baixo custo |
| **ChatGPT** | auxiliar externo | ⚠️ não integrado | externo | não integrar — usar como ferramenta de apoio manual |
| **Cowork** | sessão colaborativa Claude | ✅ resolvido | projeto migrado para fora da sessão | — path definitivo definido |
| **MiroFish** | simulação preditiva | 🚫 bloqueado | fase 2 — não implementar | — |
| **n8n / Make / Supabase / Vercel / Railway** | automação / deploy | ❌ ausente | nenhuma integração no código | — não é prioridade agora |
| **GitHub Actions / CI** | automação de deploy | ❌ ausente | `.github/` sem workflows | — fase 2 |

---

## Path oficial do projeto

```
C:/Users/liant/OneDrive/Desktop/Claude Code/agency-gateway-repo/
```

Path permanente definido em 2026-03-27. Migrado da sessão Cowork temporária.
OneDrive ativo: arquivos sincronizados com a nuvem.
Git inicializado: histórico local preservado a partir do commit 647f40c.

Path antigo (`sessions/zen-inspiring-hopper/mnt/outputs/agency-gateway/`) — obsoleto.
Não usar. Pode ser deletado quando quiser.

---

## Integrações reais confirmadas no código

Nenhuma. O sistema é 100% local:
- HTTP server Python puro (stdlib)
- Persistência em JSON
- Markdown para vault e logs
- Sem banco de dados, sem API externa, sem webhook, sem token

---

## O que depende de credencial externa

| Item | Credencial | Status |
|---|---|---|
| GitHub remote | conta GitHub + auth | ✅ conectado — origin/main ativo |
| Antigravity / Gemini | API key Gemini | não integrado ao código ainda |

Nenhuma credencial sensível está em disco. Zero risco de exposição.
