import os
import shutil
import unittest
from unittest import mock

from studio import studio_manager as sm


class StudioManagerTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = os.path.join(os.getcwd(), "tests", "_tmp_studio_manager")
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        os.makedirs(self.tmpdir, exist_ok=True)
        self.addCleanup(shutil.rmtree, self.tmpdir, True)
        self.data_dir = os.path.join(self.tmpdir, "clients")
        os.makedirs(self.data_dir, exist_ok=True)
        self.data_dir_patch = mock.patch.object(sm, "DATA_DIR", self.data_dir)
        self.data_dir_patch.start()
        self.addCleanup(self.data_dir_patch.stop)

    def _create_client_stub(self, client_id: str = "cliente-asset") -> str:
        client_dir = os.path.join(self.data_dir, client_id)
        os.makedirs(client_dir, exist_ok=True)
        sm._write_json(
            os.path.join(client_dir, "client.json"),
            {"id": client_id, "nome": "Cliente Asset", "instagram": ""},
        )
        sm._write_json(
            os.path.join(client_dir, "brand.json"),
            {"cliente_id": client_id, "cores": [], "fontes": [], "observacoes_identidade": ""},
        )
        return client_id

    def test_save_client_asset_preserves_source_extension_when_original_name_has_none(self):
        client_id = self._create_client_stub()
        source_path = os.path.join(self.tmpdir, "logo.png")
        with open(source_path, "wb") as handle:
            handle.write(b"png-bytes")

        asset = sm.save_client_asset(client_id, source_path, original_name="logo")

        self.assertEqual(asset["nome"], "logo.png")
        self.assertTrue(asset["path"].endswith("logo.png"))
        self.assertTrue(os.path.exists(asset["path"]))

    def test_save_client_asset_appends_numeric_suffix_when_name_already_exists(self):
        client_id = self._create_client_stub()
        source_path = os.path.join(self.tmpdir, "logo.png")
        with open(source_path, "wb") as handle:
            handle.write(b"png-bytes")

        first_asset = sm.save_client_asset(client_id, source_path, original_name="logo.png")
        second_asset = sm.save_client_asset(client_id, source_path, original_name="logo.png")

        self.assertEqual(first_asset["nome"], "logo.png")
        self.assertEqual(second_asset["nome"], "logo-1.png")
        self.assertTrue(os.path.exists(first_asset["path"]))
        self.assertTrue(os.path.exists(second_asset["path"]))

    def test_save_client_asset_appends_incremental_suffix_for_multiple_collisions(self):
        client_id = self._create_client_stub()
        source_path = os.path.join(self.tmpdir, "logo.png")
        with open(source_path, "wb") as handle:
            handle.write(b"png-bytes")

        first_asset = sm.save_client_asset(client_id, source_path, original_name="logo.png")
        second_asset = sm.save_client_asset(client_id, source_path, original_name="logo.png")
        third_asset = sm.save_client_asset(client_id, source_path, original_name="logo.png")

        self.assertEqual(first_asset["nome"], "logo.png")
        self.assertEqual(second_asset["nome"], "logo-1.png")
        self.assertEqual(third_asset["nome"], "logo-2.png")
        self.assertTrue(os.path.exists(third_asset["path"]))

    def test_save_client_asset_appends_incremental_suffix_for_multiple_collisions_without_extension(self):
        client_id = self._create_client_stub()
        source_path = os.path.join(self.tmpdir, "logo.png")
        with open(source_path, "wb") as handle:
            handle.write(b"png-bytes")

        first_asset = sm.save_client_asset(client_id, source_path, original_name="logo")
        second_asset = sm.save_client_asset(client_id, source_path, original_name="logo")
        third_asset = sm.save_client_asset(client_id, source_path, original_name="logo")

        self.assertEqual(first_asset["nome"], "logo.png")
        self.assertEqual(second_asset["nome"], "logo-1.png")
        self.assertEqual(third_asset["nome"], "logo-2.png")
        self.assertTrue(os.path.exists(first_asset["path"]))
        self.assertTrue(os.path.exists(second_asset["path"]))
        self.assertTrue(os.path.exists(third_asset["path"]))

    def test_sanitize_asset_name_normalizes_invalid_name_to_safe_predictable_output(self):
        sanitized = sm._sanitize_asset_name(' ..Lo*go<>:"?/\\\\  final!!.png ')

        self.assertEqual(sanitized, "final.png")
        self.assertNotRegex(sanitized, r'[<>:"?/\\\\]')
        self.assertTrue(sanitized.endswith(".png"))

    def test_sanitize_asset_name_empty_string_uses_safe_fallback(self):
        sanitized = sm._sanitize_asset_name("")

        self.assertRegex(sanitized, r"^asset-\d{8}-\d{6}\.bin$")
        self.assertNotRegex(sanitized, r'[<>:"?/\\\\]')
        self.assertTrue(sanitized.endswith(".bin"))

    def test_update_audit_consolidates_brand_identity_when_client_has_no_instagram(self):
        client_id = self._create_client_stub("cliente-audit")

        audit = sm.update_audit(
            client_id,
            {
                "diagnostico_perfil": "Perfil inconsistente e sem assinatura visual clara.",
                "identidade_visual_atual": "Sem padrão visual, alternando paleta e tipografia.",
                "linha_visual_sugerida": "Contraste alto, fundo escuro e destaque quente para CTA.",
                "oportunidades": ["Padronizar assinatura visual", "Reforçar contraste no feed"],
                "observacoes_criativo": "Manter visual direto, focado em performance e leitura rápida.",
            },
        )

        brand = sm._read_json(os.path.join(self.data_dir, client_id, "brand.json"))
        status = sm.get_client_pipeline_status(client_id)

        self.assertEqual(audit["cliente_id"], client_id)
        self.assertEqual(brand["origem_identidade"], "auditoria")
        self.assertTrue(brand["cores"])
        self.assertTrue(brand["fontes"])
        self.assertIn("Contraste alto", brand["observacoes_identidade"])
        self.assertTrue(status["brand_ready"])
        self.assertTrue(status["job_ready"])
        self.assertEqual(sm.ensure_brand_identity(client_id)["observacoes_identidade"], brand["observacoes_identidade"])

    def test_ensure_brand_identity_still_requires_instagram_or_audit_signal(self):
        client_id = self._create_client_stub("cliente-vazio")

        with self.assertRaisesRegex(ValueError, "brand.json sem identidade visual"):
            sm.ensure_brand_identity(client_id)

    def test_create_job_persists_client_pipeline_state_with_active_job(self):
        client_id = self._create_client_stub("cliente-job")
        sm.update_audit(
            client_id,
            {
                "diagnostico_perfil": "Perfil já auditado.",
                "linha_visual_sugerida": "Contraste forte e assinatura estável.",
            },
        )

        job = sm.create_job(
            client_id,
            {
                "tipo": "post_estatico",
                "briefing": "Teste de continuidade operacional.",
                "formato": "feed_quadrado",
            },
        )

        state = sm.get_client_pipeline_state(client_id)

        self.assertEqual(state["etapa_atual"], "job_criado")
        self.assertEqual(state["job_id_ativo"], job["id"])
        self.assertIn("auditoria_consolidada", state["etapas_concluidas"])
        self.assertIn("job_criado", state["etapas_concluidas"])

    def test_get_resume_job_id_prefers_pipeline_active_job(self):
        client_id = self._create_client_stub("cliente-resume")
        sm.update_audit(
            client_id,
            {
                "diagnostico_perfil": "Perfil já auditado.",
                "linha_visual_sugerida": "Base visual suficiente.",
            },
        )
        first = sm.create_job(
            client_id,
            {"tipo": "post_estatico", "briefing": "Primeiro job", "formato": "feed_quadrado"},
        )
        second = sm.create_job(
            client_id,
            {"tipo": "post_estatico", "briefing": "Segundo job", "formato": "feed_quadrado"},
        )

        sm.record_client_pipeline_state(
            client_id,
            etapa_atual="auditoria_consolidada",
            etapas_concluidas=["cliente_criado", "auditoria_consolidada", "job_criado"],
            origem_da_execucao="teste",
            job_id=first["id"],
            proximo_passo_sugerido="Retomar do job ativo.",
        )

        self.assertEqual(sm.get_resume_job_id(client_id), first["id"])
        self.assertEqual(sm.get_resume_job_id(client_id, second["id"]), second["id"])


if __name__ == "__main__":
    unittest.main()
