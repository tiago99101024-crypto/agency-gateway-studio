#!/usr/bin/env python3
"""studio_server.py — Social Content Studio Server. Porta 8766.

Uso:
    python studio_server.py

Interface web em: http://localhost:8766
API REST em: http://localhost:8766/api/*

Endpoints:
    GET  /api/clients                              — lista clientes
    POST /api/clients                              — cria cliente
    GET  /api/clients/:id                          — get cliente
    PUT  /api/clients/:id                          — atualiza cliente
    GET  /api/clients/:id/brand                    — get brand
    PUT  /api/clients/:id/brand                    — atualiza brand
    GET  /api/clients/:id/audit                    — get auditoria
    PUT  /api/clients/:id/audit                    — atualiza auditoria (manual)
    POST /api/clients/:id/audit/pre                — gera pré-auditoria (Toguro)
    GET  /api/clients/:id/jobs                     — lista jobs
    POST /api/clients/:id/jobs                     — cria job
    GET  /api/clients/:id/jobs/:jid                — get job
    POST /api/clients/:id/jobs/:jid/angles         — gera ângulos estratégicos (Toguro)
    POST /api/clients/:id/jobs/:jid/run            — executa job {angle_index: int}
    POST /api/clients/:id/jobs/:jid/result         — registra resultado do post
    GET  /api/clients/:id/jobs/:jid/files          — lista arquivos de output
    GET  /api/clients/:id/jobs/:jid/file/:fn       — download de arquivo
    GET  /api/formats                              — configuracao de formatos sociais
"""

import http.server
import json
import mimetypes
import os
import sys
import threading
import traceback
import urllib.parse
from datetime import datetime
from pathlib import Path
from email import policy
from email.parser import BytesParser

PORT = 8766
STUDIO_HTML = os.path.join(os.path.dirname(__file__), "studio", "studio.html")
FORMATS_CONFIG = "config/social_formats.json"


def _json_resp(handler, data, status=200):
    body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def _read_body(handler) -> dict:
    length = int(handler.headers.get("Content-Length", 0))
    if length == 0:
        return {}
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return {}


def _import_studio():
    sys.path.insert(0, os.path.abspath("."))
    import studio.studio_manager as sm
    return sm


def _import_runner():
    sys.path.insert(0, os.path.abspath("."))
    import studio.job_runner as jr
    return jr


def _run_threaded(task, timeout_seconds: int) -> dict:
    result_holder = {}

    def _target():
        try:
            result_holder["result"] = task()
        except Exception as exc:
            result_holder["error"] = {
                "erro": str(exc),
                "erro_tipo": exc.__class__.__name__,
                "erro_traceback": traceback.format_exc(),
            }

    thread = threading.Thread(target=_target)
    thread.start()
    thread.join(timeout=timeout_seconds)

    if thread.is_alive():
        return {"erro": "Timeout ou erro interno."}
    if "error" in result_holder:
        return result_holder["error"]
    return result_holder.get("result", {"erro": "Timeout ou erro interno."})


class StudioHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Silencia logs de acesso — so imprime erros
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        parts = [p for p in path.split("/") if p]

        try:
            # Serve HTML da interface
            if path in ("", "/", "/studio"):
                self._serve_html()
                return

            if not parts or parts[0] != "api":
                self._serve_html()
                return

            sm = _import_studio()

            # GET /api/clients
            if parts == ["api", "clients"]:
                _json_resp(self, sm.list_clients())
                return

            # GET /api/clients/:id
            if len(parts) == 3 and parts[1] == "clients":
                _json_resp(self, sm.get_client(parts[2]))
                return

            # GET /api/clients/:id/bundle
            if len(parts) == 4 and parts[1] == "clients" and parts[3] == "bundle":
                _json_resp(self, sm.get_client_bundle(parts[2]))
                return

            # GET /api/clients/:id/brand
            if len(parts) == 4 and parts[1] == "clients" and parts[3] == "brand":
                cdir = sm._client_dir(parts[2])
                data = sm._read_json(os.path.join(cdir, "brand.json"))
                _json_resp(self, data)
                return

            # GET /api/clients/:id/assets
            if len(parts) == 4 and parts[1] == "clients" and parts[3] == "assets":
                _json_resp(self, sm.list_client_assets(parts[2]))
                return

            # GET /api/clients/:id/asset/:fn
            if len(parts) == 5 and parts[1] == "clients" and parts[3] == "asset":
                assets_dir = sm._assets_dir(parts[2])
                fname = os.path.basename(urllib.parse.unquote(parts[4]))
                fpath = os.path.join(assets_dir, fname)
                if not os.path.exists(fpath):
                    _json_resp(self, {"erro": "Asset nao encontrado."}, 404)
                    return
                self._serve_file(fpath, fname)
                return

            # GET /api/clients/:id/audit
            if len(parts) == 4 and parts[1] == "clients" and parts[3] == "audit":
                _json_resp(self, sm.get_audit(parts[2]))
                return

            # GET /api/clients/:id/pipeline
            if len(parts) == 4 and parts[1] == "clients" and parts[3] == "pipeline":
                _json_resp(self, sm.get_client_pipeline_state(parts[2]))
                return

            # GET /api/clients/:id/jobs
            if len(parts) == 4 and parts[1] == "clients" and parts[3] == "jobs":
                _json_resp(self, sm.list_jobs(parts[2]))
                return

            # GET /api/clients/:id/jobs/:jid
            if len(parts) == 5 and parts[1] == "clients" and parts[3] == "jobs":
                _json_resp(self, sm.get_job(parts[2], parts[4]))
                return

            # GET /api/clients/:id/jobs/:jid/files
            if len(parts) == 6 and parts[1] == "clients" and parts[3] == "jobs" and parts[5] == "files":
                _json_resp(self, sm.get_job_output_files(parts[2], parts[4]))
                return

            # GET /api/clients/:id/jobs/:jid/file/:fn
            if len(parts) == 7 and parts[1] == "clients" and parts[3] == "jobs" and parts[5] == "file":
                jdir = sm._job_dir(parts[2], parts[4])
                fname = urllib.parse.unquote(parts[6])
                fpath = os.path.join(jdir, fname)
                if not os.path.exists(fpath):
                    _json_resp(self, {"erro": "Arquivo nao encontrado."}, 404)
                    return
                self._serve_file(fpath, fname)
                return

            # GET /api/clients/:id/jobs/:jid/plan
            if len(parts) == 6 and parts[1] == "clients" and parts[3] == "jobs" and parts[5] == "plan":
                job = sm.get_job(parts[2], parts[4])
                saved = job.get("plano_execucao")
                if saved:
                    _json_resp(self, saved)
                else:
                    _json_resp(self, {"aviso": "Plano nao gerado ainda. Gere angulos primeiro."})
                return

            # GET /api/clients/:id/learning
            if len(parts) == 4 and parts[1] == "clients" and parts[3] == "learning":
                sys.path.insert(0, os.path.abspath("."))
                from studio.bruxo_orchestrator import get_learning_summary
                _json_resp(self, get_learning_summary(parts[2]))
                return

            # GET /api/formats
            if parts == ["api", "formats"]:
                if os.path.exists(FORMATS_CONFIG):
                    with open(FORMATS_CONFIG, encoding="utf-8") as f:
                        _json_resp(self, json.load(f))
                else:
                    _json_resp(self, {})
                return

            _json_resp(self, {"erro": "Rota nao encontrada."}, 404)

        except FileNotFoundError as e:
            _json_resp(self, {"erro": str(e)}, 404)
        except Exception as e:
            _json_resp(self, {"erro": str(e)}, 500)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        parts = [p for p in path.split("/") if p]

        try:
            sm = _import_studio()

            # POST /api/clients
            if parts == ["api", "clients"]:
                body = _read_body(self)
                client = sm.create_client(body)
                _json_resp(self, client, 201)
                return

            # POST /api/identity/analyze
            if parts == ["api", "identity", "analyze"]:
                body = _read_body(self)
                username = body.get("instagram") or body.get("username") or ""
                analysis = sm.analyze_instagram_identity(username)
                _json_resp(self, analysis)
                return

            # POST /api/clients/:id/assets
            if len(parts) == 4 and parts[1] == "clients" and parts[3] == "assets":
                asset = self._save_asset_upload(sm, parts[2])
                _json_resp(self, asset, 201)
                return

            # POST /api/clients/:id/jobs
            if len(parts) == 4 and parts[1] == "clients" and parts[3] == "jobs":
                body = _read_body(self)
                job = sm.create_job(parts[2], body)
                _json_resp(self, job, 201)
                return

            # POST /api/clients/:id/audit/pre
            if len(parts) == 5 and parts[1] == "clients" and parts[3] == "audit" and parts[4] == "pre":
                jr = _import_runner()
                _json_resp(self, _run_threaded(lambda: jr.generate_pre_audit(parts[2]), timeout_seconds=180))
                return

            # POST /api/clients/:id/jobs/:jid/angles
            if len(parts) == 6 and parts[1] == "clients" and parts[3] == "jobs" and parts[5] == "angles":
                jr = _import_runner()
                cid, jid = parts[2], parts[4]
                _json_resp(self, _run_threaded(lambda: jr.generate_angles(cid, jid), timeout_seconds=180))
                return

            # POST /api/clients/:id/jobs/:jid/run
            if len(parts) == 6 and parts[1] == "clients" and parts[3] == "jobs" and parts[5] == "run":
                jr = _import_runner()
                body = _read_body(self)
                angle_index = body.get("angle_index")
                angle_snapshot = body.get("angle_snapshot")
                visual_replay_raw_output = body.get("visual_replay_raw_output")
                if angle_index is not None:
                    angle_index = int(angle_index)
                cid, jid = parts[2], parts[4]
                sm.update_job(cid, jid, {
                    "status": "executando",
                    "pipeline": {
                        "stage": "executando",
                        "origem_da_execucao": "studio",
                        "started_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    },
                })
                result = _run_threaded(
                    lambda: jr.run_job(
                        cid,
                        jid,
                        angle_index,
                        angle_snapshot=angle_snapshot,
                        visual_replay_raw_output=visual_replay_raw_output,
                    ),
                    timeout_seconds=360,
                )
                if isinstance(result, dict) and result.get("erro"):
                    tb_text = result.get("erro_traceback") or ""
                    if tb_text:
                        tb_path = os.path.join(sm._job_dir(cid, jid), "last_error_traceback.txt")
                        with open(tb_path, "w", encoding="utf-8") as f:
                            f.write(tb_text)
                    sm.update_job(cid, jid, {
                        "status": "erro",
                        "pipeline": {
                            "stage": "erro",
                            "failed_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "origem_da_execucao": "studio",
                            "erro": result.get("erro"),
                        },
                        "erro_mensagem": result.get("erro"),
                        "erro_tipo": result.get("erro_tipo") or "RuntimeError",
                        "erro_traceback_file": result.get("erro_traceback_file") or "last_error_traceback.txt",
                    })
                _json_resp(self, result)
                return

            # POST /api/clients/:id/jobs/:jid/result
            if len(parts) == 6 and parts[1] == "clients" and parts[3] == "jobs" and parts[5] == "result":
                sm = _import_studio()
                body = _read_body(self)
                learning = sm.save_job_result(parts[2], parts[4], body)
                _json_resp(self, learning)
                return

            # POST /api/clients/:id/pipeline/resume
            if len(parts) == 5 and parts[1] == "clients" and parts[3] == "pipeline" and parts[4] == "resume":
                body = _read_body(self)
                cid = parts[2]
                stage = body.get("stage") or "auditoria"
                if stage != "auditoria":
                    raise ValueError("Resume suportado apenas a partir da etapa de auditoria nesta versao.")
                job_id = sm.get_resume_job_id(cid, body.get("job_id", ""))
                sm.record_client_pipeline_state(
                    cid,
                    etapa_atual="reexecutando_desde_auditoria",
                    etapas_concluidas=["cliente_criado", "auditoria_consolidada", "job_criado"],
                    origem_da_execucao="resume_auditoria",
                    job_id=job_id,
                    proximo_passo_sugerido="Aguardando reexecucao do job a partir da auditoria.",
                )
                jr = _import_runner()
                generated = _run_threaded(lambda: jr.generate_angles(cid, job_id), timeout_seconds=180)
                job = sm.get_job(cid, job_id)
                angulos = job.get("angulos", []) or []
                angle_index = next((i for i, item in enumerate(angulos) if item.get("recomendado")), 0) if angulos else None
                result = _run_threaded(lambda: jr.run_job(cid, job_id, angle_index), timeout_seconds=360)
                _json_resp(self, {"job_id": job_id, "generated_angles": generated.get("angulos", []), "result": result})
                return

            _json_resp(self, {"erro": "Rota nao encontrada."}, 404)

        except ValueError as e:
            _json_resp(self, {"erro": str(e)}, 400)
        except FileNotFoundError as e:
            _json_resp(self, {"erro": str(e)}, 404)
        except Exception as e:
            _json_resp(self, {"erro": str(e)}, 500)

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        parts = [p for p in path.split("/") if p]

        try:
            sm = _import_studio()
            body = _read_body(self)

            # PUT /api/clients/:id
            if len(parts) == 3 and parts[1] == "clients":
                client = sm.update_client(parts[2], body)
                _json_resp(self, client)
                return

            # PUT /api/clients/:id/brand
            if len(parts) == 4 and parts[1] == "clients" and parts[3] == "brand":
                cdir = sm._client_dir(parts[2])
                brand = sm._read_json(os.path.join(cdir, "brand.json"))
                brand.update(body)
                brand["atualizado_em"] = sm._ts()
                sm._write_json(os.path.join(cdir, "brand.json"), brand)
                sm._rebuild_brand_summary(parts[2])
                _json_resp(self, brand)
                return

            # PUT /api/clients/:id/audit
            if len(parts) == 4 and parts[1] == "clients" and parts[3] == "audit":
                audit = sm.update_audit(parts[2], body)
                _json_resp(self, audit)
                return

            _json_resp(self, {"erro": "Rota nao encontrada."}, 404)

        except FileNotFoundError as e:
            _json_resp(self, {"erro": str(e)}, 404)
        except Exception as e:
            _json_resp(self, {"erro": str(e)}, 500)

    def _serve_html(self):
        if os.path.exists(STUDIO_HTML):
            with open(STUDIO_HTML, "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            body = b"<h1>studio/studio.html nao encontrado.</h1>"
            self.send_response(404)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(body)

    def _serve_file(self, fpath: str, fname: str):
        mime, _ = mimetypes.guess_type(fname)
        mime = mime or "application/octet-stream"
        with open(fpath, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Access-Control-Allow-Origin", "*")
        # Imagens servidas inline para permitir preview no browser
        if not mime.startswith("image/"):
            self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _save_asset_upload(self, sm, client_id: str):
        content_type = self.headers.get("Content-Type", "")
        if not content_type.lower().startswith("multipart/form-data"):
            raise ValueError("Upload deve usar multipart/form-data.")

        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            raise ValueError("Nenhum arquivo enviado.")

        raw_body = self.rfile.read(length)
        parser_input = (
            f"Content-Type: {content_type}\r\n"
            f"MIME-Version: 1.0\r\n"
            f"\r\n"
        ).encode("utf-8") + raw_body
        message = BytesParser(policy=policy.default).parsebytes(parser_input)

        file_part = None
        category = ""
        for part in message.iter_parts():
            if part.get_content_disposition() != "form-data":
                continue
            field_name = part.get_param("name", header="content-disposition")
            if field_name == "file" and part.get_filename():
                file_part = part
            elif field_name == "category":
                payload = part.get_payload(decode=True) or b""
                category = payload.decode("utf-8", errors="replace").strip()

        if file_part is None or not file_part.get_filename():
            raise ValueError("Nenhum arquivo enviado.")

        temp_dir = Path("data") / "_tmp_uploads"
        temp_dir.mkdir(parents=True, exist_ok=True)
        filename = os.path.basename(file_part.get_filename())
        temp_name = f"upload-{threading.get_ident()}-{filename}"
        temp_path = temp_dir / temp_name

        payload = file_part.get_payload(decode=True) or b""
        with open(temp_path, "wb") as f:
            f.write(payload)

        try:
            asset = sm.save_client_asset(client_id, str(temp_path), filename, category)
            return asset
        finally:
            try:
                temp_path.unlink(missing_ok=True)
            except Exception:
                pass


def run():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = http.server.HTTPServer(("localhost", PORT), StudioHandler)
    print(f"Social Content Studio: http://localhost:{PORT}")
    print("Ctrl+C para parar.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")


if __name__ == "__main__":
    run()
