# Social Content Studio — Guia Operacional

**Servidor:** `python studio_server.py` → http://localhost:8766

---

## Início rápido

```bash
python studio_server.py
# Abrir: http://localhost:8766
```

Fluxo:
1. Tab **Clientes** → Novo Cliente → preencher → salvar
2. Tab **Auditoria** → selecionar cliente → preencher → Salvar Auditoria
3. Tab **Novo Job** → selecionar cliente → tipo → briefing → Criar → Executar
4. Tab **Jobs** → ver outputs → download

---

## Módulos

### 1. Clientes (`data/clients/<client-id>/`)

Cadastro local por cliente. Após criar:

```
data/clients/<id>/
├── client.json             — dados completos
├── client_summary.json     — resumo compacto para prompts (~300 chars)
├── brand.json              — identidade visual
├── brand_summary.json      — resumo compacto de marca (~200 chars)
├── audit/                  — auditorias
├── assets/                 — logos, refs visuais
└── jobs/                   — jobs de conteúdo
```

### 2. Auditoria

**Nunca automática. Sempre manual e explícita.**

Preencha via interface → Tab Auditoria → Salvar.

Gera `audit_summary.json` compacto que alimenta os jobs sem recarregar a auditoria completa.

Para atualizar: Tab Auditoria → selecionar cliente → editar → Salvar.

### 3. Jobs de conteúdo

| Tipo | O que entrega |
|------|--------------|
| `carrossel` | copy por slide + legenda + CTA + visual brief |
| `post_estatico` | conceito + copy + legenda + CTA + visual brief |
| `reel_pack` | roteiro + edit manifest + captions SRT + thumbnail + descrição |

Cada job fica em: `data/clients/<id>/jobs/<job-id>/`

### 4. Export

Todos os arquivos ficam disponíveis para download via:
- Interface: Tab Jobs → Ver Detalhes → links de download
- Direto no disco: `data/clients/<id>/jobs/<job-id>/`

---

## Economia de tokens

| Abordagem | Contexto injetado | Tokens estimados |
|-----------|-------------------|-----------------|
| Arquivos completos | ~17.000 chars | ~4.000 tokens |
| Summaries compactos | ~1.100 chars | ~280 tokens |
| Economia | ~94% | ~93% |

Como funciona:
1. Criar/atualizar cliente → gera `client_summary.json` automaticamente
2. Criar/atualizar brand → gera `brand_summary.json` automaticamente
3. Salvar auditoria → gera `audit_summary.json` automaticamente
4. Job runner carrega **apenas os summaries** — nunca os arquivos completos
5. Arquivos completos ficam disponíveis para consulta humana, não para prompts

---

## Antigravity / Gemini

**Papel:** cheap_model — visual brief, thumbnails, brainstorming visual

**Ativar:**
```bash
# Windows CMD
set ANTIGRAVITY_API_KEY=sua_chave

# PowerShell
$env:ANTIGRAVITY_API_KEY="sua_chave"
```

Sem a variável: fallback automático para Claude em todas as etapas. Nenhuma mudança de código necessária.

**O que Antigravity faz:**
- Visual brief (carrossel, post, reel)
- Thumbnail concept

**O que Antigravity NÃO faz:**
- Gerar imagens PNG/JPG
- Analisar imagens (vision)

Para gerar PNGs: use o `visual_brief.md` gerado como prompt em Canva, Midjourney, DALL-E, etc.

---

## Formatos sociais (`config/social_formats.json`)

Configuração editável. Valores padrão:

| Formato | Dimensões | Safe zone | Uso |
|---------|-----------|-----------|-----|
| `feed_square` | 1080×1080 | 80px | carrossel, post |
| `feed_portrait` | 1080×1350 | 80px | post, thumbnail |
| `reel_vertical` | 1080×1920 | top 150px, bottom 350px | reels |

---

## Relação com pipeline existente (run_manager.py)

O Studio opera **independentemente** do pipeline de runs.

Compartilha:
- `adapters/model_provider.py` — mesmo roteamento de modelos
- `config/model_routing.json` — mesmas regras de custo

Não compartilha:
- `dashboard/data/runs/` — runs ficam separadas de jobs do Studio
- `logs/executions/` — logs de jobs ficam em `data/clients/`

Runs continuam funcionando normalmente. Nenhuma compatibilidade quebrada.

---

## API REST (referência)

```
GET  /api/clients                          — lista clientes
POST /api/clients                          — cria cliente
GET  /api/clients/:id                      — get cliente
PUT  /api/clients/:id                      — atualiza cliente
PUT  /api/clients/:id/brand                — atualiza brand
GET  /api/clients/:id/audit                — get auditoria
PUT  /api/clients/:id/audit                — salva auditoria
GET  /api/clients/:id/jobs                 — lista jobs
POST /api/clients/:id/jobs                 — cria job
POST /api/clients/:id/jobs/:jid/run        — executa job
GET  /api/clients/:id/jobs/:jid/files      — lista arquivos
GET  /api/clients/:id/jobs/:jid/file/:fn   — download arquivo
GET  /api/formats                          — config de formatos
```

---

## Fase 2 (fora do escopo atual)

- Geração de PNG diretamente (requer integração com Replicate, Stability AI, etc.)
- Publicação automática no Instagram
- Scraping recorrente de concorrentes
- Editor de vídeo integrado
- Landing page
