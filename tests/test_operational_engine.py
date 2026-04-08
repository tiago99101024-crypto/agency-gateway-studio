import json
import os
import re
import shutil
import tempfile
import unittest
from unittest import mock

from studio import operational_engine as oe
from studio import job_runner as jr


class _PatchTs:
    def __init__(self, value: str):
        self.value = value
        self.original = oe._ts

    def __enter__(self):
        oe._ts = lambda: self.value

    def __exit__(self, exc_type, exc, tb):
        oe._ts = self.original


class OperationalEngineTests(unittest.TestCase):
    def _make_workspace_tmpdir(self):
        return tempfile.mkdtemp(dir=os.getcwd())

    def _make_state_path(self, suffix: str) -> str:
        path = os.path.join(os.getcwd(), "data", "clients", f"test-state-{suffix}", "active_creatives.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    def test_is_active_creative_valid_and_invalid(self):
        active = {
            "creative_id": "c1",
            "_missing_creative_id": False,
            "operational_decision": {"action": "scale"},
        }
        missing_id = {
            "_missing_creative_id": False,
            "operational_decision": {"action": "scale"},
        }
        missing_flag = {
            "creative_id": "c2",
            "_missing_creative_id": True,
            "operational_decision": {"action": "scale"},
        }
        killed = {
            "creative_id": "c3",
            "_missing_creative_id": False,
            "operational_decision": {"action": "kill"},
        }

        self.assertTrue(oe._is_active_creative(active))
        self.assertFalse(oe._is_active_creative(missing_id))
        self.assertFalse(oe._is_active_creative(missing_flag))
        self.assertFalse(oe._is_active_creative(killed))

    def test_is_new_creative_new_and_not_new(self):
        new_card = {
            "creative_id": "c1",
            "_missing_creative_id": False,
            "time_active_hours": 12,
            "operational_decision": {"action": "test"},
        }
        old_card = {
            "creative_id": "c2",
            "_missing_creative_id": False,
            "time_active_hours": 30,
            "operational_decision": {"action": "maintain"},
        }
        unknown_age = {
            "creative_id": "c3",
            "_missing_creative_id": False,
            "operational_decision": {"action": "scale"},
        }

        self.assertTrue(oe._is_new_creative(new_card))
        self.assertFalse(oe._is_new_creative(old_card))
        self.assertFalse(oe._is_new_creative(unknown_age))

    def test_classify_performance_trend_falling(self):
        history = [
            {"performance_score": 60, "updated_at": "2026-04-05T12:00:00Z"},
            {"performance_score": 61, "updated_at": "2026-04-05T11:00:00Z"},
            {"performance_score": 62, "updated_at": "2026-04-05T10:00:00Z"},
            {"performance_score": 63, "updated_at": "2026-04-05T09:00:00Z"},
            {"performance_score": 64, "updated_at": "2026-04-05T08:00:00Z"},
            {"performance_score": 65, "updated_at": "2026-04-05T07:00:00Z"},
            {"performance_score": 72, "updated_at": "2026-03-28T12:00:00Z"},
            {"performance_score": 73, "updated_at": "2026-03-28T11:00:00Z"},
            {"performance_score": 74, "updated_at": "2026-03-28T10:00:00Z"},
            {"performance_score": 75, "updated_at": "2026-03-28T09:00:00Z"},
            {"performance_score": 76, "updated_at": "2026-03-28T08:00:00Z"},
            {"performance_score": 77, "updated_at": "2026-03-28T07:00:00Z"},
        ]
        with _PatchTs("2026-04-05T12:30:00Z"):
            self.assertEqual(oe._classify_performance_trend(history), "caindo")

    def test_build_trend_history_without_previous_history(self):
        cards = [
            {"creative_id": "c1", "_missing_creative_id": False, "performance_score": 70, "operational_decision": {"action": "scale"}},
            {"creative_id": "c2", "_missing_creative_id": False, "performance_score": 60, "operational_decision": {"action": "test"}},
            {"creative_id": "", "_missing_creative_id": False, "performance_score": 90, "operational_decision": {"action": "scale"}},
        ]
        history = oe._build_trend_history([], cards, "2026-04-05T12:00:00Z", cycle_id="run-1")

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["source"], "current_cycle")
        self.assertEqual(history[0]["updated_at"], "2026-04-05T12:00:00Z")
        self.assertEqual(history[0]["cycle_id"], "run-1")

    def test_build_trend_history_ignores_corrupted_previous_history(self):
        previous_history = [
            {"creative_id": "ok-1", "performance_score": 70, "updated_at": "2026-04-04T12:00:00Z", "source": "execution_state"},
            {"creative_id": "", "performance_score": 65, "updated_at": "2026-04-04T11:00:00Z", "source": "execution_state"},
            {"creative_id": "bad-ts", "performance_score": 60, "updated_at": "invalid", "source": "execution_state"},
            {"creative_id": "bad-score", "performance_score": "x", "updated_at": "2026-04-04T10:00:00Z", "source": "execution_state"},
            "broken",
        ]
        cards = [
            {"creative_id": "ok-2", "_missing_creative_id": False, "performance_score": 80, "operational_decision": {"action": "maintain"}},
        ]
        history = oe._build_trend_history(previous_history, cards, "2026-04-05T12:00:00Z", cycle_id="run-2")

        self.assertEqual(len(history), 2)
        self.assertEqual({item["creative_id"] for item in history}, {"ok-1", "ok-2"})
        self.assertEqual({item["source"] for item in history}, {"execution_state", "current_cycle"})

    def test_classify_performance_trend_with_insufficient_explicit_history_is_stable(self):
        history = [
            {"creative_id": "c1", "performance_score": 70, "updated_at": "2026-04-05T12:00:00Z", "source": "execution_state"},
            {"creative_id": "c2", "performance_score": 71, "updated_at": "2026-04-05T11:00:00Z", "source": "execution_state"},
            {"creative_id": "c3", "performance_score": 69, "updated_at": "2026-03-28T12:00:00Z", "source": "execution_state"},
            {"creative_id": "c4", "performance_score": 70, "updated_at": "2026-03-28T11:00:00Z", "source": "execution_state"},
        ]
        with _PatchTs("2026-04-05T12:30:00Z"):
            self.assertEqual(oe._classify_performance_trend(history), "estavel")

    def test_build_trend_history_dedupes_by_creative_id_and_updated_at(self):
        previous_history = [
            {"creative_id": "c1", "performance_score": 70, "updated_at": "2026-04-04T12:00:00Z", "source": "execution_state"},
            {"creative_id": "c1", "performance_score": 70, "updated_at": "2026-04-04T12:00:00Z", "source": "execution_state"},
            {"creative_id": "c2", "performance_score": 60, "updated_at": "2026-04-04T11:00:00Z", "source": "execution_state"},
        ]

        history = oe._build_trend_history(previous_history, [], "2026-04-05T12:00:00Z", cycle_id="run-3")

        self.assertEqual(len(history), 2)
        self.assertEqual(
            [(item["creative_id"], item["updated_at"]) for item in history],
            [("c1", "2026-04-04T12:00:00Z"), ("c2", "2026-04-04T11:00:00Z")],
        )

    def test_build_trend_history_rerun_same_cycle_does_not_duplicate(self):
        previous_history = [
            {"creative_id": "c1", "performance_score": 70, "updated_at": "2026-04-05T12:00:00Z", "source": "execution_state", "cycle_id": "run-same"},
        ]
        cards = [
            {"creative_id": "c1", "_missing_creative_id": False, "performance_score": 70, "operational_decision": {"action": "scale"}},
        ]

        history = oe._build_trend_history(previous_history, cards, "2026-04-05T12:00:00Z", cycle_id="run-same")

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["source"], "execution_state")

    def test_build_trend_history_same_second_different_cycles_stay_distinct(self):
        previous_history = [
            {"creative_id": "c1", "performance_score": 70, "updated_at": "2026-04-05T12:00:00Z", "source": "execution_state", "cycle_id": "run-a"},
        ]
        cards = [
            {"creative_id": "c1", "_missing_creative_id": False, "performance_score": 71, "operational_decision": {"action": "scale"}},
        ]

        history = oe._build_trend_history(previous_history, cards, "2026-04-05T12:00:00Z", cycle_id="run-b")

        self.assertEqual(len(history), 2)
        self.assertEqual({item["cycle_id"] for item in history}, {"run-a", "run-b"})

    def test_build_trend_history_duplicate_real_record_is_removed(self):
        previous_history = [
            {"creative_id": "c1", "performance_score": 70, "updated_at": "2026-04-05T12:00:00Z", "source": "execution_state", "cycle_id": "run-a"},
            {"creative_id": "c1", "performance_score": 70, "updated_at": "2026-04-05T12:00:00Z", "source": "replay", "cycle_id": "run-a"},
        ]

        history = oe._build_trend_history(previous_history, [], "2026-04-05T12:00:00Z", cycle_id="run-x")

        self.assertEqual(len(history), 1)

    def test_build_trend_history_preserves_valid_source_and_marks_unknown_as_migrated(self):
        previous_history = [
            {"creative_id": "c1", "performance_score": 70, "updated_at": "2026-04-04T12:00:00Z", "source": "replay"},
            {"creative_id": "c2", "performance_score": 60, "updated_at": "2026-04-04T11:00:00Z", "source": "legacy-import"},
        ]

        history = oe._build_trend_history(previous_history, [], "2026-04-05T12:00:00Z")

        by_id = {item["creative_id"]: item for item in history}
        self.assertEqual(by_id["c1"]["source"], "replay")
        self.assertEqual(by_id["c2"]["source"], "migrated")

    def test_sanitize_trend_history_applies_temporal_and_size_retention(self):
        records = []
        for idx in range(65):
            day = 30 - (idx % 30)
            hour = idx % 24
            records.append({
                "creative_id": f"c{idx}",
                "performance_score": 60 + idx,
                "updated_at": f"2026-03-{day:02d}T{hour:02d}:00:00Z",
                "source": "execution_state",
            })
        records.append({
            "creative_id": "too-old",
            "performance_score": 10,
            "updated_at": "2026-02-01T12:00:00Z",
            "source": "execution_state",
        })

        with _PatchTs("2026-04-05T12:30:00Z"):
            history = oe._sanitize_trend_history(records)

        self.assertLessEqual(len(history), oe.TREND_HISTORY_MAX_ITEMS)
        self.assertNotIn("too-old", {item["creative_id"] for item in history})

    def test_extract_block_and_validate_copy_structure_accept_real_cta_output(self):
        raw_output = """HEADLINE:  
Você perde 27% da margem para o app

CTA:  
Peca direto no WhatsApp

VISUAL_BRIEF:  
- cena: smartphone frontal com tela exibindo lista de pedidos e valores de comissão do delivery app  
- composicao: vertical 4:5, número "27%" laranja enorme no topo ocupando 28% da altura, headline branca centralizada logo abaixo ocupando 12% da altura, celular frontal centralizado ocupando entre 38% e 42% da altura, espaço vazio entre headline e celular e nas laterais do celular, faixa preta no rodapé com CTA centralizado ocupando 12% da altura  
- estilo_visual: imagem estática, fundo preto liso (#111111), número 27% em laranja vibrante (#FF6B35) com fonte Montserrat Bold, texto da headline e CTA em branco creme (#F7F3E8) com fonte Poppins SemiBold, alto contraste, sem texturas ou elementos extras, visual comercial direto e rígido  
- alinhamento_brand: aplicação rigorosa das cores da marca (#FF6B35, #111111, #F7F3E8), tipografia Montserrat Bold para número e Poppins SemiBold para texto, composição limpa, rígida e altamente legível reforçando a mensagem direta e comercial

SEO_KEYWORDS_PRINCIPAIS:  
- comissao app delivery  
- pedido direto whatsapp

SEO_KEYWORDS_SECUNDARIAS:  
- delivery pizza artesanal  
- reduzir comissao ifood

HASHTAGS:  
- #delivery  
- #pizzasempre  
- #pedidoja  
- #parcelivre  
- #comissaoliquida"""

        self.assertEqual(jr._extract_block(raw_output, "CTA"), "Peca direto no WhatsApp")
        structure = jr._validate_copy_structure(raw_output)
        self.assertTrue(structure["ok"])
        self.assertNotIn("CTA", structure["missing_blocks"])

    def test_tokenize_accepts_real_replay_text_and_legacy_range_would_break(self):
        legacy_pattern = r"[a-zA-ZÃ€-Ã¿0-9]+"
        replay_text = "VocÃª perde 27% da margem para o app"

        with self.assertRaises(re.error):
            re.findall(legacy_pattern, replay_text.lower())

        self.assertEqual(
            jr._tokenize(replay_text),
            ["vocãª", "perde", "27", "da", "margem", "para", "o", "app"],
        )

    def test_execute_post_estatico_copy_cycle_uses_replay_raw_output_without_provider_call(self):
        replay_raw_output = """HEADLINE:  
VocÃª perde 27% da margem para o app

CTA:  
Peca direto no WhatsApp

VISUAL_BRIEF:  
- cena: smartphone frontal mostrando app de delivery com lista de pedido e comissao destacada, tela legivel e limpa, sem elementos extras  
- composicao: vertical 4:5, numero 27% em laranja enorme no topo ocupando 28% da altura, headline branca centralizada logo abaixo em duas linhas, smartphone centralizado ocupando 40% da altura, espaco em preto liso nas laterais e entre headline e celular, faixa horizontal no rodape com CTA em fundo liso preto e texto em branco, tudo alinhado rigidamente e simetrico  
- estilo_visual: design grafico plano, fundo preto liso, alto contraste, tipografia Montserrat Bold para numero e headline, Poppins SemiBold para CTA, cores da marca usadas com precisao, luz neutra, sem texturas ou sombras  
- alinhamento_brand: aplicacao estrita das cores da marca, tipografia Montserrat Bold e Poppins SemiBold conforme identidade, composicao rigida e mecanica, evitando qualquer elemento adicional fora do briefing

SEO_KEYWORDS_PRINCIPAIS:  
- comissao app delivery

SEO_KEYWORDS_SECUNDARIAS:  
- pedido direto whatsapp

HASHTAGS:  
- #delivery"""

        tmpdir = self._make_workspace_tmpdir()
        self.addCleanup(lambda: shutil.rmtree(tmpdir, ignore_errors=True))
        job = {"id": "job-replay", "tipo": "post_estatico"}
        angle = {"nome": "Angulo", "headline_exemplo": "VocÃª perde 27% da margem para o app"}

        with mock.patch.object(jr, "_build_post_estatico_prompt", return_value=("PROMPT VISUAL", "", "", {"cliente": {}})), \
             mock.patch.object(jr, "_invoke_with_retries", side_effect=AssertionError("provider nao deveria ser chamado no replay")), \
             mock.patch.object(jr, "_persist_attempt_log"), \
             mock.patch.object(jr, "_ensure_copy_seo", side_effect=lambda text, *_args, **_kwargs: (text, {})), \
             mock.patch.object(jr, "_validate_copy_contract", return_value={"ok": True, "issues": []}), \
             mock.patch.object(jr, "_build_creative_summary", return_value={
                 "headline": "VocÃª perde 27% da margem para o app",
                 "subheadline": "",
                 "cta": "Peca direto no WhatsApp",
                 "visual_direction": "",
                 "creative_id": "creative-replay",
             }), \
             mock.patch.object(jr, "_standardize_image_prompts", return_value={"prompt_dalle": "prompt", "_fallback": False}), \
             mock.patch.object(jr, "_validate_image_contract", return_value={"ok": True, "issues": []}), \
             mock.patch.object(jr, "_validate_visual_identity_usage", return_value={"ok": True, "issues": []}), \
             mock.patch.object(jr, "_persist_visual_generation_trace"), \
             mock.patch.object(jr, "_write_json_file"), \
             mock.patch.object(jr, "_write"):
            cycle = jr._execute_post_estatico_copy_cycle(
                ctx="CTX",
                job=job,
                jdir=tmpdir,
                angle=angle,
                plan=None,
                client_id="client-replay",
                visual_replay_raw_output=replay_raw_output,
            )

        self.assertTrue(cycle["replay_used"])
        self.assertEqual(cycle["provider_result"]["provider_used"], "replay_visual_smoke")
        self.assertEqual(cycle["provider_raw_output"], replay_raw_output.strip())
        self.assertEqual(cycle["visual_prompt"], "PROMPT VISUAL")
        self.assertEqual(cycle["summary"]["cta"], "Peca direto no WhatsApp")
        self.assertIn("smartphone frontal mostrando app de delivery", cycle["visual_brief"])

    def test_generate_image_accepts_placeholder_only_when_explicitly_allowed(self):
        tmpdir = self._make_workspace_tmpdir()
        self.addCleanup(lambda: shutil.rmtree(tmpdir, ignore_errors=True))
        output_path = os.path.join(tmpdir, "output_image.png")
        placeholder_result = {
            "output_path": output_path,
            "provider_used": "local_placeholder",
            "model_used": "none",
            "fallback_used": True,
            "error": "OPENAI_API_KEY nao definido.",
        }

        with mock.patch("adapters.image_provider.generate_image_from_prompt", return_value=placeholder_result):
            with self.assertRaisesRegex(ValueError, "Geracao de imagem real indisponivel"):
                jr._generate_image(tmpdir, "output_image.png", {"prompt_dalle": "prompt"}, "1:1")

        with mock.patch("adapters.image_provider.generate_image_from_prompt", return_value=placeholder_result):
            result = jr._generate_image(
                tmpdir,
                "output_image.png",
                {"prompt_dalle": "prompt"},
                "1:1",
                allow_placeholder=True,
            )

        self.assertEqual(result["provider_used"], "local_placeholder")
        self.assertTrue(result["fallback_used"])

    def test_classify_performance_trend_stable(self):
        history = [
            {"performance_score": 67, "updated_at": "2026-04-05T12:00:00Z"},
            {"performance_score": 68, "updated_at": "2026-04-05T11:00:00Z"},
            {"performance_score": 66, "updated_at": "2026-04-05T10:00:00Z"},
            {"performance_score": 69, "updated_at": "2026-04-04T12:00:00Z"},
            {"performance_score": 68, "updated_at": "2026-04-04T11:00:00Z"},
            {"performance_score": 67, "updated_at": "2026-04-04T10:00:00Z"},
        ]
        with _PatchTs("2026-04-05T12:30:00Z"):
            self.assertEqual(oe._classify_performance_trend(history), "estavel")

    def test_classify_performance_trend_rising(self):
        history = [
            {"performance_score": 78, "updated_at": "2026-04-05T12:00:00Z"},
            {"performance_score": 79, "updated_at": "2026-04-05T11:00:00Z"},
            {"performance_score": 80, "updated_at": "2026-04-05T10:00:00Z"},
            {"performance_score": 81, "updated_at": "2026-04-05T09:00:00Z"},
            {"performance_score": 82, "updated_at": "2026-04-05T08:00:00Z"},
            {"performance_score": 83, "updated_at": "2026-04-05T07:00:00Z"},
            {"performance_score": 66, "updated_at": "2026-03-28T12:00:00Z"},
            {"performance_score": 67, "updated_at": "2026-03-28T11:00:00Z"},
            {"performance_score": 68, "updated_at": "2026-03-28T10:00:00Z"},
            {"performance_score": 69, "updated_at": "2026-03-28T09:00:00Z"},
            {"performance_score": 70, "updated_at": "2026-03-28T08:00:00Z"},
            {"performance_score": 71, "updated_at": "2026-03-28T07:00:00Z"},
        ]
        with _PatchTs("2026-04-05T12:30:00Z"):
            self.assertEqual(oe._classify_performance_trend(history), "subindo")

    def test_compute_exploration_envelope_clamp_max_and_smoothing(self):
        cards = [
            {"creative_id": "c1", "_missing_creative_id": False, "time_active_hours": 10, "operational_decision": {"action": "test"}},
            {"creative_id": "c2", "_missing_creative_id": False, "time_active_hours": 12, "operational_decision": {"action": "maintain"}},
        ]
        history = [
            {"performance_score": 50, "updated_at": "2026-04-05T12:00:00Z"},
            {"performance_score": 51, "updated_at": "2026-04-05T11:00:00Z"},
            {"performance_score": 49, "updated_at": "2026-04-05T10:00:00Z"},
            {"performance_score": 52, "updated_at": "2026-04-05T09:00:00Z"},
            {"performance_score": 50, "updated_at": "2026-04-05T08:00:00Z"},
            {"performance_score": 51, "updated_at": "2026-04-05T07:00:00Z"},
            {"performance_score": 80, "updated_at": "2026-03-28T12:00:00Z"},
            {"performance_score": 81, "updated_at": "2026-03-28T11:00:00Z"},
            {"performance_score": 79, "updated_at": "2026-03-28T10:00:00Z"},
            {"performance_score": 82, "updated_at": "2026-03-28T09:00:00Z"},
            {"performance_score": 80, "updated_at": "2026-03-28T08:00:00Z"},
            {"performance_score": 81, "updated_at": "2026-03-28T07:00:00Z"},
        ]
        with _PatchTs("2026-04-05T12:30:00Z"):
            result = oe._compute_exploration_envelope(cards, history, previous_envelope=0.12, refresh_allowed=True)

        self.assertEqual(result["performance_trend"], "caindo")
        self.assertEqual(result["active_count"], 2)
        self.assertTrue(result["has_new_creative"])
        self.assertAlmostEqual(result["target_envelope"], 0.17, places=4)
        self.assertAlmostEqual(result["exploration_envelope"], 0.135, places=4)

    def test_compute_exploration_envelope_clamp_min(self):
        cards = [
            {"creative_id": "c1", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "scale"}},
            {"creative_id": "c2", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "scale"}},
            {"creative_id": "c3", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "maintain"}},
            {"creative_id": "c4", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "maintain"}},
            {"creative_id": "c5", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "test"}},
        ]
        history = [
            {"performance_score": 90, "updated_at": "2026-04-05T12:00:00Z"},
            {"performance_score": 91, "updated_at": "2026-04-05T11:00:00Z"},
            {"performance_score": 89, "updated_at": "2026-04-05T10:00:00Z"},
            {"performance_score": 92, "updated_at": "2026-04-05T09:00:00Z"},
            {"performance_score": 90, "updated_at": "2026-04-05T08:00:00Z"},
            {"performance_score": 91, "updated_at": "2026-04-05T07:00:00Z"},
            {"performance_score": 70, "updated_at": "2026-03-28T12:00:00Z"},
            {"performance_score": 71, "updated_at": "2026-03-28T11:00:00Z"},
            {"performance_score": 69, "updated_at": "2026-03-28T10:00:00Z"},
            {"performance_score": 72, "updated_at": "2026-03-28T09:00:00Z"},
            {"performance_score": 70, "updated_at": "2026-03-28T08:00:00Z"},
            {"performance_score": 71, "updated_at": "2026-03-28T07:00:00Z"},
        ]
        with _PatchTs("2026-04-05T12:30:00Z"):
            result = oe._compute_exploration_envelope(cards, history, previous_envelope=0.06, refresh_allowed=True)

        self.assertEqual(result["performance_trend"], "subindo")
        self.assertAlmostEqual(result["target_envelope"], 0.08, places=4)
        self.assertAlmostEqual(result["exploration_envelope"], 0.066, places=4)

    def test_compute_exploration_envelope_freeze_keeps_previous(self):
        cards = [
            {"creative_id": "c1", "_missing_creative_id": False, "time_active_hours": 10, "operational_decision": {"action": "test"}},
        ]
        history = [
            {"performance_score": 40, "updated_at": "2026-04-05T12:00:00Z"},
            {"performance_score": 41, "updated_at": "2026-04-05T11:00:00Z"},
            {"performance_score": 39, "updated_at": "2026-04-05T10:00:00Z"},
            {"performance_score": 42, "updated_at": "2026-04-05T09:00:00Z"},
            {"performance_score": 40, "updated_at": "2026-04-05T08:00:00Z"},
            {"performance_score": 41, "updated_at": "2026-04-05T07:00:00Z"},
            {"performance_score": 70, "updated_at": "2026-03-28T12:00:00Z"},
            {"performance_score": 71, "updated_at": "2026-03-28T11:00:00Z"},
            {"performance_score": 69, "updated_at": "2026-03-28T10:00:00Z"},
            {"performance_score": 72, "updated_at": "2026-03-28T09:00:00Z"},
            {"performance_score": 70, "updated_at": "2026-03-28T08:00:00Z"},
            {"performance_score": 71, "updated_at": "2026-03-28T07:00:00Z"},
        ]
        with _PatchTs("2026-04-05T12:30:00Z"):
            result = oe._compute_exploration_envelope(cards, history, previous_envelope=0.18, refresh_allowed=False)

        self.assertFalse(result["refresh_allowed"])
        self.assertAlmostEqual(result["exploration_envelope"], 0.18, places=4)
        self.assertAlmostEqual(result["target_envelope"], 0.18, places=4)

    def test_compute_exploration_envelope_insufficient_history_is_stable(self):
        cards = [
            {"creative_id": "c1", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "maintain"}},
            {"creative_id": "c2", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "test"}},
            {"creative_id": "c3", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "scale"}},
        ]
        history = [
            {"performance_score": 60, "updated_at": "2026-04-05T12:00:00Z"},
            {"performance_score": 61, "updated_at": "2026-04-05T11:00:00Z"},
            {"performance_score": 62, "updated_at": "2026-04-04T12:00:00Z"},
            {"performance_score": 63, "updated_at": "2026-04-04T11:00:00Z"},
        ]
        with _PatchTs("2026-04-05T12:30:00Z"):
            result = oe._compute_exploration_envelope(cards, history, previous_envelope=0.12, refresh_allowed=True)

        self.assertEqual(result["performance_trend"], "estavel")
        self.assertAlmostEqual(result["target_envelope"], 0.15, places=4)
        self.assertAlmostEqual(result["exploration_envelope"], 0.129, places=4)

    def test_compute_exploration_envelope_cycle_1_base_value(self):
        cards = [
            {"creative_id": "c1", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "scale"}},
            {"creative_id": "c2", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "maintain"}},
            {"creative_id": "c3", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "maintain"}},
            {"creative_id": "c4", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "test"}},
            {"creative_id": "c5", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "scale"}},
        ]
        history = [
            {"performance_score": 70, "updated_at": "2026-04-05T12:00:00Z"},
            {"performance_score": 69, "updated_at": "2026-04-05T11:00:00Z"},
            {"performance_score": 71, "updated_at": "2026-04-05T10:00:00Z"},
            {"performance_score": 70, "updated_at": "2026-03-28T12:00:00Z"},
            {"performance_score": 69, "updated_at": "2026-03-28T11:00:00Z"},
            {"performance_score": 71, "updated_at": "2026-03-28T10:00:00Z"},
        ]
        with _PatchTs("2026-04-05T12:30:00Z"):
            result = oe._compute_exploration_envelope(cards, history, previous_envelope=0.12, refresh_allowed=True)

        self.assertEqual(result["performance_trend"], "estavel")
        self.assertAlmostEqual(result["target_envelope"], 0.12, places=4)
        self.assertAlmostEqual(result["exploration_envelope"], 0.12, places=4)

    def test_compute_exploration_envelope_cycle_2_uses_previous_value_with_falling_trend(self):
        cards = [
            {"creative_id": "c1", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "scale"}},
            {"creative_id": "c2", "_missing_creative_id": False, "time_active_hours": 12, "operational_decision": {"action": "test"}},
            {"creative_id": "c3", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "maintain"}},
        ]
        history = [
            {"performance_score": 55, "updated_at": "2026-04-06T12:00:00Z"},
            {"performance_score": 54, "updated_at": "2026-04-06T11:00:00Z"},
            {"performance_score": 56, "updated_at": "2026-04-06T10:00:00Z"},
            {"performance_score": 57, "updated_at": "2026-04-06T09:00:00Z"},
            {"performance_score": 55, "updated_at": "2026-04-06T08:00:00Z"},
            {"performance_score": 56, "updated_at": "2026-04-06T07:00:00Z"},
            {"performance_score": 80, "updated_at": "2026-03-29T12:00:00Z"},
            {"performance_score": 81, "updated_at": "2026-03-29T11:00:00Z"},
            {"performance_score": 79, "updated_at": "2026-03-29T10:00:00Z"},
            {"performance_score": 82, "updated_at": "2026-03-29T09:00:00Z"},
            {"performance_score": 80, "updated_at": "2026-03-29T08:00:00Z"},
            {"performance_score": 81, "updated_at": "2026-03-29T07:00:00Z"},
        ]
        previous_envelope = 0.12
        with _PatchTs("2026-04-06T12:30:00Z"):
            result = oe._compute_exploration_envelope(cards, history, previous_envelope=previous_envelope, refresh_allowed=True)

        self.assertEqual(result["performance_trend"], "caindo")
        self.assertAlmostEqual(result["target_envelope"], 0.17, places=4)
        self.assertAlmostEqual(result["exploration_envelope"], 0.135, places=4)
        self.assertEqual(previous_envelope, 0.12)

    def test_compute_exploration_envelope_cycle_3_uses_previous_value_with_rising_trend(self):
        cards = [
            {"creative_id": "c1", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "scale"}},
            {"creative_id": "c2", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "test"}},
            {"creative_id": "c3", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "maintain"}},
        ]
        history = [
            {"performance_score": 90, "updated_at": "2026-04-07T12:00:00Z"},
            {"performance_score": 91, "updated_at": "2026-04-07T11:00:00Z"},
            {"performance_score": 89, "updated_at": "2026-04-07T10:00:00Z"},
            {"performance_score": 92, "updated_at": "2026-04-07T09:00:00Z"},
            {"performance_score": 90, "updated_at": "2026-04-07T08:00:00Z"},
            {"performance_score": 91, "updated_at": "2026-04-07T07:00:00Z"},
            {"performance_score": 70, "updated_at": "2026-03-30T12:00:00Z"},
            {"performance_score": 71, "updated_at": "2026-03-30T11:00:00Z"},
            {"performance_score": 69, "updated_at": "2026-03-30T10:00:00Z"},
            {"performance_score": 72, "updated_at": "2026-03-30T09:00:00Z"},
            {"performance_score": 70, "updated_at": "2026-03-30T08:00:00Z"},
            {"performance_score": 71, "updated_at": "2026-03-30T07:00:00Z"},
        ]
        previous_envelope = 0.135
        with _PatchTs("2026-04-07T12:30:00Z"):
            result = oe._compute_exploration_envelope(cards, history, previous_envelope=previous_envelope, refresh_allowed=True)

        self.assertEqual(result["performance_trend"], "subindo")
        self.assertAlmostEqual(result["target_envelope"], 0.11, places=4)
        self.assertAlmostEqual(result["exploration_envelope"], 0.1275, places=4)
        self.assertEqual(previous_envelope, 0.135)

    def test_compute_exploration_envelope_freeze_reuses_previous_value_without_recalculation(self):
        cards = [
            {"creative_id": "c1", "_missing_creative_id": False, "time_active_hours": 10, "operational_decision": {"action": "test"}},
            {"creative_id": "c2", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "scale"}},
        ]
        history = [
            {"performance_score": 40, "updated_at": "2026-04-08T12:00:00Z"},
            {"performance_score": 41, "updated_at": "2026-04-08T11:00:00Z"},
            {"performance_score": 39, "updated_at": "2026-04-08T10:00:00Z"},
            {"performance_score": 70, "updated_at": "2026-03-31T12:00:00Z"},
            {"performance_score": 71, "updated_at": "2026-03-31T11:00:00Z"},
            {"performance_score": 69, "updated_at": "2026-03-31T10:00:00Z"},
        ]
        previous_envelope = 0.1305
        with _PatchTs("2026-04-08T12:30:00Z"):
            result = oe._compute_exploration_envelope(cards, history, previous_envelope=previous_envelope, refresh_allowed=False)

        self.assertFalse(result["refresh_allowed"])
        self.assertAlmostEqual(result["target_envelope"], previous_envelope, places=4)
        self.assertAlmostEqual(result["exploration_envelope"], previous_envelope, places=4)

    def test_apply_missing_creative_id_guard_blocks_card_consistently(self):
        card = {"job_id": "job-1", "portfolio_action": "entrar", "portfolio_decision": "subir"}
        original_operational = {"action": "scale", "budget_change": 0.3, "priority": 88, "reason": "ok"}

        guarded_card, guarded_operational = oe._apply_missing_creative_id_guard(card, original_operational)

        self.assertTrue(guarded_card["_missing_creative_id"])
        self.assertEqual(guarded_operational["action"], "kill")
        self.assertEqual(guarded_operational["priority"], 0)
        self.assertEqual(guarded_operational["budget_change"], -1.0)
        self.assertIn("creative_id ausente", guarded_operational["reason"])
        self.assertEqual(guarded_card["priority"], 0)
        self.assertEqual(guarded_card["allocated_budget"], 0.0)
        self.assertEqual(guarded_card["budget_share"], 0.0)
        self.assertEqual(guarded_card["portfolio_action"], "descartar")
        self.assertEqual(guarded_card["portfolio_decision"], "descartar")

    def test_apply_missing_creative_id_guard_does_not_leak_mutation_between_cards(self):
        shared_operational = {"action": "scale", "budget_change": 0.3, "priority": 90, "reason": "baseline"}

        card_missing = {}
        _, mutated_operational = oe._apply_missing_creative_id_guard(card_missing, shared_operational)
        card_ok = {"creative_id": "creative-1"}
        _, untouched_operational = oe._apply_missing_creative_id_guard(card_ok, shared_operational)

        self.assertEqual(shared_operational["action"], "scale")
        self.assertEqual(shared_operational["priority"], 90)
        self.assertEqual(mutated_operational["action"], "kill")
        self.assertEqual(untouched_operational["action"], "scale")
        self.assertFalse(card_ok["_missing_creative_id"])

    def test_decide_creative_action_recovered_item_does_not_scale_and_loses_priority(self):
        base = {
            "performance_score": 85,
            "penalty_strength": 0.1,
            "confidence_score": 0.8,
            "stability_score": 0.9,
        }

        normal = oe._decide_creative_action(base)
        recovered = oe._decide_creative_action({**base, "_id_recovered": True})

        self.assertEqual(normal["action"], "scale")
        self.assertEqual(recovered["action"], "maintain")
        self.assertLess(recovered["priority"], normal["priority"])

    def test_portfolio_rank_key_prefers_priority_over_portfolio_score(self):
        higher_priority = {
            "portfolio_score": 70,
            "operational_decision": {"priority": 80},
        }
        higher_score = {
            "portfolio_score": 95,
            "operational_decision": {"priority": 40},
        }

        ranked = sorted([higher_score, higher_priority], key=oe._portfolio_rank_key, reverse=True)
        self.assertIs(ranked[0], higher_priority)

    def test_should_refresh_allocation_without_timestamp(self):
        self.assertTrue(oe._should_refresh_allocation({}, 10))

    def test_should_refresh_allocation_with_invalid_timestamp(self):
        self.assertTrue(oe._should_refresh_allocation({"allocation_last_updated_at": "invalid"}, 10))

    def test_should_refresh_allocation_with_strong_priority_delta(self):
        card = {
            "allocation_last_updated_at": "2026-04-05T09:00:00Z",
            "_previous_allocation_priority": 10,
        }
        with _PatchTs("2026-04-05T10:00:00Z"):
            self.assertTrue(oe._should_refresh_allocation(card, 35))

    def test_should_refresh_allocation_after_six_hours(self):
        card = {
            "allocation_last_updated_at": "2026-04-05T03:00:00Z",
            "_previous_allocation_priority": 10,
        }
        with _PatchTs("2026-04-05T09:30:00Z"):
            self.assertTrue(oe._should_refresh_allocation(card, 15))

    def test_should_refresh_allocation_stays_frozen_inside_window(self):
        card = {
            "allocation_last_updated_at": "2026-04-05T08:00:00Z",
            "_previous_allocation_priority": 50,
        }
        with _PatchTs("2026-04-05T11:00:00Z"):
            self.assertFalse(oe._should_refresh_allocation(card, 55))

    def test_allocate_creative_budget_keeps_existing_share_when_refresh_false(self):
        creatives = [
            {
                "creative_id": "locked",
                "operational_decision": {"action": "maintain", "priority": 50},
                "budget_share": 0.3,
                "allocated_budget": 300.0,
                "allocation_last_updated_at": "2026-04-05T08:00:00Z",
                "_previous_allocation_priority": 45,
            },
            {
                "creative_id": "fresh",
                "operational_decision": {"action": "scale", "priority": 100},
            },
        ]
        with _PatchTs("2026-04-05T11:00:00Z"):
            allocated = oe._allocate_creative_budget(creatives, 1000.0)

        by_id = {item["creative_id"]: item for item in allocated}
        self.assertAlmostEqual(by_id["locked"]["budget_share"], 0.3, places=6)
        self.assertAlmostEqual(by_id["locked"]["allocated_budget"], 300.0, places=2)
        self.assertAlmostEqual(sum(item["budget_share"] for item in allocated), 1.0, places=6)

    def test_allocate_creative_budget_kill_gets_zero_and_total_share_closes(self):
        creatives = [
            {"creative_id": "scale", "operational_decision": {"action": "scale", "priority": 80}},
            {"creative_id": "maintain", "operational_decision": {"action": "maintain", "priority": 60}},
            {"creative_id": "kill", "operational_decision": {"action": "kill", "priority": 999}},
        ]
        with _PatchTs("2026-04-05T12:00:00Z"):
            allocated = oe._allocate_creative_budget(creatives, 1000.0)

        by_id = {item["creative_id"]: item for item in allocated}
        self.assertEqual(by_id["kill"]["budget_share"], 0.0)
        self.assertEqual(by_id["kill"]["allocated_budget"], 0.0)
        self.assertAlmostEqual(sum(item["budget_share"] for item in allocated), 1.0, places=6)

    def test_allocate_creative_budget_respects_test_minimum_and_action_weights(self):
        creatives = [
            {"creative_id": "scale", "operational_decision": {"action": "scale", "priority": 100}},
            {"creative_id": "maintain", "operational_decision": {"action": "maintain", "priority": 70}},
            {"creative_id": "test", "operational_decision": {"action": "test", "priority": 1}},
        ]
        with _PatchTs("2026-04-05T12:00:00Z"):
            allocated = oe._allocate_creative_budget(creatives, 1000.0)

        by_id = {item["creative_id"]: item for item in allocated}
        self.assertGreaterEqual(by_id["test"]["budget_share"], 0.05)
        self.assertGreater(by_id["scale"]["budget_share"], by_id["maintain"]["budget_share"])
        self.assertGreater(by_id["maintain"]["budget_share"], by_id["test"]["budget_share"])
        self.assertAlmostEqual(sum(item["budget_share"] for item in allocated), 1.0, places=6)

    def test_allocate_creative_budget_budget_key_stays_stable_across_passes(self):
        creatives = [
            {"operational_decision": {"action": "maintain", "priority": 10}},
        ]
        with _PatchTs("2026-04-05T12:00:00Z"):
            first = oe._allocate_creative_budget(creatives, 100.0)
        with _PatchTs("2026-04-05T13:00:00Z"):
            second = oe._allocate_creative_budget(first, 100.0)

        self.assertEqual(first[0]["_budget_key"], second[0]["_budget_key"])

    def test_allocate_creative_budget_stress_freeze_kill_sum_and_caps(self):
        creatives = [
            {
                "creative_id": "locked-scale",
                "operational_decision": {"action": "scale", "priority": 95},
                "budget_share": 0.22,
                "allocated_budget": 220.0,
                "allocation_last_updated_at": "2026-04-05T08:30:00Z",
                "_previous_allocation_priority": 90,
            },
            {
                "creative_id": "locked-test",
                "operational_decision": {"action": "test", "priority": 30},
                "budget_share": 0.08,
                "allocated_budget": 80.0,
                "allocation_last_updated_at": "2026-04-05T08:30:00Z",
                "_previous_allocation_priority": 25,
            },
            {"creative_id": "scale-1", "operational_decision": {"action": "scale", "priority": 52}},
            {"creative_id": "scale-2", "operational_decision": {"action": "scale", "priority": 51}},
            {"creative_id": "maintain-1", "operational_decision": {"action": "maintain", "priority": 50}},
            {"creative_id": "maintain-2", "operational_decision": {"action": "maintain", "priority": 49}},
            {"creative_id": "test-1", "operational_decision": {"action": "test", "priority": 48}},
            {"creative_id": "test-2", "operational_decision": {"action": "test", "priority": 47}},
            {"creative_id": "test-3", "operational_decision": {"action": "test", "priority": 46}},
            {"creative_id": "kill-1", "operational_decision": {"action": "kill", "priority": 99}},
            {"creative_id": "kill-2", "operational_decision": {"action": "kill", "priority": 60}},
            {"creative_id": "zero-priority", "operational_decision": {"action": "maintain", "priority": 0}},
        ]

        with _PatchTs("2026-04-05T12:00:00Z"):
            allocated = oe._allocate_creative_budget(creatives, 1000.0)

        by_id = {item["creative_id"]: item for item in allocated}
        self.assertAlmostEqual(sum(item["budget_share"] for item in allocated), 1.0, places=6)
        self.assertAlmostEqual(by_id["locked-scale"]["budget_share"], 0.22, places=6)
        self.assertAlmostEqual(by_id["locked-test"]["budget_share"], 0.08, places=6)
        self.assertEqual(by_id["kill-1"]["budget_share"], 0.0)
        self.assertEqual(by_id["kill-2"]["budget_share"], 0.0)
        self.assertEqual(by_id["zero-priority"]["budget_share"], 0.0)
        self.assertAlmostEqual(
            by_id["test-1"]["budget_share"] + by_id["test-2"]["budget_share"] + by_id["test-3"]["budget_share"],
            0.084,
            places=6,
        )
        self.assertLessEqual(by_id["scale-1"]["budget_share"], 0.4)
        self.assertLessEqual(by_id["scale-2"]["budget_share"], 0.4)

    def test_allocate_creative_budget_stress_performance_monotonicity_under_close_priorities(self):
        creatives = [
            {"creative_id": "scale-52", "operational_decision": {"action": "scale", "priority": 52}},
            {"creative_id": "scale-51", "operational_decision": {"action": "scale", "priority": 51}},
            {"creative_id": "maintain-50", "operational_decision": {"action": "maintain", "priority": 50}},
            {"creative_id": "maintain-49", "operational_decision": {"action": "maintain", "priority": 49}},
            {"creative_id": "test-48", "operational_decision": {"action": "test", "priority": 48}},
            {"creative_id": "test-47", "operational_decision": {"action": "test", "priority": 47}},
            {"creative_id": "test-46", "operational_decision": {"action": "test", "priority": 46}},
            {"creative_id": "kill-45", "operational_decision": {"action": "kill", "priority": 45}},
            {"creative_id": "scale-44", "operational_decision": {"action": "scale", "priority": 44}},
            {"creative_id": "maintain-43", "operational_decision": {"action": "maintain", "priority": 43}},
        ]

        with _PatchTs("2026-04-05T12:00:00Z"):
            allocated = oe._allocate_creative_budget(creatives, 1000.0)

        by_id = {item["creative_id"]: item for item in allocated}
        weighted = []
        action_weight = {"scale": 1.0, "maintain": 0.6, "test": 0.3, "kill": 0.0}
        for item in creatives:
            action = item["operational_decision"]["action"]
            priority = item["operational_decision"]["priority"]
            weight = 0.0 if action == "kill" or priority == 0 else action_weight[action] * priority
            weighted.append((item["creative_id"], weight, by_id[item["creative_id"]]["budget_share"]))

        performance_only = [
            (cid, w, s)
            for cid, w, s in weighted
            if cid.startswith("scale") or cid.startswith("maintain")
        ]
        sorted_non_kill = sorted(performance_only, key=lambda x: x[1], reverse=True)
        inversions = []
        for idx in range(len(sorted_non_kill) - 1):
            left = sorted_non_kill[idx]
            right = sorted_non_kill[idx + 1]
            if left[1] > right[1] and left[2] + 1e-6 < right[2]:
                inversions.append((left, right))

        self.assertEqual(by_id["kill-45"]["budget_share"], 0.0)
        self.assertAlmostEqual(sum(item["budget_share"] for item in allocated), 1.0, places=6)
        self.assertEqual(inversions, [])
        self.assertGreater(by_id["test-48"]["budget_share"], 0.0)

    def test_allocate_creative_budget_stress_partial_freeze_preserves_locked_and_remaining_distribution(self):
        creatives = [
            {
                "creative_id": "locked-a",
                "operational_decision": {"action": "maintain", "priority": 55},
                "budget_share": 0.25,
                "allocated_budget": 250.0,
                "allocation_last_updated_at": "2026-04-05T09:00:00Z",
                "_previous_allocation_priority": 50,
            },
            {
                "creative_id": "locked-b",
                "operational_decision": {"action": "test", "priority": 25},
                "budget_share": 0.07,
                "allocated_budget": 70.0,
                "allocation_last_updated_at": "2026-04-05T09:00:00Z",
                "_previous_allocation_priority": 20,
            },
            {"creative_id": "scale-a", "operational_decision": {"action": "scale", "priority": 80}},
            {"creative_id": "scale-b", "operational_decision": {"action": "scale", "priority": 79}},
            {"creative_id": "maintain-a", "operational_decision": {"action": "maintain", "priority": 60}},
            {"creative_id": "test-a", "operational_decision": {"action": "test", "priority": 20}},
            {"creative_id": "kill-a", "operational_decision": {"action": "kill", "priority": 100}},
        ]

        with _PatchTs("2026-04-05T12:00:00Z"):
            allocated = oe._allocate_creative_budget(creatives, 1000.0)

        by_id = {item["creative_id"]: item for item in allocated}
        self.assertAlmostEqual(by_id["locked-a"]["budget_share"], 0.25, places=6)
        self.assertAlmostEqual(by_id["locked-b"]["budget_share"], 0.07, places=6)
        self.assertEqual(by_id["kill-a"]["budget_share"], 0.0)
        self.assertAlmostEqual(sum(item["budget_share"] for item in allocated), 1.0, places=6)
        self.assertGreaterEqual(by_id["test-a"]["budget_share"], 0.05)

    def test_allocate_creative_budget_residual_does_not_cross_pools(self):
        creatives = [
            {"creative_id": "scale-a", "operational_decision": {"action": "scale", "priority": 100}},
            {"creative_id": "maintain-a", "operational_decision": {"action": "maintain", "priority": 60}},
            {"creative_id": "test-a", "operational_decision": {"action": "test", "priority": 50}},
            {"creative_id": "test-b", "operational_decision": {"action": "test", "priority": 49}},
        ]

        with _PatchTs("2026-04-05T12:00:00Z"):
            allocated = oe._allocate_creative_budget(creatives, 1000.0)

        by_id = {item["creative_id"]: item for item in allocated}
        performance_total = by_id["scale-a"]["budget_share"] + by_id["maintain-a"]["budget_share"]
        exploration_total = by_id["test-a"]["budget_share"] + by_id["test-b"]["budget_share"]

        self.assertAlmostEqual(exploration_total, 0.12, places=6)
        self.assertAlmostEqual(performance_total, 0.88, places=6)
        self.assertGreater(by_id["scale-a"]["budget_share"], by_id["maintain-a"]["budget_share"])

    def test_allocate_creative_budget_exploration_increases_when_trend_falls(self):
        creatives = [
            {"creative_id": "scale-a", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "scale", "priority": 100}},
            {"creative_id": "maintain-a", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "maintain", "priority": 60}},
            {"creative_id": "test-a", "_missing_creative_id": False, "time_active_hours": 10, "operational_decision": {"action": "test", "priority": 50}},
        ]
        history = [
            {"performance_score": 50, "updated_at": "2026-04-05T12:00:00Z"},
            {"performance_score": 51, "updated_at": "2026-04-05T11:00:00Z"},
            {"performance_score": 49, "updated_at": "2026-04-05T10:00:00Z"},
            {"performance_score": 52, "updated_at": "2026-04-05T09:00:00Z"},
            {"performance_score": 50, "updated_at": "2026-04-05T08:00:00Z"},
            {"performance_score": 51, "updated_at": "2026-04-05T07:00:00Z"},
            {"performance_score": 80, "updated_at": "2026-03-28T12:00:00Z"},
            {"performance_score": 81, "updated_at": "2026-03-28T11:00:00Z"},
            {"performance_score": 79, "updated_at": "2026-03-28T10:00:00Z"},
            {"performance_score": 82, "updated_at": "2026-03-28T09:00:00Z"},
            {"performance_score": 80, "updated_at": "2026-03-28T08:00:00Z"},
            {"performance_score": 81, "updated_at": "2026-03-28T07:00:00Z"},
        ]
        with _PatchTs("2026-04-05T12:30:00Z"):
            envelope = oe._compute_exploration_envelope(creatives, history, previous_envelope=0.12, refresh_allowed=True)
            allocated = oe._allocate_creative_budget(
                creatives,
                1000.0,
                exploration_envelope=envelope["exploration_envelope"],
            )

        by_id = {item["creative_id"]: item for item in allocated}
        exploration_total = by_id["test-a"]["budget_share"]
        self.assertAlmostEqual(envelope["exploration_envelope"], 0.135, places=3)
        self.assertGreater(exploration_total, 0.12)

    def test_allocate_creative_budget_exploration_reduces_when_trend_rises(self):
        creatives = [
            {"creative_id": "scale-a", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "scale", "priority": 100}},
            {"creative_id": "maintain-a", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "maintain", "priority": 60}},
            {"creative_id": "test-a", "_missing_creative_id": False, "time_active_hours": 30, "operational_decision": {"action": "test", "priority": 50}},
        ]
        history = [
            {"performance_score": 90, "updated_at": "2026-04-05T12:00:00Z"},
            {"performance_score": 91, "updated_at": "2026-04-05T11:00:00Z"},
            {"performance_score": 89, "updated_at": "2026-04-05T10:00:00Z"},
            {"performance_score": 92, "updated_at": "2026-04-05T09:00:00Z"},
            {"performance_score": 90, "updated_at": "2026-04-05T08:00:00Z"},
            {"performance_score": 91, "updated_at": "2026-04-05T07:00:00Z"},
            {"performance_score": 70, "updated_at": "2026-03-28T12:00:00Z"},
            {"performance_score": 71, "updated_at": "2026-03-28T11:00:00Z"},
            {"performance_score": 69, "updated_at": "2026-03-28T10:00:00Z"},
            {"performance_score": 72, "updated_at": "2026-03-28T09:00:00Z"},
            {"performance_score": 70, "updated_at": "2026-03-28T08:00:00Z"},
            {"performance_score": 71, "updated_at": "2026-03-28T07:00:00Z"},
        ]
        with _PatchTs("2026-04-05T12:30:00Z"):
            envelope = oe._compute_exploration_envelope(creatives, history, previous_envelope=0.12, refresh_allowed=True)
            allocated = oe._allocate_creative_budget(
                creatives,
                1000.0,
                exploration_envelope=envelope["exploration_envelope"],
            )

        by_id = {item["creative_id"]: item for item in allocated}
        exploration_total = by_id["test-a"]["budget_share"]
        self.assertAlmostEqual(envelope["exploration_envelope"], 0.117, places=3)
        self.assertLess(exploration_total, 0.12)

    def test_load_execution_state_returns_safe_default_when_history_missing(self):
        state_path = self._make_state_path("missing")
        try:
            with mock.patch.object(jr, "_execution_state_path", return_value=state_path):
                state = jr.load_execution_state("client-x")
        finally:
            shutil.rmtree(os.path.dirname(os.path.dirname(state_path)), ignore_errors=True)

        self.assertEqual(state["trend_history"], [])
        self.assertEqual(state["active_creatives"], [])

    def test_load_execution_state_returns_safe_default_when_corrupted(self):
        state_path = self._make_state_path("corrupted")
        try:
            with open(state_path, "w", encoding="utf-8") as f:
                f.write("{not-json")
            with mock.patch.object(jr, "_execution_state_path", return_value=state_path):
                state = jr.load_execution_state("client-x")
        finally:
            shutil.rmtree(os.path.dirname(os.path.dirname(state_path)), ignore_errors=True)

        self.assertEqual(state["trend_history"], [])
        self.assertEqual(state["replacements"], [])

    def test_build_execution_state_persists_deduped_trend_history(self):
        portfolio_decision = {
            "top_creatives": [],
            "test_creatives": [],
            "discard_creatives": [],
            "allocation_policy": {
                "cycle_id": "portfolio-run-1",
                "performance_history_audit": {"count": 2},
            },
            "trend_history": [
                {"creative_id": "c1", "performance_score": 70, "updated_at": "2026-04-05T12:00:00Z", "source": "current_cycle", "cycle_id": "2026-04-05T12:00:00Z"},
                {"creative_id": "c1", "performance_score": 70, "updated_at": "2026-04-05T12:00:00Z", "source": "current_cycle", "cycle_id": "2026-04-05T12:00:00Z"},
                {"creative_id": "c2", "performance_score": 60, "updated_at": "2026-04-05T11:00:00Z", "source": "replay"},
                {"creative_id": "c3", "performance_score": 55, "updated_at": "2026-04-05T10:00:00Z", "source": "legacy"},
                {"creative_id": "", "performance_score": 80, "updated_at": "2026-04-05T10:00:00Z", "source": "current_cycle"},
            ],
        }
        state_path = self._make_state_path("persisted")
        try:
            with mock.patch.object(jr, "_execution_state_path", return_value=state_path), \
                 mock.patch.object(jr, "load_performance_memory", return_value={"items": []}), \
                 mock.patch.object(jr, "_ts", return_value="2026-04-05T12:30:00Z"):
                state = jr._build_execution_state("client-x", portfolio_decision)
                reloaded = jr.load_execution_state("client-x")
        finally:
            shutil.rmtree(os.path.dirname(os.path.dirname(state_path)), ignore_errors=True)

        self.assertEqual(len(state["trend_history"]), 3)
        self.assertEqual(len(reloaded["trend_history"]), 3)
        self.assertEqual(
            [(item["creative_id"], item["source"]) for item in state["trend_history"]],
            [("c1", "current_cycle"), ("c2", "replay"), ("c3", "migrated")],
        )
        self.assertEqual(state["trend_history"][0]["cycle_id"], "2026-04-05T12:00:00Z")

    def test_build_execution_state_uses_root_trend_history_not_audit_mirror(self):
        portfolio_decision = {
            "top_creatives": [],
            "test_creatives": [],
            "discard_creatives": [],
            "allocation_policy": {
                "cycle_id": "portfolio-run-root",
                "performance_history_audit": {"count": 99},
                "performance_history": [
                    {"creative_id": "wrong", "performance_score": 1, "updated_at": "2026-04-05T09:00:00Z", "source": "execution_state"},
                ],
            },
            "trend_history": [
                {"creative_id": "right", "performance_score": 70, "updated_at": "2026-04-05T12:00:00Z", "source": "current_cycle"},
            ],
        }
        state_path = self._make_state_path("root-source")
        try:
            with mock.patch.object(jr, "_execution_state_path", return_value=state_path), \
                 mock.patch.object(jr, "load_performance_memory", return_value={"items": []}), \
                 mock.patch.object(jr, "_ts", return_value="2026-04-05T12:30:00Z"):
                state = jr._build_execution_state("client-x", portfolio_decision)
        finally:
            shutil.rmtree(os.path.dirname(os.path.dirname(state_path)), ignore_errors=True)

        self.assertEqual([item["creative_id"] for item in state["trend_history"]], ["right"])

    def test_build_allocation_trace_generates_cycle_trace_with_correct_pool(self):
        cards = [
            {
                "creative_id": "c-scale",
                "operational_decision": {"action": "scale", "priority": 80, "reason": "winner"},
                "_refresh_allocation": True,
                "_previous_budget_share": 0.1,
                "_previous_allocated_budget": 100.0,
                "allocated_budget": 300.0,
                "budget_share": 0.3,
                "_budget_key": "bk-scale",
            },
            {
                "creative_id": "c-test",
                "operational_decision": {"action": "test", "priority": 40, "reason": "explore"},
                "_refresh_allocation": False,
                "_previous_budget_share": 0.05,
                "_previous_allocated_budget": 50.0,
                "allocated_budget": 50.0,
                "budget_share": 0.05,
                "_budget_key": "bk-test",
            },
        ]

        trace = jr._build_allocation_trace(cards, "cycle-1", 0.12, "2026-04-05T12:30:00Z")

        self.assertEqual(trace["cycle_id"], "cycle-1")
        self.assertEqual(len(trace["items"]), 2)
        by_id = {item["creative_id"]: item for item in trace["items"]}
        self.assertEqual(by_id["c-scale"]["pool"], "performance")
        self.assertEqual(by_id["c-test"]["pool"], "exploration")
        self.assertEqual(by_id["c-test"]["cycle_id"], "cycle-1")

    def test_build_execution_state_persists_allocation_trace(self):
        portfolio_decision = {
            "top_creatives": [],
            "test_creatives": [],
            "discard_creatives": [],
            "allocation_policy": {"cycle_id": "cycle-1"},
            "trend_history": [],
            "allocation_trace": {
                "cycle_id": "cycle-1",
                "generated_at": "2026-04-05T12:30:00Z",
                "items": [
                    {
                        "creative_id": "c1",
                        "cycle_id": "cycle-1",
                        "pool": "performance",
                        "action": "scale",
                        "priority": 80,
                        "refresh_allowed": True,
                        "previous_budget_share": 0.1,
                        "previous_allocated_budget": 100.0,
                        "exploration_envelope": 0.12,
                        "allocated_budget": 300.0,
                        "budget_share": 0.3,
                        "_budget_key": "bk-1",
                        "reason": "winner",
                    }
                ],
            },
        }
        state_path = self._make_state_path("trace-persist")
        try:
            with mock.patch.object(jr, "_execution_state_path", return_value=state_path), \
                 mock.patch.object(jr, "load_performance_memory", return_value={"items": []}), \
                 mock.patch.object(jr, "_ts", return_value="2026-04-05T12:30:00Z"):
                state = jr._build_execution_state("client-x", portfolio_decision)
                reloaded = jr.load_execution_state("client-x")
        finally:
            shutil.rmtree(os.path.dirname(os.path.dirname(state_path)), ignore_errors=True)

        self.assertEqual(state["allocation_traces"][0]["cycle_id"], "cycle-1")
        self.assertEqual(reloaded["allocation_traces"][0]["items"][0]["pool"], "performance")

    def test_build_execution_state_rerun_with_new_cycle_id_keeps_previous_trace(self):
        previous_state = {
            "client_id": "client-x",
            "updated_at": "2026-04-05T12:30:00Z",
            "active_creatives": [],
            "testing_creatives": [],
            "historical_creatives": [],
            "replacements": [],
            "trend_history": [],
            "allocation_traces": [
                {
                    "cycle_id": "cycle-old",
                    "generated_at": "2026-04-05T12:30:00Z",
                    "items": [{"creative_id": "c1", "cycle_id": "cycle-old", "pool": "performance"}],
                }
            ],
        }
        portfolio_decision = {
            "top_creatives": [],
            "test_creatives": [],
            "discard_creatives": [],
            "allocation_policy": {"cycle_id": "cycle-new"},
            "trend_history": [],
            "allocation_trace": {
                "cycle_id": "cycle-new",
                "generated_at": "2026-04-05T13:30:00Z",
                "items": [{"creative_id": "c2", "cycle_id": "cycle-new", "pool": "exploration"}],
            },
        }
        state_path = self._make_state_path("trace-rerun")
        try:
            with mock.patch.object(jr, "_execution_state_path", return_value=state_path), \
                 mock.patch.object(jr, "load_execution_state", return_value=previous_state), \
                 mock.patch.object(jr, "load_performance_memory", return_value={"items": []}), \
                 mock.patch.object(jr, "_ts", return_value="2026-04-05T13:30:00Z"):
                state = jr._build_execution_state("client-x", portfolio_decision)
        finally:
            shutil.rmtree(os.path.dirname(os.path.dirname(state_path)), ignore_errors=True)

        self.assertEqual([trace["cycle_id"] for trace in state["allocation_traces"]], ["cycle-new", "cycle-old"])

    def test_sanitize_allocation_traces_retains_recent_cycles(self):
        traces = []
        for idx in range(jr.ALLOCATION_TRACE_MAX_CYCLES + 5):
            traces.append({
                "cycle_id": f"cycle-{idx}",
                "generated_at": f"2026-04-{30 - (idx % 20):02d}T12:00:00Z",
                "items": [{"creative_id": f"c{idx}", "cycle_id": f"cycle-{idx}", "pool": "performance"}],
            })

        sanitized = jr._sanitize_allocation_traces(traces)

        self.assertEqual(len(sanitized), jr.ALLOCATION_TRACE_MAX_CYCLES)

    def test_portfolio_cycle_id_is_persisted_in_allocation_policy_and_reused_by_history_records(self):
        previous_state = {
            "active_creatives": [],
            "testing_creatives": [],
            "historical_creatives": [],
            "replacements": [],
            "trend_history": [],
        }
        portfolio_jobs = [{
            "job_id": "job-1",
            "jdir": "unused",
            "job": {"id": "job-1"},
        }]
        executive_summary = {"job_id": "job-1", "status_final": "aprovado", "score_quality_gate": 90}
        media_decision = {
            "media_next_action": "manter",
            "_action_engine": {
                "creative_id": "c1",
                "_id_recovered": False,
                "performance_score": 80,
                "penalty_strength": 0.1,
                "confidence_score": 0.8,
                "stability_score": 0.7,
                "time_active_hours": 10,
            },
        }
        creative_summary = {"headline": "headline"}
        state_path = self._make_state_path("cycle-id")
        try:
            with mock.patch.object(jr, "load_execution_state", return_value=previous_state), \
                 mock.patch.object(jr, "_resolve_portfolio_jobs", return_value=portfolio_jobs), \
                 mock.patch.object(jr, "_read_json_file", side_effect=[executive_summary, media_decision, creative_summary]), \
                 mock.patch.object(jr, "_compute_portfolio_score", return_value=82), \
                 mock.patch.object(jr, "_execution_state_path", return_value=state_path), \
                 mock.patch.object(jr, "load_performance_memory", return_value={"items": []}), \
                 mock.patch.object(jr, "_ts", return_value="2026-04-05T12:30:00Z"), \
                 mock.patch.object(jr.uuid, "uuid4", side_effect=["portfolio-run-1"]):
                output = jr._build_portfolio_decision("client-x", job_ids=["job-1"], recent_n=1)
        finally:
            shutil.rmtree(os.path.dirname(os.path.dirname(state_path)), ignore_errors=True)

        self.assertEqual(output["allocation_policy"]["cycle_id"], "portfolio-run-1")
        self.assertEqual(output["allocation_policy"]["performance_history_audit"]["count"], 1)


if __name__ == "__main__":
    unittest.main()
