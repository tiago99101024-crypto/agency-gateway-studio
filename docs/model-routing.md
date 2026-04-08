# Model Routing — Guia operacional

**Arquivo de config:** `config/model_routing.json`

---

## Como funciona

O roteador decide qual modelo usar por etapa do pipeline.
Há 3 classes de custo:

| Classe | Modelo padrão | Custo | Quando |
|--------|--------------|-------|--------|
| `local_only` | — (Python puro) | zero | advance, status, next, handoffs |
| `cheap_model` | Antigravity/Gemini | mínimo | arte, rascunhos, variações |
| `smart_model` | Claude | médio | analise, copy, revisao |

---

## Configurar

Edite `config/model_routing.json`:

```json
{
  "routing_rules": {
    "analise": "smart_model",
    "copy":    "smart_model",
    "arte":    "cheap_model",
    "revisao": "smart_model"
  },
  "models": {
    "smart_model": "claude",
    "cheap_model": "antigravity"
  },
  "fallback": {
    "cheap_model": "claude"
  }
}
```

Para usar Claude em tudo (enquanto Antigravity não estiver configurado):
```json
"models": {
  "smart_model": "claude",
  "cheap_model": "claude"
}
```

---

## Ativar Antigravity

1. Obtenha sua API key em `app.antigravity.app`
2. Defina a variável de ambiente:
   ```
   # Windows CMD
   set ANTIGRAVITY_API_KEY=sua_chave

   # PowerShell
   $env:ANTIGRAVITY_API_KEY="sua_chave"

   # bash/zsh
   export ANTIGRAVITY_API_KEY="sua_chave"
   ```
3. (Opcional) Ajuste `base_url` e `model` em `config/model_routing.json` → `providers.antigravity`
4. Teste:
   ```bash
   python runs/run_manager.py next <run-id>
   ```
   O roteador vai indicar `cheap_model → antigravity` para a etapa `arte`.

**Fallback automático:** se `ANTIGRAVITY_API_KEY` não estiver definida, o roteador cai para Claude sem nenhuma ação necessária.

---

## Handoffs (redução de tokens)

Após cada etapa aprovada, o sistema gera automaticamente um handoff compacto:

```
outputs/active/<run-id>/handoffs/
  briefing.json  (após briefing aprovado)
  analise.json   (após analise aprovada)
  copy.json      (após copy aprovada)
  arte.json      (após arte aprovada)
```

**Formato:**
```json
{
  "run_id": "run-20260401-001",
  "etapa_origem": "analise",
  "objetivo": "...",
  "formato": "carrossel",
  "canal": "instagram",
  "publico": "...",
  "consciencia": "...",
  "temperatura": "...",
  "mecanismo": "...",
  "restricoes": [],
  "output_path": "outputs/active/.../analise-nicho.md",
  "resumo_curto": "..."
}
```

**Economia estimada por execução:**
- Sem handoff: ~17.000 chars (análise completa) no prompt de copy
- Com handoff: ~400 chars
- Redução: ~97% do contexto da análise no prompt de copy

---

## Pipeline com etapa arte

```
briefing → analise → copy → arte → revisao → publicacao → metricas
```

| Etapa | Executor | Modelo | Auto via exec? |
|-------|----------|--------|---------------|
| briefing | humano | — | não |
| analise | toguro | smart_model | sim |
| copy | toto | smart_model | sim |
| arte | neymar | cheap_model | sim |
| revisao | capitão | smart_model | não (usa prompt) |
| publicacao | humano | — | não |
| metricas | tesla | — | não |

---

## Compatibilidade com runs antigas

Runs criadas antes da etapa `arte` (sem `arte` em `pipeline.etapas`) continuam funcionando.

Ao avançar `copy → aprovado` em uma run legada, o sistema pula `arte` automaticamente e vai direto para `revisao`.

Nenhuma migração necessária.

---

## Adapters disponíveis

| Adapter | Arquivo | Status |
|---------|---------|--------|
| Claude | `adapters/claude_adapter.py` | Funcional |
| Antigravity | `adapters/antigravity_adapter.py` | Pronto (requer ANTIGRAVITY_API_KEY) |
