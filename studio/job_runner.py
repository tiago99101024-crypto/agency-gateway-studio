"""job_runner.py â€” Executa jobs do Social Content Studio.

Fluxo de execuÃ§Ã£o:
  1. Bruxo monta ExecutionPlan (local, zero custo)
  2. generate_angles()  â€” Toguro gera 3 Ã¢ngulos + decisao automatica de conversao
  3. run_job(angle_idx) â€” TotÃ³, Neymar, CapitÃ£o executam conforme o plano
  4. Antigravity gera visual brief + prompts de imagem (MJ/DALL-E/SD)

Token economy por design:
  - Bruxo: zero tokens (regras locais)
  - Ã‚ngulos: ~800 chars de contexto compacto + aprendizado injetado
  - Copy: ~1.500 chars (summaries + Ã¢ngulo + skills compactas)
  - Visual: ~600 chars (copy resumida + contexto de marca)
"""

import json
import os
import re
import sys
import traceback
import unicodedata
import uuid
from difflib import SequenceMatcher
from datetime import datetime, timedelta
from studio.operational_engine import (
    TREND_HISTORY_MAX_ITEMS,
    _sanitize_trend_history,
    _allocate_creative_budget,
    _apply_missing_creative_id_guard,
    _build_trend_history,
    _compute_exploration_envelope,
    _decide_creative_action,
    _portfolio_rank_key,
    _should_refresh_allocation,
)


def _ts():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _invoke(etapa: str, prompt: str) -> dict:
    sys.path.insert(0, os.path.abspath("."))
    from adapters.model_provider import invoke_for_etapa
    return invoke_for_etapa(etapa, prompt)


def _normalize_context_fragment(value):
    if isinstance(value, (list, tuple, set)):
        normalized = [_normalize_context_fragment(item) for item in value if item is not None]
        normalized = [item for item in normalized if item]
        return " | ".join(normalized)
    if isinstance(value, dict):
        return " | ".join(f"{k}:{_normalize_context_fragment(v)}" for k, v in value.items())
    if value is None:
        return ""
    return str(value)


def _normalize_sequence(values):
    return [item for item in (_normalize_context_fragment(v) for v in (values or [])) if item]


def _safe_join(items, sep=" | "):
    normalized = []
    for item in (items or []):
        fragment = _normalize_context_fragment(item)
        if fragment:
            normalized.append(fragment)
    return sep.join(normalized)


def _build_context(client_id: str, job: dict, plan=None) -> str:
    """Contexto compacto: summaries + contextos extras do plano. Nunca arquivos completos."""
    from studio.studio_manager import get_client_summary, get_brand_summary, get_audit_summary

    cs = get_client_summary(client_id)
    bs = get_brand_summary(client_id)
    aud = get_audit_summary(client_id)

    parts = [
        f"CLIENTE: {cs.get('nome','')} | nicho: {cs.get('nicho','')} | produto: {cs.get('produto','')}",
        f"objetivo: {cs.get('objetivo','')} | tom: {cs.get('tom_voz','')} | praca: {cs.get('cidade','')}",
    ]
    if bs.get("cores"):
        parts.append(f"MARCA: cores={','.join(bs.get('cores',[]))} | {bs.get('tom_keywords','')[:80]}")
    if aud.get("diagnostico"):
        parts.append(f"AUDIT: {aud.get('diagnostico','')[:180]}")
    if aud.get("linha_editorial"):
        parts.append(f"editorial: {aud.get('linha_editorial','')[:100]}")
    if aud.get("oportunidades_top"):
        parts.append(f"oportunidades: {' | '.join(aud.get('oportunidades_top',[]))}")
    parts.append(f"JOB: {job.get('briefing','')} | tipo: {job.get('tipo','')} | objetivo_job: {job.get('objetivo_job','')}")
    mesa_guerra = job.get("mesa_guerra", {})
    if mesa_guerra:
        parts.append(
            "MESA_GUERRA: "
            f"angulo_base={mesa_guerra.get('angulo_final','')} | "
            f"tese={mesa_guerra.get('tese','')} | "
            f"direcao_copy={mesa_guerra.get('direcao_copy','')} | "
            f"direcao_visual={mesa_guerra.get('direcao_visual','')}"
        )

    # Injeta contextos extras do Bruxo (nicho, aprendizado)
    if plan and plan.contextos_extras:
        for ctx in _normalize_sequence(plan.contextos_extras):
            parts.append(ctx)

    return "\n".join(parts)


def _format_angle(angle: dict) -> str:
    if not angle:
        return ""
    return (
        f"\nANGULO ESTRATEGICO SELECIONADO:\n"
        f"nome: {angle.get('nome','')}\n"
        f"tensao: {angle.get('tensao','')}\n"
        f"mecanismo: {angle.get('mecanismo','')}\n"
        f"headline_exemplo: {angle.get('headline_exemplo','')}\n"
    )


def _get_skill_block(plan, agente: str) -> str:
    """Monta bloco de skills para um agente a partir do plano."""
    if not plan:
        return ""
    from studio.bruxo_orchestrator import get_skill_content
    skills = plan.skills_por_agente.get(agente, [])
    blocks = []
    for skill_name in skills:
        content = get_skill_content(skill_name, max_chars=400)
        if content:
            blocks.append(f"[SKILL:{skill_name}]\n{content}")
    return "\n".join(blocks)


QUALITY_RULES = """
REGRAS OBRIGATORIAS â€” SEM EXCECAO:
PROIBIDO (uso de qualquer uma dessas = output rejeitado):
- "descubra como" / "aprenda" / "veja" / "saiba" / "confia"
- "transforme seu negocio" / "leve seu negocio" / "eleve sua marca"
- headline sem contraste real (afirmacao positiva morna sem tensao)
- legenda com excesso de explicacao que o post ja deu
- CTA generico: "acesse o link" / "entre em contato" sem contexto de dor

OBRIGATORIO:
- Tensao real: conflito, perda, custo oculto ou dado que muda perspectiva
- Dado concreto OU comparacao especifica OU sequencia logica com quebra
- Progressao: cada slide/parte aumenta pressao ou revela mais â€” nao repete
- CTA: consequencia direta da dor explorada â€” nao apendice

PARA NICHO DELIVERY especificamente:
- Sempre que possivel: puxar comissao de plataforma, retencao de cliente, dependencia, margem
- "quanto voce pagou de comissao esse mes?" > "aumente seus lucros"
- "seu cliente pediu pelo iFood, nao por voce" > "fidelize seus clientes"
- Comparacao de ticket direto vs plataforma > beneficio generico
"""

PIPELINE_VERSION = "1.0"
ANGLE_SCORE_MIN = 8
ANGLE_MAX_ATTEMPTS = 3
HEADLINE_MIN_WORDS = 3
HEADLINE_MAX_WORDS = 12
CTA_MAX_WORDS = 18
SEO_CONTEXT_MIN_MATCHES = 3
GENERIC_SEO_TERMS = {"marketing", "conteudo", "instagram", "social", "resultado", "negocio"}
CTA_ACTION_TERMS = {
    "chame", "fale", "mande", "manda", "clique", "responda", "peca", "peÃ§a", "salve",
    "comente", "acesse", "envie", "compare", "reveja", "abra", "faca", "faÃ§a",
    "descubra", "veja", "calcule", "simule",
}
PERFORMANCE_MEMORY_MAX_ITEMS = 120
PERFORMANCE_MEMORY_GOOD_SCORE = 80
PERFORMANCE_MEMORY_BAD_SCORE = 60
PERFORMANCE_BAD_SIMILARITY_REJECT = 0.78
PERFORMANCE_SIMILARITY_HIGH = 0.45
ALLOCATION_TRACE_MAX_CYCLES = 20
# Portfolio engine impÃµe escassez real: o sistema sempre precisa escolher poucos vencedores.
PORTFOLIO_MAX_TOP_CREATIVES = 3
PORTFOLIO_MAX_TEST_CREATIVES = 2
DEFAULT_BENCHMARK_PROFILE = {
    "niche": "generic",
    "objective": "generic",
    "ctr_good": 2.2,
    "ctr_bad": 0.8,
    "cpa_good": 25.0,
    "cpa_bad": 80.0,
    "roas_good": 4.0,
    "roas_bad": 1.2,
}
BENCHMARK_PROFILES = [
    {
        "niche": "delivery",
        "objective": "conversao",
        "ctr_good": 1.8,
        "ctr_bad": 0.7,
        "cpa_good": 18.0,
        "cpa_bad": 45.0,
        "roas_good": 3.0,
        "roas_bad": 1.1,
    },
    {
        "niche": "clinica",
        "objective": "lead",
        "ctr_good": 1.4,
        "ctr_bad": 0.6,
        "cpa_good": 35.0,
        "cpa_bad": 90.0,
        "roas_good": 2.5,
        "roas_bad": 1.0,
    },
    {
        "niche": "ecom",
        "objective": "venda",
        "ctr_good": 2.0,
        "ctr_bad": 0.9,
        "cpa_good": 30.0,
        "cpa_bad": 95.0,
        "roas_good": 3.5,
        "roas_bad": 1.3,
    },
    {
        "niche": "branding",
        "objective": "alcance",
        "ctr_good": 1.2,
        "ctr_bad": 0.5,
        "cpa_good": 12.0,
        "cpa_bad": 35.0,
        "roas_good": 1.8,
        "roas_bad": 0.8,
    },
]


def _load_identity_context(client_id: str) -> dict:
    from studio.studio_manager import ensure_brand_identity, get_client_summary, get_brand_summary, get_audit_summary

    cs = get_client_summary(client_id)
    brand_raw = ensure_brand_identity(client_id)
    bs = get_brand_summary(client_id)
    aud = get_audit_summary(client_id)
    return {
        "cliente": cs,
        "brand_raw": brand_raw,
        "brand": bs,
        "audit": aud,
    }


def _record_job_error(client_id: str, job_id: str, error_message: str, error_type: str, traceback_text: str, jdir: str) -> dict:
    tb_path = os.path.join(jdir, "last_error_traceback.txt")
    with open(tb_path, "w", encoding="utf-8") as f:
        f.write(traceback_text or error_message or "")
    err_payload = {
        "status": "erro",
        "erro_mensagem": error_message,
        "erro_tipo": error_type,
        "erro_traceback_file": "last_error_traceback.txt",
        "erro_salvo_em": _ts(),
    }
    update_job(client_id, job_id, err_payload)
    return err_payload


def _identity_prompt_block(identity: dict) -> str:
    cliente = identity.get("cliente", {})
    brand = identity.get("brand_raw", {})
    audit = identity.get("audit", {})
    cores = brand.get("cores", [])
    fontes = brand.get("fontes", [])
    observacoes = (brand.get("observacoes_identidade", "") or "").strip()
    if not cores or not fontes or not observacoes:
        raise ValueError("Visual Agent bloqueado: brand.json sem identidade visual completa.")
    parts = []
    if cliente.get("instagram"):
        parts.append(f"INSTAGRAM_REFERENCIA: @{cliente.get('instagram')}")
    parts.append("IDENTIDADE_VISUAL_OBRIGATORIA: usar brand.json como fonte de verdade.")
    parts.append(f"CORES_MARCA: {', '.join(cores)}")
    parts.append(f"FONTES_MARCA: {', '.join(fontes)}")
    parts.append(f"OBS_IDENTIDADE: {observacoes}")
    if audit.get("linha_visual"):
        parts.append(f"LINHA_VISUAL_AUDIT: {audit.get('linha_visual')}")
    return "\n".join(parts)


def _seo_defaults(client_id: str, job: dict, angle: dict) -> dict:
    from studio.studio_manager import get_client_summary

    cs = get_client_summary(client_id)
    base_terms = [
        cs.get("nicho", ""),
        cs.get("produto", ""),
        job.get("objetivo_job", ""),
        angle.get("nome", "") if angle else "",
        angle.get("tensao", "") if angle else "",
    ]
    tokens = []
    for term in base_terms:
        for token in re.findall(r"[a-zA-ZÃ€-Ã¿0-9]+", term.lower()):
            if len(token) >= 4 and token not in tokens:
                tokens.append(token)

    principais = tokens[:3] or ["instagram", "conteudo", "negocio"]
    secundarias = tokens[3:6] or ["marketing", "social", "resultado"]
    hashtags = [f"#{t.replace(' ', '')}" for t in (principais + secundarias)[:6]]
    return {
        "principais": principais,
        "secundarias": secundarias,
        "hashtags": hashtags,
    }


def _extract_list_block(text: str, header: str) -> list:
    block = _extract_block(text, header)
    items = []
    for line in block.splitlines():
        clean = line.strip().lstrip("-").strip()
        if clean:
            items.append(clean)
    return items


def _ensure_copy_seo(text: str, client_id: str, job: dict, angle: dict) -> tuple[str, dict]:
    seo = {
        "principais": _extract_list_block(text, "SEO_KEYWORDS_PRINCIPAIS:"),
        "secundarias": _extract_list_block(text, "SEO_KEYWORDS_SECUNDARIAS:"),
        "hashtags": _extract_list_block(text, "HASHTAGS:"),
    }
    return text, seo


def _tokenize(text: str) -> list:
    # Keep alphanumeric word tokens without relying on fragile encoded ranges.
    return re.findall(r"[^\W_]+", (text or "").lower(), flags=re.UNICODE)


def _looks_like_design_spec(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    if re.search(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})", text):
        return True
    if re.search(r"\b\d+\s*(?:pt|px)\b", lowered):
        return True
    design_terms = [
        "tipografia", "composicao", "composiÃ§Ã£o", "fundo", "layout",
        "cor exata", "safe zone", "peso", "destaque", "elemento_visual",
    ]
    return any(term in lowered for term in design_terms)


def _build_seo_context_terms(client_id: str, job: dict, angle: dict) -> set:
    from studio.studio_manager import get_client_summary

    cs = get_client_summary(client_id)
    terms = set()
    for source in [
        cs.get("nicho", ""),
        cs.get("produto", ""),
        cs.get("objetivo", ""),
        job.get("briefing", ""),
        job.get("objetivo_job", ""),
        angle.get("nome", "") if angle else "",
        angle.get("tensao", "") if angle else "",
        angle.get("mecanismo", "") if angle else "",
        angle.get("headline_exemplo", "") if angle else "",
    ]:
        for token in _tokenize(source):
            if len(token) >= 4:
                terms.add(token)
    return terms


def _extract_primary_copy_signal(text: str, header: str) -> str:
    block = _extract_block(text, header)
    if not block:
        return ""
    first_line = _clean_value_line(block)
    if first_line:
        return first_line
    for line in block.splitlines():
        clean = _clean_value_line(line)
        if clean:
            return clean
    return ""


def _fixed_copy_contract_block() -> str:
    return """

CONTRATO_FIXO_DE_SAIDA_DO_COPY:
- Use exatamente estes headers: HEADLINE, CTA, VISUAL_BRIEF, SEO_KEYWORDS_PRINCIPAIS, SEO_KEYWORDS_SECUNDARIAS, HASHTAGS
- VISUAL_BRIEF deve conter exatamente estes subcampos: cena, composicao, estilo_visual, alinhamento_brand
- VISUAL_BRIEF deve traduzir DIRECAO_VISUAL em instrucao executavel, sem inventar um conceito novo
- composicao deve conter plano, posicao, foco e profundidade
- estilo_visual deve conter tipo de imagem, iluminacao, contraste e cor
- alinhamento_brand deve conter aplicacao da identidade da marca com cores, fontes ou posicionamento quando existirem no contexto
- Em estilo_visual e alinhamento_brand, cite cores e fontes do brand.json quando existirem no contexto
- CTA deve comecar com verbo de acao explicito
- Verbos validos de CTA: Clique, Agende, Fale, Descubra, Envie, Peca, Compre
- Nao escreva nada fora da estrutura
- Nao omita blocos

EXEMPLO_ESTRUTURAL:
HEADLINE:
Pare de perder margem no iFood

CTA:
Fale no WhatsApp e venda direto hoje

VISUAL_BRIEF:
- cena: dono de delivery olhando painel com pedidos do iFood caindo, expressao de frustracao
- composicao: plano medio, personagem a esquerda, tela com numeros a direita, foco no contraste entre volume de pedidos e lucro baixo
- estilo_visual: fotografia realista, iluminacao fria, contraste medio, cores da marca (#FF6B35, #1A1A1A), tipografia Montserrat Bold aplicada em overlay
- alinhamento_brand: uso das cores principais (#FF6B35 e #1A1A1A), tipografia Montserrat Bold, estetica alinhada com posicionamento de crescimento e controle de margem

SEO_KEYWORDS_PRINCIPAIS:
- trafego pago delivery
- sair do ifood

SEO_KEYWORDS_SECUNDARIAS:
- marketing para delivery
- vendas diretas

HASHTAGS:
- #delivery
- #trafegopago
"""


def _retry_copy_if_needed(base_prompt: str, copy_text: str, errors: list, attempt: int) -> dict:
    retry_prompt = f"""{base_prompt}

CORRECAO_OBRIGATORIA_DE_ESTRUTURA:
- tentativa_atual: {attempt + 1}/3
    - erros_detectados: {_safe_join(errors)}
- Corrija apenas os blocos invalidos
- Mantenha os blocos validos inalterados
- Use exatamente os headers obrigatorios
- Se VISUAL_BRIEF estiver invalido, traduza DIRECAO_VISUAL em instrucoes executaveis
- composicao deve conter plano, posicao, foco e profundidade
- estilo_visual deve conter tipo de imagem, iluminacao, contraste e cor
- alinhamento_brand deve conter aplicacao da identidade da marca com cores, fontes ou posicionamento
- Em estilo_visual e alinhamento_brand, cite cores e fontes do brand.json quando existirem no contexto
- CTA deve comecar com verbo de acao explicito
- Verbos validos de CTA: Clique, Agende, Fale, Descubra, Envie, Peca, Compre
- Nao escreva nada fora da estrutura

EXEMPLO_ESTRUTURAL:
HEADLINE:
Pare de perder margem no iFood

CTA:
Fale no WhatsApp e venda direto hoje

VISUAL_BRIEF:
- cena: dono de delivery olhando painel com pedidos do iFood caindo, expressao de frustracao
- composicao: plano medio, personagem a esquerda, tela com numeros a direita, foco no contraste entre volume de pedidos e lucro baixo
- estilo_visual: fotografia realista, iluminacao fria, contraste medio, cores da marca (#FF6B35, #1A1A1A), tipografia Montserrat Bold aplicada em overlay
- alinhamento_brand: uso das cores principais (#FF6B35 e #1A1A1A), tipografia Montserrat Bold, estetica alinhada com posicionamento de crescimento e controle de margem

SEO_KEYWORDS_PRINCIPAIS:
- trafego pago delivery
- sair do ifood

SEO_KEYWORDS_SECUNDARIAS:
- marketing para delivery
- vendas diretas

HASHTAGS:
- #delivery
- #trafegopago

SAIDA_ANTERIOR_COM_ERRO:
{copy_text.strip()[:4000]}"""
    retry_result = _invoke_with_retries("copy", retry_prompt, attempts=3)
    return {
        "text": retry_result.get("output", "") or "",
        "provider_used": retry_result.get("provider_used"),
        "provider_requested": retry_result.get("provider_requested"),
        "erro": retry_result.get("erro", ""),
        "raw": retry_result,
    }


def _build_war_room_copy_block(job: dict) -> str:
    mesa = job.get("mesa_guerra", {}) or {}
    if not mesa:
        return ""
    return (
        "DECISAO_MESA_DE_GUERRA:\n"
        f"- ANGULO_FINAL: {mesa.get('angulo_final', '')}\n"
        f"- TESE: {mesa.get('tese', '')}\n"
        f"- DIRECAO_COPY: {mesa.get('direcao_copy', '')}\n"
        f"- DIRECAO_VISUAL: {mesa.get('direcao_visual', '')}\n"
    )


def _repair_visual_brief_only(copy_text: str, errors: list, war_room_block: str = "", identity_block: str = "") -> dict:
    retry_prompt = f"""CORRECAO_CIRURGICA_DO_VISUAL_BRIEF:
- Responda somente com VISUAL_BRIEF
- Reescreva apenas esse bloco
- Entregue os 4 subcampos na mesma linha do header, separados por " | "
- Use exatamente estes 4 subcampos: cena, composicao, estilo_visual, alinhamento_brand
    - erros_detectados: {_safe_join(errors)}
- VISUAL_BRIEF deve traduzir DIRECAO_VISUAL em instrucao executavel
- composicao deve conter plano, posicao, foco e profundidade
- estilo_visual deve conter tipo de imagem, iluminacao, contraste e cor
- alinhamento_brand deve mostrar como a identidade da marca foi aplicada
- Cite cores e fontes do brand.json quando existirem no contexto
- Nao escreva nada fora do bloco

{war_room_block}
{identity_block}

EXEMPLO_ESTRUTURAL:
VISUAL_BRIEF: cena: dono de delivery olhando painel com pedidos do iFood caindo, expressao de frustracao | composicao: plano medio, personagem a esquerda, tela com numeros a direita, foco no contraste entre volume de pedidos e lucro baixo | estilo_visual: fotografia realista, iluminacao fria, contraste medio, cores da marca (#FF6B35, #1A1A1A), tipografia Montserrat Bold aplicada em overlay | alinhamento_brand: uso das cores principais (#FF6B35 e #1A1A1A), tipografia Montserrat Bold, estetica alinhada com posicionamento de crescimento e controle de margem

SAIDA_ATUAL:
{copy_text.strip()[:4000]}"""
    retry_result = _invoke_with_retries("copy", retry_prompt, attempts=3)
    repaired_block = (retry_result.get("output", "") or "").strip()
    if repaired_block and "VISUAL_BRIEF" in repaired_block.upper():
        pattern = r"(?is)(VISUAL_BRIEF\s*:.*?)(?=\n[A-Z][A-Z_]+(?:\s*:)|\Z)"
        if re.search(pattern, copy_text):
            merged_text = re.sub(pattern, repaired_block, copy_text, count=1)
        else:
            merged_text = copy_text.rstrip() + "\n\n" + repaired_block
    else:
        merged_text = copy_text
    return {
        "text": merged_text,
        "provider_used": retry_result.get("provider_used"),
        "provider_requested": retry_result.get("provider_requested"),
        "erro": retry_result.get("erro", ""),
        "raw": retry_result,
    }


def _score_angle_conversion_potential(angle: dict, job: dict, client_summary: dict, audit_summary: dict, past_top: list) -> dict:
    text_blob = " ".join([
        angle.get("nome", ""),
        angle.get("tensao", ""),
        angle.get("mecanismo", ""),
        angle.get("headline_exemplo", ""),
        angle.get("por_que_funciona", ""),
    ]).lower()
    score_modelo = max(1, min(int(angle.get("score_estimado", 5) or 5), 10))
    score = max(1, min(int(round(score_modelo * 0.65)), 10))
    breakdown = {"modelo": score_modelo, "base_ponderada": score}
    reasons = []

    pain_terms = ["perda", "custo", "comissao", "dependencia", "risco", "erro", "desperd", "margem", "controle"]
    proof_terms = ["dado", "compar", "antes", "depois", "vs", "numero", "quanto", "%", "ticket", "margem"]
    action_terms = ["whatsapp", "pedido", "agendamento", "venda", "convers", "cliente", "reserva", "lead"]
    generic_terms = ["sucesso", "crescer", "cresca", "mais vendas", "melhor", "incrivel", "transforme"]

    if any(term in text_blob for term in pain_terms):
        score += 1
        breakdown["dor_real"] = 1
        reasons.append("explora dor ligada a perda ou controle")
    if any(term in text_blob for term in proof_terms):
        score += 1
        breakdown["prova_especifica"] = 1
        reasons.append("traz promessa com prova ou comparacao")
    if any(term in text_blob for term in action_terms):
        score += 1
        breakdown["acao_comercial"] = 1
        reasons.append("aproxima a mensagem de acao comercial mensuravel")
    if re.search(r"\d", text_blob):
        score += 1
        breakdown["especificidade"] = 1
        reasons.append("usa numero ou especificidade concreta")
    else:
        score -= 1
        breakdown["sem_especificidade"] = -1

    niche_terms = set(_tokenize(" ".join([
        client_summary.get("nicho", ""),
        client_summary.get("produto", ""),
        job.get("objetivo_job", ""),
        audit_summary.get("oportunidades_top", ""),
    ])))
    overlap = len(niche_terms.intersection(set(_tokenize(text_blob))))
    if overlap >= 2:
        score += 1
        breakdown["aderencia_nicho"] = 1
        reasons.append("aderente ao nicho e objetivo do job")
    else:
        score -= 1
        breakdown["aderencia_fraca"] = -1

    if any(term in text_blob for term in generic_terms):
        score -= 2
        breakdown["genericidade"] = -2
        reasons.append("tem risco de soar generico")

    nome_lower = angle.get("nome", "").lower()
    similar_past = next(
        (item for item in past_top if nome_lower and (nome_lower in item.get("angulo_nome", "").lower() or item.get("angulo_nome", "").lower() in nome_lower)),
        None,
    )
    if similar_past:
        score += 2
        breakdown["historico"] = 2
        reasons.append("similar a angulo com historico real de conversao")

    final_score = max(1, min(score, 10))
    cta_frame = "acao direta para recuperar controle e capturar demanda agora"
    if any(term in text_blob for term in ["comissao", "plataforma", "dependencia"]):
        cta_frame = "convite para sair da dependencia e recuperar margem"
    elif any(term in text_blob for term in ["ticket", "margem", "lucro", "custo"]):
        cta_frame = "convite para revisar custo oculto e proteger margem"

    return {
        "score_conversao": final_score,
        "motivo": "; ".join(reasons[:3]) or "angulo sem sinais fortes de conversao",
        "score_breakdown": breakdown,
        "copy_direcao": {
            "tensao_central": angle.get("tensao", ""),
            "mecanismo_prova": angle.get("mecanismo", ""),
            "headline_base": angle.get("headline_exemplo", ""),
            "cta_frame": cta_frame,
            "proibido_desviar_para": "beneficio generico, motivacao vaga ou promessa sem consequencia",
        },
    }


def _build_copy_decision_block(angle: dict) -> str:
    decision = angle.get("copy_direcao", {}) if angle else {}
    if not decision:
        return ""
    return (
        "DECISAO_DE_MENSAGEM_OBRIGATORIA:\n"
        f"- tensao_central: {decision.get('tensao_central', '')}\n"
        f"- mecanismo_de_prova: {decision.get('mecanismo_prova', '')}\n"
        f"- headline_base: {decision.get('headline_base', '')}\n"
        f"- framing_de_cta: {decision.get('cta_frame', '')}\n"
        f"- score_minimo_aceitavel: {ANGLE_SCORE_MIN}/10\n"
        f"- score_deste_angulo: {angle.get('score_final', angle.get('score_estimado', 'n/a'))}\n"
        f"- proibido_desviar_para: {decision.get('proibido_desviar_para', '')}\n"
        "- adapte toda a narrativa a esta logica; nao apenas repita o nome do angulo."
    )


def _validate_visual_identity_usage(visual_text: str, identity: dict) -> dict:
    brand = identity.get("brand_raw", {})
    visual_lower = (visual_text or "").lower()
    issues = []

    cores = [str(item).lower() for item in brand.get("cores", []) if item]
    fontes = [str(item).lower() for item in brand.get("fontes", []) if item]

    if cores and not any(cor in visual_lower for cor in cores):
        issues.append("visual nao referencia nenhuma cor de brand.json")

    font_hits = []
    for fonte in fontes:
        family = fonte.split()[0].lower()
        if fonte in visual_lower or family in visual_lower:
            font_hits.append(fonte)
    if fontes and not font_hits:
        issues.append("visual nao referencia nenhuma fonte de brand.json")

    return {
        "ok": not issues,
        "issues": issues,
        "validated_at": _ts(),
    }


def _build_handoff(stage: str, client_id: str, job: dict, payload: dict, status: str = "ok") -> dict:
    return {
        "version": PIPELINE_VERSION,
        "stage": stage,
        "status": status,
        "job_id": job.get("id"),
        "client_id": client_id,
        "tipo": job.get("tipo"),
        "generated_at": _ts(),
        "payload": payload,
    }


def _persist_handoff(jdir: str, order: int, stage: str, payload: dict, client_id: str, job: dict, status: str = "ok") -> dict:
    handoff = _build_handoff(stage, client_id, job, payload, status)
    _write_json_file(jdir, f"{order:02d}_{stage}_handoff.json", handoff)
    return handoff


def _build_creative_summary(
    *,
    client_id: str,
    job: dict,
    angle: dict,
    headline: str,
    subheadline: str = "",
    cta: str = "",
    mood: str = "",
    visual_direction: str = "",
    prompt_primary: str = "",
    seo: dict = None,
    aspect_ratio: str = "1:1",
    extra: dict = None,
) -> dict:
    summary = {
        "version": PIPELINE_VERSION,
        "job_id": job.get("id"),
        "client_id": client_id,
        "tipo": job.get("tipo"),
        "headline": (headline or "").strip(),
        "subheadline": (subheadline or "").strip(),
        "cta": (cta or "").strip(),
        "mood": (mood or "").strip(),
        "visual_direction": (visual_direction or "").strip(),
        "prompt_primary": (prompt_primary or "").strip(),
        "aspect_ratio": aspect_ratio,
        "angle": {
            "nome": angle.get("nome", "") if angle else "",
            "tensao": angle.get("tensao", "") if angle else "",
            "mecanismo": angle.get("mecanismo", "") if angle else "",
        },
        "seo": seo or {"principais": [], "secundarias": [], "hashtags": []},
        "generated_at": _ts(),
    }
    if extra:
        summary["extra"] = extra
    return summary


def _standardize_image_prompts(img_prompts: dict, creative_summary: dict, aspect_ratio: str, source_stage: str) -> dict:
    prompts = dict(img_prompts or {})
    standardized = {
        "version": PIPELINE_VERSION,
        "source_stage": source_stage,
        "aspect_ratio": aspect_ratio,
        "prompt_primary": (
            prompts.get("prompt_dalle")
            or prompts.get("prompt_midjourney")
            or prompts.get("prompt_sd")
            or ""
        ),
        "prompt_dalle": prompts.get("prompt_dalle", ""),
        "prompt_midjourney": prompts.get("prompt_midjourney", ""),
        "prompt_sd": prompts.get("prompt_sd", ""),
        "negative_prompt": prompts.get("negative_prompt", ""),
        "fallback_used": bool(prompts.get("_fallback")),
        "creative_headline": creative_summary.get("headline", ""),
        "creative_cta": creative_summary.get("cta", ""),
        "style_keywords": creative_summary.get("seo", {}).get("principais", []),
        "validation": {},
    }
    standardized["validation"] = {
        "has_primary_prompt": bool(standardized["prompt_primary"]),
        "has_negative_prompt": bool(standardized["negative_prompt"]),
        "has_headline": bool(standardized["creative_headline"]),
    }
    return standardized


def _validate_image_contract(creative_summary: dict, image_prompts: dict) -> dict:
    issues = []
    if not creative_summary.get("headline"):
        issues.append("creative_summary.headline ausente")
    seo = creative_summary.get("seo", {})
    if not seo.get("principais") or not seo.get("secundarias"):
        issues.append("SEO obrigatÃ³rio ausente no creative_summary")
    if not image_prompts.get("prompt_primary"):
        issues.append("image_prompts.prompt_primary ausente")
    if not image_prompts.get("negative_prompt"):
        issues.append("image_prompts.negative_prompt ausente")
    return {
        "ok": not issues,
        "issues": issues,
        "validated_at": _ts(),
    }


def _validate_copy_structure(text: str) -> dict:
    normalized = (text or "").strip()
    required_blocks = {
        "HEADLINE": _extract_block(normalized, "HEADLINE"),
        "CTA": _extract_block(normalized, "CTA"),
        "VISUAL_BRIEF": _extract_block(normalized, "VISUAL_BRIEF") or _extract_block(normalized, "VISUAL BRIEF"),
        "SEO_KEYWORDS_PRINCIPAIS": "\n".join(_extract_list_block(normalized, "SEO_KEYWORDS_PRINCIPAIS")),
        "SEO_KEYWORDS_SECUNDARIAS": "\n".join(_extract_list_block(normalized, "SEO_KEYWORDS_SECUNDARIAS")),
        "HASHTAGS": "\n".join(_extract_list_block(normalized, "HASHTAGS")),
    }
    issues = []
    missing_blocks = []
    incomplete_blocks = []
    for block_name, value in required_blocks.items():
        if not (value or "").strip():
            missing_blocks.append(block_name)
            issues.append(f"bloco obrigatorio ausente: {block_name}")

    visual_brief = required_blocks["VISUAL_BRIEF"]
    if visual_brief:
        visual_lower = visual_brief.lower()
        for required_item in ("cena:", "composicao:", "estilo_visual:", "alinhamento_brand:"):
            if required_item not in visual_lower:
                incomplete_blocks.append(f"VISUAL_BRIEF.{required_item.rstrip(':')}")
                issues.append(f"visual_brief incompleto: campo {required_item.rstrip(':')} ausente")
        generic_visual_terms = [
            "foto bonita", "visual bonito", "imagem impactante", "arte bonita",
            "design moderno", "algo clean", "algo premium", "bonito e profissional",
        ]
        if any(term in visual_lower for term in generic_visual_terms):
            incomplete_blocks.append("VISUAL_BRIEF.genericidade")
            issues.append("visual_brief generico demais")

    return {
        "ok": not issues,
        "issues": issues,
        "missing_blocks": missing_blocks,
        "incomplete_blocks": incomplete_blocks,
        "validated_at": _ts(),
    }


def _validate_copy_contract(text: str, job_type: str, angle: dict, client_id: str, job: dict) -> dict:
    issues = []
    normalized = (text or "").strip()

    if len(normalized) < 300:
        issues.append("copy curta demais para sustentar o job")

    headline = _extract_primary_copy_signal(normalized, "HEADLINE")
    slides = []
    if job_type == "carrossel":
        slides = _parse_slides(normalized)
        if not headline and slides:
            headline = (slides[0].get("headline", "") or "").strip()
    cta = _clean_value_line(
        _extract_block(normalized, "CTA")
        or _extract_block(normalized, "CTA_FINAL")
    )
    visual_brief = _extract_block(normalized, "VISUAL_BRIEF") or _extract_block(normalized, "VISUAL BRIEF")

    if not headline:
        issues.append("headline ausente")
    else:
        headline_words = _tokenize(headline)
        if _looks_like_design_spec(headline):
            issues.append("headline invalida: parece especificacao visual")
        if len(headline_words) < HEADLINE_MIN_WORDS:
            issues.append("headline curta demais")
        if len(headline_words) > HEADLINE_MAX_WORDS:
            issues.append("headline longa demais")
        if any(term in headline.lower() for term in ["descubra", "aprenda", "saiba", "veja", "transforme seu negocio", "eleve sua marca"]):
            issues.append("headline fraca ou generica")
    if not cta:
        issues.append("cta ausente")
    else:
        cta_words = _tokenize(cta)
        if _looks_like_design_spec(cta):
            issues.append("cta invalido: parece especificacao visual")
        if len(cta_words) > CTA_MAX_WORDS:
            issues.append("cta longo demais")
        if not any(word in CTA_ACTION_TERMS for word in cta_words):
            issues.append("cta sem verbo de acao claro")
    if not visual_brief and job_type in {"post_estatico", "reel_pack"}:
        issues.append("visual_brief ausente")

    if job_type == "carrossel":
        if len(slides) < 4:
            issues.append("carrossel sem quantidade minima de slides validos")
    elif job_type == "reel_pack":
        hook = _clean_value_line(_extract_block(normalized, "HOOK"))
        if not hook:
            issues.append("hook ausente no reel")
        captions = _extract_block(normalized, "CAPTIONS_SRT")
        if not captions or len(captions) < 20:
            issues.append("captions_srt ausente ou curto demais")

    seo = {
        "principais": _extract_list_block(normalized, "SEO_KEYWORDS_PRINCIPAIS"),
        "secundarias": _extract_list_block(normalized, "SEO_KEYWORDS_SECUNDARIAS"),
        "hashtags": _extract_list_block(normalized, "HASHTAGS"),
    }
    if not seo["principais"] or not seo["secundarias"] or not seo["hashtags"]:
        issues.append("seo incompleto no output de copy")
    else:
        seo_tokens = set()
        for section in seo.values():
            for item in section:
                seo_tokens.update(token for token in _tokenize(item) if len(token) >= 4)
        contextual_terms = _build_seo_context_terms(client_id, job, angle)
        context_matches = seo_tokens.intersection(contextual_terms)
        if len(context_matches) < SEO_CONTEXT_MIN_MATCHES:
            issues.append("seo sem aderencia contextual suficiente ao nicho/angulo")
        if seo_tokens and seo_tokens.issubset(GENERIC_SEO_TERMS):
            issues.append("seo generico demais")

    angle_tokens = set(_tokenize(" ".join([
        angle.get("headline_exemplo", "") if angle else "",
        angle.get("tensao", "") if angle else "",
        angle.get("mecanismo", "") if angle else "",
    ])))
    copy_tokens = set(_tokenize(normalized))
    shared_tokens = angle_tokens.intersection(copy_tokens)
    if angle_tokens and len(shared_tokens) < 2:
        issues.append("copy nao refletiu de forma suficiente a tensao do angulo escolhido")

    return {
        "ok": not issues,
        "issues": issues,
        "headline": headline,
        "cta": cta,
        "validated_at": _ts(),
    }


def _build_war_room_radar(client_summary: dict, audit_summary: dict, plan, job: dict, top_past: list) -> dict:
    nicho = client_summary.get("nicho", "") or client_summary.get("produto", "")
    produto = client_summary.get("produto", "")
    objetivo = job.get("objetivo_job", "") or client_summary.get("objetivo", "")
    dores = []
    for term in [
        audit_summary.get("diagnostico", ""),
        " | ".join(audit_summary.get("oportunidades_top", []) or []),
        " | ".join(_normalize_sequence(plan.contextos_extras if plan else [])),
        objetivo,
        nicho,
        produto,
    ]:
        for snippet in re.split(r"[|;\n]+", term):
            clean = snippet.strip()
            if clean and len(clean) > 18 and clean not in dores:
                dores.append(clean)

    oportunidades = list(audit_summary.get("oportunidades_top", []) or [])
    if not oportunidades:
        oportunidades = [
            "recuperar margem hoje com pedido direto",
            "expor custo oculto da plataforma sobre cliente recorrente",
            "reconquistar controle da demanda local",
        ]

    historico = []
    for item in top_past[:3]:
        nome = item.get("angulo_nome", "")
        if nome:
            historico.append(
                f"{nome} -> conversoes:{item.get('conversoes',0)} cliques:{item.get('cliques',0)}"
            )

    return {
        "nicho": nicho,
        "produto": produto,
        "objetivo": objetivo,
        "momento": "operacao local com pressao por margem e dependencia de plataforma",
        "dores": dores[:4],
        "saturacao": "feed saturado por promessas genericas, social proof vazio e criativos sem tensao",
        "oportunidades": oportunidades[:4],
        "contextos_extras": _normalize_sequence((plan.contextos_extras if plan else [])[:3]),
        "historico": historico,
    }


def _build_intel_squad_prompt(
    client_summary: dict,
    audit_summary: dict,
    plan,
    job: dict,
    top_past: list,
    identity: dict,
) -> str:
    brand = identity.get("brand_raw", {}) or {}
    cores = ", ".join(brand.get("cores", []) or []) or "nao informadas"
    fontes = ", ".join(brand.get("fontes", []) or []) or "nao informadas"
    historico = []
    for item in top_past[:3]:
        nome = item.get("angulo_nome", "")
        if nome:
            historico.append(
                f"- {nome} | conversoes={item.get('conversoes', 0)} | cliques={item.get('cliques', 0)}"
            )
    historico_block = "\n".join(historico) or "- sem historico forte disponivel"
    extras = "\n".join(f"- {item[:220]}" for item in _normalize_sequence((plan.contextos_extras if plan else [])[:4])) or "- sem sinais extras"
    oportunidades = "\n".join(f"- {item}" for item in (audit_summary.get("oportunidades_top", []) or [])[:4]) or "- sem oportunidades estruturadas"
    return f"""Voce e o INTEL_SQUAD do Agency Gateway.
Sua funcao e abastecer a Mesa de Guerra principal com um dossie curto, especifico e utilizavel.
Voce NAO decide a campanha final.
Nao use markdown fora dos headers e listas exigidas.

CLIENTE: {client_summary.get('nome', '')}
NICHO: {client_summary.get('nicho', '')}
PRODUTO: {client_summary.get('produto', '')}
OBJETIVO: {job.get('objetivo_job', '') or client_summary.get('objetivo', '')}
PRACA: {client_summary.get('cidade', '')}
BRIEFING: {job.get('briefing', '')}
DIAGNOSTICO_AUDIT: {audit_summary.get('diagnostico', '')}
OPORTUNIDADES_AUDIT:
{oportunidades}
IDENTIDADE_MARCA:
- cores: {cores}
- fontes: {fontes}
- observacoes: {(brand.get('observacoes_identidade', '') or '').strip() or 'nao informadas'}
HISTORICO_RELEVANTE:
{historico_block}
SINAIS_DE_SKILLS:
{extras}

ENTREGUE SOMENTE NESTE FORMATO:
SCOUTTREND_SINAIS:
- ...
- ...
- ...
SCOUTTREND_OPORTUNIDADES:
- ...
- ...
SCOUTTREND_SATURACOES:
- ...
- ...
ANALISTA_NICHO:
- dor_central: ...
- desejo_central: ...
- objecao_dominante: ...
- timing_comercial: ...
CURADOR_FORMATO:
- formato_recomendado: ...
- formato_secundario: ...
- risco_1: ...
- risco_2: ...
CURADOR_VISUAL:
- linguagem_visual_recomendada: ...
- estetica_a_evitar: ...
- gatilho_visual_principal: ...
ARCHIVIST:
- sinais_historicos_relevantes: ...
- repeticao_a_evitar: ...
- consistencia_de_marca_a_manter: ...
CONTRARIAN:
- critica_1: ...
- critica_2: ...
- critica_3: ...
- risco_1: ...
- risco_2: ...
- correcao_obrigatoria: ...
SINTESE_EXECUTIVA:
- oportunidade_prioritaria: ...
- risco_principal: ...
- direcao_recomendada: ...
- coisa_a_evitar_1: ...
- coisa_a_evitar_2: ...

REGRAS:
- seja especifico para negocio local / delivery quando o contexto apontar isso
- evite frases genericas como "melhorar resultado", "crescer nas redes", "fortalecer marca"
- contrarian deve atacar a tese com risco comercial real
- sintese executiva deve ser utilizavel pela Mesa de Guerra principal
- nao decidir a campanha final"""


def _extract_keyed_value(block: str, key: str) -> str:
    for line in (block or "").splitlines():
        clean = line.strip().lstrip("-").strip()
        if clean.lower().startswith(f"{key.lower()}:"):
            return clean.split(":", 1)[1].strip()
    return ""


def _parse_intel_squad_output(text: str) -> dict:
    normalized = (text or "").replace("```", "").strip()
    scout_sinais = _extract_list_block(normalized, "SCOUTTREND_SINAIS")
    scout_oportunidades = _extract_list_block(normalized, "SCOUTTREND_OPORTUNIDADES")
    scout_saturacoes = _extract_list_block(normalized, "SCOUTTREND_SATURACOES")
    analista = _extract_block(normalized, "ANALISTA_NICHO")
    formato = _extract_block(normalized, "CURADOR_FORMATO")
    visual = _extract_block(normalized, "CURADOR_VISUAL")
    archivist = _extract_block(normalized, "ARCHIVIST")
    contrarian = _extract_block(normalized, "CONTRARIAN")
    sintese = _extract_block(normalized, "SINTESE_EXECUTIVA")
    return {
        "scout_trend": {
            "sinais": scout_sinais,
            "oportunidades": scout_oportunidades,
            "saturacoes": scout_saturacoes,
        },
        "analista_nicho": {
            "dor_central": _extract_keyed_value(analista, "dor_central"),
            "desejo_central": _extract_keyed_value(analista, "desejo_central"),
            "objecao_dominante": _extract_keyed_value(analista, "objecao_dominante"),
            "timing_comercial": _extract_keyed_value(analista, "timing_comercial"),
        },
        "curador_formato": {
            "formato_recomendado": _extract_keyed_value(formato, "formato_recomendado"),
            "formato_secundario": _extract_keyed_value(formato, "formato_secundario"),
            "riscos": [
                _extract_keyed_value(formato, "risco_1"),
                _extract_keyed_value(formato, "risco_2"),
            ],
        },
        "curador_visual": {
            "linguagem_visual_recomendada": _extract_keyed_value(visual, "linguagem_visual_recomendada"),
            "estetica_a_evitar": _extract_keyed_value(visual, "estetica_a_evitar"),
            "gatilho_visual_principal": _extract_keyed_value(visual, "gatilho_visual_principal"),
        },
        "archivist": {
            "sinais_historicos_relevantes": _extract_keyed_value(archivist, "sinais_historicos_relevantes"),
            "repeticao_a_evitar": _extract_keyed_value(archivist, "repeticao_a_evitar"),
            "consistencia_de_marca_a_manter": _extract_keyed_value(archivist, "consistencia_de_marca_a_manter"),
        },
        "contrarian": {
            "criticas": [
                _extract_keyed_value(contrarian, "critica_1"),
                _extract_keyed_value(contrarian, "critica_2"),
                _extract_keyed_value(contrarian, "critica_3"),
            ],
            "riscos": [
                _extract_keyed_value(contrarian, "risco_1"),
                _extract_keyed_value(contrarian, "risco_2"),
            ],
            "correcao_obrigatoria": _extract_keyed_value(contrarian, "correcao_obrigatoria"),
        },
        "sintese_executiva": {
            "oportunidade_prioritaria": _extract_keyed_value(sintese, "oportunidade_prioritaria"),
            "risco_principal": _extract_keyed_value(sintese, "risco_principal"),
            "direcao_recomendada": _extract_keyed_value(sintese, "direcao_recomendada"),
            "coisas_a_evitar": [
                _extract_keyed_value(sintese, "coisa_a_evitar_1"),
                _extract_keyed_value(sintese, "coisa_a_evitar_2"),
            ],
        },
        "raw": normalized,
    }


def _validate_intel_squad_output(data: dict) -> dict:
    issues = []
    required = [
        "scout_trend",
        "analista_nicho",
        "curador_formato",
        "curador_visual",
        "archivist",
        "contrarian",
        "sintese_executiva",
    ]
    for key in required:
        if not data.get(key):
            issues.append(f"intel_squad sem {key}")
    scout = data.get("scout_trend", {})
    if len([item for item in scout.get("sinais", []) if item]) < 2:
        issues.append("intel_squad scout_trend sem sinais suficientes")
    if len([item for item in scout.get("oportunidades", []) if item]) < 1:
        issues.append("intel_squad scout_trend sem oportunidades")
    analista = data.get("analista_nicho", {})
    for key in ("dor_central", "desejo_central", "objecao_dominante", "timing_comercial"):
        if not analista.get(key):
            issues.append(f"intel_squad analista_nicho sem {key}")
    formato = data.get("curador_formato", {})
    if not formato.get("formato_recomendado"):
        issues.append("intel_squad curador_formato sem formato_recomendado")
    visual = data.get("curador_visual", {})
    if not visual.get("linguagem_visual_recomendada") or not visual.get("gatilho_visual_principal"):
        issues.append("intel_squad curador_visual incompleto")
    archivist = data.get("archivist", {})
    if not archivist.get("repeticao_a_evitar"):
        issues.append("intel_squad archivist sem repeticao_a_evitar")
    contrarian = data.get("contrarian", {})
    if len([item for item in contrarian.get("criticas", []) if item]) < 2:
        issues.append("intel_squad contrarian sem critica suficiente")
    if not contrarian.get("correcao_obrigatoria"):
        issues.append("intel_squad contrarian sem correcao_obrigatoria")
    sintese = data.get("sintese_executiva", {})
    for key in ("oportunidade_prioritaria", "risco_principal", "direcao_recomendada"):
        if not sintese.get(key):
            issues.append(f"intel_squad sintese_executiva sem {key}")
    density_blob = " ".join([
        " ".join(scout.get("sinais", [])),
        " ".join(scout.get("oportunidades", [])),
        analista.get("dor_central", ""),
        analista.get("objecao_dominante", ""),
        visual.get("gatilho_visual_principal", ""),
        contrarian.get("correcao_obrigatoria", ""),
        sintese.get("direcao_recomendada", ""),
    ]).strip()
    if len(density_blob) < 160:
        issues.append("intel_squad com densidade insuficiente")
    return {"ok": not issues, "issues": issues, "validated_at": _ts()}


def _build_intel_squad_contingency(
    client_summary: dict,
    audit_summary: dict,
    plan,
    job: dict,
    top_past: list,
    identity: dict,
) -> dict:
    brand = identity.get("brand_raw", {}) or {}
    nicho = client_summary.get("nicho", "") or client_summary.get("produto", "") or "negocio local"
    objetivo = job.get("objetivo_job", "") or client_summary.get("objetivo", "") or "gerar venda"
    oportunidade = (audit_summary.get("oportunidades_top", []) or ["recuperar margem com pedido direto"])[0]
    dor = (audit_summary.get("diagnostico", "") or "Dependencia de plataforma reduz margem e controle do relacionamento.")[:220]
    historico_nome = top_past[0].get("angulo_nome", "") if top_past else ""
    cores = ", ".join(brand.get("cores", [])[:2]) or "cores da marca"
    fontes = ", ".join(brand.get("fontes", [])[:2]) or "tipografia da marca"
    return {
        "scout_trend": {
            "sinais": [
                f"Anuncios de {nicho} saturados em promessa vaga e sem prova de margem.",
                f"Conteudo com comparacao direta de custo e autonomia tende a cortar o feed mais rapido.",
                f"Publico local responde melhor a leitura de risco imediato do que a branding abstrato.",
            ],
            "oportunidades": [
                f"Transformar {oportunidade} em confronto visivel com perda atual.",
                f"Usar tese de controle comercial imediato ligada a {objetivo}.",
            ],
            "saturacoes": [
                "Criativo bonito sem numero, prova ou contraste comercial.",
                "Promessa de crescimento sem tensao concreta nem comparacao.",
            ],
        },
        "analista_nicho": {
            "dor_central": "A operacao vende, mas perde margem e relacionamento ao depender da plataforma.",
            "desejo_central": "Controlar a venda direta sem reduzir volume.",
            "objecao_dominante": "Medo de perder pedidos ao sair do fluxo acomodado.",
            "timing_comercial": "Janela favoravel para mensagem de comparacao imediata e decisao rapida.",
        },
        "curador_formato": {
            "formato_recomendado": "post_estatico de confronto com numero ou contraste unico",
            "formato_secundario": "carrossel curto com comparacao de perda versus controle",
            "riscos": [
                "estetica polida demais enfraquecer a tensao comercial",
                "excesso de texto matar a leitura instantanea do contraste",
            ],
        },
        "curador_visual": {
            "linguagem_visual_recomendada": f"confronto direto, produto ou operador em tensao, contraste forte usando {cores}",
            "estetica_a_evitar": "mockup corporativo generico, neon gratuito, feed motivacional clean demais",
            "gatilho_visual_principal": "mostrar a perda invisivel ficando legivel em um unico ponto de foco",
        },
        "archivist": {
            "sinais_historicos_relevantes": historico_nome or "historico ainda raso; priorizar contraste comercial claro",
            "repeticao_a_evitar": "headline de beneficio generico sem prova ou custo explicito",
            "consistencia_de_marca_a_manter": f"usar {cores} e {fontes} como assinatura, sem quebrar o posicionamento de performance",
        },
        "contrarian": {
            "criticas": [
                "Se a tese ficar abstrata, vira mais um criativo de marketing para delivery.",
                "Se o visual disputar com a mensagem, perde scroll stop e urgencia.",
                "Se o angulo nao mostrar custo observavel, o publico racionaliza e ignora.",
            ],
            "riscos": [
                "romantizar autonomia sem mostrar o sacrificio atual",
                "usar repertorio saturado de crescimento e engajamento",
            ],
            "correcao_obrigatoria": "Forcar comparacao concreta entre dependencia atual e controle de margem.",
        },
        "sintese_executiva": {
            "oportunidade_prioritaria": oportunidade,
            "risco_principal": "a campanha parecer correta, mas generica e pouco urgente",
            "direcao_recomendada": f"Traduzir {dor} em prova visual e verbal de perda imediata no {nicho}.",
            "coisas_a_evitar": [
                "beneficio generico sem numero, contraste ou consequencia",
                "visual bonito sem relacao direta com a dor central",
            ],
        },
        "provider": "contingencia_local",
        "attempt": 0,
        "contingency_used": True,
    }


def _intel_squad_block(dossier: dict) -> str:
    if not dossier:
        return ""
    scout = dossier.get("scout_trend", {})
    analista = dossier.get("analista_nicho", {})
    formato = dossier.get("curador_formato", {})
    visual = dossier.get("curador_visual", {})
    archivist = dossier.get("archivist", {})
    contrarian = dossier.get("contrarian", {})
    sintese = dossier.get("sintese_executiva", {})
    lines = ["INTEL_SQUAD_DOSSIER:"]
    lines.append(f"- ScoutTrend sinais: {' | '.join([item for item in scout.get('sinais', []) if item])}")
    lines.append(f"- ScoutTrend oportunidades: {' | '.join([item for item in scout.get('oportunidades', []) if item])}")
    lines.append(f"- ScoutTrend saturacoes: {' | '.join([item for item in scout.get('saturacoes', []) if item])}")
    lines.append(
        "- AnalistaNicho: "
        f"dor={analista.get('dor_central', '')} | "
        f"desejo={analista.get('desejo_central', '')} | "
        f"objecao={analista.get('objecao_dominante', '')} | "
        f"timing={analista.get('timing_comercial', '')}"
    )
    lines.append(
        "- CuradorFormato: "
        f"principal={formato.get('formato_recomendado', '')} | "
        f"secundario={formato.get('formato_secundario', '')} | "
        f"riscos={' | '.join([item for item in formato.get('riscos', []) if item])}"
    )
    lines.append(
        "- CuradorVisual: "
        f"linguagem={visual.get('linguagem_visual_recomendada', '')} | "
        f"evitar={visual.get('estetica_a_evitar', '')} | "
        f"gatilho={visual.get('gatilho_visual_principal', '')}"
    )
    lines.append(
        "- Archivist: "
        f"historico={archivist.get('sinais_historicos_relevantes', '')} | "
        f"evitar={archivist.get('repeticao_a_evitar', '')} | "
        f"manter={archivist.get('consistencia_de_marca_a_manter', '')}"
    )
    lines.append(
        "- Contrarian: "
        f"criticas={' | '.join([item for item in contrarian.get('criticas', []) if item])} | "
        f"riscos={' | '.join([item for item in contrarian.get('riscos', []) if item])} | "
        f"correcao={contrarian.get('correcao_obrigatoria', '')}"
    )
    lines.append(
        "- SinteseExecutiva: "
        f"oportunidade={sintese.get('oportunidade_prioritaria', '')} | "
        f"risco={sintese.get('risco_principal', '')} | "
        f"direcao={sintese.get('direcao_recomendada', '')} | "
        f"evitar={' | '.join([item for item in sintese.get('coisas_a_evitar', []) if item])}"
    )
    return "\n".join(lines)


def _run_intel_squad(client_id: str, job: dict, plan, client_summary: dict, audit_summary: dict, top_past: list) -> dict:
    from studio.studio_manager import _job_dir

    identity = _load_identity_context(client_id)
    prompt = _build_intel_squad_prompt(client_summary, audit_summary, plan, job, top_past, identity)
    provider_candidates = _get_provider_candidates("analise", include_alt_provider=True)
    primary_provider = provider_candidates[0]
    attempt_logs = []
    last = {"provider_used": None, "erro": None, "output": ""}
    jdir = _job_dir(client_id, job.get("id"))

    for attempt in range(1, 4):
        for provider_name in provider_candidates:
            if provider_name == primary_provider:
                result = _invoke("analise", prompt)
            else:
                result = _invoke_specific_provider(provider_name, prompt)
            text = result.get("output", "") or ""
            last = result
            parsed = _parse_intel_squad_output(text)
            validation = _validate_intel_squad_output(parsed)
            attempt_logs.append({
                "attempt": attempt,
                "provider_requested": provider_name,
                "provider_used": result.get("provider_used"),
                "erro": _summarize_provider_error(result.get("erro")) if result.get("erro") else None,
                "output_chars": len(text),
                "validation_ok": validation["ok"],
                "validation_issues": validation["issues"],
            })
            _persist_attempt_log(jdir, "intel_squad_attempts.json", job, client_id, attempt_logs)
            if validation["ok"]:
                parsed["provider"] = result.get("provider_used") or provider_name
                parsed["attempt"] = attempt
                parsed["contingency_used"] = False
                parsed["attempt_logs"] = attempt_logs
                return parsed

    provider_failures_only = all(
        entry.get("erro") and not entry.get("output_chars")
        for entry in attempt_logs
    ) if attempt_logs else False
    if provider_failures_only:
        contingency = _build_intel_squad_contingency(client_summary, audit_summary, plan, job, top_past, identity)
        validation = _validate_intel_squad_output(contingency)
        if validation["ok"]:
            contingency["attempt_logs"] = attempt_logs
            contingency["fallback_reason"] = _summarize_provider_error(last.get("erro"))
            _persist_attempt_log(jdir, "intel_squad_attempts.json", job, client_id, attempt_logs, {"contingency_used": True})
            return contingency

    attempt_summary = " | ".join(
        f"tentativa {entry['attempt']}:{entry.get('provider_requested')}={entry.get('erro') or ','.join(entry.get('validation_issues', [])) or 'falha'}"
        for entry in attempt_logs[-4:]
    )
    raise ValueError(
        "Intel Squad falhou: "
        + (_summarize_provider_error(last.get("erro")) or "saida invalida")
        + (f" | tentativas: {attempt_summary}" if attempt_summary else "")
    )


def _war_room_radar_block(radar: dict) -> str:
    lines = [
        f"RADAR_NICHO: {radar.get('nicho', '')}",
        f"RADAR_PRODUTO: {radar.get('produto', '')}",
        f"RADAR_OBJETIVO: {radar.get('objetivo', '')}",
        f"RADAR_MOMENTO: {radar.get('momento', '')}",
        f"RADAR_SATURACAO: {radar.get('saturacao', '')}",
        "RADAR_DORES:",
    ]
    for item in radar.get("dores", []):
        lines.append(f"- {item}")
    lines.append("RADAR_OPORTUNIDADES:")
    for item in radar.get("oportunidades", []):
        lines.append(f"- {item}")
    if radar.get("contextos_extras"):
        lines.append("RADAR_SKILLS_E_SINAIS:")
        for item in radar.get("contextos_extras", []):
            lines.append(f"- {item[:220]}")
    if radar.get("historico"):
        lines.append("RADAR_HISTORICO:")
        for item in radar.get("historico", []):
            lines.append(f"- {item}")
    return "\n".join(lines)


def _parse_war_room_output(text: str) -> dict:
    text = (text or "").replace("```", "")
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    conflitos = []
    conflitos_match = re.search(r"^\s*CONFLITOS:\s*(?P<body>.*?)(?=^\s*ANGULO_FINAL:|\Z)", text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    if conflitos_match:
        for line in conflitos_match.group("body").splitlines():
            clean = line.strip()
            if clean.startswith("-"):
                conflitos.append(clean.lstrip("- ").strip())
    return {
        "bruxo_tese": _extract_block(text, "BRUXO_TESE"),
        "bruxo_linha": _extract_block(text, "BRUXO_LINHA"),
        "toguro_tensao": _extract_block(text, "TOGURO_TENSAO"),
        "toguro_promessa": _extract_block(text, "TOGURO_PROMESSA"),
        "toguro_critica": _extract_block(text, "TOGURO_CRITICA"),
        "neymar_scroll": _extract_block(text, "NEYMAR_SCROLL_STOP"),
        "neymar_visual": _extract_block(text, "NEYMAR_FORMATO_VISUAL"),
        "neymar_critica": _extract_block(text, "NEYMAR_CRITICA"),
        "conflitos": conflitos,
        "angulo_final": _extract_block(text, "ANGULO_FINAL"),
        "tese": _extract_block(text, "TESE_FINAL"),
        "direcao_copy": _extract_block(text, "DIRECAO_COPY"),
        "direcao_visual": _extract_block(text, "DIRECAO_VISUAL"),
        "raw": (text or "").strip(),
    }


def _validate_war_room_output(data: dict) -> dict:
    issues = []
    if not data.get("angulo_final"):
        issues.append("war_room sem angulo_final")
    if not data.get("tese") or len(data.get("tese", "").split()) < 8:
        issues.append("war_room sem tese clara")
    if not data.get("direcao_copy") or len(data.get("direcao_copy", "").split()) < 8:
        issues.append("war_room sem direcao_copy utilizavel")
    if not data.get("direcao_visual") or len(data.get("direcao_visual", "").split()) < 8:
        issues.append("war_room sem direcao_visual utilizavel")
    conflitos = data.get("conflitos", [])
    if len(conflitos) < 2:
        issues.append("war_room sem conflito real")
    generic_terms = ["crescer", "melhorar", "inovar", "engajar mais", "fortalecer marca", "ser visto"]
    text_blob = " ".join([
        data.get("angulo_final", ""),
        data.get("tese", ""),
        data.get("direcao_copy", ""),
        data.get("direcao_visual", ""),
        " | ".join(conflitos),
    ]).lower()
    if sum(1 for term in generic_terms if term in text_blob) >= 2:
        issues.append("war_room generica demais")
    if len(text_blob) < 180:
        issues.append("war_room com densidade insuficiente")
    return {"ok": not issues, "issues": issues, "validated_at": _ts()}


def _summarize_provider_error(err: str) -> str:
    message = (err or "").strip()
    if not message:
        return "erro vazio do provider"
    if "stderr:" in message and message.rstrip().endswith("stderr:"):
        return message + " [stderr vazio]"
    return message


def _invoke_specific_provider(provider_name: str, prompt: str) -> dict:
    from adapters.model_provider import _try_with_prompt

    output, err = _try_with_prompt(provider_name, prompt)
    return {
        "output": output,
        "provider_requested": provider_name,
        "provider_used": provider_name if output is not None else None,
        "fallback_used": False,
        "erro": err,
    }


def _is_provider_available(provider_name: str) -> bool:
    try:
        from adapters.model_provider import _build
        provider = _build(provider_name)
        return bool(provider and provider.is_available())
    except Exception:
        return False


def _get_provider_candidates(etapa: str, include_alt_provider: bool = True) -> list:
    from adapters.model_provider import get_routing_info

    routing = get_routing_info(etapa)
    primary_provider = routing.get("provider_requested") or "claude"
    fallback_provider = routing.get("fallback")
    candidates = []
    for name in [primary_provider, fallback_provider]:
        if not name or name in candidates:
            continue
        if _is_provider_available(name):
            candidates.append(name)
    if include_alt_provider:
        for extra_provider in ["openai", "antigravity"]:
            if extra_provider in candidates:
                continue
            if _is_provider_available(extra_provider):
                candidates.append(extra_provider)
    return candidates or [primary_provider]


def _persist_attempt_log(jdir: str, filename: str, job: dict, client_id: str, attempts: list, extra: dict = None):
    payload = {
        "job_id": job.get("id"),
        "client_id": client_id,
        "attempts": attempts,
        "updated_at": _ts(),
    }
    if extra:
        payload.update(extra)
    _write_json_file(jdir, filename, payload)


def _invoke_with_retries(etapa: str, prompt: str, attempts: int = 3, include_alt_provider: bool = True) -> dict:
    from adapters.model_provider import get_routing_info

    routing = get_routing_info(etapa)
    primary_provider = routing.get("provider_requested") or "claude"
    provider_candidates = _get_provider_candidates(etapa, include_alt_provider=include_alt_provider)

    attempt_logs = []
    last = {"output": None, "erro": None, "provider_used": None, "provider_requested": primary_provider, "attempt_logs": []}
    for attempt in range(1, attempts + 1):
        for provider_name in provider_candidates:
            if provider_name == primary_provider:
                result = _invoke(etapa, prompt)
            else:
                result = _invoke_specific_provider(provider_name, prompt)
            log_entry = {
                "attempt": attempt,
                "provider_requested": provider_name,
                "provider_used": result.get("provider_used"),
                "erro": _summarize_provider_error(result.get("erro")) if result.get("erro") else None,
                "output_chars": len(result.get("output", "") or ""),
            }
            attempt_logs.append(log_entry)
            last = dict(result)
            last["attempt_logs"] = list(attempt_logs)
            if result.get("output"):
                return last
    return last


def _build_war_room_contingency(radar: dict, intel_squad: dict, client_summary: dict, job: dict) -> dict:
    nicho = client_summary.get("nicho", "") or client_summary.get("produto", "") or "negocio local"
    sintese = intel_squad.get("sintese_executiva", {}) or {}
    contrarian = intel_squad.get("contrarian", {}) or {}
    analista = intel_squad.get("analista_nicho", {}) or {}
    curador_visual = intel_squad.get("curador_visual", {}) or {}
    scout = intel_squad.get("scout_trend", {}) or {}
    archivist = intel_squad.get("archivist", {}) or {}
    tese_base = (
        sintese.get("direcao_recomendada")
        or analista.get("dor_central")
        or radar.get("momento")
        or job.get("objetivo_job", "")
    )
    oportunidade = sintese.get("oportunidade_prioritaria", "")
    if not oportunidade:
        oportunidades = radar.get("oportunidades") or []
        if oportunidades:
            oportunidade = oportunidades[0]
    pressao = analista.get("dor_central", "")
    if not pressao:
        dores = radar.get("dores") or []
        if dores:
            pressao = dores[0]
    risco_principal = sintese.get("risco_principal", "") or (contrarian.get("riscos", [""]) or [""])[0]
    gatilho_visual = curador_visual.get("gatilho_visual_principal", "")
    evitar = curador_visual.get("estetica_a_evitar", "")
    repeticao = archivist.get("repeticao_a_evitar", "")
    angulo_final = (
        f"Explorar a perda invisivel no {nicho} com uma prova concreta e imediata: "
        f"{oportunidade or tese_base or 'mostrar o custo de continuar dependente da plataforma'}."
    ).strip()
    tese = (
        f"O cliente ja foi conquistado, mas a operacao continua pagando para manter acesso a ele. "
        f"{tese_base or 'A mensagem precisa transformar dependencia em custo visivel e comparavel.'} "
        f"Risco central a evitar: {risco_principal or 'cair em beneficio generico e pouco urgente'}."
    ).strip()
    direcao_copy = (
        f"A headline deve expor a dor principal sem abstracao. "
        f"Use uma prova especifica ligada a {pressao or 'margem e dependencia'}. "
        f"O CTA deve pedir acao direta para calcular ou revisar a perda real da operacao. "
        f"Evite repetir {repeticao or 'promessa vaga sem contraste comercial'}."
    ).strip()
    direcao_visual = (
        "Traduzir a tensao em um unico contraste visual dominante, sem elemento decorativo. "
        f"Usar {gatilho_visual or 'um ponto unico de perda legivel'} como gatilho visual principal, "
        f"evitando {evitar or 'estetica generica ou decorativa'}, e usar a identidade da marca como prova de consistencia."
    )
    conflitos = [
        f"Bruxo prioriza tese e contexto; a execucao precisa cortar abstracao e tornar a dor numerica ou observavel em {pressao or 'margem e dependencia'}.",
        f"Toguro empurra tensao e consequencia direta; sem isso a ideia cai no risco destacado pelo Contrarian: {risco_principal or 'genericidade comercial'}.",
        f"Neymar exige um visual de scroll stop com um unico elemento central, usando {gatilho_visual or 'contraste visual dominante'} sem recair em {evitar or 'decoracao gratuita'}.",
    ]
    if scout.get("saturacoes"):
        conflitos.append(f"ScoutTrend alertou saturacao em: {scout.get('saturacoes', [])[0]}")
    return {
        "angulo_final": angulo_final,
        "tese": tese,
        "direcao_copy": direcao_copy,
        "direcao_visual": direcao_visual,
        "conflitos": conflitos,
        "provider": "contingencia_local",
        "attempt": 0,
        "contingency_used": True,
    }


def _run_war_room(client_id: str, job: dict, plan, client_summary: dict, audit_summary: dict, top_past: list) -> dict:
    from studio.studio_manager import _job_dir

    radar = _build_war_room_radar(client_summary, audit_summary, plan, job, top_past)
    radar_block = _war_room_radar_block(radar)
    intel_squad = job.get("intel_squad", {}) or {}
    intel_block = _intel_squad_block(intel_squad)
    provider_candidates = _get_provider_candidates("analise", include_alt_provider=True)
    primary_provider = provider_candidates[0]
    attempt_logs = []
    last = {"provider_used": None, "erro": None, "output": ""}
    jdir = _job_dir(client_id, job.get("id"))

    for attempt in range(1, 4):
        prompt = f"""Voce e a MESA_DE_GUERRA do Agency Gateway.
Use o RADAR abaixo e conduza uma sequencia obrigatoria entre Bruxo, Toguro, Neymar e Capitao.

{radar_block}
{intel_block}
JOB_TIPO: {job.get('tipo', '')}
JOB_OBJETIVO: {job.get('objetivo_job', '')}
BRIEFING: {job.get('briefing', '')}

REGRAS:
- Bruxo identifica oportunidade e tese
- Toguro critica Bruxo e aumenta tensao e promessa
- Neymar critica se nao parar scroll e define direcao visual
- CONFLITOS e obrigatorio
- Capitao decide no final
- Nao concorde automaticamente
- Nao seja generico
- Use INTEL_SQUAD_DOSSIER como municao obrigatoria, sem terceirizar a decisao final
- Nao use markdown
- Nao use blocos de codigo
- Nao escreva texto antes do primeiro header
- Nao escreva texto depois de DIRECAO_VISUAL
- Entregue somente no formato abaixo

FORMATO_OBRIGATORIO:
BRUXO_TESE: ...
BRUXO_LINHA: ...
TOGURO_TENSAO: ...
TOGURO_PROMESSA: ...
TOGURO_CRITICA: ...
NEYMAR_SCROLL_STOP: ...
NEYMAR_FORMATO_VISUAL: ...
NEYMAR_CRITICA: ...
CONFLITOS:
- ...
- ...
ANGULO_FINAL: ...
TESE_FINAL: ...
DIRECAO_COPY: ...
DIRECAO_VISUAL: ...

CORRECAO_ATUAL:
- tentativa: {attempt}/3
- se faltar conflito ou decisao final, a saida sera rejeitada
- se houver genericidade, reescreva com mais tensao, prova e especificidade local"""
        for provider_name in provider_candidates:
            if provider_name == primary_provider:
                result = _invoke("analise", prompt)
            else:
                result = _invoke_specific_provider(provider_name, prompt)

            text = result.get("output", "") or ""
            last = result
            parsed = _parse_war_room_output(text)
            validation = _validate_war_room_output(parsed)
            provider_error = _summarize_provider_error(result.get("erro"))
            log_entry = {
                "attempt": attempt,
                "provider_requested": provider_name,
                "provider_used": result.get("provider_used"),
                "erro": provider_error or None,
                "output_chars": len(text),
                "validation_ok": validation["ok"],
                "validation_issues": validation["issues"],
            }
            attempt_logs.append(log_entry)
            _persist_attempt_log(jdir, "war_room_attempts.json", job, client_id, attempt_logs)
            if validation["ok"]:
                parsed["provider"] = result.get("provider_used") or provider_name
                parsed["attempt"] = attempt
                parsed["radar"] = radar
                parsed["attempt_logs"] = attempt_logs
                parsed["contingency_used"] = False
                return parsed

    provider_failures_only = all(
        entry.get("erro") and not entry.get("output_chars")
        for entry in attempt_logs
    ) if attempt_logs else False
    if provider_failures_only:
        contingency = _build_war_room_contingency(radar, intel_squad, client_summary, job)
        validation = _validate_war_room_output(contingency)
        if validation["ok"]:
            contingency["radar"] = radar
            contingency["attempt_logs"] = attempt_logs
            contingency["fallback_reason"] = _summarize_provider_error(last.get("erro"))
            _persist_attempt_log(jdir, "war_room_attempts.json", job, client_id, attempt_logs, {"contingency_used": True})
            return contingency

    attempt_summary = " | ".join(
        f"tentativa {entry['attempt']}:{entry.get('provider_requested')}={entry.get('erro') or ','.join(entry.get('validation_issues', [])) or 'falha'}"
        for entry in attempt_logs[-4:]
    )
    raise ValueError(
        "Mesa de Guerra falhou: "
        + (_summarize_provider_error(last.get("erro")) or "saida invalida")
        + (f" | tentativas: {attempt_summary}" if attempt_summary else "")
    )


def _build_failure_validation(stage: str, reason: str, existing: dict = None) -> dict:
    validation = dict(existing or {})
    base_issues = list(validation.get("issues", []))
    if reason and reason not in base_issues:
        base_issues.append(reason)
    validation.update({
        "ok": False,
        "stage": stage,
        "reason": reason,
        "issues": base_issues,
        "validated_at": _ts(),
    })
    return validation


def _performance_memory_path(client_id: str) -> str:
    return os.path.join("data", "clients", client_id, "performance_memory.json")


def load_performance_memory(client_id: str) -> dict:
    path = _performance_memory_path(client_id)
    if not os.path.exists(path):
        payload = {"client_id": client_id, "items": [], "updated_at": _ts()}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return payload
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    items = data.get("items", []) if isinstance(data, dict) else []
    return {
        "client_id": client_id,
        "items": items if isinstance(items, list) else [],
        "updated_at": data.get("updated_at") if isinstance(data, dict) else None,
    }


def _write_performance_memory(client_id: str, payload: dict):
    path = _performance_memory_path(client_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _classify_performance(ctr, cpa):
    ctr = float(ctr or 0)
    cpa = float(cpa or 0)
    if ctr >= 1.8 and (cpa <= 0 or cpa <= 45):
        return "bom"
    if ctr <= 0.9 and cpa > 65:
        return "ruim"
    return "neutro"


def _detect_hook_type(headline: str) -> str:
    text = (headline or "").strip().lower()
    if not text:
        return "indefinido"
    if re.search(r"\d", text):
        return "numerico"
    if "?" in text:
        return "pergunta"
    if any(term in text for term in ["perde", "perda", "custa", "drena", "vazando", "oculto", "refem", "refÃ©m"]):
        return "perda"
    if any(term in text for term in ["vs", "contra", "menos", "mais", "antes", "depois"]):
        return "contraste"
    if any(term in text for term in ["segredo", "ninguem", "ninguÃ©m", "erro", "mito", "verdade"]):
        return "curiosidade"
    return "beneficio_direto"


def _resolve_creative_id() -> str:
    return str(uuid.uuid4())


def _require_creative_id(item: dict, context: str) -> str:
    creative_id = str((item or {}).get("creative_id", "") or "").strip()
    if not creative_id:
        creative_id = str(uuid.uuid4())
        item["creative_id"] = creative_id
        item["_id_recovered"] = True
    return creative_id


def _compute_similarity(a, b) -> float:
    text_a = " ".join(_tokenize(a))
    text_b = " ".join(_tokenize(b))
    if not text_a or not text_b:
        return 0.0
    tokens_a = set(text_a.split())
    tokens_b = set(text_b.split())
    jaccard = len(tokens_a & tokens_b) / max(1, len(tokens_a | tokens_b))
    sequence = SequenceMatcher(None, text_a, text_b).ratio()
    return round((jaccard * 0.55) + (sequence * 0.45), 4)


def _memory_bucket(entry: dict) -> str:
    explicit = (entry.get("performance_class") or "").strip().lower()
    if explicit in {"bom", "neutro", "ruim"}:
        return explicit
    score = int(entry.get("score_quality_gate", 0) or 0)
    if score >= PERFORMANCE_MEMORY_GOOD_SCORE:
        return "bom"
    if score <= PERFORMANCE_MEMORY_BAD_SCORE or entry.get("status") == "reprovado_quality_gate":
        return "ruim"
    return "neutro"


def _build_memory_reference(entry: dict) -> str:
    angle = entry.get("angle", {}) or {}
    return " | ".join([
        entry.get("headline", ""),
        entry.get("hook_type", ""),
        angle.get("nome", ""),
        angle.get("tensao", ""),
        angle.get("mecanismo", ""),
    ]).strip()


def _select_memory_examples(memory: dict, bucket: str, limit: int = 3) -> list:
    items = []
    for entry in memory.get("items", []):
        if _memory_bucket(entry) != bucket:
            continue
        items.append(entry)
    items.sort(
        key=lambda item: (
            int(item.get("score_quality_gate", 0) or 0),
            item.get("updated_at", ""),
        ),
        reverse=(bucket == "bom"),
    )
    return items[:limit]


def _format_memory_examples(label: str, items: list) -> str:
    if not items:
        return f"{label}: nenhum historico relevante ainda"
    lines = [f"{label}:"]
    for item in items:
        angle = item.get("angle", {}) or {}
        lines.append(
            "- "
            f"headline={item.get('headline', '')} | "
            f"hook_type={item.get('hook_type', '')} | "
            f"angulo={angle.get('nome', '')} | "
            f"tensao={angle.get('tensao', '')} | "
            f"score_qg={item.get('score_quality_gate', 0)}"
        )
    return "\n".join(lines)


def _build_performance_memory_prompt_block(client_id: str) -> str:
    memory = load_performance_memory(client_id)
    good = _select_memory_examples(memory, "bom", limit=3)
    bad = _select_memory_examples(memory, "ruim", limit=3)
    return (
        "\nPERFORMANCE_MEMORY_ESTRATEGICA:\n"
        + _format_memory_examples("PADROES_QUE_FUNCIONAM", good)
        + "\n"
        + _format_memory_examples("PADROES_A_EVITAR", bad)
        + "\nUse PADROES_QUE_FUNCIONAM como referencia de estrutura, nao de copia literal.\n"
        + "Evite repetir a logica, o hook e a tensao dos PADROES_A_EVITAR.\n"
    )


def _find_memory_similarities(memory: dict, headline: str, angle: dict, limit: int = 3) -> dict:
    angle = angle or {}
    candidate_ref = " | ".join([
        headline or "",
        angle.get("nome", ""),
        angle.get("tensao", ""),
        angle.get("mecanismo", ""),
    ])
    scored = {"bom": [], "ruim": []}
    for entry in memory.get("items", []):
        bucket = _memory_bucket(entry)
        if bucket not in scored:
            continue
        similarity = _compute_similarity(candidate_ref, _build_memory_reference(entry))
        if similarity <= 0:
            continue
        scored[bucket].append({
            "similarity": similarity,
            "headline": entry.get("headline", ""),
            "score_quality_gate": entry.get("score_quality_gate", 0),
            "job_id": entry.get("job_id", ""),
            "hook_type": entry.get("hook_type", ""),
        })
    for bucket in scored:
        scored[bucket].sort(key=lambda item: item["similarity"], reverse=True)
        scored[bucket] = scored[bucket][:limit]
    return scored


def save_creative_performance(
    client_id: str,
    job_id: str,
    headline: str,
    angle: dict,
    score_quality_gate: int,
    status: str,
    ctr=None,
    cpa=None,
    extra: dict = None,
):
    memory = load_performance_memory(client_id)
    angle = angle or {}
    performance_class = _classify_performance(ctr, cpa) if (ctr is not None or cpa is not None) else None
    record = {
        "job_id": job_id,
        "creative_id": (extra or {}).get("creative_id", ""),
        "_id_recovered": bool((extra or {}).get("_id_recovered", False)),
        "headline": (headline or "").strip(),
        "hook_type": _detect_hook_type(headline),
        "angle": {
            "nome": angle.get("nome", ""),
            "tensao": angle.get("tensao", ""),
            "mecanismo": angle.get("mecanismo", ""),
            "headline_exemplo": angle.get("headline_exemplo", ""),
        },
        "score_quality_gate": int(score_quality_gate or 0),
        "status": status,
        "ctr": ctr,
        "cpa": cpa,
        "performance_class": performance_class,
        "updated_at": _ts(),
    }
    if extra:
        record.update(extra)

    if record.get("_id_recovered"):
        return

    items = [
        item for item in memory.get("items", [])
        if not (
            item.get("job_id") == job_id
            and int(item.get("quality_attempt", 1) or 1) == int(record.get("quality_attempt", 1) or 1)
        )
    ]
    items.insert(0, record)
    payload = {
        "client_id": client_id,
        "items": items[:PERFORMANCE_MEMORY_MAX_ITEMS],
        "updated_at": _ts(),
    }
    _write_performance_memory(client_id, payload)
    return record


class QualityGateRejected(Exception):
    def __init__(self, gate_result: dict, validation: dict = None):
        score = gate_result.get("score", 0)
        super().__init__(f"Quality Gate reprovado: score {score}/100")
        self.gate_result = gate_result
        self.validation = validation or {}


def _quality_gate_overlap(source_a: str, source_b: str) -> int:
    tokens_a = {token for token in _tokenize(source_a) if len(token) >= 4}
    tokens_b = {token for token in _tokenize(source_b) if len(token) >= 4}
    return len(tokens_a & tokens_b)


def _build_quality_gate_context_snapshot(
    headline: str,
    subheadline: str,
    cta: str,
    visual_brief: str,
    creative_summary: dict,
    angle: dict,
    client_context: dict,
) -> dict:
    headline = (headline or "").strip()
    subheadline = (subheadline or "").strip()
    cta = (cta or "").strip()
    visual_brief = (visual_brief or "").strip()
    creative_summary = creative_summary or {}
    angle = angle or {}
    client_context = client_context or {}

    combined_copy = " ".join([headline, subheadline, cta]).strip()
    angle_context = " ".join([
        angle.get("nome", ""),
        angle.get("tensao", ""),
        angle.get("mecanismo", ""),
        angle.get("headline_exemplo", ""),
    ]).strip()
    client_blob = " ".join([
        client_context.get("nicho", ""),
        client_context.get("produto", ""),
        client_context.get("objetivo", ""),
        client_context.get("tom_voz", ""),
    ]).strip()
    visual_direction = (creative_summary.get("visual_direction", "") or "").strip()
    visual_blob = " ".join([visual_brief, visual_direction]).strip()
    return {
        "headline": headline,
        "subheadline": subheadline,
        "cta": cta,
        "visual_brief": visual_brief,
        "visual_direction": visual_direction,
        "combined_copy": combined_copy,
        "angle_context": angle_context,
        "client_blob": client_blob,
        "visual_blob": visual_blob,
    }


def _run_quality_gate(
    headline: str,
    subheadline: str,
    cta: str,
    visual_brief: str,
    creative_summary: dict,
    angle: dict,
    client_context: dict,
    client_id: str = "",
    attempt: int = 1,
) -> dict:
    context_snapshot = _build_quality_gate_context_snapshot(
        headline=headline,
        subheadline=subheadline,
        cta=cta,
        visual_brief=visual_brief,
        creative_summary=creative_summary,
        angle=angle,
        client_context=client_context,
    )
    headline = context_snapshot["headline"]
    subheadline = context_snapshot["subheadline"]
    cta = context_snapshot["cta"]
    visual_brief = context_snapshot["visual_brief"]
    creative_summary = creative_summary or {}
    angle = angle or {}
    client_context = client_context or {}

    combined_copy = context_snapshot["combined_copy"]
    angle_context = context_snapshot["angle_context"]
    client_blob = context_snapshot["client_blob"]
    visual_blob = context_snapshot["visual_blob"]
    memory = load_performance_memory(client_id) if client_id else {"items": []}
    similarities = _find_memory_similarities(memory, headline, angle, limit=3)
    top_bad_similarity = similarities["ruim"][0]["similarity"] if similarities["ruim"] else 0.0
    top_good_similarity = similarities["bom"][0]["similarity"] if similarities["bom"] else 0.0

    generic_terms = {
        "marketing", "conteudo", "resultado", "crescer", "engajamento", "presenca",
        "visibilidade", "solucao", "estrategia", "performance", "negocio",
    }
    tension_terms = {
        "perde", "perda", "custa", "cobra", "oculto", "esconde", "drena", "refem",
        "refÃ©m", "dependencia", "dependÃªncia", "erro", "caro", "mais", "menos", "contra",
    }
    benefit_terms = {
        "margem", "lucro", "controle", "economia", "pedido", "direto", "cliente",
        "whatsapp", "lead", "venda", "conversao", "conversÃ£o",
    }
    visual_generic_terms = {
        "bonita", "bonito", "clean", "premium", "impactante", "moderno", "profissional",
        "atrativo", "chamativo", "criativo", "visual forte",
    }
    hook_words = _tokenize(headline)
    cta_words = _tokenize(cta)
    copy_tokens = set(_tokenize(combined_copy))
    generic_hits = sorted(term for term in generic_terms if term in copy_tokens)
    tension_hits = sorted(term for term in tension_terms if term in copy_tokens)
    benefit_hits = sorted(term for term in benefit_terms if term in copy_tokens)
    angle_overlap = _quality_gate_overlap(combined_copy, angle_context)
    client_overlap = _quality_gate_overlap(combined_copy, client_blob)
    visual_overlap = _quality_gate_overlap(visual_blob, angle_context + " " + client_blob)

    score_hook = 20
    if len(hook_words) < 3 or len(hook_words) > 8:
        score_hook -= 5
    if len(generic_hits) >= 2:
        score_hook -= 7
    if not (re.search(r"\d", headline) or "?" in headline or tension_hits):
        score_hook -= 5
    if angle_overlap == 0:
        score_hook -= 4
    score_hook = max(0, min(20, score_hook))

    score_clareza = 20
    if angle_overlap < 2:
        score_clareza -= 7
    if not benefit_hits:
        score_clareza -= 6
    if not cta:
        score_clareza -= 4
    if client_overlap == 0:
        score_clareza -= 3
    score_clareza = max(0, min(20, score_clareza))

    score_diferenciacao = 20
    if len(generic_hits) >= 2:
        score_diferenciacao -= 8
    if angle_overlap < 2:
        score_diferenciacao -= 6
    if client_overlap == 0:
        score_diferenciacao -= 3
    if headline.lower() == (angle.get("headline_exemplo", "") or "").strip().lower():
        score_diferenciacao -= 3
    score_diferenciacao = max(0, min(20, score_diferenciacao))

    score_tensao = 20
    if len(tension_hits) < 1:
        score_tensao -= 7
    if not re.search(r"\d|mais|menos|contra|sem|perde|custa|cobra", combined_copy.lower()):
        score_tensao -= 7
    if angle_overlap == 0:
        score_tensao -= 4
    score_tensao = max(0, min(20, score_tensao))

    visual_required_hits = sum(
        1 for marker in ["cena:", "composicao:", "estilo_visual:", "alinhamento_brand:"]
        if marker in visual_brief.lower()
    )
    score_visual = 20
    if visual_required_hits < 4:
        score_visual -= 8
    if any(term in visual_brief.lower() for term in visual_generic_terms):
        score_visual -= 6
    if not re.search(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})", visual_brief):
        score_visual -= 3
    if visual_overlap == 0:
        score_visual -= 3
    score_visual = max(0, min(20, score_visual))

    if top_bad_similarity >= PERFORMANCE_SIMILARITY_HIGH:
        score_diferenciacao -= 5
        score_hook -= 3
    if top_good_similarity >= PERFORMANCE_SIMILARITY_HIGH:
        score_hook += 2
        score_clareza += 2
        score_visual += 1
    score_hook = max(0, min(20, score_hook))
    score_clareza = max(0, min(20, score_clareza))
    score_diferenciacao = max(0, min(20, score_diferenciacao))
    score_visual = max(0, min(20, score_visual))

    cta_is_actionable = bool(cta_words) and any(word in CTA_ACTION_TERMS for word in cta_words) and len(cta_words) <= 8

    falhas = []
    critical_failures = []
    if len(generic_hits) >= 2 or score_diferenciacao <= 10:
        critical_failures.append("generico")
        falhas.append("genÃ©rico: headline/copy parecem intercambiÃ¡veis e pouco proprietÃ¡rios")
    if score_clareza <= 11 or not benefit_hits:
        critical_failures.append("promessa fraca")
        falhas.append("promessa fraca: benefÃ­cio comercial nÃ£o ficou direto")
    if not cta_is_actionable:
        critical_failures.append("CTA fraco")
        falhas.append("CTA fraco: sem verbo de aÃ§Ã£o forte ou sem consequÃªncia direta")
    if score_visual <= 11:
        critical_failures.append("visual sem forÃ§a")
        falhas.append("visual sem forÃ§a: brief pouco especÃ­fico ou sem scroll stop")
    if top_bad_similarity >= PERFORMANCE_BAD_SIMILARITY_REJECT:
        critical_failures.append("repeticao_historico_ruim")
        falhas.append("repetiÃ§Ã£o ruim: criativo muito parecido com histÃ³rico fraco reprovado")
    if score_tensao <= 11:
        falhas.append("tensÃ£o baixa: contraste insuficiente para provocar aÃ§Ã£o")
    if score_hook <= 11:
        falhas.append("hook fraco: chamada inicial nÃ£o corta o feed com clareza")

    acoes = []
    if "generico" in critical_failures:
        acoes.append("trocar headline por formulaÃ§Ã£o com perda, contraste ou dado impossÃ­vel de copiar por qualquer agÃªncia")
    if "promessa fraca" in critical_failures:
        acoes.append("explicitar a dor e o ganho em linguagem comercial direta, sem abstraÃ§Ã£o")
    if "CTA fraco" in critical_failures:
        acoes.append("encurtar CTA e usar verbo de aÃ§Ã£o com consequÃªncia comercial concreta")
    if "visual sem forÃ§a" in critical_failures:
        acoes.append("reescrever o visual brief com um Ãºnico foco, contraste alto e elemento central especÃ­fico")
    if "repeticao_historico_ruim" in critical_failures:
        acoes.append("trocar o hook, a tensÃ£o e a estrutura para fugir dos padrÃµes historicamente reprovados")
    if score_tensao <= 11:
        acoes.append("aumentar desconforto produtivo com comparaÃ§Ã£o, perda visÃ­vel ou inversÃ£o de senso comum")
    if not acoes:
        acoes.append("manter a execuÃ§Ã£o atual")

    total_score = score_hook + score_clareza + score_diferenciacao + score_tensao + score_visual
    approved = total_score >= 70 and not critical_failures
    return {
        "approved": approved,
        "score": total_score,
        "decisao": "approved" if approved else "reprovado_quality_gate",
        "tentativa": attempt,
        "diagnostico": {
            "hook": score_hook,
            "clareza": score_clareza,
            "diferenciacao": score_diferenciacao,
            "tensao": score_tensao,
            "visual": score_visual,
            "cta_direto": cta_is_actionable,
            "generic_terms": generic_hits,
            "angle_overlap": angle_overlap,
            "client_overlap": client_overlap,
            "visual_overlap": visual_overlap,
            "top_good_similarity": top_good_similarity,
            "top_bad_similarity": top_bad_similarity,
            "similar_good_examples": similarities["bom"],
            "similar_bad_examples": similarities["ruim"],
            "critical_failures": critical_failures,
        },
        "falhas": falhas,
        "acoes_recomendadas": acoes,
    }


def _persist_quality_gate(jdir: str, gate_result: dict, history: list = None, extra: dict = None):
    payload = dict(gate_result or {})
    payload["updated_at"] = _ts()
    if history is not None:
        payload["history"] = history
    if extra:
        payload.update(extra)
    _write_json_file(jdir, "quality_gate.json", payload)


def _select_asset_for_visual_audit(client_id: str) -> dict:
    from studio.studio_manager import list_client_assets

    assets = list_client_assets(client_id)
    image_assets = [item for item in assets if item.get("categoria") == "imagem"]
    selected = image_assets[0] if len(image_assets) == 1 else (image_assets[-1] if image_assets else {})
    return {
        "selected": selected,
        "items": image_assets,
    }


def _persist_visual_audit_trace(
    jdir: str,
    job: dict,
    cycle: dict,
    angle: dict,
    client_id: str,
    gate_result: dict,
    quality_attempt: int,
):
    summary = cycle.get("summary", {}) or {}
    provider_result = cycle.get("provider_result", {}) or {}
    identity = (cycle.get("identity", {}) or {}).get("cliente", {}) or {}
    context_snapshot = _build_quality_gate_context_snapshot(
        headline=summary.get("headline", ""),
        subheadline=summary.get("subheadline", ""),
        cta=summary.get("cta", ""),
        visual_brief=cycle.get("visual_brief", ""),
        creative_summary=summary,
        angle=angle,
        client_context=identity,
    )
    existing = _read_json_file(jdir, "audit_visual_trace.json")
    attempts = existing.get("attempts", []) if isinstance(existing, dict) else []
    attempts.append({
        "quality_attempt": int(quality_attempt or 1),
        "recorded_at": _ts(),
        "provider_used": provider_result.get("provider_used"),
        "asset_used": _select_asset_for_visual_audit(client_id),
        "visual_brief": context_snapshot["visual_brief"],
        "creative_summary_visual_direction": context_snapshot["visual_direction"],
        "angle_context": context_snapshot["angle_context"],
        "client_blob": context_snapshot["client_blob"],
        "visual_blob": context_snapshot["visual_blob"],
        "headline": summary.get("headline", ""),
        "cta": summary.get("cta", ""),
        "quality_gate": {
            "approved": gate_result.get("approved"),
            "decisao": gate_result.get("decisao"),
            "score_quality_gate": gate_result.get("score"),
            "critical_failures": gate_result.get("diagnostico", {}).get("critical_failures", []),
            "angle_overlap": gate_result.get("diagnostico", {}).get("angle_overlap"),
            "visual_overlap": gate_result.get("diagnostico", {}).get("visual_overlap"),
            "diferenciacao": gate_result.get("diagnostico", {}).get("diferenciacao"),
        },
    })
    payload = {
        "version": PIPELINE_VERSION,
        "job_id": job.get("id"),
        "client_id": client_id,
        "job_tipo": job.get("tipo"),
        "attempts": attempts,
    }
    _write_json_file(jdir, "audit_visual_trace.json", payload)


def _persist_visual_generation_trace(
    jdir: str,
    job: dict,
    cycle: dict,
    angle: dict,
    client_id: str,
    gate_result: dict,
    quality_attempt: int,
    failure_reason: str = "",
):
    summary = cycle.get("summary", {}) or {}
    provider_result = cycle.get("provider_result", {}) or {}
    identity = (cycle.get("identity", {}) or {}).get("cliente", {}) or {}
    context_snapshot = _build_quality_gate_context_snapshot(
        headline=summary.get("headline", ""),
        subheadline=summary.get("subheadline", ""),
        cta=summary.get("cta", ""),
        visual_brief=cycle.get("visual_brief", ""),
        creative_summary=summary,
        angle=angle,
        client_context=identity,
    )
    existing = _read_json_file(jdir, "audit_visual_generation_trace.json")
    attempts = existing.get("attempts", []) if isinstance(existing, dict) else []
    attempts.append({
        "quality_attempt": int(quality_attempt or 1),
        "recorded_at": _ts(),
        "failure_reason": failure_reason or "",
        "provider_used": provider_result.get("provider_used"),
        "replay_used": bool(cycle.get("replay_used")),
        "asset_used": _select_asset_for_visual_audit(client_id),
        "angle_snapshot_used": angle or {},
        "angle_context": context_snapshot["angle_context"],
        "visual_prompt_exact": cycle.get("visual_prompt", ""),
        "provider_raw_output": cycle.get("provider_raw_output", ""),
        "visual_brief_final": context_snapshot["visual_brief"],
        "creative_summary_visual_direction_final": context_snapshot["visual_direction"],
        "quality_gate": {
            "approved": (gate_result or {}).get("approved"),
            "decisao": (gate_result or {}).get("decisao"),
            "score_quality_gate": (gate_result or {}).get("score"),
            "critical_failures": (gate_result or {}).get("diagnostico", {}).get("critical_failures", []),
            "angle_overlap": (gate_result or {}).get("diagnostico", {}).get("angle_overlap"),
            "visual_overlap": (gate_result or {}).get("diagnostico", {}).get("visual_overlap"),
            "diferenciacao": (gate_result or {}).get("diagnostico", {}).get("diferenciacao"),
        },
    })
    payload = {
        "version": PIPELINE_VERSION,
        "job_id": job.get("id"),
        "client_id": client_id,
        "job_tipo": job.get("tipo"),
        "attempts": attempts,
    }
    _write_json_file(jdir, "audit_visual_generation_trace.json", payload)


def _build_visual_replay_result(replay_raw_output: str) -> dict:
    text = (replay_raw_output or "").strip()
    if not text:
        raise ValueError("visual_replay_raw_output vazio para replay visual.")
    return {
        "output": text,
        "erro": None,
        "provider_used": "replay_visual_smoke",
        "provider_requested": "replay_visual_smoke",
        "attempt_logs": [
            {
                "attempt": 1,
                "provider_requested": "replay_visual_smoke",
                "provider_used": "replay_visual_smoke",
                "erro": None,
                "output_chars": len(text),
            }
        ],
    }


def _build_quality_gate_feedback_block(gate_result: dict) -> str:
    gate_result = gate_result or {}
    falhas = gate_result.get("falhas", []) or []
    acoes = gate_result.get("acoes_recomendadas", []) or []
    return (
        "\nQUALITY_GATE_FEEDBACK_OBRIGATORIO:\n"
        f"- score_anterior: {gate_result.get('score', 0)}/100\n"
        f"- falhas_criticas: {' | '.join(gate_result.get('diagnostico', {}).get('critical_failures', [])) or 'nenhuma'}\n"
        f"- falhas_detectadas: {' | '.join(falhas) or 'nenhuma'}\n"
        f"- acoes_recomendadas: {' | '.join(acoes) or 'nenhuma'}\n"
        "- Reescreva o angulo e o copy para corrigir essas falhas sem suavizar a tensao.\n"
    )


def _rerun_toguro_for_quality_gate(client_id: str, job: dict, gate_result: dict) -> dict:
    from studio.studio_manager import get_client_summary, get_audit_summary
    from studio.bruxo_orchestrator import load_past_results, rank_past_angles

    cs = get_client_summary(client_id)
    aud = get_audit_summary(client_id)
    past = load_past_results(client_id)
    top_past = rank_past_angles(past)
    war_room = job.get("mesa_guerra", {}) or {}
    feedback_block = _build_quality_gate_feedback_block(gate_result)
    performance_memory_block = _build_performance_memory_prompt_block(client_id)
    prompt = f"""Voce e Toguro.
Reescreva EXATAMENTE 3 angulos com mais tensao, especificidade e apelo comercial.

CLIENTE: {cs.get('nome','')} | nicho: {cs.get('nicho','')} | produto: {cs.get('produto','')}
objetivo: {job.get('objetivo_job','')} | briefing: {job.get('briefing','')}
MESA_DE_GUERRA:
angulo_base: {war_room.get('angulo_final', '')}
tese: {war_room.get('tese', '')}
direcao_copy: {war_room.get('direcao_copy', '')}
direcao_visual: {war_room.get('direcao_visual', '')}
{feedback_block}
{performance_memory_block}

FORMATO OBRIGATORIO:
ANGULO 1
nome: ...
tensao: ...
mecanismo: ...
headline_exemplo: ...
por_que_funciona: ...
score_estimado: ...

ANGULO 2
nome: ...
tensao: ...
mecanismo: ...
headline_exemplo: ...
por_que_funciona: ...
score_estimado: ...

ANGULO 3
nome: ...
tensao: ...
mecanismo: ...
headline_exemplo: ...
por_que_funciona: ...
score_estimado: ..."""

    result = _invoke_with_retries("analise", prompt, attempts=3, include_alt_provider=True)
    text = result.get("output", "") or ""
    new_angles = _parse_angles_extended(text)
    if not new_angles:
        return {"angle": job.get("angulos", [{}])[0] if job.get("angulos") else {}, "provider": result.get("provider_used"), "raw": text}
    ranked = _rank_and_recommend(new_angles, job, cs, aud, top_past[:3])
    return {"angle": ranked[0], "provider": result.get("provider_used"), "raw": text}


# â”€â”€â”€ PrÃ©-auditoria (Toguro) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def generate_pre_audit(client_id: str) -> dict:
    """Toguro infere prÃ©-auditoria. Requer validaÃ§Ã£o manual antes de salvar."""
    from studio.studio_manager import get_client_summary, get_brand_summary
    from studio.bruxo_orchestrator import _load_catalog, _read_file_compact

    cs = get_client_summary(client_id)
    bs = get_brand_summary(client_id)

    # Injeta contexto de nicho se disponÃ­vel
    nicho_ctx = ""
    nicho = (cs.get("nicho", "") + " " + cs.get("produto", "")).lower()
    catalog = _load_catalog()
    for skill_name, skill_def in catalog.get("skills", {}).items():
        kws = skill_def.get("triggers", {}).get("nicho_keywords", [])
        if any(kw in nicho for kw in kws):
            path = skill_def.get("path", "")
            if os.path.exists(path):
                content = _read_file_compact(path, max_chars=600)
                if content:
                    nicho_ctx = f"\nCONTEXTO DE NICHO DISPONIVEL:\n{content[:400]}"
                    break

    prompt = f"""Voce e Toguro, especialista em diagnostico de presenca digital para pequenos negocios.

CLIENTE: {cs.get('nome','')} | nicho: {cs.get('nicho','')} | produto: {cs.get('produto','')}
instagram: @{cs.get('instagram','')} | objetivo: {cs.get('objetivo','')} | praca: {cs.get('cidade','')}
concorrentes: {', '.join('@' + c for c in cs.get('concorrentes',[]) if c) or 'nenhum informado'}
marca: cores={', '.join(bs.get('cores',[]))} | {bs.get('tom_keywords','')[:80]}{nicho_ctx}

Gere PRE-AUDITORIA inferida. Voce NAO tem acesso ao perfil real â€” infira o mais provavel para este nicho.
Seja especifico para o nicho, nao generico.

DIAGNOSTICO_PERFIL: (2-3 frases especificas para o nicho e porte)

PADROES_DETECTADOS:
- (padrao tipico 1)
- (padrao tipico 2)
- (padrao tipico 3)

ERROS_VISUAIS_PROVAVEIS:
- (erro mais comum em negocios deste nicho)
- (erro 2)

OPORTUNIDADES:
- (maior oportunidade para este nicho/objetivo)
- (oportunidade 2)
- (oportunidade 3)

LINHA_VISUAL_SUGERIDA: (1-2 frases de direcao visual)

LINHA_EDITORIAL_SUGERIDA: (1-2 frases de direcao de conteudo)

OBSERVACOES_COPY: (como se comunicar com este publico â€” 1 frase)

LACUNAS_VALIDAR:
- (o que precisa ser confirmado vendo o perfil real)
- (lacuna 2)"""

    result = _invoke("analise", prompt)
    text = result.get("output", "") or ""

    def _extract(label):
        m = re.search(rf'{label}:\s*(.+?)(?=\n[A-Z_]{{3,}}:|$)', text, re.DOTALL)
        return m.group(1).strip() if m else ""

    def _extract_list(label):
        block = _extract(label)
        return [l.lstrip('- ').strip() for l in block.split('\n') if l.strip().startswith('-')]

    return {
        "diagnostico_perfil": _extract("DIAGNOSTICO_PERFIL"),
        "padroes_detectados": _extract_list("PADROES_DETECTADOS"),
        "erros_visuais": _extract_list("ERROS_VISUAIS_PROVAVEIS"),
        "oportunidades": _extract_list("OPORTUNIDADES"),
        "linha_visual_sugerida": _extract("LINHA_VISUAL_SUGERIDA"),
        "linha_editorial_sugerida": _extract("LINHA_EDITORIAL_SUGERIDA"),
        "observacoes_copy": _extract("OBSERVACOES_COPY"),
        "lacunas_validar": _extract_list("LACUNAS_VALIDAR"),
        "gerado_em": _ts(),
        "status": "aguardando_validacao",
        "provider": result.get("provider_used"),
        "raw": text,
    }


# â”€â”€â”€ Ã‚ngulos estratÃ©gicos (Toguro) + Ranking â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def generate_angles(client_id: str, job_id: str) -> dict:
    """Toguro gera 3 Ã¢ngulos + avaliacao local de conversao + recomendaÃ§Ã£o.

    Usa aprendizado de resultados anteriores quando disponÃ­vel.
    """
    from studio.studio_manager import get_job, update_job, get_client_summary, get_audit_summary, _job_dir, record_client_pipeline_state
    from studio.bruxo_orchestrator import build_plan, load_past_results, rank_past_angles
    job = get_job(client_id, job_id)
    plan = build_plan(client_id, job)
    jdir = _job_dir(client_id, job_id)

    cs = get_client_summary(client_id)
    aud = get_audit_summary(client_id)

    # Contexto compacto para Ã¢ngulos
    ctx_lines = [
        f"CLIENTE: {cs.get('nome','')} | nicho: {cs.get('nicho','')} | produto: {cs.get('produto','')}",
        f"objetivo: {cs.get('objetivo','')} | praca: {cs.get('cidade','')}",
        f"concorrentes: {', '.join('@' + c for c in cs.get('concorrentes',[]) if c)}",
    ]
    if aud.get("diagnostico"):
        ctx_lines.append(f"AUDIT: {aud.get('diagnostico','')[:150]}")
    if aud.get("oportunidades_top"):
        ctx_lines.append(f"oportunidades: {' | '.join(aud.get('oportunidades_top',[]))}")

    # Injeta contextos do plano (nicho context, aprendizado)
    for extra in plan.contextos_extras:
        ctx_lines.append(extra[:300])

    ctx = "\n".join(ctx_lines)

    # Flags de auditoria para o modelo
    flags_str = ""
    if plan.flags:
        flags_str = f"\nADVERTENCIAS: {' | '.join(plan.flags)}"

    past = load_past_results(client_id)
    top_past = rank_past_angles(past)
    memory = load_performance_memory(client_id)
    memory_good = _select_memory_examples(memory, "bom", limit=3)
    memory_bad = _select_memory_examples(memory, "ruim", limit=3)
    performance_memory_block = _build_performance_memory_prompt_block(client_id)
    intel_squad = _run_intel_squad(client_id, job, plan, cs, aud, top_past[:3])
    update_job(client_id, job_id, {
        "intel_squad": {
            "scout_trend": intel_squad.get("scout_trend", {}),
            "analista_nicho": intel_squad.get("analista_nicho", {}),
            "curador_formato": intel_squad.get("curador_formato", {}),
            "curador_visual": intel_squad.get("curador_visual", {}),
            "archivist": intel_squad.get("archivist", {}),
            "contrarian": intel_squad.get("contrarian", {}),
            "sintese_executiva": intel_squad.get("sintese_executiva", {}),
            "provider": intel_squad.get("provider"),
            "attempt": intel_squad.get("attempt"),
            "contingency_used": intel_squad.get("contingency_used", False),
        }
    })
    job = get_job(client_id, job_id)
    war_room = _run_war_room(client_id, job, plan, cs, aud, top_past[:3])

    prompt = f"""Voce e Toguro, especialista em inteligencia de mercado e angulos estrategicos.
{ctx}{flags_str}
BRIEFING: {job.get('briefing','')}
TIPO DE CONTEUDO: {job.get('tipo','')}

MESA_DE_GUERRA_DECIDIU:
angulo_base: {war_room.get('angulo_final', '')}
tese: {war_room.get('tese', '')}
direcao_copy: {war_room.get('direcao_copy', '')}
direcao_visual: {war_room.get('direcao_visual', '')}
conflitos: {' | '.join(war_room.get('conflitos', []))}
{performance_memory_block}

Sua funcao nao e inventar do zero.
Sua funcao e desenvolver EXATAMENTE 3 angulos derivados desta decisao central, mantendo a mesma tese e aumentando especificidade, tensao e prova.

Gere EXATAMENTE 3 angulos estrategicos explorando tensoes DIFERENTES dentro da mesma tese.

Priorize angulos nao-obvios:
- Custo oculto nao calculado (financeiro, tempo, dependencia de plataforma)
- Perda de controle ou autonomia
- Dado que vai contra o senso comum do nicho
- Identidade ("que tipo de negocio voce quer ser")
- Comparacao humilhante/reveladora que o publico nunca fez

Evite: beneficio generico, motivacao, "voce pode conseguir".

Para cada angulo, entregue EXATAMENTE neste formato (sem texto extra):

ANGULO 1
nome: (titulo curto â€” max 5 palavras)
tensao: (dor ou perda explorada â€” 1 frase direta)
mecanismo: (como o conteudo trabalha esta tensao â€” 1 frase)
headline_exemplo: (headline usando este angulo â€” max 10 palavras, sem ponto final)
por_que_funciona: (motivo especifico para este nicho â€” 1 frase)
score_estimado: (1-10 baseado em potencial de conversao para este publico)

ANGULO 2
nome: ...
tensao: ...
mecanismo: ...
headline_exemplo: ...
por_que_funciona: ...
score_estimado: ...

ANGULO 3
nome: ...
tensao: ...
mecanismo: ...
headline_exemplo: ...
por_que_funciona: ...
score_estimado: ..."""

    provider_candidates = _get_provider_candidates("analise", include_alt_provider=True)
    primary_provider = provider_candidates[0]
    angle_attempt_logs = []
    last_result = {"provider_used": None, "erro": None, "output": ""}
    text = ""
    angles = []
    result = {"provider_used": None, "fallback_used": False, "erro": None}
    for attempt in range(1, 4):
        current_text = ""
        current_angles = []
        current_result = {"provider_used": None, "fallback_used": False, "erro": None}
        for provider_name in provider_candidates:
            if provider_name == primary_provider:
                current_result = _invoke("analise", prompt)
            else:
                current_result = _invoke_specific_provider(provider_name, prompt)
            current_text = current_result.get("output", "") or ""
            current_angles = _parse_angles_extended(current_text)
            current_angles = _rank_and_recommend(current_angles, job, cs, aud, top_past[:3])
            angle_attempt_logs.append({
                "attempt": attempt,
                "provider_requested": provider_name,
                "provider_used": current_result.get("provider_used"),
                "erro": _summarize_provider_error(current_result.get("erro")) if current_result.get("erro") else None,
                "output_chars": len(current_text),
                "angles_count": len(current_angles),
                "best_score": current_angles[0].get("score_final", current_angles[0].get("score_estimado", 0)) if current_angles else 0,
                "best_angle": current_angles[0].get("nome", "") if current_angles else "",
            })
            _persist_attempt_log(
                jdir,
                "angles_attempts.json",
                job,
                client_id,
                angle_attempt_logs,
                {
                    "performance_memory_loaded": {
                        "good_examples": len(memory_good),
                        "bad_examples": len(memory_bad),
                    }
                },
            )
            if current_angles:
                text = current_text
                angles = current_angles
                result = current_result
                break
        if angles:
            break
        last_result = current_result

    provider_failures_only = all(
        entry.get("erro") and not entry.get("output_chars")
        for entry in angle_attempt_logs
    ) if angle_attempt_logs else False
    if not angles and provider_failures_only:
        angles = _rank_and_recommend(_build_angles_contingency(war_room), job, cs, aud, top_past[:3])
        text = "ANGULOS_CONTINGENCIA_LOCAL"
        result = {
            "provider_used": "contingencia_local",
            "fallback_used": True,
            "erro": _summarize_provider_error(last_result.get("erro")),
        }
        _persist_attempt_log(
            jdir,
            "angles_attempts.json",
            job,
            client_id,
            angle_attempt_logs,
            {
                "contingency_used": True,
                "performance_memory_loaded": {
                    "good_examples": len(memory_good),
                    "bad_examples": len(memory_bad),
                },
            },
        )

    update_job(client_id, job_id, {
        "angulos": angles,
        "angulos_raw": text,
        "angulos_gerados_em": _ts(),
        "angulos_provider": result.get("provider_used"),
        "pipeline": {
            "version": PIPELINE_VERSION,
            "stage": "angulos_gerados",
            "origem_da_execucao": "geracao_angulos",
            "updated_at": _ts(),
        },
        "intel_squad": {
            "scout_trend": intel_squad.get("scout_trend", {}),
            "analista_nicho": intel_squad.get("analista_nicho", {}),
            "curador_formato": intel_squad.get("curador_formato", {}),
            "curador_visual": intel_squad.get("curador_visual", {}),
            "archivist": intel_squad.get("archivist", {}),
            "contrarian": intel_squad.get("contrarian", {}),
            "sintese_executiva": intel_squad.get("sintese_executiva", {}),
            "provider": intel_squad.get("provider"),
            "attempt": intel_squad.get("attempt"),
            "contingency_used": intel_squad.get("contingency_used", False),
        },
        "mesa_guerra": {
            "angulo_final": war_room.get("angulo_final", ""),
            "tese": war_room.get("tese", ""),
            "direcao_copy": war_room.get("direcao_copy", ""),
            "direcao_visual": war_room.get("direcao_visual", ""),
            "conflitos": war_room.get("conflitos", []),
            "provider": war_room.get("provider"),
            "attempt": war_room.get("attempt"),
            "contingency_used": war_room.get("contingency_used", False),
        },
        "plano_execucao": plan.to_dict(),
        "performance_memory_context": {
            "good_examples": len(memory_good),
            "bad_examples": len(memory_bad),
        },
    })
    record_client_pipeline_state(
        client_id,
        etapa_atual="angulos_gerados",
        etapas_concluidas=["cliente_criado", "auditoria_consolidada", "job_criado", "angulos_gerados"],
        origem_da_execucao="geracao_angulos",
        job_id=job_id,
        proximo_passo_sugerido="Executar o job com o angulo recomendado.",
    )

    return {
        "angulos": angles,
        "intel_squad": intel_squad,
        "mesa_guerra": war_room,
        "plano": plan.to_dict(),
        "raw": text,
        "provider": result.get("provider_used"),
        "fallback": result.get("fallback_used", False),
        "attempt_logs": angle_attempt_logs,
    }


def _parse_angles_extended(text: str) -> list:
    """Parseia Ã¢ngulos com campos extras (score_estimado, por_que_funciona)."""
    angles = []
    blocks = re.split(r'ANGULO \d+', text, flags=re.IGNORECASE)
    for block in blocks[1:]:
        angulo = {}
        for field in ["nome", "tensao", "mecanismo", "headline_exemplo",
                       "por_que_funciona", "score_estimado"]:
            m = re.search(
                rf'{field}:\s*(.+?)(?=\n(?:nome|tensao|mecanismo|headline_exemplo|por_que_funciona|score_estimado|ANGULO)|$)',
                block, re.IGNORECASE | re.DOTALL
            )
            if m:
                val = m.group(1).strip().split('\n')[0].strip()
                angulo[field] = val
        if angulo.get("nome"):
            # Normaliza score
            try:
                angulo["score_estimado"] = int(re.search(r'\d+', angulo.get("score_estimado", "5")).group())
            except Exception:
                angulo["score_estimado"] = 5
            angles.append(angulo)
    return angles[:3]


def _rank_and_recommend(angles: list, job: dict, client_summary: dict, audit_summary: dict, past_top: list) -> list:
    """Ranqueia angulos por potencial real de conversao e marca recomendado."""
    for angle in angles:
        evaluation = _score_angle_conversion_potential(angle, job, client_summary, audit_summary, past_top)
        angle["score_modelo"] = angle.get("score_estimado", 5)
        angle["score_final"] = evaluation["score_conversao"]
        angle["score_breakdown"] = evaluation["score_breakdown"]
        angle["copy_direcao"] = evaluation["copy_direcao"]
        angle["motivo_recomendacao"] = evaluation["motivo"]

    ranked = sorted(
        angles,
        key=lambda a: (a.get("score_final", 0), a.get("score_modelo", 0)),
        reverse=True,
    )

    for i, angle in enumerate(ranked):
        angle["recomendado"] = i == 0
    return ranked


def _angles_above_threshold(angles: list) -> bool:
    return bool(angles and angles[0].get("score_final", 0) >= ANGLE_SCORE_MIN)


def _build_angles_contingency(war_room: dict) -> list:
    base_angle = war_room.get("angulo_final", "")
    tese = war_room.get("tese", "")
    direcao_copy = war_room.get("direcao_copy", "")
    direcao_visual = war_room.get("direcao_visual", "")
    conflitos = war_room.get("conflitos", [])
    return [
        {
            "nome": "Custo invisivel recorrente",
            "tensao": tese or base_angle,
            "mecanismo": direcao_copy or "Tornar a perda recorrente concreta e comparavel.",
            "headline_exemplo": "Quanto voce perde por cliente fiel?",
            "por_que_funciona": conflitos[0] if conflitos else "Transforma a tese em prova especifica e acionavel.",
            "score_estimado": 8,
        },
        {
            "nome": "Dependencia que reduz margem",
            "tensao": base_angle or tese,
            "mecanismo": "Comparar o valor que sai da operacao com o valor que ficaria no canal direto.",
            "headline_exemplo": "Sua margem evapora no canal errado",
            "por_que_funciona": conflitos[1] if len(conflitos) > 1 else "Forca contraste entre dependencia e controle.",
            "score_estimado": 8,
        },
        {
            "nome": "Visual de confronto direto",
            "tensao": tese or base_angle,
            "mecanismo": direcao_visual or "Usar um contraste visual unico para tornar a perda imediata.",
            "headline_exemplo": "O numero que o iFood leva de voce",
            "por_que_funciona": conflitos[2] if len(conflitos) > 2 else "Aproxima a decisao visual da tensao comercial.",
            "score_estimado": 8,
        },
    ]


# â”€â”€â”€ ExecuÃ§Ã£o do job â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def run_job(
    client_id: str,
    job_id: str,
    angle_index: int = None,
    angle_snapshot: dict = None,
    visual_replay_raw_output: str = "",
) -> dict:
    """Executa job como pipeline real: Bruxo -> Toguro -> Copy -> Visual -> Output."""
    from studio.studio_manager import get_job, update_job, _job_dir
    from studio.bruxo_orchestrator import build_plan

    job = get_job(client_id, job_id)
    tipo = job.get("tipo")

    saved_plan_dict = job.get("plano_execucao")
    if saved_plan_dict:
        plan = build_plan(client_id, job)
        plan.contextos_extras = []
    else:
        plan = build_plan(client_id, job)

    runners = {
        "carrossel": _run_carrossel,
        "post_estatico": _run_post_estatico,
        "reel_pack": _run_reel_pack,
    }

    runner = runners.get(tipo)
    if not runner:
        return {"erro": f"Tipo de job desconhecido: {tipo}"}

    jdir = _job_dir(client_id, job_id)
    os.makedirs(jdir, exist_ok=True)
    validation_path = os.path.join(jdir, "output_validation.json")

    _persist_handoff(
        jdir, 0, "bruxo_plan",
        {
            "agentes": plan.agentes if plan else [],
            "skills_por_agente": plan.skills_por_agente if plan else {},
            "flags": plan.flags if plan else [],
            "decisoes": plan.decisoes if plan else [],
            "profundidade": plan.profundidade if plan else "completa",
        },
        client_id, job,
    )

    frozen_angle = angle_snapshot or {}
    if frozen_angle:
        job_updates = {
            "angulos": [frozen_angle],
            "angulos_raw": "ANGLE_SNAPSHOT_OVERRIDE",
            "angulos_provider": "snapshot_override",
        }
        update_job(client_id, job_id, job_updates)
        job = get_job(client_id, job_id)

    angle_attempts = []
    if job.get("angulos"):
        initial_best = (job.get("angulos") or [{}])[0]
        angle_attempts.append({
            "attempt": 0,
            "best_score": initial_best.get("score_final", initial_best.get("score_estimado", 0)),
            "best_angle": initial_best.get("nome", ""),
            "source": "snapshot_override" if frozen_angle else "job_cache",
        })

    if not frozen_angle:
        for attempt in range(1, ANGLE_MAX_ATTEMPTS + 1):
            angulos = job.get("angulos", [])
            if _angles_above_threshold(angulos):
                break
            generated = generate_angles(client_id, job_id)
            job = get_job(client_id, job_id)
            generated_angles = generated.get("angulos", []) or job.get("angulos", [])
            best = generated_angles[0] if generated_angles else {}
            angle_attempts.append({
                "attempt": attempt,
                "best_score": best.get("score_final", best.get("score_estimado", 0)),
                "best_angle": best.get("nome", ""),
                "source": generated.get("provider"),
            })

    angulos = job.get("angulos", [])
    if not _angles_above_threshold(angulos):
        best = angulos[0] if angulos else {}
        failure_validation = _build_failure_validation(
            "angles",
            f"Toguro abaixo do threshold minimo: melhor angulo {best.get('score_final', best.get('score_estimado', 0))}/{ANGLE_SCORE_MIN}",
            {
                "angles": {
                    "ok": False,
                    "threshold_minimo": ANGLE_SCORE_MIN,
                    "attempts": angle_attempts,
                    "best_angle": best,
                    "validated_at": _ts(),
                }
            },
        )
        _write_json_file(jdir, "output_validation.json", failure_validation)
        raise ValueError(f"Toguro abaixo do threshold minimo: {best.get('score_final', best.get('score_estimado', 0))}/{ANGLE_SCORE_MIN}")

    if angulos and angle_index is None:
        angle_index = next((i for i, item in enumerate(angulos) if item.get("recomendado")), 0)
    if angulos and angle_index is not None and not (0 <= angle_index < len(angulos)):
        raise ValueError("angle_index invalido para este job.")

    intel_squad = job.get("intel_squad", {})
    if intel_squad:
        _persist_handoff(
            jdir, 1, "intel_squad",
            intel_squad,
            client_id, job,
        )

    mesa_guerra = job.get("mesa_guerra", {})
    if mesa_guerra:
        _persist_handoff(
            jdir, 2, "mesa_guerra",
            mesa_guerra,
            client_id, job,
        )

    if angulos:
        _persist_handoff(
            jdir, 3, "toguro_angles",
            {
                "angulos": angulos,
                "selected_index": angle_index,
                "provider": job.get("angulos_provider"),
                "snapshot_override": bool(frozen_angle),
                "threshold_minimo": ANGLE_SCORE_MIN,
                "attempts": angle_attempts,
            },
            client_id, job,
        )

    angle = angulos[angle_index] if angulos and angle_index is not None else None
    if angle_index is not None:
        update_job(client_id, job_id, {"angulo_selecionado": angle_index})

    ctx = _build_context(client_id, job, plan)
    update_job(client_id, job_id, {
        "status": "executando",
        "pipeline": {
            "version": PIPELINE_VERSION,
            "angle_index": angle_index,
            "stage": "executando",
            "origem_da_execucao": "run_job",
            "started_at": _ts(),
        },
    })
    record_client_pipeline_state(
        client_id,
        etapa_atual="job_executando",
        etapas_concluidas=["cliente_criado", "auditoria_consolidada", "job_criado", "angulos_gerados"],
        origem_da_execucao="run_job",
        job_id=job_id,
        proximo_passo_sugerido="Aguardando conclusao da execucao do job.",
    )

    try:
        if tipo == "post_estatico":
            result = runner(
                ctx,
                job,
                jdir,
                angle,
                plan,
                client_id,
                visual_replay_raw_output=visual_replay_raw_output,
            )
        else:
            result = runner(ctx, job, jdir, angle, plan, client_id)
        updated_job = update_job(client_id, job_id, {
            "status": "concluido",
            "executado_em": _ts(),
            "outputs": result.get("outputs", {}),
            "modelo_usado": result.get("modelo_usado"),
            "pipeline": {
                "version": PIPELINE_VERSION,
                "angle_index": angle_index,
                "stage": "concluido",
                "completed_at": _ts(),
                "handoffs": result.get("handoffs", []),
                "validation": result.get("validation", {}),
            },
        })
        record_client_pipeline_state(
            client_id,
            etapa_atual="job_concluido",
            etapas_concluidas=["cliente_criado", "auditoria_consolidada", "job_criado", "angulos_gerados", "job_concluido"],
            origem_da_execucao="run_job",
            job_id=job_id,
            proximo_passo_sugerido="Revisar outputs no Preview ou registrar resultado operacional.",
        )
        executive_summary = _build_executive_summary(client_id, updated_job, jdir, status_override="aprovado")
        updated_outputs = dict(result.get("outputs", {}))
        updated_outputs["executive_summary"] = "executive_summary.json"
        updated_outputs["media_decision"] = "media_decision.json"
        update_job(client_id, job_id, {
            "outputs": updated_outputs,
            "executive_summary_file": "executive_summary.json",
            "executive_status": executive_summary.get("status_final"),
            "executive_confidence": executive_summary.get("confianca"),
            "media_decision_file": "media_decision.json",
            "media_launch_priority": _read_json_file(jdir, "media_decision.json").get("launch_priority"),
            "media_campaign_recommendation": _read_json_file(jdir, "media_decision.json").get("campaign_recommendation"),
            "media_next_action": _read_json_file(jdir, "media_decision.json").get("next_action"),
        })
        result["outputs"] = updated_outputs
        result["executive_summary"] = "executive_summary.json"
        result["executive_status"] = executive_summary.get("status_final")
        result["executive_confidence"] = executive_summary.get("confianca")
        return result
    except Exception as e:
        tb_text = traceback.format_exc()
        existing_validation = {}
        if os.path.exists(validation_path):
            try:
                with open(validation_path, encoding="utf-8") as f:
                    existing_validation = json.load(f)
            except Exception:
                existing_validation = {}
        if isinstance(e, QualityGateRejected):
            failure_validation = _build_failure_validation("quality_gate", str(e), e.validation or existing_validation)
            failure_validation["quality_gate"] = e.gate_result
            _write_json_file(jdir, "output_validation.json", failure_validation)
            updated_job = update_job(client_id, job_id, {
                "status": "reprovado_quality_gate",
                "erro": str(e),
                "pipeline": {
                    "version": PIPELINE_VERSION,
                    "stage": "reprovado_quality_gate",
                    "failed_at": _ts(),
                    "erro": str(e),
                    "validation": failure_validation,
                },
            })
            record_client_pipeline_state(
                client_id,
                etapa_atual="job_reprovado_quality_gate",
                etapas_concluidas=["cliente_criado", "auditoria_consolidada", "job_criado", "angulos_gerados"],
                origem_da_execucao="run_job",
                job_id=job_id,
                proximo_passo_sugerido="Corrigir auditoria ou briefing e reexecutar a partir da auditoria.",
            )
            executive_summary = _build_executive_summary(client_id, updated_job, jdir, status_override="reprovado_quality_gate", error_message=str(e))
            update_job(client_id, job_id, {
                "executive_summary_file": "executive_summary.json",
                "executive_status": executive_summary.get("status_final"),
                "executive_confidence": executive_summary.get("confianca"),
                "media_decision_file": "media_decision.json",
                "media_launch_priority": _read_json_file(jdir, "media_decision.json").get("launch_priority"),
                "media_campaign_recommendation": _read_json_file(jdir, "media_decision.json").get("campaign_recommendation"),
                "media_next_action": _read_json_file(jdir, "media_decision.json").get("next_action"),
            })
            _record_job_error(client_id, job_id, str(e), e.__class__.__name__, tb_text, jdir)
            return {
                "erro": str(e),
                "erro_tipo": e.__class__.__name__,
                "erro_traceback": tb_text,
                "erro_traceback_file": "last_error_traceback.txt",
                "quality_gate": e.gate_result,
                "executive_summary": "executive_summary.json",
            }
        failure_stage = existing_validation.get("stage") or "pipeline"
        _record_job_error(client_id, job_id, str(e), e.__class__.__name__, tb_text, jdir)
        failure_validation = _build_failure_validation(failure_stage, str(e), existing_validation)
        _write_json_file(jdir, "output_validation.json", failure_validation)
        updated_job = update_job(client_id, job_id, {
            "status": "erro",
            "erro": str(e),
            "pipeline": {
                "version": PIPELINE_VERSION,
                "stage": "erro",
                "failed_at": _ts(),
                "erro": str(e),
                "validation": failure_validation,
            },
        })
        record_client_pipeline_state(
            client_id,
            etapa_atual="job_erro",
            etapas_concluidas=["cliente_criado", "auditoria_consolidada", "job_criado"],
            origem_da_execucao="run_job",
            job_id=job_id,
            proximo_passo_sugerido="Ajustar a etapa intermediaria e reexecutar a partir da auditoria.",
        )
        executive_summary = _build_executive_summary(client_id, updated_job, jdir, status_override="erro", error_message=str(e))
        update_job(client_id, job_id, {
            "executive_summary_file": "executive_summary.json",
            "executive_status": executive_summary.get("status_final"),
            "executive_confidence": executive_summary.get("confianca"),
            "media_decision_file": "media_decision.json",
            "media_launch_priority": _read_json_file(jdir, "media_decision.json").get("launch_priority"),
            "media_campaign_recommendation": _read_json_file(jdir, "media_decision.json").get("campaign_recommendation"),
            "media_next_action": _read_json_file(jdir, "media_decision.json").get("next_action"),
        })
        return {
            "erro": str(e),
            "erro_tipo": e.__class__.__name__,
            "erro_traceback": tb_text,
            "erro_traceback_file": "last_error_traceback.txt",
        }


# â”€â”€â”€ Runners por tipo â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _run_carrossel(ctx: str, job: dict, jdir: str, angle: dict, plan, client_id: str) -> dict:
    """TotÃ³ (copy) â†’ Neymar (visual + prompts de imagem via Antigravity) â†’ CapitÃ£o (revisÃ£o)."""
    ang_block = _format_angle(angle)
    copy_decision = _build_copy_decision_block(angle)
    war_room_copy = _build_war_room_copy_block(job)
    skill_copy = _get_skill_block(plan, "toto")
    copy_contract = _fixed_copy_contract_block()
    identity = _load_identity_context(client_id)
    identity_block = _identity_prompt_block(identity)

    # â”€â”€ TotÃ³: copy dos slides â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    copy_prompt = f"""Voce e Toto, especialista em copy de alta conversao.
{ctx}
{ang_block}
{copy_decision}
{war_room_copy}
{skill_copy}
{identity_block}
{QUALITY_RULES}
Crie CARROSSEL para Instagram â€” 6 a 8 slides.

Estrutura:
- Slide 1 (CAPA): headline de alto contraste â€” tensao direta. Max 8 palavras. Zero explicacao.
- Slides 2-5: desenvolvimento progressivo â€” dado, comparacao especifica, antes/depois, insight
- Slide penultimo: virada â€” o momento que muda a perspectiva
- Slide final: CTA â€” acao unica, consequencia direta da dor explorada

HEADLINE: (headline-mÃ£e do carrossel, derivada do angulo, max 8 palavras)
CTA: (acao exata, unica e consequencia direta da tensao)

VISUAL_BRIEF:
- cena: (cena central concreta do carrossel; proibido genÃ©rico)
- composicao: (hierarquia visual e distribuiÃ§Ã£o dos elementos)
- estilo_visual: (direÃ§Ã£o visual alinhada ao brand.json; citar cores/fontes)
- estilo_visual: (tipo de imagem, iluminacao, contraste e cor; alinhado ao brand.json; citar cores/fontes)

Para cada slide entregue EXATAMENTE neste formato:
SLIDE N | TITULO: ... | CORPO: (max 3 linhas, 7 palavras por linha) | OBS_VISUAL: (1 frase)

LEGENDA_INSTAGRAM: (max 2000 chars â€” primeira linha = hook â€” emojis estrategicos â€” hashtags no final)
CTA: (frase exata)

HEADLINE_VARIACOES:
- (variacao 1)
- (variacao 2)

CTA_VARIACOES:
- (variacao 1)
- (variacao 2)

SEO_KEYWORDS_PRINCIPAIS:
- (keyword 1)
- (keyword 2)
- (keyword 3)

SEO_KEYWORDS_SECUNDARIAS:
- (keyword secundaria 1)
- (keyword secundaria 2)
- (keyword secundaria 3)

HASHTAGS:
- hashtag1
- hashtag2
- hashtag3"""
    copy_prompt += _fixed_copy_contract_block()

    copy_result = _invoke_with_retries("copy", copy_prompt, attempts=3, include_alt_provider=True)
    _persist_attempt_log(jdir, "copy_attempts.json", job, client_id, copy_result.get("attempt_logs", []), {"copy_stage": "carrossel"})
    copy_text = copy_result.get("output", "") or ""
    if not copy_text:
        raise ValueError(
            f"Copy Agent falhou: provider={copy_result.get('provider_used') or copy_result.get('provider_requested') or 'n/a'} | erro={copy_result.get('erro', 'sem resposta')}"
        )
    structure_validation = _validate_copy_structure(copy_text)
    for attempt in range(1, 3):
        if structure_validation["ok"]:
            break
        only_visual_brief_incomplete = (
            not structure_validation["missing_blocks"]
            and structure_validation["incomplete_blocks"]
            and all(item.startswith("VISUAL_BRIEF.") for item in structure_validation["incomplete_blocks"])
        )
        if only_visual_brief_incomplete:
            retry = _repair_visual_brief_only(copy_text, structure_validation["issues"])
        else:
            retry = _retry_copy_if_needed(copy_prompt, copy_text, structure_validation["issues"], attempt)
        copy_text = retry["text"]
        copy_result = retry["raw"]
        if not copy_text:
            break
        structure_validation = _validate_copy_structure(copy_text)
    copy_text, seo = _ensure_copy_seo(copy_text, client_id, job, angle)
    if not structure_validation["ok"]:
        validation = _build_failure_validation("copy", "Falha de estrutura do copy", {"copy_structure": structure_validation})
        _write_json_file(jdir, "output_validation.json", validation)
        raise ValueError("Falha de estrutura do copy: " + " | ".join(structure_validation["issues"]))
    copy_validation = _validate_copy_contract(copy_text, "carrossel", angle, client_id, job)
    if not copy_validation["ok"]:
        validation = _build_failure_validation("copy", "Falha de validacao de copy", {"copy_structure": structure_validation, "copy": copy_validation})
        _write_json_file(jdir, "output_validation.json", validation)
        raise ValueError("Falha de validacao de copy: " + " | ".join(copy_validation["issues"]))

    # â”€â”€ Neymar: visual brief + prompts de imagem (Antigravity/cheap_model) â”€
    visual_prompt = f"""Voce e Neymar, diretor de arte para Instagram.
{ctx}
{ang_block}
{identity_block}
ROTEIRO (resumo):
{copy_text[:500]}

VISUAL BRIEF â€” um bloco por slide:

SLIDE N:
- alinhamento_brand: (como a identidade da marca foi aplicada; citar cores, fontes ou posicionamento)
- fundo: (cor exata ou textura â€” priorize cores da marca)
- tipografia: (estilo, peso, cor de destaque)
- elemento_visual: (especifico â€” nao "uma foto bonita")
- energia: (baixa / media / alta)

PROMPTS DE GERACAO (para o Slide 1 â€” capa):
PROMPT_MIDJOURNEY: (prompt completo em ingles â€” estilo, composicao, lighting, --ar 1:1 --v 6)
PROMPT_DALLE: (prompt em ingles para DALL-E 3 â€” cinematografico e especifico)
PROMPT_SD: (prompt Stable Diffusion)
NEGATIVE_PROMPT: blurry, text, watermark, low quality, distorted face, extra limbs

Slide 1: energia MAXIMA. Slide final: cor de contraste forte para CTA. Safe zone 80px."""

    visual_result = _invoke("arte", visual_prompt)
    visual_text = visual_result.get("output", "")
    if not visual_text:
        raise ValueError(
            f"Visual Agent falhou: provider={visual_result.get('provider_used') or visual_result.get('provider_requested') or 'n/a'} | erro={visual_result.get('erro', 'sem resposta')}"
        )

    # â”€â”€ CapitÃ£o: revisÃ£o de coerÃªncia â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    revisao_prompt = f"""Voce e Capitao Nascimento, revisor critico.
{ctx}
{ang_block}
COPY:
{copy_text[:800]}

3 criterios:

1. COERENCIA_ANGULO: explora a tensao de verdade ou desvia para generico?
STATUS: APROVADO / AJUSTE / REPROVADO
NOTA: (1-2 frases)

2. QUALIDADE_HOOK: slide 1 para o scroll? Especifico ou vago?
STATUS: APROVADO / AJUSTE / REPROVADO
NOTA: (1-2 frases)

3. FORCA_CTA: CTA e consequencia do argumento?
STATUS: APROVADO / AJUSTE / REPROVADO
NOTA: (1-2 frases)

VEREDICTO_FINAL: APROVADO | APROVADO_COM_AJUSTES | REPROVADO
AJUSTE_PRIORITARIO: (1 acao especifica se necessario)"""

    revisao_result = _invoke("revisao", revisao_prompt)
    revisao_text = revisao_result.get("output", "") or "Revisao nao executada."

    # â”€â”€ Salvar outputs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    _write(jdir, "copy_slides.md", copy_text)
    _write(jdir, "visual_brief.md", visual_text)
    _write(jdir, "revisao_capitao.md", revisao_text)

    legenda = _extract_block(copy_text, "LEGENDA_INSTAGRAM:") or _extract_block(copy_text, "LEGENDA INSTAGRAM:")
    cta = _extract_block(copy_text, "CTA:")
    copy_headline = _clean_value_line(_extract_block(copy_text, "HEADLINE:"))
    copy_visual_brief = _extract_block(copy_text, "VISUAL_BRIEF:") or _extract_block(copy_text, "VISUAL BRIEF:")
    _write(jdir, "legenda.md", legenda or copy_text[-400:])
    _write(jdir, "cta.md", cta or "")

    # slides_resumidos.json â€” estruturado para Canva/automacoes
    slides_json = _parse_slides(copy_text)
    _write_json_file(jdir, "slides_resumidos.json", {"slides": slides_json, "gerado_em": _ts()})

    img_prompts = _extract_image_prompts(visual_text)
    if not img_prompts:
        raise ValueError("Visual Agent nao retornou prompts de imagem validos.")
    img_prompts["_fallback"] = False

    visual_direction = copy_visual_brief or (slides_json[0]["observacao_visual"] if slides_json else "")
    creative_summary = _build_creative_summary(
        client_id=client_id,
        job=job,
        angle=angle,
        headline=copy_headline or (slides_json[0]["headline"] if slides_json else ""),
        subheadline=slides_json[0]["corpo"] if slides_json else "",
        cta=cta or "",
        visual_direction=visual_direction,
        prompt_primary=img_prompts.get("prompt_dalle") or img_prompts.get("prompt_midjourney") or "",
        seo=seo,
        aspect_ratio="1:1",
        extra={"slides": len(slides_json), "legenda": legenda[:180] if legenda else ""},
    )
    standardized_prompts = _standardize_image_prompts(img_prompts, creative_summary, "1:1", "visual")
    validation = _validate_image_contract(creative_summary, standardized_prompts)
    validation["copy_structure"] = structure_validation
    validation["copy"] = copy_validation
    visual_identity_validation = _validate_visual_identity_usage(visual_text, identity)
    validation["visual_identity"] = visual_identity_validation
    if not visual_identity_validation["ok"]:
        validation["issues"].extend(visual_identity_validation["issues"])
        validation["ok"] = False
    if not validation["ok"]:
        validation = _build_failure_validation("visual", "Falha de validacao visual", validation)
        _write_json_file(jdir, "output_validation.json", validation)
        raise ValueError("Falha de validacao visual: " + " | ".join(validation["issues"]))

    _write_json_file(jdir, "creative_summary.json", creative_summary)
    _write_json_file(jdir, "image_prompts.json", standardized_prompts)
    _write_json_file(jdir, "output_validation.json", validation)

    handoffs = []
    handoffs.append(_persist_handoff(
        jdir, 3, "copy",
        {
            "headline": creative_summary.get("headline", ""),
            "cta": creative_summary.get("cta", ""),
            "seo": seo,
            "slides": slides_json,
            "provider": copy_result.get("provider_used", "n/a"),
        },
        client_id, job,
    )["stage"])
    handoffs.append(_persist_handoff(
        jdir, 4, "visual",
        {
            "visual_brief_file": "visual_brief.md",
            "creative_summary_file": "creative_summary.json",
            "image_prompts_file": "image_prompts.json",
            "validation_file": "output_validation.json",
            "provider": visual_result.get("provider_used", "n/a"),
        },
        client_id, job,
    )["stage"])

    # GeraÃ§Ã£o de imagem real (capa do carrossel â€” slide 1)
    img_gen = _generate_image(jdir, "output_image.png", standardized_prompts, "1:1")
    handoffs.append(_persist_handoff(
        jdir, 5, "output",
        {
            "arquivo": "output_image.png",
            "validation_ok": validation["ok"],
            "provider": img_gen.get("provider_used"),
            "fallback": img_gen.get("fallback_used"),
        },
        client_id, job,
    )["stage"])

    arquivos = ["copy_slides.md", "slides_resumidos.json", "creative_summary.json", "visual_brief.md",
                "revisao_capitao.md", "legenda.md", "cta.md", "image_prompts.json", "output_validation.json", "manifest.json"]
    if os.path.exists(os.path.join(jdir, "output_image.png")):
        arquivos.insert(0, "output_image.png")

    manifest = {
        "job_id": job["id"], "tipo": "carrossel", "angulo": angle, "gerado_em": _ts(),
        "modelos": {
            "copy": copy_result.get("provider_used", "n/a"),
            "visual": visual_result.get("provider_used", "n/a"),
            "revisao": revisao_result.get("provider_used", "n/a"),
        },
        "imagem_gerada": {
            "arquivo": "output_image.png",
            "provider_used": img_gen["provider_used"],
            "model_used": img_gen["model_used"],
            "fallback_used": img_gen["fallback_used"],
            "error": img_gen.get("error"),
        },
        "validation": validation,
        "plano_agentes": plan.agentes if plan else [],
        "flags_bruxo": plan.flags if plan else [],
        "arquivos": arquivos,
    }
    _write_json_file(jdir, "manifest.json", manifest)

    return {
        "outputs": {
            "copy": "copy_slides.md",
            "slides_json": "slides_resumidos.json",
            "creative_summary": "creative_summary.json",
            "visual": "visual_brief.md",
            "image_prompts": "image_prompts.json",
            "validation": "output_validation.json",
            "revisao": "revisao_capitao.md",
            "legenda": "legenda.md",
            "output_image": "output_image.png",
            "slide_01": "output_image.png",
        },
        "modelo_usado": f"copy:{copy_result.get('provider_used')} | visual:{visual_result.get('provider_used')} | revisao:{revisao_result.get('provider_used')}",
        "fallbacks": {"imagem": img_gen["fallback_used"]},
        "imagem_gerada": img_gen,
        "handoffs": handoffs,
        "validation": validation,
    }


def _build_post_estatico_prompt(ctx: str, angle: dict, job: dict, plan, client_id: str, quality_feedback: str = "") -> tuple[str, str, str, dict]:
    ang_block = _format_angle(angle)
    copy_decision = _build_copy_decision_block(angle)
    war_room_copy = _build_war_room_copy_block(job)
    skill_copy = _get_skill_block(plan, "toto")
    copy_contract = _fixed_copy_contract_block()
    identity = _load_identity_context(client_id)
    identity_block = _identity_prompt_block(identity)
    prompt = f"""Voce e Toto e Neymar - copy e arte para Instagram.
{ctx}
{ang_block}
{copy_decision}
{war_room_copy}
{skill_copy}
{identity_block}
{QUALITY_RULES}
Crie POST ESTATICO para Instagram (1080x1080).

Objetivo:
- transformar a decisao da Mesa de Guerra em uma peca estatica de alto contraste
- manter coerencia total entre angulo, headline, CTA e VISUAL_BRIEF
- traduzir DIRECAO_VISUAL em execucao concreta, sem inventar conceito novo

Orientacoes do post:
- HEADLINE: max 8 palavras
- SUBTEXTO: opcional, max 1 linha
- CTA_CRIATIVO: opcional, max 4 palavras
- LEGENDA_INSTAGRAM: primeira linha forte, legenda completa e hashtags no final
- CTA: acao exata e coerente com a headline e com o angulo
- VISUAL_BRIEF: preencha somente os 4 subcampos obrigatorios e de forma executavel

{copy_contract}"""
    if quality_feedback:
        prompt += quality_feedback
    return prompt, war_room_copy, identity_block, identity


def _execute_post_estatico_copy_cycle(
    ctx: str,
    job: dict,
    jdir: str,
    angle: dict,
    plan,
    client_id: str,
    quality_feedback: str = "",
    quality_attempt: int = 1,
    visual_replay_raw_output: str = "",
) -> dict:
    prompt, war_room_copy, identity_block, identity = _build_post_estatico_prompt(
        ctx, angle, job, plan, client_id, quality_feedback=quality_feedback
    )
    replay_used = bool((visual_replay_raw_output or "").strip())
    if replay_used:
        result = _build_visual_replay_result(visual_replay_raw_output)
    else:
        result = _invoke_with_retries("copy", prompt, attempts=3)
    _persist_attempt_log(jdir, "copy_attempts.json", job, client_id, result.get("attempt_logs", []), {"copy_stage": "post_estatico", "quality_attempt": quality_attempt})
    text = result.get("output", "") or ""
    if not text:
        raise ValueError(
            f"Copy Agent falhou: provider={result.get('provider_used') or result.get('provider_requested') or 'n/a'} | erro={result.get('erro', 'sem resposta')}"
        )
    structure_validation = _validate_copy_structure(text)
    for attempt in range(1, 3):
        if structure_validation["ok"]:
            break
        only_visual_brief_incomplete = (
            not structure_validation["missing_blocks"]
            and structure_validation["incomplete_blocks"]
            and all(item.startswith("VISUAL_BRIEF.") for item in structure_validation["incomplete_blocks"])
        )
        if only_visual_brief_incomplete:
            retry = _repair_visual_brief_only(text, structure_validation["issues"], war_room_copy, identity_block)
        else:
            retry = _retry_copy_if_needed(prompt, text, structure_validation["issues"], attempt)
        text = retry["text"]
        result = retry["raw"]
        _persist_attempt_log(jdir, "copy_attempts.json", job, client_id, result.get("attempt_logs", []), {"retry_used": True, "quality_attempt": quality_attempt})
        if not text:
            break
        structure_validation = _validate_copy_structure(text)
    provider_raw_output = text
    text, seo = _ensure_copy_seo(text, client_id, job, angle)
    partial_visual_brief = _extract_block(text, "VISUAL_BRIEF:") or _extract_block(text, "VISUAL BRIEF:") or ""
    if not structure_validation["ok"]:
        _persist_visual_generation_trace(
            jdir=jdir,
            job=job,
            cycle={
                "provider_result": result,
                "visual_prompt": prompt,
                "provider_raw_output": provider_raw_output,
                "visual_brief": partial_visual_brief,
                "replay_used": replay_used,
                "identity": identity,
                "summary": {
                    "visual_direction": partial_visual_brief,
                },
            },
            angle=angle,
            client_id=client_id,
            gate_result={},
            quality_attempt=quality_attempt,
            failure_reason="Falha de estrutura do copy: " + " | ".join(structure_validation["issues"]),
        )
        validation = _build_failure_validation("copy", "Falha de estrutura do copy", {"copy_structure": structure_validation})
        _write_json_file(jdir, "output_validation.json", validation)
        raise ValueError("Falha de estrutura do copy: " + " | ".join(structure_validation["issues"]))
    copy_validation = _validate_copy_contract(text, "post_estatico", angle, client_id, job)
    if not copy_validation["ok"]:
        _persist_visual_generation_trace(
            jdir=jdir,
            job=job,
            cycle={
                "provider_result": result,
                "visual_prompt": prompt,
                "provider_raw_output": provider_raw_output,
                "visual_brief": partial_visual_brief,
                "replay_used": replay_used,
                "identity": identity,
                "summary": {
                    "visual_direction": partial_visual_brief,
                },
            },
            angle=angle,
            client_id=client_id,
            gate_result={},
            quality_attempt=quality_attempt,
            failure_reason="Falha de validacao de copy: " + " | ".join(copy_validation["issues"]),
        )
        validation = _build_failure_validation("copy", "Falha de validacao de copy", {"copy_structure": structure_validation, "copy": copy_validation})
        _write_json_file(jdir, "output_validation.json", validation)
        raise ValueError("Falha de validacao de copy: " + " | ".join(copy_validation["issues"]))

    visual_brief = partial_visual_brief
    _write(jdir, "conceito_e_copy.md", text)
    _write(jdir, "legenda.md", _extract_block(text, "LEGENDA_INSTAGRAM:") or _extract_block(text, "LEGENDA INSTAGRAM:") or "")
    _write(jdir, "cta.md", _extract_block(text, "CTA:") or "")
    _write(jdir, "visual_brief.md", visual_brief or "")

    img_prompts = _extract_image_prompts(text)
    if not img_prompts:
        img_prompts = _fallback_image_prompts(angle, ctx)
    else:
        img_prompts["_fallback"] = False

    summary = _build_creative_summary(
        client_id=client_id,
        job=job,
        angle=angle,
        headline=_clean_value_line(_extract_block(text, "HEADLINE:")),
        subheadline=_clean_value_line(_extract_block(text, "SUBTEXTO:")),
        cta=_clean_value_line(_extract_block(text, "CTA:")),
        mood="",
        visual_direction=visual_brief,
        prompt_primary=img_prompts.get("prompt_dalle", img_prompts.get("prompt_midjourney", "")),
        seo=seo,
        aspect_ratio="1:1",
    )
    mood_match = re.search(r'mood:\s*(.+)', visual_brief or "", re.IGNORECASE)
    if mood_match:
        summary["mood"] = mood_match.group(1).strip()
    if not summary.get("creative_id"):
        summary["creative_id"] = _resolve_creative_id()

    standardized_prompts = _standardize_image_prompts(img_prompts, summary, "1:1", "copy_visual")
    validation = _validate_image_contract(summary, standardized_prompts)
    validation["copy_structure"] = structure_validation
    validation["copy"] = copy_validation
    visual_identity_validation = _validate_visual_identity_usage(text, identity)
    validation["visual_identity"] = visual_identity_validation
    if not visual_identity_validation["ok"]:
        validation["issues"].extend(visual_identity_validation["issues"])
        validation["ok"] = False
    if not validation["ok"]:
        _persist_visual_generation_trace(
            jdir=jdir,
            job=job,
            cycle={
                "provider_result": result,
                "visual_prompt": prompt,
                "provider_raw_output": provider_raw_output,
                "visual_brief": visual_brief,
                "replay_used": replay_used,
                "identity": identity,
                "summary": summary,
            },
            angle=angle,
            client_id=client_id,
            gate_result={},
            quality_attempt=quality_attempt,
            failure_reason="Falha de validacao visual: " + " | ".join(validation["issues"]),
        )
        validation = _build_failure_validation("visual", "Falha de validacao visual", validation)
        _write_json_file(jdir, "output_validation.json", validation)
        raise ValueError("Falha de validacao visual: " + " | ".join(validation["issues"]))

    _write_json_file(jdir, "creative_summary.json", summary)
    _write_json_file(jdir, "image_prompts.json", standardized_prompts)
    _write_json_file(jdir, "output_validation.json", validation)
    return {
        "provider_result": result,
        "visual_prompt": prompt,
        "provider_raw_output": provider_raw_output,
        "replay_used": replay_used,
        "seo": seo,
        "summary": summary,
        "prompts": standardized_prompts,
        "validation": validation,
        "visual_brief": visual_brief,
        "identity": identity,
    }

# Single active post_estatico path. Live and replay diverge only inside the copy cycle.
def _run_post_estatico(
    ctx: str,
    job: dict,
    jdir: str,
    angle: dict,
    plan,
    client_id: str,
    visual_replay_raw_output: str = "",
) -> dict:
    from studio.studio_manager import get_job

    quality_history = []
    quality_feedback = ""
    current_angle = angle
    cycle = None

    for quality_attempt in range(1, 3):
        cycle = _execute_post_estatico_copy_cycle(
            ctx,
            job,
            jdir,
            current_angle,
            plan,
            client_id,
            quality_feedback=quality_feedback,
            quality_attempt=quality_attempt,
            visual_replay_raw_output=visual_replay_raw_output,
        )
        summary = cycle["summary"]
        creative_id = _require_creative_id(summary, "copy_summary")
        gate_result = _run_quality_gate(
            headline=summary.get("headline", ""),
            subheadline=summary.get("subheadline", ""),
            cta=summary.get("cta", ""),
            visual_brief=cycle.get("visual_brief", ""),
            creative_summary=summary,
            angle=current_angle,
            client_context=cycle.get("identity", {}).get("cliente", {}),
            client_id=client_id,
            attempt=quality_attempt,
        )
        save_creative_performance(
            client_id=client_id,
            job_id=job.get("id"),
            headline=summary.get("headline", ""),
            angle=current_angle,
            score_quality_gate=gate_result.get("score", 0),
            status=gate_result.get("decisao", ""),
            extra={
                "creative_id": creative_id,
                "_id_recovered": bool(summary.get("_id_recovered", False)),
                "quality_attempt": quality_attempt,
                "job_type": job.get("tipo", ""),
                "approved": gate_result.get("approved", False),
                "critical_failures": gate_result.get("diagnostico", {}).get("critical_failures", []),
            },
        )
        quality_history.append(gate_result)
        cycle["validation"]["quality_gate"] = gate_result
        _write_json_file(jdir, "output_validation.json", cycle["validation"])
        _persist_quality_gate(
            jdir,
            gate_result,
            history=quality_history,
            extra={"headline": summary.get("headline", ""), "cta": summary.get("cta", ""), "provider_used": cycle["provider_result"].get("provider_used")},
        )
        _persist_visual_audit_trace(
            jdir=jdir,
            job=job,
            cycle=cycle,
            angle=current_angle,
            client_id=client_id,
            gate_result=gate_result,
            quality_attempt=quality_attempt,
        )
        _persist_visual_generation_trace(
            jdir=jdir,
            job=job,
            cycle=cycle,
            angle=current_angle,
            client_id=client_id,
            gate_result=gate_result,
            quality_attempt=quality_attempt,
        )
        if gate_result["approved"]:
            break
        if quality_attempt >= 2:
            rejected_validation = _build_failure_validation("quality_gate", "Quality Gate reprovado", cycle["validation"])
            rejected_validation["quality_gate"] = gate_result
            _write_json_file(jdir, "output_validation.json", rejected_validation)
            raise QualityGateRejected(gate_result, rejected_validation)

        refreshed_job = get_job(client_id, job.get("id"))
        togguro_retry = _rerun_toguro_for_quality_gate(client_id, refreshed_job, gate_result)
        current_angle = togguro_retry.get("angle") or current_angle
        quality_feedback = _build_quality_gate_feedback_block(gate_result)

    summary = cycle["summary"]
    prompts = cycle["prompts"]
    validation = cycle["validation"]
    result = cycle["provider_result"]
    validation["quality_gate"] = quality_history[-1]
    _write_json_file(jdir, "output_validation.json", validation)

    handoffs = []
    handoffs.append(_persist_handoff(
        jdir, 3, "copy",
        {
            "headline": summary.get("headline", ""),
            "cta": summary.get("cta", ""),
            "seo": cycle["seo"],
            "provider": result.get("provider_used", "n/a"),
        },
        client_id, job,
    )["stage"])
    handoffs.append(_persist_handoff(
        jdir, 4, "visual",
        {
            "creative_summary_file": "creative_summary.json",
            "image_prompts_file": "image_prompts.json",
            "validation_file": "output_validation.json",
        },
        client_id, job,
    )["stage"])
    handoffs.append(_persist_handoff(
        jdir, 5, "quality_gate",
        {
            "quality_gate_file": "quality_gate.json",
            "approved": quality_history[-1].get("approved"),
            "score": quality_history[-1].get("score"),
            "tentativa": quality_history[-1].get("tentativa"),
        },
        client_id, job,
    )["stage"])

    img_gen = _generate_image(
        jdir,
        "output_image.png",
        prompts,
        "1:1",
        allow_placeholder=bool(cycle.get("replay_used")),
    )
    handoffs.append(_persist_handoff(
        jdir, 6, "output",
        {
            "arquivo": "output_image.png",
            "validation_ok": validation["ok"],
            "provider": img_gen.get("provider_used"),
            "fallback": img_gen.get("fallback_used"),
        },
        client_id, job,
    )["stage"])

    arquivos_post = ["conceito_e_copy.md", "creative_summary.json", "visual_brief.md", "quality_gate.json", "audit_visual_trace.json", "audit_visual_generation_trace.json", "legenda.md", "cta.md", "image_prompts.json", "output_validation.json", "manifest.json"]
    if os.path.exists(os.path.join(jdir, "output_image.png")):
        arquivos_post.insert(0, "output_image.png")

    manifest = {
        "job_id": job["id"], "tipo": "post_estatico", "angulo": current_angle, "gerado_em": _ts(),
        "modelo_usado": result.get("provider_used", "n/a"),
        "replay_used": bool(cycle.get("replay_used")),
        "quality_gate": quality_history[-1],
        "imagem_gerada": {
            "arquivo": "output_image.png",
            "provider_used": img_gen["provider_used"],
            "model_used": img_gen["model_used"],
            "fallback_used": img_gen["fallback_used"],
            "error": img_gen.get("error"),
        },
        "validation": validation,
        "plano_agentes": plan.agentes if plan else [],
        "arquivos": arquivos_post,
    }
    _write_json_file(jdir, "manifest.json", manifest)

    return {
        "outputs": {
            "copy": "conceito_e_copy.md",
            "creative_summary": "creative_summary.json",
            "visual": "visual_brief.md",
            "quality_gate": "quality_gate.json",
            "audit_visual_trace": "audit_visual_trace.json",
            "audit_visual_generation_trace": "audit_visual_generation_trace.json",
            "image_prompts": "image_prompts.json",
            "validation": "output_validation.json",
            "output_image": "output_image.png",
            "post": "output_image.png",
        },
        "modelo_usado": result.get("provider_used", "n/a"),
        "imagem_gerada": img_gen,
        "handoffs": handoffs,
        "validation": validation,
    }


def _run_reel_pack(ctx: str, job: dict, jdir: str, angle: dict, plan, client_id: str) -> dict:
    """TotÃ³ (roteiro) â†’ Neymar (thumbnail via Antigravity) â†’ CapitÃ£o (hook+CTA)."""
    ang_block = _format_angle(angle)
    copy_decision = _build_copy_decision_block(angle)
    skill_reel = _get_skill_block(plan, "neymar")
    identity = _load_identity_context(client_id)
    identity_block = _identity_prompt_block(identity)

    # â”€â”€ TotÃ³: roteiro â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    roteiro_prompt = f"""Voce e Toto e Neymar â€” copy e direcao de Reels.
{ctx}
{ang_block}
{copy_decision}
{skill_reel}
{identity_block}
{QUALITY_RULES}
Crie REEL PACK completo â€” 25-35 segundos.

HOOK: (frase que para o scroll â€” explore a tensao imediatamente â€” max 12 palavras)

HEADLINE: (headline principal do reel, derivada do angulo, max 8 palavras)
CTA: (acao exata, unica e consequencia direta da tensao)

ROTEIRO:
[00:00-00:03] HOOK: ... [PUNCH]
[00:03-00:08] TENSAO: ... [SFX]
[00:08-00:15] DADO: ...
[00:15-00:22] VIRADA: ...
[00:22-00:28] CTA: ... [PUNCH]

VISUAL_BRIEF:
- cena: (thumbnail/cena central concreta; proibido generico)
- composicao: (hierarquia visual da thumb/cena)
- estilo_visual: (direcao visual alinhada ao brand.json; citar cores/fontes)
- alinhamento_brand: (como brand.json foi aplicado)

CAPTIONS_SRT:
1
00:00:00,000 --> 00:00:02,400
HOOK EM CAPS

2
00:00:02,400 --> 00:00:05,000
texto aqui

DESCRICAO_POST: (legenda completa â€” hook na primeira linha â€” emojis â€” hashtags no final)
CTA_FINAL: (acao exata â€” 1 linha)"""

    roteiro_prompt += _fixed_copy_contract_block()
    roteiro_result = _invoke_with_retries("copy", roteiro_prompt, attempts=3, include_alt_provider=True)
    _persist_attempt_log(jdir, "copy_attempts.json", job, client_id, roteiro_result.get("attempt_logs", []), {"copy_stage": "reel_pack"})
    roteiro_text = roteiro_result.get("output", "") or ""
    if not roteiro_text:
        raise ValueError(
            f"Copy Agent falhou: provider={roteiro_result.get('provider_used') or roteiro_result.get('provider_requested') or 'n/a'} | erro={roteiro_result.get('erro', 'sem resposta')}"
        )
    structure_validation = _validate_copy_structure(roteiro_text)
    for attempt in range(1, 3):
        if structure_validation["ok"]:
            break
        only_visual_brief_incomplete = (
            not structure_validation["missing_blocks"]
            and structure_validation["incomplete_blocks"]
            and all(item.startswith("VISUAL_BRIEF.") for item in structure_validation["incomplete_blocks"])
        )
        if only_visual_brief_incomplete:
            retry = _repair_visual_brief_only(roteiro_text, structure_validation["issues"])
        else:
            retry = _retry_copy_if_needed(roteiro_prompt, roteiro_text, structure_validation["issues"], attempt)
        roteiro_text = retry["text"]
        roteiro_result = retry["raw"]
        if not roteiro_text:
            break
        structure_validation = _validate_copy_structure(roteiro_text)
    roteiro_text, seo = _ensure_copy_seo(roteiro_text, client_id, job, angle)
    if not structure_validation["ok"]:
        validation = _build_failure_validation("copy", "Falha de estrutura do copy", {"copy_structure": structure_validation})
        _write_json_file(jdir, "output_validation.json", validation)
        raise ValueError("Falha de estrutura do copy: " + " | ".join(structure_validation["issues"]))
    copy_validation = _validate_copy_contract(roteiro_text, "reel_pack", angle, client_id, job)
    if not copy_validation["ok"]:
        validation = _build_failure_validation("copy", "Falha de validacao de copy", {"copy_structure": structure_validation, "copy": copy_validation})
        _write_json_file(jdir, "output_validation.json", validation)
        raise ValueError("Falha de validacao de copy: " + " | ".join(copy_validation["issues"]))

    hook_extraido = _extract_block(roteiro_text, "HOOK:") or roteiro_text[:120]

    # SRT: sempre garantir saida valida
    captions_raw = _extract_block(roteiro_text, "CAPTIONS_SRT:")
    if not captions_raw or len(captions_raw) < 20:
        captions_raw = _fallback_srt(roteiro_text)

    # â”€â”€ Neymar: thumbnail (Antigravity) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    thumb_prompt = f"""Voce e Neymar, diretor de arte especialista em thumbnails.
{ctx}
{ang_block}
{identity_block}
HOOK: {hook_extraido[:150]}

THUMBNAIL (1080x1350 retrato 4:5):
- conceito: (tensao capturada visualmente)
- elemento_principal: (o que ocupa 60%+ da imagem)
- texto_na_thumb: (max 5 palavras â€” funciona sem contexto)
- expressao_facial: (se pessoa â€” emocao que amplifica o hook)
- cores_dominantes: (3 cores â€” marca + contraste)

PROMPT_MIDJOURNEY: (ingles â€” fotografico ou ilustrativo â€” lighting â€” expressao â€” --ar 4:5 --v 6)
PROMPT_DALLE: (ingles â€” DALL-E 3 â€” cinematografico)
NEGATIVE_PROMPT: blurry, text, watermark, low quality, extra limbs"""

    thumb_result = _invoke("arte", thumb_prompt)
    thumb_text = thumb_result.get("output", "")
    if not thumb_text:
        raise ValueError(
            f"Visual Agent falhou na thumbnail: provider={thumb_result.get('provider_used') or thumb_result.get('provider_requested') or 'n/a'} | erro={thumb_result.get('erro', 'sem resposta')}"
        )

    # â”€â”€ CapitÃ£o: hook + CTA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    revisao_prompt = f"""Voce e Capitao Nascimento.
{ctx}
{ang_block}
HOOK: {hook_extraido[:200]}
CTA: {(_extract_block(roteiro_text, 'CTA:') or _extract_block(roteiro_text, 'CTA_FINAL:'))[:100]}

2 criterios criticos:

1. HOOK: para o scroll? Especifico, urgente, tensao real?
STATUS: APROVADO / AJUSTE / REPROVADO
NOTA: (1-2 frases)
HOOK_ALTERNATIVO: (se ajuste â€” 1 opcao mais forte)

2. CTA: consequencia do argumento? Acao unica?
STATUS: APROVADO / AJUSTE / REPROVADO
NOTA: (1-2 frases)

VEREDICTO_FINAL: APROVADO | APROVADO_COM_AJUSTES | REPROVADO"""

    revisao_result = _invoke("revisao", revisao_prompt)
    revisao_text = revisao_result.get("output", "") or "Revisao nao executada."

    # â”€â”€ Salvar outputs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    _write(jdir, "roteiro.md", roteiro_text)
    _write(jdir, "captions.srt", captions_raw)
    _write(jdir, "hook.txt", hook_extraido.strip())
    _write(jdir, "thumbnail_visual_brief.md", thumb_text)
    _write(jdir, "revisao_capitao.md", revisao_text)
    _write(jdir, "descricao_post.md", _extract_block(roteiro_text, "DESCRICAO_POST:") or "")
    _write(jdir, "cta.md", _extract_block(roteiro_text, "CTA:") or _extract_block(roteiro_text, "CTA_FINAL:") or "")

    # thumbnail_text.txt â€” texto da thumbnail isolado
    thumb_text_line = ""
    m = re.search(r'texto_na_thumb:\s*(.+)', thumb_text, re.IGNORECASE)
    if m:
        thumb_text_line = m.group(1).strip()
    _write(jdir, "thumbnail_text.txt", thumb_text_line or hook_extraido[:40])

    img_prompts = _extract_image_prompts(thumb_text)
    if not img_prompts:
        raise ValueError("Visual Agent nao retornou prompts validos para thumbnail.")
    img_prompts["_fallback"] = False

    creative_summary = _build_creative_summary(
        client_id=client_id,
        job=job,
        angle=angle,
        headline=_clean_value_line(_extract_block(roteiro_text, "HEADLINE:")) or _clean_value_line(hook_extraido),
        subheadline=_clean_value_line(_extract_block(roteiro_text, "CTA:") or _extract_block(roteiro_text, "CTA_FINAL:")),
        cta=_clean_value_line(_extract_block(roteiro_text, "CTA:") or _extract_block(roteiro_text, "CTA_FINAL:")),
        visual_direction=_extract_block(roteiro_text, "VISUAL_BRIEF:") or _extract_block(roteiro_text, "VISUAL BRIEF:") or thumb_text,
        prompt_primary=img_prompts.get("prompt_dalle", img_prompts.get("prompt_midjourney", "")),
        seo=seo,
        aspect_ratio="4:5",
        extra={"thumbnail_text": thumb_text_line or hook_extraido[:40]},
    )
    standardized_prompts = _standardize_image_prompts(img_prompts, creative_summary, "4:5", "thumbnail")
    validation = _validate_image_contract(creative_summary, standardized_prompts)
    validation["copy_structure"] = structure_validation
    validation["copy"] = copy_validation
    visual_identity_validation = _validate_visual_identity_usage(thumb_text, identity)
    validation["visual_identity"] = visual_identity_validation
    if not visual_identity_validation["ok"]:
        validation["issues"].extend(visual_identity_validation["issues"])
        validation["ok"] = False
    if not validation["ok"]:
        validation = _build_failure_validation("visual", "Falha de validacao visual", validation)
        _write_json_file(jdir, "output_validation.json", validation)
        raise ValueError("Falha de validacao visual: " + " | ".join(validation["issues"]))

    _write_json_file(jdir, "creative_summary.json", creative_summary)
    _write_json_file(jdir, "image_prompts.json", standardized_prompts)
    _write_json_file(jdir, "output_validation.json", validation)

    handoffs = []
    handoffs.append(_persist_handoff(
        jdir, 3, "copy",
        {
            "hook": _clean_value_line(hook_extraido),
            "cta": _clean_value_line(_extract_block(roteiro_text, "CTA:") or _extract_block(roteiro_text, "CTA_FINAL:")),
            "seo": seo,
            "provider": roteiro_result.get("provider_used", "n/a"),
        },
        client_id, job,
    )["stage"])
    handoffs.append(_persist_handoff(
        jdir, 4, "visual",
        {
            "creative_summary_file": "creative_summary.json",
            "image_prompts_file": "image_prompts.json",
            "validation_file": "output_validation.json",
            "provider": thumb_result.get("provider_used", "n/a"),
        },
        client_id, job,
    )["stage"])

    # GeraÃ§Ã£o de imagem real (thumbnail do reel â€” 4:5 retrato)
    img_gen = _generate_image(jdir, "thumb.png", standardized_prompts, "4:5")
    handoffs.append(_persist_handoff(
        jdir, 5, "output",
        {
            "arquivo": "thumb.png",
            "validation_ok": validation["ok"],
            "provider": img_gen.get("provider_used"),
            "fallback": img_gen.get("fallback_used"),
        },
        client_id, job,
    )["stage"])

    edit_manifest = {
        "stimulus_change_interval_sec": 2.4,
        "hook_window_sec": 3,
        "remove_pauses_above_sec": 0.3,
        "caption_words_per_line": 4,
        "caption_highlight_keywords": True,
        "safe_zone": {"top_px": 150, "bottom_px": 350},
        "formato": "1080x1920 vertical 9:16",
        "thumb_formato": "1080x1350 retrato 4:5",
        "checklist": [
            "Hook nos primeiros 3s â€” tensao do angulo",
            "Mudanca de estimulo a cada ~2.4s",
            "Pausas >0.3s cortadas",
            "Captions na safe zone (top150 / bot350)",
            "Keywords em CAPS nas captions",
            "CTA nos ultimos 5-7s",
            "Thumbnail gerada com image_prompts.json",
        ],
    }
    _write_json_file(jdir, "edit_manifest.json", edit_manifest)

    arquivos_reel = ["roteiro.md", "hook.txt", "captions.srt", "edit_manifest.json",
                     "creative_summary.json", "thumbnail_visual_brief.md", "thumbnail_text.txt", "image_prompts.json",
                     "output_validation.json", "descricao_post.md", "cta.md", "revisao_capitao.md", "manifest.json"]
    if os.path.exists(os.path.join(jdir, "thumb.png")):
        arquivos_reel.insert(0, "thumb.png")

    manifest = {
        "job_id": job["id"], "tipo": "reel_pack", "angulo": angle, "gerado_em": _ts(),
        "modelos": {
            "roteiro": roteiro_result.get("provider_used", "n/a"),
            "thumb": thumb_result.get("provider_used", "n/a"),
            "revisao": revisao_result.get("provider_used", "n/a"),
        },
        "imagem_gerada": {
            "arquivo": "thumb.png",
            "provider_used": img_gen["provider_used"],
            "model_used": img_gen["model_used"],
            "fallback_used": img_gen["fallback_used"],
            "error": img_gen.get("error"),
        },
        "validation": validation,
        "plano_agentes": plan.agentes if plan else [],
        "arquivos": arquivos_reel,
    }
    _write_json_file(jdir, "manifest.json", manifest)

    return {
        "outputs": {
            "roteiro": "roteiro.md",
            "hook": "hook.txt",
            "captions": "captions.srt",
            "edit_manifest": "edit_manifest.json",
            "creative_summary": "creative_summary.json",
            "thumbnail": "thumbnail_visual_brief.md",
            "thumbnail_text": "thumbnail_text.txt",
            "image_prompts": "image_prompts.json",
            "validation": "output_validation.json",
            "revisao": "revisao_capitao.md",
            "thumb": "thumb.png",
        },
        "modelo_usado": f"roteiro:{roteiro_result.get('provider_used')} | thumb:{thumb_result.get('provider_used')} | revisao:{revisao_result.get('provider_used')}",
        "fallbacks": {"imagem": img_gen["fallback_used"]},
        "imagem_gerada": img_gen,
        "handoffs": handoffs,
        "validation": validation,
    }


# â”€â”€â”€ Aprendizado (chamado pelo server) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def save_job_result(client_id: str, job_id: str, result_data: dict) -> dict:
    """Registra resultado do post com campos completos e calcula rates localmente."""
    from studio.studio_manager import get_job, update_job, _job_dir, record_client_pipeline_state

    job = get_job(client_id, job_id)
    jdir = _job_dir(client_id, job_id)

    angulos = job.get("angulos", [])
    idx = job.get("angulo_selecionado")
    angulo = angulos[idx] if idx is not None and 0 <= idx < len(angulos) else {}

    # Campos completos
    alcance      = int(result_data.get("alcance", 0))
    impressoes   = int(result_data.get("impressoes", 0))
    curtidas     = int(result_data.get("curtidas", 0))
    comentarios  = int(result_data.get("comentarios", 0))
    salvamentos  = int(result_data.get("salvamentos", 0))
    compartilhamentos = int(result_data.get("compartilhamentos", 0))
    cliques      = int(result_data.get("cliques", 0))
    conversoes   = int(result_data.get("conversoes", 0))
    cpa_value    = float(result_data.get("cpa", 0) or 0)
    roas_value   = float(result_data.get("roas", 0) or 0)

    # Rates calculados localmente
    base_er = alcance if alcance > 0 else impressoes
    engagement_rate = round(
        (curtidas + comentarios + salvamentos + compartilhamentos) / base_er * 100, 2
    ) if base_er > 0 else 0

    conversion_rate = round(conversoes / cliques * 100, 2) if cliques > 0 else 0
    ctr_rate = round(cliques / impressoes * 100, 2) if impressoes > 0 else 0

    resultado_completo = {
        "alcance": alcance,
        "impressoes": impressoes,
        "curtidas": curtidas,
        "comentarios": comentarios,
        "salvamentos": salvamentos,
        "compartilhamentos": compartilhamentos,
        "cliques": cliques,
        "conversoes": conversoes,
        "tipo_conversao": result_data.get("tipo_conversao", ""),
        "publicado_em": result_data.get("publicado_em", ""),
        "notas_operador": result_data.get("notas_operador", result_data.get("notas", "")),
        # Calculados
        "ctr_pct": ctr_rate,
        "cpa": cpa_value if cpa_value > 0 else None,
        "roas": roas_value if roas_value > 0 else None,
        "engagement_rate_pct": engagement_rate,
        "conversion_rate_pct": conversion_rate,
    }

    learning = {
        "job_id": job_id,
        "cliente_id": client_id,
        "tipo": job.get("tipo"),
        "angulo_index": idx,
        "angulo": angulo,
        "briefing": job.get("briefing", ""),
        "resultado": resultado_completo,
        "registrado_em": _ts(),
    }

    path = os.path.join(jdir, "resultado.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(learning, f, ensure_ascii=False, indent=2)

    creative_summary = _read_json_file(jdir, "creative_summary.json")
    creative_id = _require_creative_id(creative_summary, "creative_summary.json")
    quality_gate = _read_json_file(jdir, "quality_gate.json")
    save_creative_performance(
        client_id=client_id,
        job_id=job_id,
        headline=creative_summary.get("headline", ""),
        angle=angulo,
        score_quality_gate=quality_gate.get("score", 0),
        status=quality_gate.get("decisao", "resultado_registrado"),
        ctr=ctr_rate,
        cpa=resultado_completo.get("cpa"),
        extra={
            "creative_id": creative_id,
            "_id_recovered": bool(creative_summary.get("_id_recovered", False)),
            "quality_attempt": quality_gate.get("tentativa", 1),
            "resultado_registrado": True,
            "roas": resultado_completo.get("roas"),
            "engagement_rate_pct": engagement_rate,
            "conversion_rate_pct": conversion_rate,
            "publicado_em": resultado_completo.get("publicado_em", ""),
            "tipo_conversao": resultado_completo.get("tipo_conversao", ""),
        },
    )

    update_job(client_id, job_id, {"resultado_registrado": True, "resultado_em": _ts()})
    _build_portfolio_decision(client_id, recent_n=8)
    return learning


# â”€â”€â”€ Fallbacks de output â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _fallback_visual_brief(copy_summary: str, angle: dict) -> str:
    """Visual brief mÃ­nimo gerado localmente quando Antigravity falha."""
    nome = angle.get("nome", "conteudo") if angle else "conteudo"
    tensao = angle.get("tensao", "") if angle else ""
    return (
        f"[FALLBACK â€” Antigravity indisponivel. Gere o visual manualmente.]\n\n"
        f"CONCEITO VISUAL BASE:\n"
        f"- Angulo: {nome}\n"
        f"- Tensao a comunicar: {tensao}\n\n"
        f"SLIDE 1 (capa):\n"
        f"- composicao: headline centralizado, fundo escuro, elemento de impacto atras\n"
        f"- fundo: use a cor mais escura da marca ou preto\n"
        f"- tipografia: bold, cor de alto contraste (branco ou cor de destaque)\n"
        f"- elemento_visual: relacionado diretamente com a tensao do angulo\n"
        f"- energia: ALTA\n\n"
        f"SLIDES INTERMEDIARIOS:\n"
        f"- Mantenha identidade coerente com o slide 1\n"
        f"- Progressao de cor ou elemento visual conforme a tensao aumenta\n\n"
        f"SLIDE FINAL (CTA):\n"
        f"- Cor contrastante em relacao ao restante\n"
        f"- CTA isolado, legivel, sem elemento competindo\n"
    )


def _fallback_image_prompts(angle: dict, ctx: str) -> dict:
    """Prompts de imagem minimos gerados localmente quando modelo falha."""
    nome = angle.get("nome", "") if angle else ""
    tensao = angle.get("tensao", "") if angle else ""
    headline = angle.get("headline_exemplo", "") if angle else ""
    return {
        "prompt_midjourney": (
            f"high contrast editorial photo, {tensao[:60] if tensao else 'tension and conflict'}, "
            f"dark background, bold typography overlay, professional lighting, "
            f"Instagram feed format, --ar 1:1 --v 6"
        ),
        "prompt_dalle": (
            f"Professional Instagram post visual. Concept: {nome or 'contrast and tension'}. "
            f"Style: editorial, high contrast, dark background. "
            f"Element: strong central subject related to '{tensao[:80]}'. No text overlay."
        ),
        "negative_prompt": "blurry, text, watermark, low quality, distorted, extra limbs, amateur",
        "_nota": "Prompts gerados localmente como fallback. Edite conforme a identidade visual do cliente.",
        "_fallback": True,
    }


def _fallback_srt(roteiro_text: str) -> str:
    """Gera SRT minimo a partir dos timecodes do roteiro quando modelo nao entrega SRT valido."""
    srt_lines = []
    # Procura linhas com formato [HH:MM:SS-HH:MM:SS] ...
    timecode_blocks = re.findall(
        r'\[(\d{2}:\d{2}-\d{2}:\d{2})\]\s*(?:HOOK|TENSAO|DADO|VIRADA|CTA|DESENVOLVIMENTO)[:\s]*(.+?)(?=\[|\n\n|$)',
        roteiro_text, re.IGNORECASE | re.DOTALL
    )

    if not timecode_blocks:
        # Fallback plano: SRT generico de 30 segundos
        return (
            "1\n00:00:00,000 --> 00:00:05,000\n[texto do hook aqui]\n\n"
            "2\n00:00:05,000 --> 00:00:15,000\n[desenvolvimento aqui]\n\n"
            "3\n00:00:15,000 --> 00:00:25,000\n[virada aqui]\n\n"
            "4\n00:00:25,000 --> 00:00:30,000\n[CTA aqui]\n"
        )

    idx = 1
    for tc, content in timecode_blocks:
        parts = tc.split("-")
        start = f"00:{parts[0]},000"
        end   = f"00:{parts[1]},000"
        # Trunca conteudo e limpa
        text = content.strip().split('\n')[0][:60].upper()
        srt_lines.append(f"{idx}\n{start} --> {end}\n{text}\n")
        idx += 1

    return "\n".join(srt_lines)


def _parse_slides(copy_text: str) -> list:
    """Parseia slides do output do modelo para slides_resumidos.json."""
    slides = []
    # Procura padrÃ£o: SLIDE N | TITULO: ... | CORPO: ... | OBS_VISUAL: ...
    blocks = re.findall(
        r'SLIDE\s*(\d+)\s*\|?\s*TITULO:\s*(.+?)\s*\|\s*CORPO:\s*(.+?)\s*\|?\s*OBS[_\s]?VISUAL:\s*(.+?)(?=SLIDE|\Z)',
        copy_text, re.IGNORECASE | re.DOTALL
    )
    for b in blocks:
        slides.append({
            "slide": int(b[0]),
            "headline": b[1].strip(),
            "corpo": b[2].strip().replace('\n', ' '),
            "observacao_visual": b[3].strip().split('\n')[0],
        })

    # Fallback: se nao parseiou nada, cria entrada unica com o texto completo
    if not slides:
        slides.append({
            "slide": 1,
            "headline": "[parse falhou â€” ver copy_slides.md]",
            "corpo": copy_text[:300],
            "observacao_visual": "",
        })
    return slides


# â”€â”€â”€ Helpers: extraÃ§Ã£o e escrita â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _extract_prompt_section(text: str, markers: list[str]) -> str:
    normalized = (text or "").replace("\r\n", "\n")
    heading_pattern = re.compile(r"(?im)^\s*(?:#{2,3}\s*)?(?:\*\*)?PROMPT[^\n]*(?:\*\*)?\s*$")
    for match in heading_pattern.finditer(normalized):
        heading = match.group(0).lower()
        if not all(marker.lower() in heading for marker in markers):
            continue
        rest = normalized[match.end():]
        next_heading = re.search(r"(?im)^\s*(?:#{2,3}\s+\S.*$|\*\*.+?\*\*\s*$|[A-Z][A-Z _]+:)", rest)
        block = rest[:next_heading.start()] if next_heading else rest
        return _clean_extracted_block(block)
    return ""


def _extract_image_prompts(text: str) -> dict:
    """Extrai prompts de geraÃ§Ã£o de imagem do output do modelo."""
    prompts = {}
    prompts["prompt_midjourney"] = _extract_prompt_section(text, ["midjourney"])
    prompts["prompt_dalle"] = _extract_prompt_section(text, ["dall"])
    prompts["prompt_sd"] = _extract_prompt_section(text, ["stable"]) or _extract_prompt_section(text, ["sd"])
    prompts["negative_prompt"] = _extract_block(text, "NEGATIVE_PROMPT") or _extract_block(text, "NEGATIVE PROMPT")
    prompts = {k: v for k, v in prompts.items() if v}
    if prompts:
        prompts["_nota"] = "Cole estes prompts diretamente em Midjourney, DALL-E 3, ou Stable Diffusion."
    return prompts


def _generate_image(
    jdir: str,
    filename: str,
    img_prompts: dict,
    aspect_ratio: str = "1:1",
    allow_placeholder: bool = False,
) -> dict:
    """Gera imagem real via Gemini Imagen e salva no diretÃ³rio do job.

    Usa o melhor prompt disponÃ­vel em img_prompts.
    Se cair em placeholder local, trata como erro controlado.
    """
    from adapters.image_provider import generate_image_from_prompt

    prompt = (
        img_prompts.get("prompt_dalle")
        or img_prompts.get("prompt_midjourney")
        or img_prompts.get("prompt_sd")
        or ""
    )
    output_path = os.path.join(jdir, filename)
    result = generate_image_from_prompt(prompt, output_path, aspect_ratio)
    if (result.get("provider_used") == "local_placeholder" or result.get("fallback_used")) and not allow_placeholder:
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except OSError:
                pass
        raise ValueError("Geracao de imagem real indisponivel: " + str(result.get("error", "provider sem retorno real")))
    return result


def _write(jdir: str, fname: str, content: str):
    os.makedirs(jdir, exist_ok=True)
    with open(os.path.join(jdir, fname), "w", encoding="utf-8") as f:
        f.write(content)


def _write_json_file(jdir: str, fname: str, data: dict):
    os.makedirs(jdir, exist_ok=True)
    with open(os.path.join(jdir, fname), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _read_json_file(jdir: str, fname: str) -> dict:
    path = os.path.join(jdir, fname)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _normalize_status_label(status: str) -> str:
    raw = (status or "").strip().lower()
    if raw in {"concluido", "approved", "aprovado"}:
        return "aprovado"
    if raw == "reprovado_quality_gate":
        return "reprovado_quality_gate"
    return "erro"


def _executive_best_use(status_final: str, score_quality_gate: int, critical_failures: list) -> str:
    if status_final == "reprovado_quality_gate":
        return "nÃ£o vale mÃ­dia"
    if status_final == "erro":
        return "reter para nova iteraÃ§Ã£o"
    if score_quality_gate >= 85 and not critical_failures:
        return "subir como criativo principal"
    if score_quality_gate >= 70:
        return "usar como teste secundÃ¡rio"
    if score_quality_gate >= 55:
        return "reter para nova iteraÃ§Ã£o"
    return "nÃ£o vale mÃ­dia"


def _executive_confidence(status_final: str, score_quality_gate: int, quality_gate: dict) -> int:
    diagnostico = quality_gate.get("diagnostico", {}) if quality_gate else {}
    confidence = int(score_quality_gate or 0)
    if status_final == "reprovado_quality_gate":
        confidence -= 20
    if status_final == "erro":
        confidence = min(confidence, 35)
    if int(quality_gate.get("tentativa", 1) or 1) > 1:
        confidence -= 8
    confidence += int(round((diagnostico.get("top_good_similarity", 0) or 0) * 20))
    confidence -= int(round((diagnostico.get("top_bad_similarity", 0) or 0) * 35))
    return max(0, min(100, confidence))


def _summarize_retry_change(quality_gate: dict, memory: dict, job_id: str) -> str:
    history = quality_gate.get("history", []) or []
    if len(history) < 2:
        return "NÃ£o houve retry relevante."
    current_attempt = int(quality_gate.get("tentativa", len(history)) or len(history))
    current_entry = next(
        (item for item in memory.get("items", []) if item.get("job_id") == job_id and int(item.get("quality_attempt", 1) or 1) == current_attempt),
        {},
    )
    previous_entry = next(
        (item for item in memory.get("items", []) if item.get("job_id") == job_id and int(item.get("quality_attempt", 1) or 1) == current_attempt - 1),
        {},
    )
    score_before = int(history[-2].get("score", 0) or 0)
    score_after = int(history[-1].get("score", 0) or 0)
    delta = score_after - score_before
    headline_before = previous_entry.get("headline", "")
    headline_after = current_entry.get("headline", "")
    if headline_before and headline_after and headline_before != headline_after:
        return f"O retry trocou a linha principal e elevou o score de {score_before} para {score_after}."
    if delta > 0:
        return f"O retry corrigiu as falhas crÃ­ticas e elevou o score de {score_before} para {score_after}."
    return "Houve retry, mas a melhora foi limitada."


def _executive_reference_line(example: dict, fallback: str) -> str:
    if not example:
        return fallback
    headline = example.get("headline", "")
    hook_type = example.get("hook_type", "")
    if headline:
        return f"{headline} ({hook_type})".strip()
    return fallback


def _infer_funnel_stage(headline: str, cta: str, angle: dict, job: dict) -> str:
    text = " ".join([headline or "", cta or "", angle.get("tensao", ""), job.get("objetivo_job", "")]).lower()
    if any(term in text for term in ["remarketing", "volte", "recupere", "retome", "reengaje"]):
        return "remarketing"
    if any(term in text for term in ["chame", "peÃ§a", "peca", "agende", "compre", "fale", "clique", "ganhe"]):
        return "fundo"
    if any(term in text for term in ["compare", "saiba", "descubra", "entenda", "por que", "porque", "custo", "perde", "perda"]):
        return "meio"
    return "topo"


def _infer_audience_temperature(funnel_stage: str, status_final: str, score_quality_gate: int) -> str:
    if status_final != "aprovado":
        return "fria"
    if funnel_stage in {"remarketing", "fundo"}:
        return "quente"
    if score_quality_gate >= 85:
        return "morna"
    return "fria"


def _infer_fatigue_risk(top_good_similarity: float, top_bad_similarity: float) -> str:
    if top_bad_similarity >= PERFORMANCE_SIMILARITY_HIGH:
        return "alto"
    if top_good_similarity >= PERFORMANCE_SIMILARITY_HIGH:
        return "moderado"
    if top_good_similarity == 0 and top_bad_similarity == 0:
        return "baixo"
    return "baixo"


def _infer_campaign_recommendation(status_final: str, funnel_stage: str, score_quality_gate: int, critical_failures: list, fatigue_risk: str, cta: str) -> str:
    if status_final != "aprovado":
        return "nÃ£o subir"
    if fatigue_risk == "alto":
        return "retenÃ§Ã£o de criativo"
    if funnel_stage == "remarketing":
        return "remarketing"
    if funnel_stage == "fundo" and any(term in (cta or "").lower() for term in ["peÃ§a", "peca", "agende", "compre", "chame"]):
        return "aquisiÃ§Ã£o" if score_quality_gate >= 85 and not critical_failures else "validaÃ§Ã£o de oferta"
    if funnel_stage == "meio":
        return "validaÃ§Ã£o de oferta"
    return "validaÃ§Ã£o de hook"


def _infer_budget_posture(status_final: str, score_quality_gate: int, launch_priority: str) -> str:
    if status_final != "aprovado" or launch_priority == "bloquear":
        return "nÃ£o investir"
    if score_quality_gate >= 90:
        return "moderado"
    return "baixo para teste"


def _infer_launch_priority(status_final: str, score_quality_gate: int, critical_failures: list, fatigue_risk: str) -> str:
    if status_final != "aprovado":
        return "bloquear"
    if fatigue_risk == "alto":
        return "baixa"
    if score_quality_gate >= 85 and not critical_failures:
        return "alta"
    if score_quality_gate >= 70:
        return "media"
    return "baixa"


def _infer_test_type(status_final: str, funnel_stage: str, quality_gate: dict, visual_brief: str, cta: str) -> str:
    if status_final != "aprovado":
        return "nÃ£o testar"
    falhas = quality_gate.get("falhas", []) or []
    if any("visual" in failure.lower() for failure in falhas):
        return "teste de visual"
    if any("cta" in failure.lower() for failure in falhas):
        return "teste de CTA"
    if funnel_stage == "fundo" and cta:
        return "teste de oferta"
    if visual_brief and len(_tokenize(visual_brief)) < 18:
        return "teste de visual"
    return "teste de hook"


def _infer_expected_strength(status_final: str, score_quality_gate: int) -> str:
    if status_final != "aprovado":
        return "fraca"
    if score_quality_gate >= 90:
        return "muito forte"
    if score_quality_gate >= 80:
        return "forte"
    if score_quality_gate >= 70:
        return "boa"
    return "limitada"


def _infer_subniche(client_context: dict, briefing: str, headline: str, angle: dict, creative_summary: dict) -> str:
    niche = (client_context.get("nicho", "") or "").strip().lower()
    product = (client_context.get("produto", "") or "").strip().lower()
    combined = " ".join([
        niche,
        product,
        briefing or "",
        headline or "",
        angle.get("nome", ""),
        creative_summary.get("headline", ""),
    ]).lower()
    if "hamburg" in combined:
        return "hamburgueria delivery"
    if "pizza" in combined or "pizzaria" in combined:
        return "pizzaria premium" if any(term in combined for term in ["premium", "gourmet", "artesanal"]) else "pizzaria delivery"
    if "delivery" in combined:
        return "delivery local"
    if any(term in combined for term in ["trafego pago", "trÃ¡fego pago", "lead", "captaÃ§Ã£o"]):
        return "trÃ¡fego pago para negÃ³cio local"
    if any(term in combined for term in ["clinica", "clÃ­nica", "consulta"]):
        return "clÃ­nica local"
    if any(term in combined for term in ["conveniencia", "conveniÃªncia", "varejo"]):
        return "varejo de conveniÃªncia"
    if niche:
        return niche
    if product:
        return product
    return "negÃ³cio local"


def _infer_offer_type(headline: str, cta: str, angle: dict, objetivo_job: str) -> str:
    text = " ".join([headline or "", cta or "", objetivo_job or "", angle.get("tensao", ""), angle.get("mecanismo", "")]).lower()
    if any(term in text for term in ["lead", "whatsapp", "agende", "agendamento", "fale", "chame"]):
        return "captaÃ§Ã£o de lead"
    if any(term in text for term in ["compar", "vs", "mais caro", "menos", "diferenÃ§a", "diferenca", "compare"]):
        return "comparaÃ§Ã£o de custo"
    if any(term in text for term in ["perde", "perda", "drena", "some", "evapora", "oculto"]):
        return "prova de perda"
    if any(term in text for term in ["margem", "lucro", "recupere", "recuperar"]):
        return "recuperaÃ§Ã£o de margem"
    if any(term in text for term in ["autoridade", "especialista", "prova", "caso"]):
        return "reforÃ§o de autoridade"
    if any(term in text for term in ["volte", "retome", "recupere cliente", "reative"]):
        return "recuperaÃ§Ã£o de cliente"
    if any(term in text for term in ["marca", "presenÃ§a", "presenca", "relacionamento", "branding"]):
        return "branding leve"
    return "oferta direta"


def _get_decision_mode(client_context: dict, job: dict) -> str:
    """Define o grau de tolerÃ¢ncia do motor operacional.

    strict:
    - privilegia corte rÃ¡pido
    - bloqueia ou empurra para refazer quando o encaixe nÃ£o sustenta mÃ­dia

    exploratory:
    - aceita criativos medianos como teste
    - reduz o nÃ­vel de corte para explorar variaÃ§Ã£o
    """
    raw = (job.get("decision_mode") or client_context.get("decision_mode") or "").strip().lower()
    if raw in {"strict", "exploratory"}:
        return raw
    objective = " ".join([job.get("objetivo_job", ""), job.get("briefing", ""), client_context.get("objetivo", "")]).lower()
    if any(term in objective for term in ["lead", "venda", "agendamento", "pedido", "cpa", "convers"]):
        return "strict"
    return "exploratory"


def _classify_subniche_profile(client_context: dict, briefing: str, headline: str, angle: dict, creative_summary: dict) -> dict:
    """Classifica o contexto comercial em um perfil operacional.

    O motor de mÃ­dia nÃ£o trabalha sÃ³ com um rÃ³tulo de nicho.
    Ele usa:
    - macro_niche
    - subniche
    - business_model
    - ticket_level
    - decision_type
    - sales_cycle

    Esse perfil orienta deduÃ§Ã£o de urgÃªncia, tipo de oferta, leitura de funil e
    tolerÃ¢ncia de decisÃ£o.
    """
    subniche = _infer_subniche(client_context, briefing, headline, angle, creative_summary)
    combined = " ".join([
        subniche,
        (client_context.get("nicho", "") or ""),
        (client_context.get("produto", "") or ""),
        briefing or "",
        headline or "",
        creative_summary.get("headline", ""),
    ]).lower()
    profile = {
        "macro_niche": "negocio local",
        "subniche": subniche,
        "business_model": "servico_local",
        "ticket_level": "medio",
        "decision_type": "racional",
        "sales_cycle": "medio",
    }
    if any(term in combined for term in ["delivery", "hamburg", "pizza", "pizzaria", "lanche"]):
        profile.update({
            "macro_niche": "alimentacao local",
            "business_model": "delivery",
            "decision_type": "impulso",
            "sales_cycle": "curto",
            "ticket_level": "medio" if any(term in combined for term in ["premium", "gourmet", "artesanal"]) else "baixo",
        })
    elif any(term in combined for term in ["clinica", "clÃƒÂ­nica", "consulta", "tratamento"]):
        profile.update({
            "macro_niche": "saude local",
            "business_model": "agendamento",
            "decision_type": "racional",
            "sales_cycle": "medio",
            "ticket_level": "alto" if any(term in combined for term in ["implante", "cirurgia", "estetica", "estÃƒÂ©tica"]) else "medio",
        })
    elif any(term in combined for term in ["trafego pago", "trÃƒÂ¡fego pago", "lead", "captaÃƒÂ§ÃƒÂ£o", "campanha"]):
        profile.update({
            "macro_niche": "servicos de crescimento",
            "business_model": "servico",
            "decision_type": "racional",
            "sales_cycle": "medio",
            "ticket_level": "medio",
        })
    elif any(term in combined for term in ["conveniencia", "conveniÃƒÂªncia", "mercado", "varejo", "loja"]):
        profile.update({
            "macro_niche": "varejo local",
            "business_model": "loja",
            "decision_type": "recorrente",
            "sales_cycle": "curto",
            "ticket_level": "baixo",
        })
    if any(term in combined for term in ["assinatura", "mensal", "recorrencia", "recorrÃƒÂªncia"]):
        profile["decision_type"] = "recorrente"
    return profile


def _reconstruct_briefing_if_weak(client_context: dict, job: dict, performance_memory: dict, subniche_profile: dict) -> dict:
    """ReconstrÃ³i briefing quando a entrada nÃ£o sustenta decisÃ£o.

    Flags atuais:
    - briefing_generico
    - objetivo_fraco
    - oferta_ausente

    Quando alguma flag dispara, o sistema recompÃµe briefing e objetivo a partir de:
    - subnicho classificado
    - tipo de decisÃ£o comercial do contexto
    - melhor padrÃ£o jÃ¡ aprovado na PME
    - padrÃ£o ruim a evitar

    Objetivo: nÃ£o depender de input humano perfeito para tomar decisÃ£o de mÃ­dia.
    """
    briefing = (job.get("briefing", "") or "").strip()
    objetivo_job = (job.get("objetivo_job", "") or "").strip()
    weakness_flags = []
    generic_markers = {"conteudo", "post", "anuncio", "anÃƒÂºncio", "criativo", "marketing", "divulgar"}
    briefing_tokens = set(_tokenize(briefing.lower()))
    if not briefing or len(briefing_tokens) <= 5 or len(briefing_tokens.intersection(generic_markers)) >= 2:
        weakness_flags.append("briefing_generico")
    if not objetivo_job or len(_tokenize(objetivo_job.lower())) <= 2:
        weakness_flags.append("objetivo_fraco")
    if not any(term in " ".join([briefing, objetivo_job]).lower() for term in ["lead", "margem", "pedido", "agende", "whatsapp", "lucro", "perda", "oferta"]):
        weakness_flags.append("oferta_ausente")
    if not weakness_flags:
        return {
            "briefing": briefing,
            "objetivo_job": objetivo_job,
            "reconstructed": False,
            "weakness_flags": [],
        }

    best_good = {}
    best_bad = {}
    for item in performance_memory.get("entries", []) or []:
        if item.get("classification") == "bom" and not best_good:
            best_good = item
        if item.get("classification") == "ruim" and not best_bad:
            best_bad = item
        if best_good and best_bad:
            break

    offer_hint = best_good.get("offer_type") or "oferta direta"
    subniche = subniche_profile.get("subniche", "negÃƒÂ³cio local")
    if not objetivo_job:
        objetivo_job = "gerar conversÃƒÂ£o imediata" if subniche_profile.get("decision_type") == "impulso" else "validar oferta com clareza comercial"
    if not briefing:
        briefing = f"Criar peÃƒÂ§a para {subniche} com foco em {offer_hint} e CTA claro."
    else:
        briefing = f"{briefing.rstrip('.')} Foco reconstruÃƒÂ­do: {offer_hint} para {subniche} com objetivo {objetivo_job}."
    if best_bad.get("headline"):
        briefing += f" Evitar repetir padrÃƒÂ£o fraco como '{best_bad.get('headline')}'."

    return {
        "briefing": briefing.strip(),
        "objetivo_job": objetivo_job.strip(),
        "reconstructed": True,
        "weakness_flags": weakness_flags,
    }


def _infer_brand_maturity(client_context: dict, job: dict, creative_summary: dict) -> str:
    objective = " ".join([job.get("objetivo_job", ""), client_context.get("objetivo", ""), job.get("tom_especifico", "")]).lower()
    instagram = (client_context.get("instagram", "") or "").strip()
    competitors = client_context.get("concorrentes", []) or []
    if not client_context:
        return "desconhecida"
    if any(term in objective for term in ["presenÃ§a", "presenca", "relacionamento", "branding"]) and instagram:
        return "madura"
    if competitors or instagram:
        return "intermediaria"
    if creative_summary.get("headline") or job.get("briefing"):
        return "inicial"
    return "desconhecida"


def _infer_commercial_urgency(objetivo_job: str, cta: str, headline: str, offer_type: str, angle: dict) -> str:
    text = " ".join([objetivo_job or "", cta or "", headline or "", offer_type or "", angle.get("tensao", "")]).lower()
    if any(term in text for term in ["agora", "hoje", "imediat", "lead", "venda", "pedido direto", "lucro"]):
        return "alta"
    if any(term in text for term in ["consider", "descubra", "compare", "entenda", "por que", "porque", "avali"]):
        return "media"
    return "baixa"


def _score_goal_fit(job: dict, creative_summary: dict, offer_type: str, commercial_urgency: str) -> int:
    objective = " ".join([job.get("objetivo_job", ""), job.get("briefing", "")]).lower()
    headline = (creative_summary.get("headline", "") or "").lower()
    score = 55
    if any(term in objective for term in ["lead", "venda", "trÃ¡fego", "trafego", "pedido direto"]):
        if offer_type in {"captaÃ§Ã£o de lead", "recuperaÃ§Ã£o de margem", "oferta direta", "prova de perda"}:
            score += 25
        if commercial_urgency == "alta":
            score += 10
        if any(term in headline for term in ["marca", "presenÃ§a", "presenca"]) and offer_type == "branding leve":
            score -= 20
    elif any(term in objective for term in ["marca", "branding", "presenÃ§a", "presenca", "relacionamento"]):
        if offer_type == "branding leve":
            score += 20
        if commercial_urgency == "alta":
            score -= 10
    else:
        score += 5 if offer_type != "branding leve" else 0
    return max(0, min(100, score))


def _score_cta_funnel_fit(cta: str, funnel_stage: str, offer_type: str) -> int:
    cta_lower = (cta or "").lower()
    action_words = sum(1 for word in _tokenize(cta_lower) if word in CTA_ACTION_TERMS)
    score = 55
    if funnel_stage in {"fundo", "remarketing"}:
        score += 20 if action_words else -20
    elif funnel_stage == "topo":
        score += 15 if action_words <= 1 else -10
    else:
        score += 10 if action_words else 0
    if offer_type == "branding leve" and action_words > 1:
        score -= 15
    if len(_tokenize(cta_lower)) > 8:
        score -= 10
    return max(0, min(100, score))


def _score_visual_campaign_fit(visual_brief: str, funnel_stage: str, score_quality_gate: int, offer_type: str) -> int:
    visual_lower = (visual_brief or "").lower()
    score = 50 + min(25, max(0, score_quality_gate - 60))
    if any(marker in visual_lower for marker in ["contraste", "alto contraste", "cena:", "composicao:", "estilo_visual:"]):
        score += 10
    if funnel_stage == "fundo" and any(term in visual_lower for term in ["clean", "acolhedor", "suave"]):
        score -= 10
    if funnel_stage == "topo" and offer_type == "branding leve" and any(term in visual_lower for term in ["acolhedor", "minimalista", "clean"]):
        score += 8
    if any(term in visual_lower for term in ["bonito", "premium"]) and offer_type in {"captaÃ§Ã£o de lead", "oferta direta"}:
        score -= 8
    return max(0, min(100, score))


def _infer_contextual_fatigue(top_good_similarity: float, top_bad_similarity: float, subniche: str, hook_type: str, offer_type: str) -> str:
    if top_bad_similarity >= PERFORMANCE_SIMILARITY_HIGH:
        return "alto"
    if top_good_similarity >= PERFORMANCE_SIMILARITY_HIGH:
        return "moderado"
    if top_good_similarity >= 0.2 and hook_type in {"numerico", "pergunta"} and offer_type in {"prova de perda", "comparaÃ§Ã£o de custo"} and "delivery" in (subniche or ""):
        return "moderado"
    return "baixo"


def _infer_brand_performance_conflict(brand_maturity: str, offer_type: str, commercial_urgency: str, goal_fit_score: int) -> str:
    if offer_type == "branding leve" and commercial_urgency == "alta":
        return "alto"
    if brand_maturity == "inicial" and offer_type == "branding leve":
        return "alto"
    if goal_fit_score < 65:
        return "moderado"
    return "baixo"


def _infer_temperature_operational(audience_temperature: str, commercial_urgency: str, goal_fit_score: int) -> str:
    if audience_temperature == "quente" and commercial_urgency == "alta" and goal_fit_score >= 75:
        return "quente"
    if goal_fit_score >= 60:
        return "morna"
    return "fria"


def _infer_goal_visual_conflict(goal_fit_score: int, visual_campaign_fit_score: int, offer_type: str) -> str:
    if goal_fit_score < 60 and visual_campaign_fit_score < 60:
        return "alto"
    if offer_type == "branding leve" and goal_fit_score < 70:
        return "moderado"
    return "baixo"


def _build_media_decision(
    executive_summary: dict,
    quality_gate: dict,
    creative_summary: dict,
    angle: dict,
    performance_memory: dict,
    job: dict,
    client_context: dict,
) -> dict:
    headline = creative_summary.get("headline", "")
    cta = creative_summary.get("cta", "")
    visual_brief = creative_summary.get("visual_direction", "")
    status_final = executive_summary.get("status_final", "erro")
    score_quality_gate = int(executive_summary.get("score_quality_gate", 0) or 0)
    diagnostico = quality_gate.get("diagnostico", {}) or {}
    critical_failures = diagnostico.get("critical_failures", []) or []
    top_good_similarity = float(diagnostico.get("top_good_similarity", 0) or 0)
    top_bad_similarity = float(diagnostico.get("top_bad_similarity", 0) or 0)

    subniche = _infer_subniche(client_context or {}, job.get("briefing", ""), headline, angle or {}, creative_summary or {})
    offer_type = _infer_offer_type(headline, cta, angle or {}, job.get("objetivo_job", ""))
    brand_maturity = _infer_brand_maturity(client_context or {}, job or {}, creative_summary or {})
    commercial_urgency = _infer_commercial_urgency(job.get("objetivo_job", ""), cta, headline, offer_type, angle or {})
    funnel_stage = _infer_funnel_stage(headline, cta, angle or {}, job or {})
    audience_temperature = _infer_audience_temperature(funnel_stage, status_final, score_quality_gate)
    goal_fit_score = _score_goal_fit(job or {}, creative_summary or {}, offer_type, commercial_urgency)
    cta_funnel_fit_score = _score_cta_funnel_fit(cta, funnel_stage, offer_type)
    visual_campaign_fit_score = _score_visual_campaign_fit(visual_brief, funnel_stage, score_quality_gate, offer_type)
    fatigue_risk = _infer_contextual_fatigue(top_good_similarity, top_bad_similarity, subniche, _detect_hook_type(headline), offer_type)
    brand_performance_conflict = _infer_brand_performance_conflict(brand_maturity, offer_type, commercial_urgency, goal_fit_score)
    operational_temperature = _infer_temperature_operational(audience_temperature, commercial_urgency, goal_fit_score)
    goal_visual_conflict = _infer_goal_visual_conflict(goal_fit_score, visual_campaign_fit_score, offer_type)

    launch_priority = _infer_launch_priority(
        status_final,
        min(score_quality_gate, int(round((goal_fit_score + cta_funnel_fit_score + visual_campaign_fit_score) / 3))),
        critical_failures,
        fatigue_risk,
    )
    campaign_recommendation = _infer_campaign_recommendation(
        status_final, funnel_stage, goal_fit_score, critical_failures, fatigue_risk, cta
    )
    budget_posture = _infer_budget_posture(status_final, goal_fit_score, launch_priority)
    test_type = _infer_test_type(status_final, funnel_stage, quality_gate or {}, visual_brief, cta)
    expected_strength = _infer_expected_strength(status_final, int(round((score_quality_gate + goal_fit_score) / 2)))

    if status_final != "aprovado":
        next_action = "nÃ£o subir e voltar para nova iteraÃ§Ã£o"
    elif launch_priority == "alta":
        next_action = "subir agora com verba moderada e monitorar resposta"
    elif campaign_recommendation in {"validaÃ§Ã£o de hook", "validaÃ§Ã£o de oferta"}:
        next_action = "subir como teste controlado com verba baixa"
    else:
        next_action = "rodar em pÃºblico menor antes de escalar"

    if status_final != "aprovado":
        media_rationale = f"NÃ£o vale mÃ­dia para {subniche} porque o criativo ficou abaixo do nÃ­vel mÃ­nimo para subir com seguranÃ§a."
    elif brand_performance_conflict == "alto":
        media_rationale = f"NÃ£o vale acelerar em {subniche}: a peÃ§a estÃ¡ mais prÃ³xima de {offer_type} do que de conversÃ£o imediata."
    elif campaign_recommendation == "aquisiÃ§Ã£o":
        media_rationale = f"PeÃ§a forte para aquisiÃ§Ã£o em {subniche}, com urgÃªncia {commercial_urgency} e verba {budget_posture}."
    elif campaign_recommendation == "remarketing":
        media_rationale = f"Boa para remarketing em {subniche}, com mensagem especÃ­fica o bastante para pÃºblico {audience_temperature}."
    elif campaign_recommendation == "validaÃ§Ã£o de oferta":
        media_rationale = f"Forte para validaÃ§Ã£o de oferta em pÃºblico {audience_temperature}, com tensÃ£o coerente e risco de saturaÃ§Ã£o {fatigue_risk}."
    else:
        media_rationale = f"Boa para validar hook em {subniche}, mas com escala contida porque o encaixe com o objetivo ainda pede confirmaÃ§Ã£o."

    return {
        "subniche": subniche,
        "offer_type": offer_type,
        "brand_maturity": brand_maturity,
        "commercial_urgency": commercial_urgency,
        "funnel_stage": funnel_stage,
        "campaign_recommendation": campaign_recommendation,
        "audience_temperature": audience_temperature,
        "budget_posture": budget_posture,
        "launch_priority": launch_priority,
        "test_type": test_type,
        "fatigue_risk": fatigue_risk,
        "expected_strength": expected_strength,
        "goal_fit_score": goal_fit_score,
        "cta_funnel_fit_score": cta_funnel_fit_score,
        "visual_campaign_fit_score": visual_campaign_fit_score,
        "brand_performance_conflict": brand_performance_conflict,
        "media_rationale": media_rationale,
        "next_action": next_action,
        "deduction_layer": {
            "subniche": subniche,
            "offer_type": offer_type,
            "brand_maturity": brand_maturity,
            "commercial_urgency": commercial_urgency,
            "operational_temperature": operational_temperature,
            "goal_fit_score": goal_fit_score,
            "cta_funnel_fit_score": cta_funnel_fit_score,
            "visual_campaign_fit_score": visual_campaign_fit_score,
            "contextual_fatigue": fatigue_risk,
            "goal_visual_conflict": goal_visual_conflict,
            "brand_performance_conflict": brand_performance_conflict,
        },
    }


def _build_media_decision_v2(
    executive_summary: dict,
    quality_gate: dict,
    creative_summary: dict,
    angle: dict,
    performance_memory: dict,
    job: dict,
    client_context: dict,
) -> dict:
    """Motor operacional de decisÃ£o de mÃ­dia.

    NÃ£o explica o criativo; decide o que fazer com ele.

    Entradas centrais de decisÃ£o:
    - decision_mode: strict ou exploratory
    - subniche_profile: contexto comercial estruturado
    - goal_fit_score: mede aderÃªncia do criativo ao objetivo real do job
    - visual_campaign_fit_score: mede se o visual serve Ã  campanha, nÃ£o sÃ³ se estÃ¡ bonito
    - quality gate, fadiga contextual e conflito branding x performance

    SaÃ­da operacional:
    - media_next_action: subir | testar | refazer | bloquear

    Regra prÃ¡tica:
    - strict corta mais cedo
    - exploratory aceita peÃ§a mÃ©dia para teste
    - goal_fit_score baixo derruba decisÃ£o mesmo com score geral bom
    - visual_campaign_fit_score baixo reduz prioridade porque visual vendÃ¡vel Ã© parte da decisÃ£o
    """
    headline = creative_summary.get("headline", "")
    cta = creative_summary.get("cta", "")
    visual_brief = creative_summary.get("visual_direction", "")
    status_final = executive_summary.get("status_final", "erro")
    score_quality_gate = int(executive_summary.get("score_quality_gate", 0) or 0)
    diagnostico = quality_gate.get("diagnostico", {}) or {}
    critical_failures = diagnostico.get("critical_failures", []) or []
    top_good_similarity = float(diagnostico.get("top_good_similarity", 0) or 0)
    top_bad_similarity = float(diagnostico.get("top_bad_similarity", 0) or 0)

    decision_mode = _get_decision_mode(client_context or {}, job or {})
    subniche_profile = _classify_subniche_profile(client_context or {}, job.get("briefing", ""), headline, angle or {}, creative_summary or {})
    subniche = subniche_profile.get("subniche", "negÃƒÂ³cio local")
    reconstructed_briefing = _reconstruct_briefing_if_weak(client_context or {}, job or {}, performance_memory or {}, subniche_profile)
    effective_goal = reconstructed_briefing.get("objetivo_job") or job.get("objetivo_job", "")
    effective_briefing = reconstructed_briefing.get("briefing") or job.get("briefing", "")
    effective_job = dict(job or {})
    effective_job["briefing"] = effective_briefing
    effective_job["objetivo_job"] = effective_goal

    offer_type = _infer_offer_type(headline, cta, angle or {}, effective_goal)
    brand_maturity = _infer_brand_maturity(client_context or {}, job or {}, creative_summary or {})
    commercial_urgency = _infer_commercial_urgency(effective_goal, cta, headline, offer_type, angle or {})
    funnel_stage = _infer_funnel_stage(headline, cta, angle or {}, job or {})
    audience_temperature = _infer_audience_temperature(funnel_stage, status_final, score_quality_gate)
    goal_fit_score = _score_goal_fit(effective_job, creative_summary or {}, offer_type, commercial_urgency)
    cta_funnel_fit_score = _score_cta_funnel_fit(cta, funnel_stage, offer_type)
    visual_campaign_fit_score = _score_visual_campaign_fit(visual_brief, funnel_stage, score_quality_gate, offer_type)
    fatigue_risk = _infer_contextual_fatigue(top_good_similarity, top_bad_similarity, subniche, _detect_hook_type(headline), offer_type)
    brand_performance_conflict = _infer_brand_performance_conflict(brand_maturity, offer_type, commercial_urgency, goal_fit_score)
    operational_temperature = _infer_temperature_operational(audience_temperature, commercial_urgency, goal_fit_score)
    goal_visual_conflict = _infer_goal_visual_conflict(goal_fit_score, visual_campaign_fit_score, offer_type)
    decision_score = min(score_quality_gate, int(round((goal_fit_score + cta_funnel_fit_score + visual_campaign_fit_score) / 3)))

    if decision_mode == "strict":
        if status_final != "aprovado" or fatigue_risk == "alto" or decision_score < 65:
            launch_priority = "bloquear"
        elif critical_failures or decision_score < 80:
            launch_priority = "baixa"
        elif decision_score >= 88:
            launch_priority = "alta"
        else:
            launch_priority = "media"
    else:
        launch_priority = _infer_launch_priority(status_final, decision_score, critical_failures, fatigue_risk)

    campaign_recommendation = _infer_campaign_recommendation(
        status_final, funnel_stage, goal_fit_score, critical_failures, fatigue_risk, cta
    )
    budget_posture = _infer_budget_posture(status_final, goal_fit_score, launch_priority)
    test_type = _infer_test_type(status_final, funnel_stage, quality_gate or {}, visual_brief, cta)
    expected_strength = _infer_expected_strength(status_final, int(round((score_quality_gate + goal_fit_score) / 2)))

    if status_final != "aprovado" or launch_priority == "bloquear":
        media_next_action = "bloquear"
    elif decision_mode == "strict" and (decision_score < 80 or fatigue_risk == "alto" or brand_performance_conflict == "alto"):
        media_next_action = "refazer"
    elif launch_priority == "alta":
        media_next_action = "subir"
    elif campaign_recommendation in {"validaÃƒÂ§ÃƒÂ£o de hook", "validaÃƒÂ§ÃƒÂ£o de oferta"} or launch_priority in {"media", "baixa"}:
        media_next_action = "testar"
    else:
        media_next_action = "subir"

    if media_next_action == "bloquear":
        media_rationale = "nÃƒÂ£o subir. bloquear."
    elif media_next_action == "refazer":
        media_rationale = "nÃƒÂ£o subir. refazer ÃƒÂ¢ngulo."
    elif media_next_action == "subir" and campaign_recommendation == "aquisiÃƒÂ§ÃƒÂ£o":
        media_rationale = f"subir. aquisiÃƒÂ§ÃƒÂ£o em {subniche}."
    elif media_next_action == "subir":
        media_rationale = f"subir. usar em {campaign_recommendation}."
    elif brand_performance_conflict == "alto":
        media_rationale = "testar leve. criativo mais branding que performance."
    elif fatigue_risk == "alto":
        media_rationale = "testar leve. risco alto de saturaÃƒÂ§ÃƒÂ£o."
    elif top_good_similarity >= 0.2:
        media_rationale = f"testar. bom encaixe com padrÃƒÂ£o forte de {subniche}."
    elif campaign_recommendation == "remarketing":
        media_rationale = "testar. subir apenas remarketing leve."
    else:
        media_rationale = f"testar. validar oferta em {subniche}."

    if status_final != "aprovado":
        campaign_recommendation = "nÃƒÂ£o subir"
    elif media_next_action == "refazer":
        campaign_recommendation = "retenÃƒÂ§ÃƒÂ£o de criativo"

    return {
        "decision_mode": decision_mode,
        "subniche_profile": subniche_profile,
        "subniche": subniche,
        "offer_type": offer_type,
        "brand_maturity": brand_maturity,
        "commercial_urgency": commercial_urgency,
        "funnel_stage": funnel_stage,
        "campaign_recommendation": campaign_recommendation,
        "audience_temperature": audience_temperature,
        "budget_posture": budget_posture,
        "launch_priority": launch_priority,
        "test_type": test_type,
        "fatigue_risk": fatigue_risk,
        "expected_strength": expected_strength,
        "goal_fit_score": goal_fit_score,
        "cta_funnel_fit_score": cta_funnel_fit_score,
        "visual_campaign_fit_score": visual_campaign_fit_score,
        "brand_performance_conflict": brand_performance_conflict,
        "media_rationale": media_rationale,
        "next_action": media_next_action,
        "media_next_action": media_next_action,
        "deduction_layer": {
            "decision_mode": decision_mode,
            "briefing_reconstructed": reconstructed_briefing.get("reconstructed", False),
            "briefing_weakness_flags": reconstructed_briefing.get("weakness_flags", []),
            "effective_briefing": effective_briefing,
            "effective_goal": effective_goal,
            "subniche_profile": subniche_profile,
            "offer_type": offer_type,
            "brand_maturity": brand_maturity,
            "commercial_urgency": commercial_urgency,
            "operational_temperature": operational_temperature,
            "goal_fit_score": goal_fit_score,
            "cta_funnel_fit_score": cta_funnel_fit_score,
            "visual_campaign_fit_score": visual_campaign_fit_score,
            "contextual_fatigue": fatigue_risk,
            "goal_visual_conflict": goal_visual_conflict,
            "brand_performance_conflict": brand_performance_conflict,
        },
    }


def _resolve_portfolio_jobs(client_id: str, job_ids: list | None = None, recent_n: int = 6) -> list:
    """Monta o input do portfÃ³lio a partir dos jobs mais recentes ou de uma lista manual."""
    from studio.studio_manager import _job_dir, get_job, list_jobs

    selected_ids = job_ids or [item.get("id") for item in list_jobs(client_id)[:max(1, recent_n)]]
    resolved = []
    seen = set()
    for job_id in selected_ids:
        if not job_id or job_id in seen:
            continue
        seen.add(job_id)
        try:
            job = get_job(client_id, job_id)
        except FileNotFoundError:
            continue
        resolved.append({
            "job": job,
            "job_id": job_id,
            "jdir": _job_dir(client_id, job_id),
        })
    return resolved


def _compute_stability_score(history: list[dict]) -> float:
    scores = []
    for item in history or []:
        if not isinstance(item, dict):
            continue
        value = item.get("performance_score")
        try:
            if value in ("", None):
                continue
            scores.append(float(value))
        except (TypeError, ValueError):
            continue

    if len(scores) < 2:
        return 0.5

    mean_score = sum(scores) / len(scores)
    if mean_score <= 0:
        return 0.5

    variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
    std_dev = variance ** 0.5
    variation_ratio = min(std_dev / mean_score, 1.0)
    stability_score = 1.0 - variation_ratio
    return round(max(0.0, min(1.0, stability_score)), 4)


def _normalize_benchmark_text(value) -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        return ""
    return unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("ascii")


def _resolve_benchmark_profile(executive_summary: dict, media_decision: dict) -> dict:
    """Resolve benchmark operacional mÃ­nimo por nicho e objetivo."""
    subniche_profile = media_decision.get("subniche_profile", {}) or {}
    niche_context = " ".join([
        _normalize_benchmark_text(media_decision.get("subniche")),
        _normalize_benchmark_text(subniche_profile.get("subniche")),
        _normalize_benchmark_text(executive_summary.get("contexto_de_uso")),
        _normalize_benchmark_text(executive_summary.get("nicho")),
    ])
    objective_context = " ".join([
        _normalize_benchmark_text(media_decision.get("campaign_recommendation")),
        _normalize_benchmark_text(media_decision.get("offer_type")),
        _normalize_benchmark_text(media_decision.get("funnel_stage")),
        _normalize_benchmark_text(executive_summary.get("tipo_de_oferta")),
        _normalize_benchmark_text(executive_summary.get("contexto_de_uso")),
    ])

    niche = "generic"
    if any(term in niche_context for term in ["delivery", "ifood", "restaurante", "lanchonete", "food"]):
        niche = "delivery"
    elif any(term in niche_context for term in ["clinica", "odont", "medic", "estet", "saude"]):
        niche = "clinica"
    elif any(term in niche_context for term in ["ecom", "e-commerce", "ecommerce", "loja virtual", "shopify"]):
        niche = "ecom"
    elif any(term in niche_context for term in ["branding", "marca", "autoridade"]):
        niche = "branding"

    objective = "generic"
    if any(term in objective_context for term in ["alcance", "branding", "topo", "autoridade", "presenca", "awareness"]):
        objective = "alcance"
    elif any(term in objective_context for term in ["lead", "captacao", "captaÃ§Ã£o", "agendamento", "whatsapp"]):
        objective = "lead"
    elif any(term in objective_context for term in ["venda", "oferta direta", "oferta", "checkout", "compra"]):
        objective = "venda"
    elif any(term in objective_context for term in ["conversao", "conversÃ£o", "aquisicao", "aquisiÃ§Ã£o", "remarketing"]):
        objective = "conversao"

    if niche == "delivery" and objective == "generic":
        objective = "conversao"
    elif niche == "clinica" and objective == "generic":
        objective = "lead"
    elif niche == "ecom" and objective == "generic":
        objective = "venda"
    elif niche == "branding" and objective == "generic":
        objective = "alcance"

    for profile in BENCHMARK_PROFILES:
        if profile["niche"] == niche and profile["objective"] == objective:
            return dict(DEFAULT_BENCHMARK_PROFILE, **profile)
    return dict(DEFAULT_BENCHMARK_PROFILE)


def _compute_dynamic_benchmark(performance_memory: list[dict]) -> dict:
    """Calcula benchmark dinÃ¢mico a partir do histÃ³rico real do cliente."""

    def _to_float(value):
        try:
            if value in ("", None):
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    def _percentile(values: list[float], percentile: float):
        if not values:
            return None
        ordered = sorted(values)
        if len(ordered) == 1:
            return ordered[0]
        rank = (len(ordered) - 1) * percentile
        lower_idx = int(rank)
        upper_idx = min(lower_idx + 1, len(ordered) - 1)
        weight = rank - lower_idx
        lower_value = ordered[lower_idx]
        upper_value = ordered[upper_idx]
        return lower_value + ((upper_value - lower_value) * weight)

    ctr_values = []
    cpa_values = []
    roas_values = []
    valid_records = 0

    for item in performance_memory or []:
        if not isinstance(item, dict):
            continue
        ctr_value = _to_float(item.get("ctr"))
        cpa_value = _to_float(item.get("cpa"))
        roas_value = _to_float(item.get("roas"))
        if ctr_value is None and cpa_value is None and roas_value is None:
            continue
        valid_records += 1
        if ctr_value is not None:
            ctr_values.append(ctr_value)
        if cpa_value is not None and cpa_value > 0:
            cpa_values.append(cpa_value)
        if roas_value is not None and roas_value >= 0:
            roas_values.append(roas_value)

    dynamic_profile = {
        "ctr_good": _percentile(ctr_values, 0.75),
        "ctr_bad": _percentile(ctr_values, 0.25),
        "cpa_good": _percentile(cpa_values, 0.25),
        "cpa_bad": _percentile(cpa_values, 0.75),
        "roas_good": _percentile(roas_values, 0.75),
        "roas_bad": _percentile(roas_values, 0.25),
        "valid_count": valid_records,
    }

    if dynamic_profile["ctr_good"] is not None and dynamic_profile["ctr_bad"] is not None:
        if dynamic_profile["ctr_good"] <= dynamic_profile["ctr_bad"]:
            spread = abs(dynamic_profile["ctr_good"] - dynamic_profile["ctr_bad"])

            if spread < 0.01:
                dynamic_profile["ctr_good"] = None
                dynamic_profile["ctr_bad"] = None
            elif spread < 0.05:
                if dynamic_profile["ctr_good"] < dynamic_profile["ctr_bad"]:
                    dynamic_profile["ctr_good"] = None
                else:
                    dynamic_profile["ctr_bad"] = None
            else:
                if dynamic_profile["ctr_good"] < dynamic_profile["ctr_bad"]:
                    dynamic_profile["ctr_good"] = None
                else:
                    dynamic_profile["ctr_bad"] = None

    if dynamic_profile["cpa_good"] is not None and dynamic_profile["cpa_bad"] is not None:
        if dynamic_profile["cpa_good"] >= dynamic_profile["cpa_bad"]:
            spread = abs(dynamic_profile["cpa_good"] - dynamic_profile["cpa_bad"])

            if spread < 0.01:
                dynamic_profile["cpa_good"] = None
                dynamic_profile["cpa_bad"] = None
            elif spread < 0.05:
                if dynamic_profile["cpa_good"] > dynamic_profile["cpa_bad"]:
                    dynamic_profile["cpa_good"] = None
                else:
                    dynamic_profile["cpa_bad"] = None
            else:
                if dynamic_profile["cpa_good"] > dynamic_profile["cpa_bad"]:
                    dynamic_profile["cpa_good"] = None
                else:
                    dynamic_profile["cpa_bad"] = None

    if dynamic_profile["roas_good"] is not None and dynamic_profile["roas_bad"] is not None:
        if dynamic_profile["roas_good"] <= dynamic_profile["roas_bad"]:
            spread = abs(dynamic_profile["roas_good"] - dynamic_profile["roas_bad"])

            if spread < 0.01:
                dynamic_profile["roas_good"] = None
                dynamic_profile["roas_bad"] = None
            elif spread < 0.05:
                if dynamic_profile["roas_good"] < dynamic_profile["roas_bad"]:
                    dynamic_profile["roas_good"] = None
                else:
                    dynamic_profile["roas_bad"] = None
            else:
                if dynamic_profile["roas_good"] < dynamic_profile["roas_bad"]:
                    dynamic_profile["roas_good"] = None
                else:
                    dynamic_profile["roas_bad"] = None

    return dynamic_profile


def _compute_portfolio_score(executive_summary: dict, media_decision: dict) -> int:
    """Calcula score final do portfÃ³lio com performance real como driver principal.

    Ordem de decisÃ£o:
    1. Se existir dado real (CTR/CPA/ROAS), performance domina o ranking.
    2. Se nÃ£o existir dado real, cai integralmente no fallback legado.
    3. Qualidade interna continua relevante, mas nÃ£o salva criativo que performa mal.
    """

    def _to_float(value):
        try:
            if value in ("", None):
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    def _clamp_0_100(value):
        return max(0, min(100, int(round(value))))

    def _legacy_score():
        score_quality_gate = int(executive_summary.get("score_quality_gate", 0) or 0)
        goal_fit_score = int(media_decision.get("goal_fit_score", 0) or 0)
        visual_fit_score = int(media_decision.get("visual_campaign_fit_score", 0) or 0)
        status_final = executive_summary.get("status_final", "erro")
        decision_mode = media_decision.get("decision_mode", "strict")
        media_next_action = media_decision.get("media_next_action") or media_decision.get("next_action") or ""

        score = (score_quality_gate * 0.45) + (goal_fit_score * 0.35) + (visual_fit_score * 0.20)
        if status_final == "aprovado":
            score += 10
        elif status_final == "reprovado_quality_gate":
            score -= 20
        else:
            score -= 30

        if decision_mode == "strict" and media_next_action in {"subir", "testar"}:
            score += 5
        if media_next_action in {"bloquear", "refazer"}:
            score = min(score, 54)
        return _clamp_0_100(score)

    def _load_latest_performance_record(job_id: str) -> dict:
        if not job_id:
            return {}
        clients_root = os.path.join("data", "clients")
        if not os.path.exists(clients_root):
            return {}

        latest = {}
        latest_ts = ""
        for client_entry in os.listdir(clients_root):
            memory_path = os.path.join(clients_root, client_entry, "performance_memory.json")
            if not os.path.exists(memory_path):
                continue
            try:
                with open(memory_path, encoding="utf-8") as f:
                    payload = json.load(f)
            except Exception:
                continue
            for item in payload.get("items", []) or []:
                if item.get("job_id") != job_id:
                    continue
                item_ts = item.get("updated_at", "") or ""
                if not latest or item_ts >= latest_ts:
                    latest = dict(item)
                    latest["client_id"] = client_entry
                    latest_ts = item_ts
        return latest

    def _load_performance_history(client_id: str, creative_id: str) -> list[dict]:
        if not client_id or not creative_id:
            return []
        performance_memory = load_performance_memory(client_id).get("items", [])
        filtered = [item for item in performance_memory if item.get("creative_id") == creative_id]
        filtered.sort(key=lambda item: item.get("updated_at", "") or "", reverse=True)
        return filtered[:10]

    def _compute_confidence_weight(record: dict) -> float:
        """Converte volume observado em confianÃ§a contÃ­nua de 0.0 a 1.0."""
        impressoes_value = _to_float(record.get("impressoes")) or 0.0
        cliques_value = _to_float(record.get("cliques")) or 0.0
        conversoes_value = _to_float(record.get("conversoes")) or 0.0

        def _scale(value: float, low: float, mid: float, high: float) -> float:
            if value <= 0:
                return 0.0
            if value < low:
                return 0.1 * (value / max(1.0, low))
            if value >= high:
                return 1.0
            if value <= mid:
                # low -> mid: 0.1 .. 0.5
                return 0.1 + ((value - low) / max(1.0, mid - low)) * 0.4
            # mid -> high: 0.5 .. 1.0
            return 0.5 + ((value - mid) / max(1.0, high - mid)) * 0.5

        # ImpressÃµes sÃ£o a base principal de confianÃ§a.
        impressoes_conf = _scale(impressoes_value, low=300.0, mid=1000.0, high=5000.0)
        # Cliques reforÃ§am a confianÃ§a de resposta.
        cliques_conf = _scale(cliques_value, low=10.0, mid=50.0, high=250.0)
        # ConversÃµes reforÃ§am a confianÃ§a de negÃ³cio.
        conversoes_conf = _scale(conversoes_value, low=1.0, mid=5.0, high=25.0)

        confidence = (
            (impressoes_conf * 0.55) +
            (cliques_conf * 0.30) +
            (conversoes_conf * 0.15)
        )
        return max(0.0, min(1.0, round(confidence, 4)))

    def _compute_time_active(record: dict) -> float:
        """Calcula hÃ¡ quantas horas o criativo estÃ¡ ativo com base no registro de performance."""

        def _parse_ts(value):
            raw = (value or "").strip()
            if not raw:
                return None
            try:
                return datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except ValueError:
                return None

        start_dt = (
            _parse_ts(record.get("created_at"))
            or _parse_ts(record.get("publicado_em"))
            or _parse_ts(record.get("updated_at"))
        )
        end_dt = _parse_ts(record.get("updated_at")) or datetime.utcnow()

        if start_dt is None:
            return 0.0

        if getattr(start_dt, "tzinfo", None) is not None and getattr(end_dt, "tzinfo", None) is None:
            end_dt = datetime.fromisoformat(_ts().replace("Z", "+00:00"))
        elif getattr(start_dt, "tzinfo", None) is None and getattr(end_dt, "tzinfo", None) is not None:
            start_dt = start_dt.replace(tzinfo=end_dt.tzinfo)

        delta = end_dt - start_dt
        return max(0.0, round(delta.total_seconds() / 3600.0, 2))

    def _score_ctr(ctr_value: float, benchmark_profile: dict) -> int:
        if ctr_value is None:
            return 50
        ctr_good = max(_to_float(benchmark_profile.get("ctr_good")) or DEFAULT_BENCHMARK_PROFILE["ctr_good"], 0.1)
        ctr_bad = max(_to_float(benchmark_profile.get("ctr_bad")) or DEFAULT_BENCHMARK_PROFILE["ctr_bad"], 0.05)
        if ctr_value >= ctr_good * 1.82:
            return 100
        if ctr_value >= ctr_good * 1.36:
            return 92
        if ctr_value >= ctr_good:
            return 82
        if ctr_value >= ((ctr_good + ctr_bad) / 2):
            return 70
        if ctr_value >= ctr_bad * 1.375:
            return 55
        if ctr_value >= ctr_bad:
            return 35
        if ctr_value >= ctr_bad * 0.625:
            return 15
        return 0

    def _score_cpa(cpa_value: float, benchmark_profile: dict) -> int:
        if cpa_value is None:
            return 50
        cpa_good = max(_to_float(benchmark_profile.get("cpa_good")) or DEFAULT_BENCHMARK_PROFILE["cpa_good"], 1.0)
        cpa_bad = max(_to_float(benchmark_profile.get("cpa_bad")) or DEFAULT_BENCHMARK_PROFILE["cpa_bad"], cpa_good + 1.0)
        if cpa_value <= cpa_good * 0.6:
            return 100
        if cpa_value <= cpa_good:
            return 90
        if cpa_value <= cpa_good + ((cpa_bad - cpa_good) * 0.18):
            return 78
        if cpa_value <= cpa_good + ((cpa_bad - cpa_good) * 0.36):
            return 65
        if cpa_value <= cpa_good + ((cpa_bad - cpa_good) * 0.64):
            return 45
        if cpa_value <= cpa_bad:
            return 20
        if cpa_value <= cpa_bad * 1.5:
            return 8
        return 0

    def _score_roas(roas_value: float, benchmark_profile: dict) -> int:
        if roas_value is None:
            return 50
        roas_good = max(_to_float(benchmark_profile.get("roas_good")) or DEFAULT_BENCHMARK_PROFILE["roas_good"], 0.1)
        roas_bad = max(_to_float(benchmark_profile.get("roas_bad")) or DEFAULT_BENCHMARK_PROFILE["roas_bad"], 0.05)
        if roas_value >= roas_good * 2:
            return 100
        if roas_value >= roas_good * 1.5:
            return 92
        if roas_value >= roas_good:
            return 82
        if roas_value >= roas_good * 0.75:
            return 70
        if roas_value >= max(roas_bad + ((roas_good - roas_bad) * 0.286), roas_bad):
            return 55
        if roas_value >= roas_bad:
            return 30
        if roas_value >= max(roas_bad * 0.833, 0.01):
            return 15
        return 0

    def _compute_performance_score(record: dict, confidence_weight: float, benchmark_profile: dict) -> dict | None:
        ctr_value = _to_float(record.get("ctr"))
        cpa_value = _to_float(record.get("cpa"))
        roas_value = _to_float(record.get("roas"))
        time_active_hours = _compute_time_active(record)
        ctr_bad = max(_to_float(benchmark_profile.get("ctr_bad")) or DEFAULT_BENCHMARK_PROFILE["ctr_bad"], 0.05)
        ctr_hard_bad = max(ctr_bad * 0.375, 0.01)
        cpa_bad = max(_to_float(benchmark_profile.get("cpa_bad")) or DEFAULT_BENCHMARK_PROFILE["cpa_bad"], 1.0)
        cpa_good = max(_to_float(benchmark_profile.get("cpa_good")) or DEFAULT_BENCHMARK_PROFILE["cpa_good"], 1.0)
        cpa_hard_bad = max(cpa_bad * 1.875, cpa_bad + 1.0)
        roas_bad = max(_to_float(benchmark_profile.get("roas_bad")) or DEFAULT_BENCHMARK_PROFILE["roas_bad"], 0.05)
        roas_good = max(_to_float(benchmark_profile.get("roas_good")) or DEFAULT_BENCHMARK_PROFILE["roas_good"], 0.1)
        roas_hard_bad = max(roas_bad * 0.4167, 0.01)

        penalty_factor = min(1.0, max(0.2, (
            (confidence_weight * 0.6) +
            (min(time_active_hours / 24.0, 1.0) * 0.4)
        )))

        available_weights = []
        weighted_sum = 0.0

        if ctr_value is not None:
            available_weights.append(0.40)
            weighted_sum += _score_ctr(ctr_value, benchmark_profile) * 0.40
        if cpa_value is not None:
            available_weights.append(0.35)
            weighted_sum += _score_cpa(cpa_value, benchmark_profile) * 0.35
        if roas_value is not None:
            available_weights.append(0.25)
            weighted_sum += _score_roas(roas_value, benchmark_profile) * 0.25

        if not available_weights:
            return None

        performance_score = weighted_sum / sum(available_weights)
        penalty_strength = (1 - penalty_factor)
        hard_penalty_strength = penalty_factor
        total_penalty_strength = 0.0

        # Penalidades agressivas: performance ruim derruba o criativo mesmo com boa qualidade interna.
        if ctr_value is not None and ctr_value < ctr_bad:
            ctr_deviation = (ctr_bad - ctr_value) / ctr_bad
            ctr_deviation = min(max(ctr_deviation, 0.0), 1.0)
            ctr_deviation = ctr_deviation ** 1.5
            total_penalty_strength += ctr_deviation * penalty_strength
        if cpa_value is not None and cpa_value > cpa_bad:
            cpa_deviation = (cpa_value - cpa_bad) / cpa_bad
            cpa_deviation = min(max(cpa_deviation, 0.0), 1.0)
            cpa_deviation = cpa_deviation ** 1.5
            total_penalty_strength += cpa_deviation * penalty_strength
        if roas_value is not None and roas_value < roas_bad:
            roas_deviation = (roas_bad - roas_value) / roas_bad
            roas_deviation = min(max(roas_deviation, 0.0), 1.0)
            roas_deviation = roas_deviation ** 1.5
            total_penalty_strength += roas_deviation * penalty_strength

        if ctr_value is not None and ctr_value < ctr_hard_bad and performance_score < 60:
            total_penalty_strength = max(total_penalty_strength, 0.7 * hard_penalty_strength)
        if cpa_value is not None and cpa_value > cpa_hard_bad and performance_score < 60:
            total_penalty_strength = max(total_penalty_strength, 0.75 * hard_penalty_strength)
        if roas_value is not None and roas_value < roas_hard_bad and performance_score < 60:
            total_penalty_strength = max(total_penalty_strength, 0.8 * hard_penalty_strength)

        total_penalty_strength = min(total_penalty_strength, 0.8)
        performance_score = performance_score * (1 - total_penalty_strength)

        # BÃ´nus forte para retorno real excepcional.
        if roas_value is not None and roas_value >= roas_good:
            performance_score += 8
        if ctr_value is not None and ctr_value >= (_to_float(benchmark_profile.get("ctr_good")) or DEFAULT_BENCHMARK_PROFILE["ctr_good"]):
            performance_score += 5
        if cpa_value is not None and cpa_value <= cpa_good:
            performance_score += 5

        # Com baixa confianÃ§a, o score real converge para neutro (50).
        performance_score = (performance_score * confidence_weight) + (50 * (1 - confidence_weight))

        return {
            "performance_score": _clamp_0_100(performance_score),
            "penalty_strength": float(round(total_penalty_strength, 4)),
        }

    def _compute_quality_score() -> int:
        score_quality_gate = int(executive_summary.get("score_quality_gate", 0) or 0)
        status_final = executive_summary.get("status_final", "erro")
        decision_mode = media_decision.get("decision_mode", "strict")
        media_next_action = media_decision.get("media_next_action") or media_decision.get("next_action") or ""

        quality_score = float(score_quality_gate)
        if status_final == "aprovado":
            quality_score += 5
        elif status_final == "reprovado_quality_gate":
            quality_score -= 20
        else:
            quality_score -= 35

        if decision_mode == "strict" and media_next_action in {"subir", "testar"}:
            quality_score += 3
        if media_next_action in {"bloquear", "refazer"}:
            quality_score = min(quality_score, 45)
        return _clamp_0_100(quality_score)

    def _compute_fit_score() -> int:
        goal_fit_score = int(media_decision.get("goal_fit_score", 0) or 0)
        visual_fit_score = int(media_decision.get("visual_campaign_fit_score", 0) or 0)
        cta_fit_score = int(media_decision.get("cta_funnel_fit_score", 0) or 0)
        fit_score = (goal_fit_score * 0.50) + (visual_fit_score * 0.30) + (cta_fit_score * 0.20)
        return _clamp_0_100(fit_score)

    job_id = executive_summary.get("job_id", "") or media_decision.get("job_id", "")
    performance_record = _load_latest_performance_record(job_id)
    benchmark_profile = _resolve_benchmark_profile(executive_summary, media_decision)
    client_id = performance_record.get("client_id", "")
    if client_id:
        performance_memory = load_performance_memory(client_id).get("items", [])
        dynamic_benchmark = _compute_dynamic_benchmark(performance_memory)
        if dynamic_benchmark.get("valid_count", 0) >= 20:
            for key in ["ctr_good", "ctr_bad", "cpa_good", "cpa_bad", "roas_good", "roas_bad"]:
                if dynamic_benchmark.get(key) is not None:
                    benchmark_profile[key] = dynamic_benchmark[key]
    confidence_weight = _compute_confidence_weight(performance_record)
    time_active_hours = _compute_time_active(performance_record)
    performance_result = _compute_performance_score(performance_record, confidence_weight, benchmark_profile)
    if performance_result is None:
        return _legacy_score()
    performance_score = performance_result["performance_score"]
    penalty_strength = performance_result["penalty_strength"]
    creative_id = str(performance_record.get("creative_id", "") or "").strip()
    id_recovered = bool(performance_record.get("_id_recovered", False))
    stability_history = []
    if creative_id:
        for history_item in _load_performance_history(client_id, creative_id):
            history_confidence = _compute_confidence_weight(history_item)
            history_result = _compute_performance_score(history_item, history_confidence, benchmark_profile)
            if history_result is None:
                continue
            stability_history.append({
                "performance_score": history_result["performance_score"],
                "updated_at": history_item.get("updated_at", ""),
            })
    stability_score = _compute_stability_score(stability_history)

    quality_score = _compute_quality_score()
    fit_score = _compute_fit_score()
    final_score = (performance_score * 0.60) + (quality_score * 0.30) + (fit_score * 0.10)

    status_final = executive_summary.get("status_final", "erro")
    media_next_action = media_decision.get("media_next_action") or media_decision.get("next_action") or ""

    if status_final == "erro":
        final_score = min(final_score, 20)
    elif status_final == "reprovado_quality_gate":
        final_score = min(final_score, 60)

    if media_next_action in {"bloquear", "refazer"}:
        final_score = min(final_score, 54)

    media_decision["_action_engine"] = {
        "creative_id": creative_id,
        "_id_recovered": id_recovered,
        "performance_score": performance_score,
        "penalty_strength": penalty_strength,
        "confidence_score": float(round(confidence_weight, 4)),
        "stability_score": stability_score,
        "time_active_hours": time_active_hours,
        "portfolio_score": _clamp_0_100(final_score),
    }

    return _clamp_0_100(final_score)


def _execution_state_path(client_id: str) -> str:
    return os.path.join("data", "clients", client_id, "active_creatives.json")


def load_execution_state(client_id: str) -> dict:
    default_state = {
        "client_id": client_id,
        "updated_at": "",
        "active_creatives": [],
        "testing_creatives": [],
        "historical_creatives": [],
        "replacements": [],
        "trend_history": [],
        "allocation_traces": [],
    }
    path = _execution_state_path(client_id)
    if not os.path.exists(path):
        return default_state
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return default_state
    if not isinstance(payload, dict):
        return default_state
    state = dict(default_state)
    state.update(payload)
    if not isinstance(state.get("trend_history"), list):
        state["trend_history"] = []
    if not isinstance(state.get("allocation_traces"), list):
        state["allocation_traces"] = []
    return state


def _build_execution_state_entry(card: dict, previous_entry: dict | None, state_label: str, now_ts: str) -> dict:
    previous_entry = previous_entry or {}
    times_used = int(previous_entry.get("times_used", 0) or 0)
    if state_label in {"active", "testing"}:
        times_used += 1
    return {
        "job_id": card.get("job_id", ""),
        "state": state_label,
        "headline": card.get("headline", ""),
        "portfolio_score": int(card.get("portfolio_score", 0) or 0),
        "performance_score": card.get("performance_score"),
        "penalty_strength": card.get("penalty_strength"),
        "confidence_score": card.get("confidence_score"),
        "stability_score": card.get("stability_score", 0.5),
        "_id_recovered": card.get("_id_recovered", False),
        "portfolio_action": card.get("portfolio_action", ""),
        "operational_decision": card.get("operational_decision", {}),
        "allocated_budget": card.get("allocated_budget", 0.0),
        "budget_share": card.get("budget_share", 0.0),
        "allocation_last_updated_at": card.get("allocation_last_updated_at") or previous_entry.get("allocation_last_updated_at", ""),
        "allocation_review_due": card.get("allocation_review_due") or previous_entry.get("allocation_review_due", ""),
        "objective_bucket": card.get("objective_bucket", ""),
        "created_at": previous_entry.get("created_at") or now_ts,
        "last_used": now_ts,
        "times_used": times_used,
        "metrics": previous_entry.get("metrics") or {
            "ctr": None,
            "cpa": None,
            "roas": None,
        },
        "source_files": {
            "executive_summary": "executive_summary.json",
            "media_decision": "media_decision.json",
            "quality_gate": "quality_gate.json",
        },
    }


def _build_allocation_trace(cards: list[dict], cycle_id: str, exploration_envelope: float, generated_at: str) -> dict:
    trace_items = []
    for card in cards or []:
        if not isinstance(card, dict):
            continue
        creative_id = str(card.get("creative_id", "") or "").strip()
        if not creative_id:
            continue
        operational_decision = card.get("operational_decision", {}) or {}
        action = str(operational_decision.get("action", "") or "").strip()
        pool = "exploration" if action == "test" else "performance"
        trace_items.append({
            "creative_id": creative_id,
            "cycle_id": cycle_id,
            "pool": pool,
            "action": action,
            "priority": int(operational_decision.get("priority", 0) or 0),
            "refresh_allowed": bool(card.get("_refresh_allocation", True)),
            "previous_budget_share": float(card.get("_previous_budget_share", 0.0) or 0.0),
            "previous_allocated_budget": float(card.get("_previous_allocated_budget", 0.0) or 0.0),
            "exploration_envelope": float(exploration_envelope or 0.0),
            "allocated_budget": float(card.get("allocated_budget", 0.0) or 0.0),
            "budget_share": float(card.get("budget_share", 0.0) or 0.0),
            "_budget_key": str(card.get("_budget_key", "") or ""),
            "reason": str(operational_decision.get("reason", "") or ""),
        })
    return {
        "cycle_id": cycle_id,
        "generated_at": generated_at,
        "items": trace_items,
    }


def _sanitize_allocation_traces(traces: list[dict], max_cycles: int = ALLOCATION_TRACE_MAX_CYCLES) -> list[dict]:
    sanitized = []
    seen_cycle_ids = set()
    for trace in traces or []:
        if not isinstance(trace, dict):
            continue
        cycle_id = str(trace.get("cycle_id", "") or "").strip()
        generated_at = str(trace.get("generated_at", "") or "").strip()
        items = trace.get("items", [])
        if not cycle_id or not generated_at or not isinstance(items, list):
            continue
        try:
            datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        except ValueError:
            continue
        if cycle_id in seen_cycle_ids:
            continue
        seen_cycle_ids.add(cycle_id)
        sanitized_items = []
        for item in items:
            if not isinstance(item, dict):
                continue
            creative_id = str(item.get("creative_id", "") or "").strip()
            item_cycle_id = str(item.get("cycle_id", "") or "").strip()
            pool = str(item.get("pool", "") or "").strip()
            if not creative_id or item_cycle_id != cycle_id or pool not in {"performance", "exploration"}:
                continue
            sanitized_items.append({
                "creative_id": creative_id,
                "cycle_id": item_cycle_id,
                "pool": pool,
                "action": str(item.get("action", "") or ""),
                "priority": int(item.get("priority", 0) or 0),
                "refresh_allowed": bool(item.get("refresh_allowed", False)),
                "previous_budget_share": float(item.get("previous_budget_share", 0.0) or 0.0),
                "previous_allocated_budget": float(item.get("previous_allocated_budget", 0.0) or 0.0),
                "exploration_envelope": float(item.get("exploration_envelope", 0.0) or 0.0),
                "allocated_budget": float(item.get("allocated_budget", 0.0) or 0.0),
                "budget_share": float(item.get("budget_share", 0.0) or 0.0),
                "_budget_key": str(item.get("_budget_key", "") or ""),
                "reason": str(item.get("reason", "") or ""),
            })
        sanitized.append({
            "cycle_id": cycle_id,
            "generated_at": generated_at,
            "items": sanitized_items,
        })
    sanitized.sort(key=lambda item: item["generated_at"], reverse=True)
    return sanitized[:max_cycles]


def _build_execution_state(client_id: str, portfolio_decision: dict) -> dict:
    previous_state = load_execution_state(client_id)
    performance_memory = load_performance_memory(client_id)
    now_ts = _ts()
    previous_entries = {}
    for key in ["active_creatives", "testing_creatives", "historical_creatives"]:
        for entry in previous_state.get(key, []) or []:
            previous_entries[entry.get("job_id", "")] = entry

    latest_metrics_by_job = {}
    for item in performance_memory.get("items", []) or []:
        job_id = item.get("job_id", "")
        if not job_id or job_id in latest_metrics_by_job:
            continue
        latest_metrics_by_job[job_id] = {
            "ctr": item.get("ctr"),
            "cpa": item.get("cpa"),
            "roas": item.get("roas"),
            "performance_class": item.get("performance_class"),
            "updated_at": item.get("updated_at", ""),
        }

    active_creatives = []
    testing_creatives = []
    historical_creatives = []
    replacements = []

    previous_active_ids = [entry.get("job_id", "") for entry in previous_state.get("active_creatives", []) or [] if entry.get("job_id")]
    current_active_ids = [card.get("job_id", "") for card in portfolio_decision.get("top_creatives", []) or [] if card.get("job_id")]
    displaced_ids = [job_id for job_id in previous_active_ids if job_id not in current_active_ids]
    new_active_ids = [job_id for job_id in current_active_ids if job_id not in previous_active_ids]

    for idx, card in enumerate(portfolio_decision.get("top_creatives", []) or []):
        entry = _build_execution_state_entry(card, previous_entries.get(card.get("job_id", "")), "active", now_ts)
        if card.get("job_id", "") in latest_metrics_by_job:
            entry["metrics"] = latest_metrics_by_job[card.get("job_id", "")]
        if card.get("job_id", "") in new_active_ids and idx < len(displaced_ids):
            entry["replaces_job_id"] = displaced_ids[idx]
            replacements.append({
                "out_job_id": displaced_ids[idx],
                "in_job_id": card.get("job_id", ""),
                "at": now_ts,
            })
        active_creatives.append(entry)

    for card in portfolio_decision.get("test_creatives", []) or []:
        entry = _build_execution_state_entry(card, previous_entries.get(card.get("job_id", "")), "testing", now_ts)
        if card.get("job_id", "") in latest_metrics_by_job:
            entry["metrics"] = latest_metrics_by_job[card.get("job_id", "")]
        testing_creatives.append(entry)

    for card in portfolio_decision.get("discard_creatives", []) or []:
        entry = _build_execution_state_entry(card, previous_entries.get(card.get("job_id", "")), "historical", now_ts)
        if card.get("job_id", "") in latest_metrics_by_job:
            entry["metrics"] = latest_metrics_by_job[card.get("job_id", "")]
        historical_creatives.append(entry)

    state = {
        "client_id": client_id,
        "updated_at": now_ts,
        "active_creatives": active_creatives,
        "testing_creatives": testing_creatives,
        "historical_creatives": historical_creatives,
        "replacements": replacements,
        "trend_history": [],
        "allocation_traces": [],
        "summary": {
            "active_count": len(active_creatives),
            "testing_count": len(testing_creatives),
            "historical_count": len(historical_creatives),
        },
    }
    raw_trend_history = (portfolio_decision.get("trend_history") or []) if isinstance(portfolio_decision, dict) else []
    state["trend_history"] = _sanitize_trend_history(raw_trend_history, max_items=TREND_HISTORY_MAX_ITEMS)
    previous_traces = previous_state.get("allocation_traces", []) or []
    current_trace = (portfolio_decision.get("allocation_trace") or {}) if isinstance(portfolio_decision, dict) else {}
    state["allocation_traces"] = _sanitize_allocation_traces([current_trace] + previous_traces)
    path = _execution_state_path(client_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    return state


def _infer_portfolio_objective(media_decision: dict, executive_summary: dict) -> str:
    """Separa competiÃ§Ã£o por objetivo.

    O ranking nÃ£o mistura tudo no mesmo saco.
    Hoje os buckets sÃ£o:
    - acquisition
    - retention
    - branding
    """
    recommendation = (media_decision.get("campaign_recommendation", "") or "").lower()
    offer_type = (media_decision.get("offer_type", "") or "").lower()
    funnel_stage = (media_decision.get("funnel_stage", "") or "").lower()
    if "remarketing" in recommendation or funnel_stage == "remarketing":
        return "retention"
    if "branding" in offer_type or "autoridade" in offer_type:
        return "branding"
    return "acquisition"


def _build_portfolio_decision(client_id: str, job_ids: list | None = None, recent_n: int = 6) -> dict:
    """Compara mÃºltiplos jobs e impÃµe prioridade real.

    Fluxo:
    1. resolve jobs do portfÃ³lio
    2. calcula portfolio_score por job
    3. separa por objetivo
    4. aplica escassez operacional
    5. marca aÃ§Ã£o final do portfÃ³lio

    portfolio_action:
    - entrar: entrou no topo sem ocupar vaga anterior
    - substituir: entrou no topo porque superou outro criativo elegÃ­vel
    - testar: nÃ£o ganhou vaga de topo, mas ainda merece experimento controlado
    - descartar: ficou abaixo do corte ou perdeu a competiÃ§Ã£o por slot

    A lÃ³gica de substituiÃ§Ã£o existe para impedir acÃºmulo artificial de "bons criativos".
    O portfÃ³lio precisa competir por poucos slots para refletir operaÃ§Ã£o real.

    DinÃ¢mica de competiÃ§Ã£o contÃ­nua:
    - criativos competem por slots limitados
    - entrada de um novo criativo pressiona saÃ­da ou rebaixamento de outro
    - a decisÃ£o Ã© recalculada a cada ciclo, nÃ£o congelada por avaliaÃ§Ã£o antiga
    - o sistema nÃ£o acumula criativos; ele substitui quando aparece opÃ§Ã£o melhor
    """
    from studio.studio_manager import get_client_summary

    def _resolve_total_budget() -> float:
        client_summary = get_client_summary(client_id)
        raw_candidates = [
            client_summary.get("orcamento_mensal"),
            client_summary.get("budget"),
            client_summary.get("verba"),
            client_summary.get("investimento"),
        ]
        for raw in raw_candidates:
            if raw in ("", None):
                continue
            if isinstance(raw, (int, float)):
                return max(float(raw), 0.0)
            try:
                normalized = str(raw).strip().lower()
                normalized = normalized.replace("r$", "").replace(".", "").replace(",", ".")
                value = float(normalized)
                return max(value, 0.0)
            except (TypeError, ValueError):
                continue
        return 0.0

    previous_allocation_state = load_execution_state(client_id)
    previous_allocation_by_key = {}
    for key in ["active_creatives", "testing_creatives", "historical_creatives"]:
        for entry in previous_allocation_state.get(key, []) or []:
            creative_id = entry.get("creative_id", "")
            lookup_key = creative_id
            if lookup_key and lookup_key not in previous_allocation_by_key:
                previous_allocation_by_key[lookup_key] = entry

    portfolio_jobs = _resolve_portfolio_jobs(client_id, job_ids=job_ids, recent_n=recent_n)
    scored_items = []
    for item in portfolio_jobs:
        jdir = item["jdir"]
        job = item["job"]
        executive_summary = _read_json_file(jdir, "executive_summary.json")
        media_decision = _read_json_file(jdir, "media_decision.json")
        creative_summary = _read_json_file(jdir, "creative_summary.json")
        if not executive_summary or not media_decision:
            continue
        portfolio_score = _compute_portfolio_score(executive_summary, media_decision)
        action_engine_inputs = media_decision.get("_action_engine", {}) or {}
        operational_decision = _decide_creative_action({
            "performance_score": action_engine_inputs.get("performance_score", portfolio_score),
            "penalty_strength": action_engine_inputs.get("penalty_strength", 0.0),
            "confidence_score": action_engine_inputs.get("confidence_score", 0.0),
            "stability_score": action_engine_inputs.get("stability_score", 0.5),
            "_id_recovered": action_engine_inputs.get("_id_recovered", False),
        })
        media_next_action = media_decision.get("media_next_action") or media_decision.get("next_action") or ""
        status_final = executive_summary.get("status_final", "erro")
        objective_bucket = _infer_portfolio_objective(media_decision, executive_summary)
        card = {
            "job_id": item["job_id"],
            "creative_id": action_engine_inputs.get("creative_id", ""),
            "_id_recovered": action_engine_inputs.get("_id_recovered", False),
            "portfolio_score": portfolio_score,
            "performance_score": action_engine_inputs.get("performance_score"),
            "penalty_strength": action_engine_inputs.get("penalty_strength"),
            "confidence_score": action_engine_inputs.get("confidence_score"),
            "stability_score": action_engine_inputs.get("stability_score", 0.5),
            "time_active_hours": action_engine_inputs.get("time_active_hours"),
            "priority": operational_decision.get("priority", 0),
            "status_final": status_final,
            "headline": creative_summary.get("headline", ""),
            "media_next_action": media_next_action,
            "score_quality_gate": int(executive_summary.get("score_quality_gate", 0) or 0),
            "goal_fit_score": int(media_decision.get("goal_fit_score", 0) or 0),
            "visual_campaign_fit_score": int(media_decision.get("visual_campaign_fit_score", 0) or 0),
            "decision_mode": media_decision.get("decision_mode", ""),
            "media_rationale": media_decision.get("media_rationale", ""),
            "objective_bucket": objective_bucket,
            "operational_decision": operational_decision,
            "paid_metrics_placeholder": {
                "ctr": None,
                "cpa": None,
                "roas": None,
            },
        }
        card, operational_decision = _apply_missing_creative_id_guard(card, operational_decision)
        previous_allocation = previous_allocation_by_key.get(card.get("creative_id", ""), {})
        card["allocated_budget"] = previous_allocation.get("allocated_budget", 0.0)
        card["budget_share"] = previous_allocation.get("budget_share", 0.0)
        card["_previous_budget_share"] = previous_allocation.get("budget_share", 0.0)
        card["_previous_allocated_budget"] = previous_allocation.get("allocated_budget", 0.0)
        card["allocation_last_updated_at"] = previous_allocation.get("allocation_last_updated_at", "")
        card["allocation_review_due"] = previous_allocation.get("allocation_review_due", "")
        card["_previous_allocation_priority"] = int((((previous_allocation.get("operational_decision") or {}).get("priority")) or card.get("priority", 0)) or 0)
        scored_items.append(card)

    scored_items.sort(key=_portfolio_rank_key, reverse=True)
    grouped_items = {"acquisition": [], "retention": [], "branding": []}
    for item in scored_items:
        grouped_items.setdefault(item["objective_bucket"], []).append(item)

    top_creatives = []
    test_creatives = []
    discard_creatives = []
    top_by_objective = {"acquisition": [], "retention": [], "branding": []}
    test_by_objective = {"acquisition": [], "retention": [], "branding": []}

    for objective_bucket, items in grouped_items.items():
        objective_top = []
        objective_test = []
        objective_discard = []
        for item in items:
            media_next_action = item.get("media_next_action", "")
            status_final = item.get("status_final", "erro")
            operational_action = ((item.get("operational_decision", {}) or {}).get("action") or "").lower()
            if operational_action == "kill":
                item["bucket"] = "discard_creatives"
                item["portfolio_decision"] = "descartar"
                item["portfolio_action"] = "descartar"
                objective_discard.append(item)
                continue
            if status_final == "erro" or media_next_action in {"bloquear", "refazer"} or item["portfolio_score"] < 55:
                item["bucket"] = "discard_creatives"
                item["portfolio_decision"] = "descartar"
                item["portfolio_action"] = "descartar"
                objective_discard.append(item)
                continue
            if len(objective_top) < PORTFOLIO_MAX_TOP_CREATIVES and status_final == "aprovado" and item["portfolio_score"] >= 78:
                item["bucket"] = "top_creatives"
                item["portfolio_decision"] = "subir"
                item["portfolio_action"] = "entrar" if not objective_top else "substituir"
                objective_top.append(item)
                continue
            if len(objective_test) < PORTFOLIO_MAX_TEST_CREATIVES:
                item["bucket"] = "test_creatives"
                item["portfolio_decision"] = "testar"
                item["portfolio_action"] = "testar"
                objective_test.append(item)
            else:
                item["bucket"] = "discard_creatives"
                item["portfolio_decision"] = "descartar"
                item["portfolio_action"] = "descartar"
                objective_discard.append(item)

        top_by_objective[objective_bucket] = objective_top
        test_by_objective[objective_bucket] = objective_test
        top_creatives.extend(objective_top)
        test_creatives.extend(objective_test)
        discard_creatives.extend(objective_discard)

    top_creatives.sort(key=_portfolio_rank_key, reverse=True)
    test_creatives.sort(key=_portfolio_rank_key, reverse=True)
    discard_creatives.sort(key=_portfolio_rank_key, reverse=True)
    top_creatives = top_creatives[:PORTFOLIO_MAX_TOP_CREATIVES]
    kept_top_ids = {item["job_id"] for item in top_creatives}
    spillover = []
    for item in top_by_objective.get("acquisition", []) + top_by_objective.get("retention", []) + top_by_objective.get("branding", []):
        if item["job_id"] not in kept_top_ids:
            demoted = dict(item)
            demoted["bucket"] = "test_creatives" if len(test_creatives) + len(spillover) < PORTFOLIO_MAX_TEST_CREATIVES else "discard_creatives"
            demoted["portfolio_decision"] = "testar" if demoted["bucket"] == "test_creatives" else "descartar"
            demoted["portfolio_action"] = "testar" if demoted["bucket"] == "test_creatives" else "descartar"
            spillover.append(demoted)
    test_creatives.extend([item for item in spillover if item["bucket"] == "test_creatives"])
    discard_creatives.extend([item for item in spillover if item["bucket"] == "discard_creatives"])
    test_creatives.sort(key=_portfolio_rank_key, reverse=True)
    if len(test_creatives) > PORTFOLIO_MAX_TEST_CREATIVES:
        overflow = test_creatives[PORTFOLIO_MAX_TEST_CREATIVES:]
        for item in overflow:
            item["bucket"] = "discard_creatives"
            item["portfolio_decision"] = "descartar"
            item["portfolio_action"] = "descartar"
        discard_creatives.extend(overflow)
        test_creatives = test_creatives[:PORTFOLIO_MAX_TEST_CREATIVES]
    discard_creatives.sort(key=_portfolio_rank_key, reverse=True)

    total_budget = _resolve_total_budget()
    previous_portfolio_path = os.path.join("data", "clients", client_id, "portfolio_decision.json")
    previous_exploration_envelope = 0.12
    previous_trend_history = previous_allocation_state.get("trend_history", []) or []
    if os.path.exists(previous_portfolio_path):
        try:
            with open(previous_portfolio_path, encoding="utf-8") as f:
                previous_portfolio = json.load(f)
            previous_exploration_envelope = float(
                ((previous_portfolio.get("allocation_policy") or {}).get("exploration_envelope")) or 0.12
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            previous_exploration_envelope = 0.12

    refresh_allowed = any(
        _should_refresh_allocation(card, int(((card.get("operational_decision") or {}).get("priority")) or 0))
        for card in (top_creatives + test_creatives)
    )
    portfolio_cycle_id = str(uuid.uuid4())
    previous_now_ts = _ts()
    performance_history = _build_trend_history(
        previous_trend_history,
        top_creatives + test_creatives,
        previous_now_ts,
        cycle_id=portfolio_cycle_id,
    )

    allocation_policy = _compute_exploration_envelope(
        top_creatives + test_creatives,
        performance_history,
        previous_envelope=previous_exploration_envelope,
        refresh_allowed=refresh_allowed,
    )
    allocation_policy["cycle_id"] = portfolio_cycle_id
    allocation_policy["performance_history_audit"] = {
        "count": len(performance_history),
        "latest_updated_at": performance_history[0]["updated_at"] if performance_history else "",
        "sources": sorted({item.get("source", "") for item in performance_history if item.get("source")}),
    }
    combined_cards = top_creatives + test_creatives + discard_creatives
    allocated_cards = _allocate_creative_budget(
        combined_cards,
        total_budget,
        exploration_envelope=allocation_policy["exploration_envelope"],
    )
    allocated_by_key = {item.get("_budget_key", ""): item for item in allocated_cards if item.get("_budget_key")}
    top_creatives = [allocated_by_key.get(item.get("_budget_key", ""), item) for item in top_creatives]
    test_creatives = [allocated_by_key.get(item.get("_budget_key", ""), item) for item in test_creatives]
    discard_creatives = [allocated_by_key.get(item.get("_budget_key", ""), item) for item in discard_creatives]
    allocation_trace = _build_allocation_trace(
        top_creatives + test_creatives + discard_creatives,
        portfolio_cycle_id,
        allocation_policy["exploration_envelope"],
        previous_now_ts,
    )
    for item in top_creatives + test_creatives + discard_creatives:
        item.pop("_budget_key", None)

    output = {
        "client_id": client_id,
        "generated_at": _ts(),
        "total_budget": total_budget,
        "allocation_policy": allocation_policy,
        "trend_history": performance_history,
        "allocation_trace": allocation_trace,
        "jobs_considered": [item["job_id"] for item in scored_items],
        "limits": {
            "max_top_creatives": PORTFOLIO_MAX_TOP_CREATIVES,
            "max_test_creatives": PORTFOLIO_MAX_TEST_CREATIVES,
        },
        "objective_groups": {
            "acquisition": [item["job_id"] for item in grouped_items.get("acquisition", [])],
            "retention": [item["job_id"] for item in grouped_items.get("retention", [])],
            "branding": [item["job_id"] for item in grouped_items.get("branding", [])],
        },
        "top_creatives": top_creatives,
        "test_creatives": test_creatives,
        "discard_creatives": discard_creatives,
    }
    execution_state = _build_execution_state(client_id, output)
    output["execution_state_file"] = "active_creatives.json"
    output["execution_summary"] = execution_state.get("summary", {})
    output.pop("trend_history", None)
    output.pop("allocation_trace", None)
    client_dir = os.path.join("data", "clients", client_id)
    os.makedirs(client_dir, exist_ok=True)
    with open(os.path.join(client_dir, "portfolio_decision.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    return output


def _build_executive_summary(client_id: str, job: dict, jdir: str, status_override: str = "", error_message: str = "") -> dict:
    from studio.studio_manager import get_client_summary

    quality_gate = _read_json_file(jdir, "quality_gate.json")
    validation = _read_json_file(jdir, "output_validation.json")
    creative_summary = _read_json_file(jdir, "creative_summary.json")
    manifest = _read_json_file(jdir, "manifest.json")
    memory = load_performance_memory(client_id)
    client_context = get_client_summary(client_id)

    status_final = _normalize_status_label(status_override or job.get("status") or quality_gate.get("decisao") or manifest.get("quality_gate", {}).get("decisao"))
    score_quality_gate = int(
        quality_gate.get("score")
        or manifest.get("quality_gate", {}).get("score")
        or validation.get("quality_gate", {}).get("score")
        or 0
    )
    gate_source = quality_gate or manifest.get("quality_gate", {}) or validation.get("quality_gate", {}) or {}
    diagnostico = gate_source.get("diagnostico", {}) or {}
    critical_failures = diagnostico.get("critical_failures", []) or []

    selected_angle = manifest.get("angulo") or job.get("angulo") or {}
    if not selected_angle and job.get("angulos") and job.get("angulo_selecionado") is not None:
        idx = int(job.get("angulo_selecionado"))
        angulos = job.get("angulos") or []
        selected_angle = angulos[idx] if 0 <= idx < len(angulos) else {}

    similar_good = (diagnostico.get("similar_good_examples") or [])
    similar_bad = (diagnostico.get("similar_bad_examples") or [])
    best_good = similar_good[0] if similar_good else {}
    best_bad = similar_bad[0] if similar_bad else {}

    if status_final == "aprovado":
        decisao_resumida = "Aprovado porque a peÃ§a ficou comercial, clara e acionÃ¡vel."
        if gate_source.get("tentativa", 1) and int(gate_source.get("tentativa", 1)) > 1:
            decisao_resumida = "Aprovado depois de retry, com ganho de clareza comercial e CTA mais direto."
    elif status_final == "reprovado_quality_gate":
        decisao_resumida = "Reprovado porque o criativo nÃ£o sustentou forÃ§a suficiente para mÃ­dia."
    else:
        decisao_resumida = "Encerrado com erro antes de consolidar um criativo confiÃ¡vel."

    if status_final == "aprovado":
        motivo_principal = "Passou porque a headline criou tensÃ£o comercial clara e o CTA ficou direto."
    elif status_final == "reprovado_quality_gate":
        if critical_failures:
            motivo_principal = f"Foi barrado porque {', '.join(critical_failures[:2])} comprometeram a peÃ§a."
        else:
            motivo_principal = "Foi barrado porque a peÃ§a ficou abaixo do nÃ­vel mÃ­nimo de forÃ§a comercial."
    else:
        motivo_principal = error_message or job.get("erro", "") or "O job falhou antes do fechamento do output."

    base_melhor_uso = _executive_best_use(status_final, score_quality_gate, critical_failures)
    o_que_mudou_no_retry = _summarize_retry_change(gate_source, memory, job.get("id", "")) if gate_source else "NÃ£o houve retry relevante."

    if best_good:
        aprendizado_do_historico = "O histÃ³rico puxou a peÃ§a para uma linha que jÃ¡ mostrou forÃ§a no mesmo contexto."
    elif best_bad:
        aprendizado_do_historico = "O histÃ³rico serviu como alerta para nÃ£o repetir uma saÃ­da fraca."
    else:
        aprendizado_do_historico = "Ainda nÃ£o hÃ¡ histÃ³rico relevante o suficiente para puxar uma referÃªncia forte."

    padrao_usado = _executive_reference_line(best_good, "Ainda nÃ£o hÃ¡ histÃ³rico relevante para usar como referÃªncia.")
    padrao_evitar = _executive_reference_line(best_bad, "Ainda nÃ£o hÃ¡ histÃ³rico ruim relevante para evitar.")
    confianca = _executive_confidence(status_final, score_quality_gate, gate_source)
    summary = {
        "job_id": job.get("id", ""),
        "status_final": status_final,
        "score_quality_gate": score_quality_gate,
        "decisao_resumida": decisao_resumida,
        "motivo_principal": motivo_principal,
        "risco_principal": "",
        "acao_recomendada": "",
        "melhor_uso": base_melhor_uso,
        "o_que_mudou_no_retry": o_que_mudou_no_retry,
        "aprendizado_do_historico": aprendizado_do_historico,
        "padrao_usado_como_referencia": padrao_usado,
        "padrao_evitar": padrao_evitar,
        "confianca": confianca,
    }
    media_decision = _build_media_decision_v2(
        summary,
        gate_source,
        creative_summary,
        selected_angle or {},
        memory,
        job,
        client_context,
    )
    _write_json_file(jdir, "media_decision.json", media_decision)

    if status_final == "aprovado":
        risk_parts = []
        if media_decision.get("fatigue_risk") in {"moderado", "alto"}:
            risk_parts.append(f"risco de fadiga {media_decision.get('fatigue_risk')}")
        if "tensÃ£o baixa: contraste insuficiente para provocar aÃ§Ã£o" in (gate_source.get("falhas") or []):
            risk_parts.append("ainda existe risco de tensÃ£o comercial abaixo do ideal")
        risco_principal = " e ".join(risk_parts) if risk_parts else "baixo risco operacional para subir em mÃ­dia."
    elif status_final == "reprovado_quality_gate":
        risco_principal = "Se subir em mÃ­dia assim, a peÃ§a tende a competir mal no feed e desperdiÃ§ar verba."
    else:
        risco_principal = "Sem corrigir o erro atual, o output nÃ£o vira decisÃ£o confiÃ¡vel de mÃ­dia."

    melhor_uso_map = {
        "alta": "subir como criativo principal",
        "media": "usar como teste secundÃ¡rio",
        "baixa": "reter para nova iteraÃ§Ã£o",
        "bloquear": "nÃ£o vale mÃ­dia",
    }
    summary["melhor_uso"] = melhor_uso_map.get(media_decision.get("launch_priority"), base_melhor_uso)
    summary["acao_recomendada"] = media_decision.get("next_action") or (
        "Corrigir o erro do pipeline antes de decidir uso em mÃ­dia." if status_final == "erro"
        else (gate_source.get("acoes_recomendadas") or ["Refazer headline, promessa e visual antes de nova tentativa."])[0]
    )
    summary["risco_principal"] = risco_principal
    summary["contexto_de_uso"] = f"{media_decision.get('campaign_recommendation')} | funil {media_decision.get('funnel_stage')}"
    summary["tipo_de_oferta"] = media_decision.get("offer_type", "")
    summary["acao_recomendada"] = {
        "subir": "Subir.",
        "testar": "Testar.",
        "refazer": "Refazer.",
        "bloquear": "Bloquear.",
    }.get(media_decision.get("media_next_action"), summary.get("acao_recomendada", ""))
    summary["contexto_de_uso"] = f"{media_decision.get('campaign_recommendation')} | {media_decision.get('subniche')}"
    summary["media_decision_file"] = "media_decision.json"
    _write_json_file(jdir, "executive_summary.json", summary)
    _build_portfolio_decision(client_id, recent_n=8)
    return summary


def _clean_extracted_block(value: str) -> str:
    cleaned = (value or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
    return cleaned.strip()


def _clean_value_line(value: str) -> str:
    cleaned = _clean_extracted_block(value)
    cleaned = cleaned.splitlines()[0] if cleaned else ""
    cleaned = cleaned.strip().lstrip("> ").strip()
    cleaned = re.sub(r"^\*\*(.+)\*\*$", r"\1", cleaned)
    cleaned = cleaned.strip().strip('"')
    return cleaned.strip()


def _label_pattern(label: str) -> str:
    tokens = [token for token in re.split(r"[\s_:\-â€”â€“]+", (label or "").strip()) if token]
    if not tokens:
        return ""
    return r"[\s_:\-â€”â€“]*".join(re.escape(token) for token in tokens)


def _extract_block(text: str, header: str) -> str:
    normalized = (text or "").replace("\r\n", "\n")
    label = (header or "").strip().rstrip(":").strip()
    if not normalized or not label:
        return ""
    label_re = _label_pattern(label)

    next_header_boundary = r"(?=^\s*(?:[A-Z][A-Z\s_]{2,}:|\*\*[A-Z][A-Z\s_]{2,}:?\*\*|#{2,3}\s+\S.*$)|\Z)"
    section_patterns = [
        rf"^\s*\*\*{label_re}:?\*\*\s*(?P<body>.*?){next_header_boundary}",
        rf"^\s*#{2,3}\s*{label_re}\s*$\n(?P<body>.*?)(?=^\s*#{2,3}\s+\S.*$|\Z)",
        rf"^\s*{label_re}:\s*(?P<body>.*?){next_header_boundary}",
    ]
    for pattern in section_patterns:
        match = re.search(pattern, normalized, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if match:
            body = _clean_extracted_block(match.group("body"))
            if body:
                return body

    lines = normalized.split("\n")
    next_header_re = re.compile(r"^\s*(?:[A-Z][A-Z\s_]{2,}:\s*|\*\*[A-Z][A-Z\s_]{2,}:?\*\*\s*|#{2,3}\s+\S.*)$")
    inline_header_re = re.compile(rf"^\s*{label_re}:\s*(?P<body>.*)$", re.IGNORECASE)
    standalone_header_patterns = [
        re.compile(rf"^\s*\*\*{label_re}:?\*\*\s*$", re.IGNORECASE),
        re.compile(rf"^\s*#{2,3}\s*{label_re}\s*$", re.IGNORECASE),
        re.compile(rf"^\s*{label_re}:\s*$", re.IGNORECASE),
    ]

    for index, line in enumerate(lines):
        collected = None
        inline_match = inline_header_re.match(line)
        if inline_match:
            collected = []
            inline_body = inline_match.group("body")
            if inline_body.strip():
                collected.append(inline_body)
        elif any(pattern.match(line) for pattern in standalone_header_patterns):
            collected = []
        if collected is None:
            continue

        cursor = index + 1
        while cursor < len(lines):
            current_line = lines[cursor]
            if next_header_re.match(current_line):
                break
            collected.append(current_line)
            cursor += 1
        body = _clean_extracted_block("\n".join(collected))
        if body:
            return body

    return ""

