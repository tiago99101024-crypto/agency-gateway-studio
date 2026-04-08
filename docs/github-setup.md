# GitHub — setup inicial

Git local: ✅ pronto (commit 647f40c)
Path oficial: `C:/Users/liant/OneDrive/Desktop/Claude Code/agency-gateway-repo/`
Email do commit: `tiago99101024@gmail.com`

Falta apenas: criar o repo no GitHub e empurrar.

---

## Opção A — GitHub Desktop (recomendado — já instalado)

GitHub Desktop está instalado em:
`C:/Users/liant/AppData/Local/GitHubDesktop/app-3.5.6/`

**Passos:**

1. Abrir GitHub Desktop
2. `File` → `Add Local Repository…`
3. Selecionar: `C:/Users/liant/OneDrive/Desktop/Claude Code/agency-gateway-repo`
4. GitHub Desktop detecta o repo e mostra o histórico
5. Clicar `Publish repository` (botão no topo)
6. Nome: `agency-gateway`
7. Marcar `Keep this code private` ✅
8. Clicar `Publish Repository`

Pronto. Remote configurado automaticamente. Histórico no GitHub.

---

## Opção B — Terminal

```bash
# Na raiz do projeto:
cd "C:/Users/liant/OneDrive/Desktop/Claude Code/agency-gateway-repo"

# 1. Criar repo em github.com/new
#    - Nome: agency-gateway
#    - Visibilidade: Private
#    - NÃO inicializar com README, .gitignore ou license

# 2. Copiar a URL e rodar:
git remote add origin https://github.com/SEU_USUARIO/agency-gateway.git
git branch -M main
git push -u origin main
```

---

## Verificar depois

```bash
git remote -v
# origin  https://github.com/... (fetch)
# origin  https://github.com/... (push)
```

---

## Labels do GitHub

Após criar o repo, aplicar as labels de `.github/labels.yml`.

Via browser:
1. Ir em `github.com/SEU_USUARIO/agency-gateway/labels`
2. Criar manualmente as labels do arquivo

---

## Issues e kanban

Templates disponíveis automaticamente após o push:
- `tarefa-campanha.md`
- `tarefa-conteudo.md`

Criar issue: `github.com/SEU_USUARIO/agency-gateway/issues/new/choose`
