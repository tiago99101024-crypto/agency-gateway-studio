"""studio_manager.py — Gestão de clientes, auditorias e jobs do Social Content Studio.

Persistência local pura. Sem dependências externas.

Estrutura de dados:
    data/clients/<client-id>/
        client.json          — dados do cliente
        client_summary.json  — resumo compacto (~300 chars) para prompts
        brand.json           — identidade visual
        brand_summary.json   — resumo compacto de marca
        audit/
            instagram_audit.json
            concorrentes.json
            audit_summary.json   — resumo compacto para prompts
            resumo.md
        assets/              — logos, refs visuais
        jobs/
            <job-id>/
                job.json         — metadados do job
                manifest.json    — outputs gerados
                roteiro.md       (reel_pack)
                legenda.md       (carrossel/post)
                cta.md
                visual_brief.md
                ...
"""

import json
import os
import re
import sys
import mimetypes
import shutil
import hashlib
from datetime import datetime


DATA_DIR = "data/clients"


# ─── Utilitários ─────────────────────────────────────────────────────────────

def _ts():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug(text: str) -> str:
    """Gera slug a partir de texto."""
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s-]+", "-", s)
    return s[:40]


def _client_dir(client_id: str) -> str:
    return os.path.join(DATA_DIR, client_id)


def _job_dir(client_id: str, job_id: str) -> str:
    return os.path.join(DATA_DIR, client_id, "jobs", job_id)


def _assets_dir(client_id: str) -> str:
    return os.path.join(DATA_DIR, client_id, "assets")


def _pipeline_state_path(client_id: str) -> str:
    return os.path.join(_client_dir(client_id), "client_pipeline.json")


def _read_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _write_text(path: str, text: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _dedupe_preserve_order(items: list) -> list:
    seen = set()
    output = []
    for item in items or []:
        normalized = str(item or "").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        output.append(normalized)
    return output


def _normalize_instagram_username(username: str) -> str:
    raw = (username or "").strip()
    raw = raw.replace("https://instagram.com/", "").replace("https://www.instagram.com/", "")
    raw = raw.replace("http://instagram.com/", "").replace("http://www.instagram.com/", "")
    raw = raw.strip().strip("/")
    raw = raw.lstrip("@")
    raw = re.sub(r"[^a-zA-Z0-9._]", "", raw)
    return raw.lower()


def _fallback_identity(username: str = "") -> dict:
    username = _normalize_instagram_username(username)
    ref = f"@{username}" if username else "perfil informado"
    return {
        "cores": ["#1A1A1A", "#F5F5F5"],
        "fonte": "Montserrat Bold",
        "estilo": "clean",
        "observacoes": (
            f"fallback aplicado para {ref}; contraste neutro, tipografia segura e base editável "
            "para não bloquear o cadastro."
        ),
        "imagens_analisadas": 0,
        "origem": "fallback",
        "fallback": True,
    }


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = (hex_color or "").replace("#", "")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _brightness(hex_color: str) -> float:
    r, g, b = _hex_to_rgb(hex_color)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def analyze_instagram_identity(username: str) -> dict:
    """Simula análise visual de perfil do Instagram com fallback determinístico."""
    normalized = _normalize_instagram_username(username)
    if not normalized:
        return _fallback_identity(username)

    try:
        # Simula "busca de imagens" de forma determinística para manter o fluxo local/offline.
        image_count = 6
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()

        base_palettes = [
            {
                "estilo": "food",
                "cores": ["#FF6B35", "#1A1A1A", "#FFD166"],
                "fonte": "Montserrat Bold",
                "observacoes": "alto contraste, foco em produto, estilo delivery",
            },
            {
                "estilo": "dark",
                "cores": ["#111111", "#F5F5F5", "#E63946"],
                "fonte": "Poppins SemiBold",
                "observacoes": "fundo escuro, contraste forte e leitura rápida em feed",
            },
            {
                "estilo": "clean",
                "cores": ["#F6F3EE", "#D9D9D9", "#222222"],
                "fonte": "Poppins Medium",
                "observacoes": "visual limpo, áreas de respiro e comunicação objetiva",
            },
            {
                "estilo": "premium",
                "cores": ["#0F172A", "#C6A969", "#F8F5F0"],
                "fonte": "Playfair Display Bold",
                "observacoes": "acabamento sofisticado, contraste refinado e percepção premium",
            },
        ]

        keyword_overrides = [
            ("burger", "food"),
            ("pizza", "food"),
            ("sushi", "food"),
            ("food", "food"),
            ("cafe", "food"),
            ("dark", "dark"),
            ("black", "dark"),
            ("clean", "clean"),
            ("studio", "clean"),
            ("premium", "premium"),
            ("gold", "premium"),
            ("lux", "premium"),
        ]

        chosen_style = None
        for keyword, style in keyword_overrides:
            if keyword in normalized:
                chosen_style = style
                break

        if not chosen_style:
            chosen_style = base_palettes[int(digest[:2], 16) % len(base_palettes)]["estilo"]

        palette = next(item for item in base_palettes if item["estilo"] == chosen_style).copy()
        accent_seed = digest[2:8]
        accent_color = f"#{accent_seed.upper()}"
        if _brightness(accent_color) < 0.18:
            accent_color = "#FF6B35"

        colors = palette["cores"][:2]
        if accent_color not in colors:
            colors.append(accent_color)

        return {
            "cores": colors,
            "fonte": palette["fonte"],
            "estilo": palette["estilo"],
            "observacoes": (
                f"simulação local com {image_count} referências do perfil @{normalized}; "
                f"{palette['observacoes']}."
            ),
            "imagens_analisadas": image_count,
            "origem": "simulada",
            "fallback": False,
        }
    except Exception:
        return _fallback_identity(normalized)


def _brand_has_identity(brand: dict) -> bool:
    return bool(
        brand.get("cores")
        and brand.get("fontes")
        and (brand.get("observacoes_identidade", "") or "").strip()
    )


def _analysis_to_brand_fields(analysis: dict) -> dict:
    observacoes = [analysis.get("observacoes", "").strip()]
    estilo = (analysis.get("estilo", "") or "").strip()
    if estilo:
        observacoes.append(f"estilo inferido: {estilo}")
    return {
        "cores": list(analysis.get("cores", [])),
        "fontes": [analysis.get("fonte", "").strip()] if analysis.get("fonte") else [],
        "observacoes_identidade": " | ".join(item for item in observacoes if item),
        "analise_instagram": {
            "origem": analysis.get("origem", ""),
            "fallback": bool(analysis.get("fallback")),
            "estilo": estilo,
            "imagens_analisadas": int(analysis.get("imagens_analisadas", 0) or 0),
            "atualizado_em": _ts(),
        },
    }


def _audit_has_identity_signal(audit: dict) -> bool:
    if not audit:
        return False
    return any([
        (audit.get("identidade_visual_atual", "") or "").strip(),
        (audit.get("linha_visual_sugerida", "") or "").strip(),
        (audit.get("diagnostico_perfil", "") or "").strip(),
        bool(audit.get("oportunidades", []) or []),
        (audit.get("observacoes_criativo", "") or "").strip(),
    ])


def _audit_to_brand_fields(audit: dict, existing_brand: dict | None = None) -> dict:
    existing_brand = existing_brand or {}
    fallback = _analysis_to_brand_fields(_fallback_identity())
    observations = [
        (audit.get("linha_visual_sugerida", "") or "").strip(),
        (audit.get("identidade_visual_atual", "") or "").strip(),
        (audit.get("diagnostico_perfil", "") or "").strip(),
        (audit.get("observacoes_criativo", "") or "").strip(),
    ]
    oportunidades = [str(item).strip() for item in (audit.get("oportunidades", []) or []) if str(item).strip()]
    if oportunidades:
        observations.append("oportunidades-chave: " + " | ".join(oportunidades[:2]))

    identidade = " | ".join(item for item in observations if item).strip()
    if not identidade:
        identidade = fallback["observacoes_identidade"]

    return {
        "cores": list(existing_brand.get("cores", []) or fallback["cores"]),
        "fontes": list(existing_brand.get("fontes", []) or fallback["fontes"]),
        "observacoes_identidade": identidade,
        "analise_instagram": existing_brand.get("analise_instagram", {}),
        "origem_identidade": "auditoria",
    }


def _sync_brand_from_audit_if_possible(client_id: str, audit: dict, force: bool = False) -> dict:
    brand_path = os.path.join(_client_dir(client_id), "brand.json")
    brand = _read_json(brand_path)
    if _brand_has_identity(brand) and not force:
        return brand
    if not _audit_has_identity_signal(audit):
        return brand

    derived = _audit_to_brand_fields(audit, brand)
    if not brand.get("cores") or force:
        brand["cores"] = derived["cores"]
    if not brand.get("fontes") or force:
        brand["fontes"] = derived["fontes"]
    if not (brand.get("observacoes_identidade", "") or "").strip() or force:
        brand["observacoes_identidade"] = derived["observacoes_identidade"]
    brand["origem_identidade"] = derived["origem_identidade"]
    if brand.get("analise_instagram"):
        brand["analise_instagram"] = brand.get("analise_instagram", {})
    brand["atualizado_em"] = _ts()

    _write_json(brand_path, brand)
    _rebuild_brand_summary(client_id)
    return brand


def ensure_brand_identity(client_id: str, force: bool = False) -> dict:
    """Garante identidade visual em brand.json a partir do Instagram do cliente."""
    cdir = _client_dir(client_id)
    client = get_client(client_id)
    brand_path = os.path.join(cdir, "brand.json")
    brand = _read_json(brand_path)

    if _brand_has_identity(brand) and not force:
        return brand

    instagram = _normalize_instagram_username(client.get("instagram", ""))
    if not instagram:
        audit = get_audit(client_id)
        brand_from_audit = _sync_brand_from_audit_if_possible(client_id, audit, force=force)
        if _brand_has_identity(brand_from_audit):
            return brand_from_audit
        raise ValueError("brand.json sem identidade visual e cliente sem Instagram para analise.")

    analysis = analyze_instagram_identity(instagram)
    derived = _analysis_to_brand_fields(analysis)

    if not brand.get("cores") or force:
        brand["cores"] = derived["cores"]
    if not brand.get("fontes") or force:
        brand["fontes"] = derived["fontes"]
    if not (brand.get("observacoes_identidade", "") or "").strip() or force:
        brand["observacoes_identidade"] = derived["observacoes_identidade"]
    brand["analise_instagram"] = derived["analise_instagram"]
    brand["atualizado_em"] = _ts()

    _write_json(brand_path, brand)
    _rebuild_brand_summary(client_id)
    return brand


# ─── Clientes ────────────────────────────────────────────────────────────────

def create_client(data: dict) -> dict:
    """Cria um novo cliente. Retorna o cliente criado com ID."""
    nome = data.get("nome", "").strip()
    if not nome:
        raise ValueError("Campo 'nome' obrigatorio.")

    client_id = _slug(nome) + "-" + datetime.utcnow().strftime("%Y%m%d")
    cdir = _client_dir(client_id)

    if os.path.exists(cdir):
        raise ValueError(f"Cliente '{client_id}' ja existe.")

    client = {
        "id": client_id,
        "nome": nome,
        "instagram": data.get("instagram", "").strip().lstrip("@"),
        "nicho": data.get("nicho", ""),
        "produto": data.get("produto", ""),
        "cidade": data.get("cidade", ""),
        "objetivo": data.get("objetivo", ""),
        "tom_voz": data.get("tom_voz", ""),
        "observacoes": data.get("observacoes", ""),
        "concorrentes": data.get("concorrentes", [])[:3],
        "criado_em": _ts(),
        "atualizado_em": _ts(),
    }

    brand = {
        "cliente_id": client_id,
        "cores": data.get("cores", []),
        "fontes": data.get("fontes", []),
        "referencias_visuais": data.get("referencias_visuais", []),
        "logo_path": data.get("logo_path", ""),
        "observacoes_identidade": data.get("observacoes_identidade", ""),
        "atualizado_em": _ts(),
    }

    os.makedirs(cdir, exist_ok=True)
    os.makedirs(os.path.join(cdir, "audit"), exist_ok=True)
    os.makedirs(os.path.join(cdir, "assets"), exist_ok=True)
    os.makedirs(os.path.join(cdir, "jobs"), exist_ok=True)

    _write_json(os.path.join(cdir, "client.json"), client)
    _write_json(os.path.join(cdir, "brand.json"), brand)
    if client["instagram"]:
        try:
            ensure_brand_identity(client_id)
        except Exception:
            pass
    _rebuild_client_summary(client_id)
    _rebuild_brand_summary(client_id)
    record_client_pipeline_state(
        client_id,
        etapa_atual="cliente_criado",
        etapas_concluidas=["cliente_criado"],
        origem_da_execucao="cadastro_cliente",
        proximo_passo_sugerido="Gerar ou salvar auditoria para consolidar contexto.",
    )

    return client


def get_client(client_id: str) -> dict:
    path = os.path.join(_client_dir(client_id), "client.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Cliente '{client_id}' nao encontrado.")
    return _read_json(path)


def update_client(client_id: str, data: dict) -> dict:
    client = get_client(client_id)
    updatable = ["nome", "instagram", "nicho", "produto", "cidade", "objetivo",
                 "tom_voz", "observacoes", "concorrentes"]
    for k in updatable:
        if k in data:
            client[k] = data[k]
    client["atualizado_em"] = _ts()
    _write_json(os.path.join(_client_dir(client_id), "client.json"), client)
    if client.get("instagram"):
        try:
            ensure_brand_identity(client_id)
        except Exception:
            pass
    _rebuild_client_summary(client_id)
    return client


def list_clients() -> list:
    if not os.path.exists(DATA_DIR):
        return []
    result = []
    for entry in sorted(os.listdir(DATA_DIR)):
        cdir = os.path.join(DATA_DIR, entry)
        path = os.path.join(cdir, "client.json")
        if os.path.isdir(cdir) and os.path.exists(path):
            c = _read_json(path)
            result.append({
                "id": c.get("id", entry),
                "nome": c.get("nome", ""),
                "nicho": c.get("nicho", ""),
                "instagram": c.get("instagram", ""),
                "objetivo": c.get("objetivo", ""),
                "criado_em": c.get("criado_em", ""),
            })
    return result


def get_client_bundle(client_id: str) -> dict:
    """Retorna cliente + brand + summaries + assets para a UI principal do Studio."""
    cdir = _client_dir(client_id)
    client = get_client(client_id)
    brand = _read_json(os.path.join(cdir, "brand.json"))
    audit = get_audit(client_id)
    return {
        "client": client,
        "brand": brand,
        "audit": audit,
        "client_summary": get_client_summary(client_id),
        "brand_summary": get_brand_summary(client_id),
        "assets": list_client_assets(client_id),
        "pipeline_status": get_client_pipeline_status(client_id),
        "pipeline_state": get_client_pipeline_state(client_id),
    }


# ─── Summaries compactos (token economy) ─────────────────────────────────────

def _rebuild_client_summary(client_id: str):
    """Gera client_summary.json — compacto para injeção em prompts."""
    c = _read_json(os.path.join(_client_dir(client_id), "client.json"))
    summary = {
        "id": c.get("id", ""),
        "nome": c.get("nome", ""),
        "instagram": c.get("instagram", ""),
        "nicho": c.get("nicho", ""),
        "produto": c.get("produto", ""),
        "cidade": c.get("cidade", ""),
        "objetivo": c.get("objetivo", ""),
        "tom_voz": c.get("tom_voz", ""),
        "concorrentes": c.get("concorrentes", []),
    }
    _write_json(os.path.join(_client_dir(client_id), "client_summary.json"), summary)


def _rebuild_brand_summary(client_id: str):
    """Gera brand_summary.json — compacto para injeção em prompts."""
    b = _read_json(os.path.join(_client_dir(client_id), "brand.json"))
    summary = {
        "cores": b.get("cores", []),
        "fontes": b.get("fontes", []),
        "tom_keywords": b.get("observacoes_identidade", "")[:120],
    }
    _write_json(os.path.join(_client_dir(client_id), "brand_summary.json"), summary)


def get_client_summary(client_id: str) -> dict:
    path = os.path.join(_client_dir(client_id), "client_summary.json")
    if not os.path.exists(path):
        _rebuild_client_summary(client_id)
    return _read_json(path)


def get_brand_summary(client_id: str) -> dict:
    path = os.path.join(_client_dir(client_id), "brand_summary.json")
    if not os.path.exists(path):
        _rebuild_brand_summary(client_id)
    return _read_json(path)


def get_audit_summary(client_id: str) -> dict:
    path = os.path.join(_client_dir(client_id), "audit", "audit_summary.json")
    return _read_json(path)  # vazio se nao existir — job runner trata


# ─── Auditoria ───────────────────────────────────────────────────────────────

def update_audit(client_id: str, data: dict) -> dict:
    """Atualiza auditoria do cliente. Sempre explícito — nunca automático."""
    cdir = _client_dir(client_id)
    audit_dir = os.path.join(cdir, "audit")
    os.makedirs(audit_dir, exist_ok=True)

    audit = {
        "cliente_id": client_id,
        "instagram": data.get("instagram", ""),
        "seguidores": data.get("seguidores", ""),
        "frequencia_posts": data.get("frequencia_posts", ""),
        "formatos_usados": data.get("formatos_usados", []),
        "diagnostico_perfil": data.get("diagnostico_perfil", ""),
        "identidade_visual_atual": data.get("identidade_visual_atual", ""),
        "padroes_detectados": data.get("padroes_detectados", []),
        "erros_visuais": data.get("erros_visuais", []),
        "oportunidades": data.get("oportunidades", []),
        "linha_visual_sugerida": data.get("linha_visual_sugerida", ""),
        "linha_editorial_sugerida": data.get("linha_editorial_sugerida", ""),
        "observacoes_copy": data.get("observacoes_copy", ""),
        "observacoes_criativo": data.get("observacoes_criativo", ""),
        "atualizado_em": _ts(),
        "atualizado_por": "manual",
    }

    concorrentes = data.get("concorrentes", [])

    _write_json(os.path.join(audit_dir, "instagram_audit.json"), audit)
    if concorrentes:
        _write_json(os.path.join(audit_dir, "concorrentes.json"),
                    {"cliente_id": client_id, "concorrentes": concorrentes, "atualizado_em": _ts()})

    # Resumo MD
    resumo = f"""# Auditoria — {client_id}
Atualizado: {_ts()}

## Diagnostico
{audit.get('diagnostico_perfil', '—')}

## Oportunidades
{chr(10).join('- ' + o for o in audit.get('oportunidades', [])) or '—'}

## Linha visual sugerida
{audit.get('linha_visual_sugerida', '—')}

## Linha editorial sugerida
{audit.get('linha_editorial_sugerida', '—')}
"""
    _write_text(os.path.join(audit_dir, "resumo.md"), resumo)

    # Rebuild audit summary
    _rebuild_audit_summary(client_id, audit, concorrentes)
    _sync_brand_from_audit_if_possible(client_id, audit)
    record_client_pipeline_state(
        client_id,
        etapa_atual="auditoria_consolidada",
        etapas_concluidas=["cliente_criado", "auditoria_consolidada"],
        origem_da_execucao="auditoria_manual",
        proximo_passo_sugerido="Criar novo job ou reexecutar a partir da auditoria.",
    )
    return audit


def get_client_pipeline_status(client_id: str) -> dict:
    client = get_client(client_id)
    brand = _read_json(os.path.join(_client_dir(client_id), "brand.json"))
    audit = get_audit(client_id)

    has_instagram = bool(_normalize_instagram_username(client.get("instagram", "")))
    brand_ready = _brand_has_identity(brand)
    audit_ready = _audit_has_identity_signal(audit)

    blockers = []
    if not brand_ready and not has_instagram and not audit_ready:
        blockers.append("Sem identidade visual persistida e sem Instagram/auditoria para consolidar brand.")
    elif not brand_ready and not has_instagram:
        blockers.append("Auditoria salva, mas a identidade visual ainda nao foi consolidada em brand.json.")

    return {
        "has_instagram": has_instagram,
        "brand_ready": brand_ready,
        "audit_ready": audit_ready,
        "job_ready": brand_ready or has_instagram,
        "blockers": blockers,
    }


def get_client_pipeline_state(client_id: str) -> dict:
    status = get_client_pipeline_status(client_id)
    path = _pipeline_state_path(client_id)
    state = _read_json(path)

    default_completed = ["cliente_criado"]
    default_stage = "cliente_criado"
    default_next = "Salvar auditoria ou completar contexto de marca."

    if status["audit_ready"]:
        default_completed.append("auditoria_consolidada")
        default_stage = "auditoria_consolidada"
        default_next = "Criar novo job ou reexecutar a partir da auditoria."
    if state.get("job_id_ativo"):
        default_stage = state.get("etapa_atual", default_stage)
        default_next = state.get("proximo_passo_sugerido", "Revisar job ativo e executar próxima etapa.")

    return {
        "cliente_id": client_id,
        "etapa_atual": state.get("etapa_atual", default_stage),
        "etapas_concluidas": _dedupe_preserve_order(state.get("etapas_concluidas", default_completed)),
        "ultima_atualizacao": state.get("ultima_atualizacao") or _ts(),
        "origem_da_execucao": state.get("origem_da_execucao", "sistema"),
        "job_id_ativo": state.get("job_id_ativo"),
        "proximo_passo_sugerido": state.get("proximo_passo_sugerido", default_next),
    }


def record_client_pipeline_state(
    client_id: str,
    etapa_atual: str,
    etapas_concluidas: list | None = None,
    origem_da_execucao: str = "sistema",
    job_id: str | None = None,
    proximo_passo_sugerido: str | None = None,
) -> dict:
    current = get_client_pipeline_state(client_id)
    completed = _dedupe_preserve_order((current.get("etapas_concluidas", []) or []) + (etapas_concluidas or []))
    if etapa_atual and etapa_atual not in completed and etapa_atual.endswith("_concluido"):
        completed.append(etapa_atual)

    updated = {
        "cliente_id": client_id,
        "etapa_atual": etapa_atual,
        "etapas_concluidas": completed,
        "ultima_atualizacao": _ts(),
        "origem_da_execucao": origem_da_execucao,
        "job_id_ativo": job_id if job_id is not None else current.get("job_id_ativo"),
        "proximo_passo_sugerido": proximo_passo_sugerido or current.get("proximo_passo_sugerido", ""),
    }
    _write_json(_pipeline_state_path(client_id), updated)
    return updated


def get_resume_job_id(client_id: str, preferred_job_id: str = "") -> str:
    if preferred_job_id:
        get_job(client_id, preferred_job_id)
        return preferred_job_id

    state = get_client_pipeline_state(client_id)
    active_job_id = state.get("job_id_ativo", "")
    if active_job_id:
        try:
            get_job(client_id, active_job_id)
            return active_job_id
        except FileNotFoundError:
            pass

    jobs = list_jobs(client_id)
    if not jobs:
        raise FileNotFoundError(f"Nenhum job encontrado para cliente '{client_id}'.")
    return jobs[0]["id"]


def _rebuild_audit_summary(client_id: str, audit: dict, concorrentes: list):
    """Gera audit_summary.json — compacto para injeção em prompts."""
    oportunidades = audit.get("oportunidades", [])[:3]
    summary = {
        "diagnostico": audit.get("diagnostico_perfil", "")[:200],
        "oportunidades_top": oportunidades,
        "linha_visual": audit.get("linha_visual_sugerida", "")[:150],
        "linha_editorial": audit.get("linha_editorial_sugerida", "")[:150],
        "erros_visuais": audit.get("erros_visuais", [])[:3],
        "concorrentes_slugs": [c.get("arroba", "") for c in concorrentes][:3],
    }
    _write_json(os.path.join(_client_dir(client_id), "audit", "audit_summary.json"), summary)


def get_audit(client_id: str) -> dict:
    path = os.path.join(_client_dir(client_id), "audit", "instagram_audit.json")
    return _read_json(path)


def get_concorrentes(client_id: str) -> list:
    path = os.path.join(_client_dir(client_id), "audit", "concorrentes.json")
    data = _read_json(path)
    return data.get("concorrentes", [])


# ─── Assets ────────────────────────────────────────────────────────────────────

def list_client_assets(client_id: str) -> list:
    """Lista assets já enviados para o cliente."""
    get_client(client_id)  # valida cliente
    assets_dir = _assets_dir(client_id)
    if not os.path.exists(assets_dir):
        return []

    result = []
    for entry in sorted(os.listdir(assets_dir)):
        fpath = os.path.join(assets_dir, entry)
        if not os.path.isfile(fpath):
            continue
        mime = mimetypes.guess_type(entry)[0] or "application/octet-stream"
        result.append({
            "nome": entry,
            "path": fpath,
            "mime": mime,
            "tamanho": os.path.getsize(fpath),
            "categoria": _infer_asset_category(entry, mime),
        })
    return result


def save_client_asset(client_id: str, source_path: str, original_name: str = "", category: str = "") -> dict:
    """Copia um arquivo local para data/clients/<id>/assets/."""
    get_client(client_id)  # valida cliente
    if not source_path or not os.path.exists(source_path):
        raise FileNotFoundError("Arquivo de asset nao encontrado.")

    assets_dir = _assets_dir(client_id)
    os.makedirs(assets_dir, exist_ok=True)

    base_name = original_name or os.path.basename(source_path)
    safe_name = _sanitize_asset_name(base_name)
    stem, ext = os.path.splitext(safe_name)
    if not ext:
        ext = os.path.splitext(source_path)[1]
    final_name = f"{stem}{ext}" if ext else safe_name
    target = os.path.join(assets_dir, final_name)

    idx = 1
    while os.path.exists(target):
        final_name = f"{stem}-{idx}{ext}"
        target = os.path.join(assets_dir, final_name)
        idx += 1

    shutil.copy2(source_path, target)

    mime = mimetypes.guess_type(final_name)[0] or "application/octet-stream"
    return {
        "nome": final_name,
        "path": target,
        "mime": mime,
        "tamanho": os.path.getsize(target),
        "categoria": category or _infer_asset_category(final_name, mime),
    }


def _sanitize_asset_name(name: str) -> str:
    name = os.path.basename((name or "").strip())
    if not name:
        name = f"asset-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.bin"
    name = re.sub(r"[^\w.\- ]+", "", name)
    name = re.sub(r"\s+", "-", name).strip(".-")
    return name[:120] or "asset.bin"


def _infer_asset_category(name: str, mime: str) -> str:
    lname = name.lower()
    if "logo" in lname:
        return "logo"
    if mime.startswith("image/"):
        return "imagem"
    return "arquivo"


# ─── Jobs ────────────────────────────────────────────────────────────────────

TIPOS_JOB = {"carrossel", "post_estatico", "reel_pack"}


def create_job(client_id: str, data: dict) -> dict:
    tipo = data.get("tipo", "")
    if tipo not in TIPOS_JOB:
        raise ValueError(f"Tipo de job invalido: '{tipo}'. Use: {TIPOS_JOB}")

    get_client(client_id)  # valida que cliente existe

    ts_now = datetime.utcnow()
    job_id = ts_now.strftime("%Y%m%d-%H%M%S") + "-" + tipo
    jdir = _job_dir(client_id, job_id)
    os.makedirs(jdir, exist_ok=True)

    job = {
        "id": job_id,
        "cliente_id": client_id,
        "tipo": tipo,
        "status": "pendente",
        "briefing": data.get("briefing", ""),
        "formato": data.get("formato", ""),
        "objetivo_job": data.get("objetivo_job", ""),
        "tom_especifico": data.get("tom_especifico", ""),
        "referencias": data.get("referencias", []),
        "criado_em": _ts(),
        "executado_em": None,
        "outputs": {},
        "pipeline": {
            "version": "1.0",
            "stage": "job_criado",
            "origem_da_execucao": "novo_job_manual",
            "handoffs": [],
        },
    }

    _write_json(os.path.join(jdir, "job.json"), job)
    record_client_pipeline_state(
        client_id,
        etapa_atual="job_criado",
        etapas_concluidas=["cliente_criado", "job_criado"],
        origem_da_execucao="novo_job_manual",
        job_id=job_id,
        proximo_passo_sugerido="Gerar ângulos para este job ou executar a partir da auditoria.",
    )
    return job


def get_job(client_id: str, job_id: str) -> dict:
    path = os.path.join(_job_dir(client_id, job_id), "job.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Job '{job_id}' nao encontrado para cliente '{client_id}'.")
    return _read_json(path)


def update_job(client_id: str, job_id: str, updates: dict):
    job = get_job(client_id, job_id)
    job.update(updates)
    _write_json(os.path.join(_job_dir(client_id, job_id), "job.json"), job)
    return job


def list_jobs(client_id: str) -> list:
    jobs_dir = os.path.join(_client_dir(client_id), "jobs")
    if not os.path.exists(jobs_dir):
        return []
    result = []
    for entry in sorted(os.listdir(jobs_dir), reverse=True):
        jdir = os.path.join(jobs_dir, entry)
        path = os.path.join(jdir, "job.json")
        if os.path.isdir(jdir) and os.path.exists(path):
            j = _read_json(path)
            result.append({
                "id": j.get("id", entry),
                "tipo": j.get("tipo", ""),
                "status": j.get("status", ""),
                "briefing": j.get("briefing", "")[:80],
                "criado_em": j.get("criado_em", ""),
                "pipeline_stage": (((j.get("pipeline") or {}).get("stage")) or ""),
                "origem_da_execucao": (((j.get("pipeline") or {}).get("origem_da_execucao")) or ""),
            })
    return result


def get_job_output_files(client_id: str, job_id: str) -> list:
    """Lista arquivos de output de um job."""
    jdir = _job_dir(client_id, job_id)
    result = []
    for fname in os.listdir(jdir):
        if fname != "job.json":
            fpath = os.path.join(jdir, fname)
            result.append({
                "nome": fname,
                "path": fpath,
                "tamanho": os.path.getsize(fpath),
            })
    return result


# ─── Ciclo de aprendizado ─────────────────────────────────────────────────────

def save_job_result(client_id: str, job_id: str, result_data: dict) -> dict:
    """Delegado ao job_runner para manter performance memory, portfolio e execution state em sincronia."""
    from studio.job_runner import save_job_result as _runner_save_job_result

    return _runner_save_job_result(client_id, job_id, result_data)
