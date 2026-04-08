# Boot — agency-gateway

Operação diária em 3 linhas.

---

## Subir o dashboard

```bat
REM Windows — qualquer terminal na raiz do projeto:
python dashboard_v2.py 8766

REM Ou via script:
scripts\start.bat
```

Abrir em: **http://localhost:8766**

O que você deve ver: sidebar com runs, menu superior com abas Runs / Skills.

---

## Encerrar

`Ctrl+C` no terminal onde o servidor está rodando.

Dados persistem em `dashboard/data/runs/*.json`. Nada se perde ao fechar.

---

## Porta

Padrão: `8766`. Para usar outra: `python dashboard_v2.py 8888`.

Se aparecer "Address already in use": a sessão anterior não encerrou.
Solução: fechar o terminal anterior, ou usar outra porta.

---

## Estado do Git

```bash
git status        # ver o que mudou
git add -A        # stagear tudo (cuidado: veja o que está subindo)
git commit -m "msg"
git push          # só depois de conectar remote (ver docs/github-setup.md)
```

---

## Abrir Claude Code no projeto

Abrir VS Code na raiz do projeto. Claude Code deve detectar `CLAUDE.md` automaticamente.

Se não detectar: confirmar que o workspace está apontando para a raiz
(`agency-gateway/`, não uma subpasta).

---

## Verificação rápida de saúde

```bash
python -c "import json, pathlib; runs = list(pathlib.Path('dashboard/data/runs').glob('*.json')); print(f'{len(runs)} runs em disco')"
```

Esperado: número de runs corresponde ao que aparece no dashboard.

---

## Shutdown / continuidade

Não há processo de shutdown especial. Fechar o servidor é suficiente.

Para continuar depois:
1. Subir o servidor (`python dashboard_v2.py 8766`)
2. Abrir http://localhost:8766
3. A run em andamento aparece com status `in_progress`

---

## O que NÃO fazer ao iniciar

- Não rodar `dashboard.py` (v1 antiga — não usar)
- Não editar `dashboard/data/runs/*.json` manualmente enquanto o servidor está rodando
- Não alterar porta na metade de uma sessão (links do browser ficam quebrados)
