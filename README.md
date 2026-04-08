# agency-gateway

Motor operacional para gestão de tráfego e conteúdo digital. Fase 1 ativa.

---

## O que é isso

Sistema de agents com mandatos definidos, memória qualificada e protocolos de execução.
Não é automação — é estrutura para trabalhar com IA de forma consistente, rastreável e
sem perder contexto entre sessões.

---

## Agents ativos (fase 1)

| Agent | Slug | Função |
|---|---|---|
| Bruxo | bruxo | Orquestrador, CEO, árbitro de coerência |
| Toguro | toguro | Inteligência de mercado, análise de nicho |
| Capitão Nascimento | capitao-nascimento | Reviewer, portão de qualidade |
| Carinha dos Anúncios | carinha-dos-anuncios | Mídia paga, performance, aquisição |
| Totó | toto | Copy, persuasão, script, CTA |
| Neymar | neymar | Criativo, visual, direção de gravação |
| Tesla | tesla | Memória qualificada, arquitetura, persistência |

Contratos completos em `.claude/agents/<slug>.md`.

---

## Como iniciar uma tarefa

1. Criar issue com briefing (template em `.github/ISSUE_TEMPLATE/`)
2. Bruxo lê o briefing, valida e define nível de handshake (completo ou parcial)
3. Agents executam em sequência conforme handshake
4. Capitão Nascimento revisa com checklist de profundidade
5. Tesla classifica e persiste aprendizado

Se o briefing estiver incompleto, o agent pede o que falta antes de executar.
Regras completas em `CLAUDE.md`.

---

## Onde ficam as coisas

```
.claude/agents/       → contratos dos 7 agents
vault/                → memória qualificada
  00-Inbox/           → entrada rápida, triagem pendente
  01-Projects/        → contexto por projeto ativo
  02-Agents/          → aprendizado específico por agent
  03-Playbooks/       → padrões reutilizáveis validados (2+ confirmações)
  04-Decisions/       → decisões estratégicas com data e justificativa
  05-Daily/           → notas operacionais datadas
  99-Archive/         → encerrado, preservado para consulta
  _templates/         → templates operacionais reutilizáveis
logs/
  executions/         → logs de execução (YYYY-MM-DD_<id>_<slug>.md)
  reviews/            → logs de revisão do Capitão
  hypotheses/         → hipóteses aguardando validação
outputs/
  active/             → peças ativas (script, direção visual, criativo)
  archive/            → peças encerradas
context/              → contexto de nicho por categoria (insumo para Toguro)
.github/
  ISSUE_TEMPLATE/     → templates de issue por tipo de tarefa
  labels.yml          → labels padrão do projeto
```

---

## Fluxos principais

### Conteúdo orgânico
Toguro → Carinha → Totó → Neymar → Capitão → Tesla

### Campanha paga
Toguro → Carinha → Totó → Neymar → Capitão → Tesla

### Diagnóstico de campanha
Toguro → Carinha → Capitão → Tesla

### Registro de aprendizado
Tesla classifica → ruído (descarta) / hipótese (logs/) / playbook (vault/03-Playbooks/) / decisão (vault/04-Decisions/)

---

## Regras essenciais

- **Número sempre com condição.** Taxa de plataforma, benchmark, projeção: declarar faixa + contexto ou substituir por mecanismo de cálculo pessoal.
- **Canal sempre declarado.** Antes de sugerir CTA, declarar contexto A–F.
- **Copy sempre com declaração.** 5 dimensões (consciência, temperatura, mecanismo, fricção, evento final) antes de escrever.
- **Hipótese nunca vira playbook direto.** Precisa de 2+ confirmações comparáveis.
- **Capitão não aprova sem parecer estruturado.**

---

## Fase 1 vs fase 2

**Fase 1 (atual):** agents definidos, motor operacional local, testes reais com @estrategiaparadelivery. Sem integrações externas. Sem GitHub CI/CD. Sem Antigravity. Sem MiroFish.

**Fase 2 (não iniciada):** MiroFish, Antigravity, automações, integrações externas, GitHub Actions.

---

## Caso de teste da fase 1

Perfil: @estrategiaparadelivery
Primeiro reel produzido: "Cálculo de Comissão" — script + direção visual aprovados.
Hipótese: ângulo de cálculo pessoal vs número fixo de plataforma.
Status: aguardando publicação e coleta de métricas.
Projeto: `vault/01-Projects/estrategiaparadelivery.md`
