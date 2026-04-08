"""bruxo_orchestrator.py — Bruxo como orquestrador real de execução.

Responsabilidade:
  Dado um job + contexto do cliente, decide:
    - quais agentes entram
    - quais skills são chamadas
    - qual profundidade de execução
    - quais contextos de nicho injetar
    - se é necessário pré-análise extra

Princípio: regras locais primeiro (zero custo). LLM só se regras não cobrem.

Retorna um ExecutionPlan que o job_runner usa para montar os prompts.
"""

import json
import os
import re
import sys
from datetime import datetime


SKILL_CATALOG = "config/skill_catalog.json"
DATA_DIR = "data/clients"


# ─── Execution Plan ───────────────────────────────────────────────────────────

class ExecutionPlan:
    """Plano de execução montado pelo Bruxo. Imutável após criação."""

    def __init__(self, job: dict, client_id: str):
        self.job_id = job.get("id")
        self.client_id = client_id
        self.tipo = job.get("tipo")
        self.briefing = job.get("briefing", "")

        # Agentes que participam (em ordem)
        self.agentes: list[str] = []

        # Skills a injetar por agente: {"copy": ["copy-producao", ...], ...}
        self.skills_por_agente: dict = {}

        # Contextos extras a injetar (texto curto, já carregado)
        self.contextos_extras: list[str] = []

        # Profundidade: "basica" | "completa" | "aprofundada"
        self.profundidade: str = "completa"

        # Flags de diagnóstico
        self.flags: list[str] = []

        # Metadados para auditoria
        self.decisoes: list[str] = []
        self.gerado_em: str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    def add_agente(self, agente: str, skill: str = None):
        if agente not in self.agentes:
            self.agentes.append(agente)
        if skill:
            self.skills_por_agente.setdefault(agente, [])
            if skill not in self.skills_por_agente[agente]:
                self.skills_por_agente[agente].append(skill)

    def add_contexto(self, texto: str, fonte: str = ""):
        if texto and texto not in self.contextos_extras:
            self.contextos_extras.append(texto)
            if fonte:
                self.decisoes.append(f"Contexto injetado: {fonte}")

    def add_flag(self, flag: str, decisao: str = ""):
        self.flags.append(flag)
        if decisao:
            self.decisoes.append(decisao)

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "client_id": self.client_id,
            "tipo": self.tipo,
            "agentes": self.agentes,
            "skills_por_agente": self.skills_por_agente,
            "profundidade": self.profundidade,
            "flags": self.flags,
            "decisoes": self.decisoes,
            "gerado_em": self.gerado_em,
        }


# ─── Bruxo principal ──────────────────────────────────────────────────────────

def build_plan(client_id: str, job: dict) -> ExecutionPlan:
    """Ponto de entrada principal. Retorna ExecutionPlan.

    Ordem de decisão:
      1. Regras locais determinísticas (zero custo)
      2. Enriquecimento de contexto (leitura de arquivo — zero custo)
      3. Análise de histórico local (zero custo)
      [4. LLM opcional — só se regras não cobrem caso edge]
    """
    plan = ExecutionPlan(job, client_id)
    catalog = _load_catalog()

    _rule_agentes_por_tipo(plan)
    _rule_skills_por_tipo(plan, catalog)
    _rule_contexto_nicho(plan, client_id, catalog)
    _rule_audit_completeness(plan, client_id)
    _rule_profundidade(plan, client_id, job)
    _rule_historico_learning(plan, client_id)

    return plan


# ─── Regras locais ────────────────────────────────────────────────────────────

def _rule_agentes_por_tipo(plan: ExecutionPlan):
    """Regra 1: quais agentes entram por tipo de job."""
    tipo = plan.tipo

    if tipo == "carrossel":
        plan.add_agente("toguro")     # ângulos estratégicos
        plan.add_agente("toto")       # copy dos slides
        plan.add_agente("neymar")     # visual brief (Antigravity)
        plan.add_agente("capitao")    # revisão de coerência
        plan.decisoes.append("carrossel: toguro→toto→neymar→capitao (fluxo completo)")

    elif tipo == "post_estatico":
        plan.add_agente("toguro")
        plan.add_agente("toto")
        plan.add_agente("neymar")
        # Capitão não entra em post simples — sem multi-slide para revisar
        plan.decisoes.append("post_estatico: toguro→toto→neymar (capitao dispensado — post simples)")

    elif tipo == "reel_pack":
        plan.add_agente("toguro")
        plan.add_agente("toto")       # roteiro + copy
        plan.add_agente("neymar")     # thumbnail + edit manifest
        plan.add_agente("capitao")    # hook + CTA críticos para retenção
        plan.decisoes.append("reel_pack: toguro→toto→neymar→capitao (hook e CTA críticos)")


def _rule_skills_por_tipo(plan: ExecutionPlan, catalog: dict):
    """Regra 2: skills ativadas por tipo de job."""
    tipo = plan.tipo
    skills = catalog.get("skills", {})

    # copy-producao sempre ativa para qualquer tipo
    _inject_skill(plan, "toto", "copy-producao", skills)

    if tipo == "carrossel":
        _inject_skill(plan, "toto", "carrossel-instagram", skills)

    if tipo == "reel_pack":
        _inject_skill(plan, "neymar", "reel-pack", skills)


def _rule_contexto_nicho(plan: ExecutionPlan, client_id: str, catalog: dict):
    """Regra 3: injeta contexto de nicho quando keywords batem."""
    from studio.studio_manager import get_client_summary

    cs = get_client_summary(client_id)
    nicho = (cs.get("nicho", "") + " " + cs.get("produto", "")).lower()
    skills = catalog.get("skills", {})

    for skill_name, skill_def in skills.items():
        triggers = skill_def.get("triggers", {})
        keywords = triggers.get("nicho_keywords", [])
        if any(kw in nicho for kw in keywords):
            path = skill_def.get("path", "")
            if os.path.exists(path):
                content = _read_file_compact(path, max_chars=1200)
                if content:
                    plan.add_contexto(f"CONTEXTO DE NICHO ({skill_name}):\n{content}", skill_name)
                    plan.decisoes.append(f"Nicho '{nicho[:30]}' ativou skill '{skill_name}'")


def _rule_audit_completeness(plan: ExecutionPlan, client_id: str):
    """Regra 4: verifica completude da auditoria e adiciona flags."""
    from studio.studio_manager import get_audit_summary, get_audit

    summary = get_audit_summary(client_id)
    full_audit = get_audit(client_id)

    if not summary or not summary.get("diagnostico"):
        plan.add_flag(
            "audit_ausente",
            "Auditoria ausente — ângulos serão mais genéricos. Recomendado: gerar pré-auditoria primeiro."
        )
        plan.profundidade = "basica"
    elif len(summary.get("diagnostico", "")) < 50:
        plan.add_flag(
            "audit_rasa",
            "Auditoria superficial — Toguro vai inferir mais do nicho do que do perfil real."
        )

    # Verifica campos-chave
    campos_criticos = ["linha_editorial_sugerida", "oportunidades_top", "linha_visual"]
    ausentes = [c for c in campos_criticos if not summary.get(c)]
    if ausentes:
        plan.add_flag(
            f"audit_incompleta:{','.join(ausentes)}",
            f"Campos ausentes na auditoria: {ausentes}. Contexto de nicho será usado como fallback."
        )


def _rule_profundidade(plan: ExecutionPlan, client_id: str, job: dict):
    """Regra 5: decide profundidade baseada em histórico do cliente."""
    n_jobs = _count_past_jobs(client_id)

    if n_jobs == 0:
        plan.profundidade = "aprofundada"
        plan.decisoes.append("Primeiro job do cliente — profundidade aprofundada (mais contexto)")
    elif n_jobs < 3:
        plan.profundidade = "completa"
    else:
        # Cliente com histórico — pode usar summaries mais enxutos
        plan.profundidade = "completa"
        plan.decisoes.append(f"Cliente com {n_jobs} jobs anteriores — profundidade completa padrão")


def _rule_historico_learning(plan: ExecutionPlan, client_id: str):
    """Regra 6: carrega aprendizado de resultados anteriores para influenciar ângulos."""
    past = load_past_results(client_id)
    if not past:
        return

    top = rank_past_angles(past)
    if top:
        summary_lines = []
        for item in top[:3]:
            summary_lines.append(
                f"- '{item['angulo_nome']}' ({item['tipo']}) → "
                f"conversoes:{item.get('conversoes',0)} cliques:{item.get('cliques',0)} "
                f"salv:{item.get('salvamentos',0)} comp:{item.get('compartilhamentos',0)}"
            )
        ctx = "APRENDIZADO — angulos com melhor resultado real (conversoes > cliques > salvamentos):\n" + "\n".join(summary_lines)
        plan.add_contexto(ctx, "historico_resultados")
        plan.decisoes.append(f"Injetado aprendizado de {len(past)} resultados anteriores")


# ─── Aprendizado — leitura de resultados ──────────────────────────────────────

def load_past_results(client_id: str) -> list:
    """Carrega todos os resultado.json do cliente. Zero custo — só leitura local."""
    results = []
    jobs_dir = os.path.join(DATA_DIR, client_id, "jobs")
    if not os.path.exists(jobs_dir):
        return results

    for job_id in os.listdir(jobs_dir):
        res_path = os.path.join(jobs_dir, job_id, "resultado.json")
        if os.path.exists(res_path):
            try:
                with open(res_path, encoding="utf-8") as f:
                    data = json.load(f)
                results.append(data)
            except Exception:
                pass

    return results


def rank_past_angles(results: list) -> list:
    """Ranqueia ângulos por performance real — conversões primeiro, vaidade por último.

    Hierarquia de peso:
      conversoes        × 50  (ação de compra/pedido/mensagem — resultado real)
      cliques           × 10  (intenção expressa)
      compartilhamentos × 5   (distribuição orgânica — valor real)
      salvamentos       × 4   (intenção futura — valor real)
      comentarios       × 2   (engajamento qualificado)
      curtidas          × 0   (vaidade — não entra no score)
    """
    scored = []
    for r in results:
        res = r.get("resultado", {})
        angulo = r.get("angulo", {})
        # Aceita resultados sem ângulo definido — usa tipo + briefing como fallback
        angulo_nome = (
            angulo.get("nome")
            or r.get("tipo", "")
            or "sem-angulo"
        )

        score = (
            int(res.get("conversoes", 0)) * 50 +
            int(res.get("cliques", 0)) * 10 +
            int(res.get("compartilhamentos", 0)) * 5 +
            int(res.get("salvamentos", 0)) * 4 +
            int(res.get("comentarios", 0)) * 2
            # curtidas intencionalmente excluídas
        )
        scored.append({
            "angulo_nome": angulo_nome,
            "angulo": angulo,
            "tipo": r.get("tipo", ""),
            "score": score,
            "conversoes": res.get("conversoes", 0),
            "cliques": res.get("cliques", 0),
            "compartilhamentos": res.get("compartilhamentos", 0),
            "salvamentos": res.get("salvamentos", 0),
            "comentarios": res.get("comentarios", 0),
        })

    return sorted(scored, key=lambda x: x["score"], reverse=True)


def get_learning_summary(client_id: str) -> dict:
    """Retorna resumo de aprendizado por nicho/tipo. Para uso em relatórios e UI."""
    past = load_past_results(client_id)
    if not past:
        return {"total_resultados": 0, "top_angulos": [], "por_tipo": {}}

    top = rank_past_angles(past)

    por_tipo: dict = {}
    for r in past:
        tipo = r.get("tipo", "")
        res = r.get("resultado", {})
        por_tipo.setdefault(tipo, {"total": 0, "conversoes": 0, "engajamento": 0})
        por_tipo[tipo]["total"] += 1
        por_tipo[tipo]["conversoes"] += int(res.get("conversoes", 0))
        por_tipo[tipo]["engajamento"] += int(res.get("engajamento", 0))

    return {
        "total_resultados": len(past),
        "top_angulos": top[:5],
        "por_tipo": por_tipo,
    }


# ─── Skill injection helper ───────────────────────────────────────────────────

def _inject_skill(plan: ExecutionPlan, agente: str, skill_name: str, catalog: dict):
    """Lê skill do catálogo e injeta no plano."""
    skill_def = catalog.get(skill_name, {})
    path = skill_def.get("path", "")
    if not path or not os.path.exists(path):
        return
    plan.add_agente(agente, skill_name)


def get_skill_content(skill_name: str, max_chars: int = 600) -> str:
    """Retorna conteúdo compacto de uma skill para injeção em prompt."""
    catalog = _load_catalog()
    skill_def = catalog.get("skills", {}).get(skill_name, {})
    path = skill_def.get("path", "")
    if not path or not os.path.exists(path):
        return ""
    return _read_file_compact(path, max_chars)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _load_catalog() -> dict:
    if os.path.exists(SKILL_CATALOG):
        with open(SKILL_CATALOG, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _read_file_compact(path: str, max_chars: int = 800) -> str:
    """Lê arquivo e retorna versão compacta — remove linhas de comentário MD pesadas."""
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        # Remove blocos de código longos e linhas de separação
        content = re.sub(r'```[\s\S]{0,2000}?```', '', content)
        content = re.sub(r'\n#{1,6} .{0,100}', '', content)  # Remove headers
        content = re.sub(r'\n---+\n', '\n', content)
        content = re.sub(r'\n{3,}', '\n\n', content).strip()
        return content[:max_chars]
    except Exception:
        return ""


def _count_past_jobs(client_id: str) -> int:
    jobs_dir = os.path.join(DATA_DIR, client_id, "jobs")
    if not os.path.exists(jobs_dir):
        return 0
    return len([d for d in os.listdir(jobs_dir)
                if os.path.isdir(os.path.join(jobs_dir, d))])
