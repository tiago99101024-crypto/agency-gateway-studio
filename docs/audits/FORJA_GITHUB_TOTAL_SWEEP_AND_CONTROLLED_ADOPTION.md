# FORJA_GITHUB_TOTAL_SWEEP_AND_CONTROLLED_ADOPTION

## PAPEL

Você é o pesquisador técnico, auditor de segurança e engenheiro de integração da FORJA.

Esta execução NÃO é apenas uma auditoria documental.

Você deve:

1. recuperar todos os repositórios, agentes, skills e ideias externas já citadas anteriormente;
2. realizar uma varredura ampla e paginada no GitHub;
3. começar pelos projetos com mais estrelas em cada categoria;
4. continuar pelas faixas intermediárias e projetos de nicho relevantes;
5. auditar licença, segurança, manutenção e compatibilidade;
6. selecionar o que realmente melhora a FORJA;
7. adaptar ou implementar os componentes aprovados em laboratório isolado;
8. integrar ao runtime ativo apenas o que passar nos testes;
9. provar operacionalmente o ganho obtido.

Não encerre a tarefa entregando somente uma lista de links, ideias, matrizes ou recomendações.

A execução deve terminar com adoções reais, adaptações reais ou rejeições tecnicamente justificadas.

## AMBIENTE

Versão ativa:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03`

Ponteiro ativo:

`C:\TiagoOS\FORJA_ACTIVE_VERSION.json`

Versões preservadas:

- `C:\TiagoOS\FORJA_FULL_V1`
- `C:\TiagoOS\FORJA_FULL_V1_1_RC_02`
- candidata original preservada

Auditoria anterior:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\agent-skill-readiness`

Remediação anterior:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\agent-skill-readiness\remediation`

Handoff obrigatório:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\FORJA_SEED_TO_BOOK_REMEDIATION_HANDOFF.md`

Estado atual conhecido:

- `FORJA_SEED_TO_BOOK_PARTIALLY_READY`
- 62 agentes encontrados
- 3 agentes operacionais
- 59 agentes parciais
- 38 skills encontradas
- 3 skills operacionais
- 35 skills sem prova operacional
- G001 a G004 resolvidos no fluxo local
- G005, G006, G007, G008, G010 e G012 resolvidos
- G009 parcial por conectores live sem autorização/configuração
- G011 aberto por ausência de análise multimodal real
- camada seed-to-book determinística conectada ao entrypoint do Bruxo
- E2E local, incremental, isolamento, retomada, idempotência e regressão em `PASS`
- teste público real ainda não executado

## AUTORIZAÇÃO DESTA EXECUÇÃO

Está autorizado:

- consultar GitHub público;
- usar GitHub API pública ou `gh` em modo somente leitura;
- clonar repositórios públicos em laboratório isolado;
- consultar documentação pública;
- consultar páginas públicas necessárias para validar bibliotecas e projetos;
- baixar código-fonte público para auditoria em laboratório;
- executar testes locais seguros dos candidatos;
- criar adaptações locais na versão ativa;
- criar ou alterar agentes, skills, adapters, registries, testes e documentação quando forem necessários para integração aprovada;
- executar um teste público somente leitura após a integração, sem login e sem envio de dados.

Estado de ações externas desta etapa:

`external_actions: READ_ONLY_PUBLIC_GITHUB_AND_WEB`

Não está autorizado:

- acessar contas privadas;
- usar credenciais reais;
- autenticar Meta, Google, CRM, WhatsApp ou sistemas de reservas;
- alterar campanhas;
- publicar no bridge;
- enviar mensagens;
- criar contas;
- modificar repositórios externos;
- abrir issues ou pull requests em projetos externos;
- executar push da FORJA;
- instalar globalmente scripts desconhecidos;
- executar `install.sh`, hooks, MCPs, daemons ou binários externos sem auditoria prévia;
- copiar pacotes inteiros diretamente para o runtime;
- retirar arquivos de quarentena;
- alterar V1, RC_02 ou a candidata original.

## REGRA CENTRAL

Não pesquisar apenas para documentar.

Não copiar apenas porque o projeto tem muitas estrelas.

Estrelas definem a ordem inicial de inspeção, não a decisão final.

Toda adoção precisa provar pelo menos um destes ganhos:

- fechar um gap atual;
- tornar um agente ou skill realmente operacional;
- melhorar descoberta pública;
- melhorar pesquisa com evidência;
- melhorar memória e inteligência incremental;
- adicionar análise multimodal real;
- reduzir custo, contexto ou tokens sem degradar resultado;
- melhorar isolamento, segurança, observabilidade ou recuperação;
- melhorar a qualidade do book de inteligência;
- reduzir duplicação entre os 62 agentes e 38 skills.

## FASE 0 — LEITURA OBRIGATÓRIA

Antes de pesquisar ou alterar qualquer coisa:

1. ler os 13 artefatos da auditoria anterior;
2. ler os relatórios da remediação;
3. ler o handoff de remediação;
4. confirmar o estado real do runtime;
5. registrar baseline dos agentes, skills, testes e gaps;
6. criar hashes dos arquivos que poderão ser alterados;
7. criar uma pasta isolada para esta execução.

Pasta sugerida:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\forja_lab\open_source_adoption`

Não reexecutar auditorias completas sem necessidade.

Usar os resultados existentes como baseline.

## FASE 1 — RECUPERAÇÃO DO QUE JÁ FOI CITADO

Localizar, identificar e auditar primeiro os projetos e pacotes que já foram discutidos, comprados, baixados, mencionados ou deixados pendentes.

### Candidatos obrigatórios

1. `ruvnet/ruflo`
2. `VoltAgent/awesome-claude-code-subagents`
3. `affaan-m/ECC`
4. `obra/superpowers`
5. `666ghj/MiroFish`
6. pacote Opensquad / Agent Agency / Squads100 localizado anteriormente em:
   
   `C:\Users\liant\Downloads\Agent_agency-main\Agent_agency-main`
7. Superpowers
8. Everything Claude Code
9. Open Design
10. referências de `CLAUDE.md` e práticas de Karpathy
11. Copy Master / materiais associados a Ladeira quando existirem localmente
12. meta skills já citadas, incluindo prompt, humanizer, fact-checker, find-skills, front-end e slides
13. todos os repositórios externos registrados em handoffs, manifests, inventários, downloads e históricos locais

### RTK

O item chamado anteriormente de `RTK` precisa ser recuperado corretamente.

Não assumir o repositório apenas pelo nome.

Pesquisar:

- arquivos locais;
- handoffs;
- históricos;
- downloads;
- manifests;
- aliases;
- URLs antigas;
- forks;
- READMEs;
- referências a token optimization;
- referências a Rust Token Killer;
- referências a skills RTK;
- referências a ferramentas de redução de contexto ou tokens.

Identificar o upstream canônico por:

- owner original;
- histórico de commits;
- README;
- releases;
- forks;
- licença;
- correspondência com a descrição citada anteriormente.

Se a identidade exata continuar incerta, registrar até cinco candidatos com evidências e não escolher silenciosamente.

### Pacote Opensquad / Squads100

Preservar a regra existente:

- não copiar diretamente para runtime;
- não executar `install.sh`;
- não ativar `.mcp.json`;
- não usar browser, secrets, daemons ou scripts sem auditoria;
- extrair somente componentes úteis e seguros;
- manter proveniência;
- adaptar para contratos da FORJA;
- evitar agentes duplicados.

## FASE 2 — VARREDURA NOVA NO GITHUB

Executar uma pesquisa ampla, paginada e reproduzível.

Não parar nos candidatos já conhecidos.

### Ordem por estrelas

Para cada categoria:

1. pesquisar por `sort=stars` e `order=desc`;
2. analisar primeiro projetos acima de 20.000 estrelas;
3. depois projetos entre 5.000 e 19.999 estrelas;
4. depois projetos entre 1.000 e 4.999 estrelas;
5. depois projetos abaixo de 1.000 estrelas somente quando preencherem um gap específico ou apresentarem solução técnica diferenciada;
6. continuar a paginação até ocorrer uma destas condições:
   - cinco páginas completas avaliadas na categoria;
   - 100 repositórios únicos avaliados na categoria;
   - três páginas consecutivas sem nenhum novo candidato viável.

Não declarar “varredura total do GitHub”.

Declarar:

`EXHAUSTIVE_WITHIN_DEFINED_QUERY_MATRIX`

Registrar todas as queries e páginas consultadas para reprodução.

### Categorias obrigatórias

1. orquestração multiagente;
2. Claude Code agents;
3. Claude Code skills;
4. subagents e registries;
5. deep research;
6. pesquisa web com citações;
7. descoberta pública de empresas;
8. browser automation;
9. crawling e scraping;
10. extração estruturada de páginas;
11. Instagram público;
12. Facebook público;
13. Google Business Profile / Google Maps público;
14. avaliações e reputação;
15. market intelligence;
16. competitor intelligence;
17. benchmark;
18. ICP e audience research;
19. brand intelligence;
20. identidade visual;
21. extração de paleta;
22. análise de imagens;
23. análise de vídeo;
24. multimodal agents;
25. OCR e document intelligence;
26. RAG;
27. knowledge graph;
28. memória temporal;
29. memória de agentes;
30. provenance e citations;
31. deduplicação e entity resolution;
32. observabilidade de agentes;
33. avaliações e benchmarks de agentes;
34. segurança de agentes;
35. sandboxing;
36. proteção contra prompt injection;
37. conectores e ingestion frameworks;
38. Meta, Google, CRM e analytics adapters;
39. context engineering;
40. token optimization;
41. compactação de contexto;
42. skill discovery;
43. skill activation;
44. self-improving agents;
45. atualização controlada de agentes;
46. agent registries e marketplaces;
47. geração de books e relatórios estruturados;
48. local-first AI;
49. Windows-compatible agent runtimes;
50. testes de retomada, idempotência e isolamento.

### Candidatos novos obrigatórios para inspeção inicial

Além dos já citados, inspecionar pelo menos:

- `microsoft/agent-framework`
- `openai/openai-agents-python`
- `FoundationAgents/MetaGPT`
- `camel-ai/camel`
- `langchain-ai/langgraph`
- `browser-use/browser-use`
- `vercel-labs/agent-browser`
- `nanobrowser/nanobrowser`
- `firecrawl/firecrawl`
- `apify/crawlee`
- `apify/crawlee-python`
- `adbar/trafilatura`
- `assafelovic/gpt-researcher`
- `Alibaba-NLP/DeepResearch`
- `dzhng/deep-research`
- `zilliztech/deep-searcher`
- `getzep/graphiti`
- `bytedance/UI-TARS-desktop`
- `StarTrail-org/PixelRAG`
- `davepoon/buildwithclaude`
- `glittercowboy/taches-cc-resources`
- `zubair-trabzada/ai-marketing-claude`

Essa lista é semente, não limite.

## FASE 3 — REGISTRO TÉCNICO DE CADA REPOSITÓRIO

Para cada repositório avaliado, registrar:

- `repository_id`;
- `owner/name`;
- URL canônica;
- categoria;
- descrição;
- estrelas;
- forks;
- watchers quando disponível;
- data de criação;
- data da última atualização;
- data do último commit;
- releases;
- issues abertas;
- contributors;
- linguagem principal;
- tamanho;
- licença;
- archived;
- upstream ou fork;
- maturidade;
- documentação;
- cobertura de testes;
- CI;
- dependências;
- scripts de instalação;
- hooks;
- MCPs;
- binários;
- telemetria;
- chamadas de rede;
- manipulação de secrets;
- permissões exigidas;
- compatibilidade Windows;
- compatibilidade Claude Code;
- compatibilidade Codex;
- compatibilidade com contratos da FORJA;
- sobreposição com agentes existentes;
- sobreposição com skills existentes;
- gap atendido;
- esforço de adoção;
- risco;
- evidência;
- commit SHA auditado.

## FASE 4 — SCORE E DECISÃO

Aplicar score de 0 a 100:

- aderência aos gaps da FORJA: 0 a 25;
- qualidade técnica e testes: 0 a 15;
- maturidade e manutenção: 0 a 15;
- segurança e licença: 0 a 20;
- compatibilidade arquitetural: 0 a 15;
- custo de integração e operação: 0 a 10.

As estrelas não entram diretamente no score final.

Elas servem para ordenar a descoberta.

Classificações permitidas:

- `ADOPT_NOW`
- `ADAPT_PATTERN`
- `SANDBOX_POC`
- `WATCHLIST`
- `REJECT_SECURITY`
- `REJECT_LICENSE`
- `REJECT_ABANDONED`
- `REJECT_DUPLICATE`
- `REJECT_INCOMPATIBLE`
- `REJECT_NO_MATERIAL_GAIN`

Toda decisão precisa apontar para evidência.

## FASE 5 — ADOÇÃO CONTROLADA

Não parar na shortlist.

Para cada item classificado como `ADOPT_NOW` ou `ADAPT_PATTERN`:

1. fixar o commit SHA analisado;
2. registrar licença;
3. identificar arquivos e conceitos realmente úteis;
4. criar adapter ou implementação mínima no laboratório;
5. não copiar o repositório inteiro;
6. preservar autoria e atribuição quando exigido;
7. adaptar interfaces aos contratos da FORJA;
8. impedir acesso a secrets;
9. impedir ações externas não autorizadas;
10. criar testes unitários;
11. criar testes de integração;
12. testar no Windows;
13. testar retomada;
14. testar idempotência;
15. testar isolamento entre clientes;
16. testar rollback;
17. comparar com o componente atual;
18. promover para o runtime somente se houver ganho comprovado.

Se um projeto externo for bom, mas muito pesado ou incompatível, implementar apenas o padrão útil.

Não criar dezenas de novos agentes por copiar listas externas.

Preferir:

- consolidar agentes redundantes;
- melhorar os agentes existentes;
- ativar skills realmente usadas;
- criar registries e adapters;
- adicionar capacidade ao Bruxo;
- manter especialização somente quando houver função distinta e testável.

## PRIORIDADES DE IMPLEMENTAÇÃO

### Prioridade 1 — Public intelligence real

Fechar a ausência de ferramenta pública read-only.

A FORJA precisa conseguir receber uma URL pública e executar:

`SEED -> DISCOVERY -> RESEARCH -> CONSOLIDATION -> BOOK`

Implementar ou adaptar capacidades para:

- navegação pública;
- crawling controlado;
- extração de texto;
- descoberta de links oficiais;
- entity resolution;
- citações;
- snapshots;
- rate limiting;
- respeito a bloqueios e indisponibilidade;
- tratamento de páginas dinâmicas;
- fallback entre extratores.

### Prioridade 2 — G011 multimodal

Implementar análise multimodal real para:

- imagens;
- logotipos;
- paleta;
- tipografia aparente;
- padrões visuais;
- formatos criativos;
- screenshots;
- documentos com conteúdo visual;
- vídeos quando tecnicamente viável.

Não declarar identidade visual completa com base apenas em texto.

### Prioridade 3 — Skills e agentes operacionais

Usar os melhores padrões encontrados para:

- provar ativação das skills;
- reduzir as 35 skills sem prova operacional;
- tornar agentes relevantes realmente operacionais;
- eliminar duplicações;
- conectar skills ao registry e ao Bruxo;
- produzir logs de ativação;
- criar testes de consumo real.

### Prioridade 4 — Pesquisa, memória e inteligência incremental

Avaliar e adotar padrões úteis para:

- deep research;
- citations;
- temporal knowledge graph;
- memória versionada;
- entity resolution;
- atualização incremental;
- detecção de contradição;
- confiança por fato;
- histórico do cliente.

### Prioridade 5 — RTK e redução de contexto

Após identificar corretamente o RTK:

- medir economia de tokens/contexto;
- medir perda de informação;
- testar em tarefas reais da FORJA;
- rejeitar se degradar evidência, proveniência ou decisões;
- adaptar somente se houver ganho mensurável.

### Prioridade 6 — G009 conectores

Não conectar contas reais nesta etapa.

Pode:

- implementar contratos;
- adapters;
- mocks;
- fixtures;
- validation schemas;
- testes de autenticação simulada;
- interfaces de autorização;
- dry-run.

Manter conectores live desativados até autorização específica.

## FASE 6 — TESTE PÚBLICO REAL

Após integrar as capacidades aprovadas, executar um teste público somente leitura.

Semente autorizada para teste:

`https://www.instagram.com/americahouseoficial/`

Regras:

- sem login;
- sem mensagem;
- sem interação;
- sem coleta de dados pessoais de consumidores;
- sem contornar bloqueios;
- sem técnicas evasivas;
- sem acessar áreas privadas;
- usar apenas fontes públicas admissíveis;
- registrar falhas de acesso honestamente;
- tentar descobrir outras fontes oficiais por links públicos e pesquisa aberta;
- gerar book proporcional à evidência encontrada.

O teste deve provar:

- resolução da identidade;
- descoberta de fontes;
- coleta pública;
- pesquisa;
- citações;
- consolidação;
- book;
- análise multimodal;
- atualização incremental;
- isolamento;
- retomada;
- ausência de ações externas de escrita.

Não usar os 4.458 arquivos do piloto como entrada do teste.

Eles podem ser usados apenas depois para comparação, nunca para alimentar a primeira execução pública.

## FASE 7 — PROMOÇÃO E ROLLBACK

Antes de promover qualquer componente:

- registrar arquivos afetados;
- registrar hashes anteriores;
- registrar versão externa e commit SHA;
- registrar licença;
- registrar testes;
- criar rollback local;
- verificar que V1 e RC_02 permanecem intactos;
- verificar isolamento do piloto America House;
- rodar regressão completa.

Não criar commit nem push nesta execução.

## SAÍDAS OBRIGATÓRIAS

Criar em:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\open-source-total-sweep`

1. `FORJA_GITHUB_QUERY_MATRIX.md`
2. `FORJA_GITHUB_REPOSITORY_INVENTORY.json`
3. `FORJA_KNOWN_CANDIDATES_RECOVERY.md`
4. `FORJA_RTK_IDENTITY_RESOLUTION.md`
5. `FORJA_RUFLO_AUDIT.md`
6. `FORJA_MIROFISH_AUDIT.md`
7. `FORJA_OPENSQUAD_SQUADS100_AUDIT.md`
8. `FORJA_AGENT_AND_SKILL_REPOSITORY_MATRIX.md`
9. `FORJA_PUBLIC_INTELLIGENCE_REPOSITORY_MATRIX.md`
10. `FORJA_MULTIMODAL_REPOSITORY_MATRIX.md`
11. `FORJA_MEMORY_RAG_KNOWLEDGE_GRAPH_MATRIX.md`
12. `FORJA_SECURITY_AND_LICENSE_REGISTER.md`
13. `FORJA_OPEN_SOURCE_SHORTLIST.md`
14. `FORJA_OPEN_SOURCE_REJECTIONS.md`
15. `FORJA_ADOPTION_DECISION_REGISTER.json`
16. `FORJA_SOURCE_CODE_PROVENANCE_LEDGER.json`
17. `FORJA_CONTROLLED_ADOPTION_IMPLEMENTATION.md`
18. `FORJA_AGENT_SKILL_ACTIVATION_AFTER_ADOPTION.md`
19. `FORJA_REAL_PUBLIC_SEED_TEST.md`
20. `FORJA_OPEN_SOURCE_ADOPTION_TEST_RESULTS.json`
21. `FORJA_OPEN_SOURCE_ADOPTION_SNAPSHOT.json`

Criar handoff:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\FORJA_GITHUB_TOTAL_SWEEP_AND_ADOPTION_HANDOFF.md`

## MÉTRICAS OBRIGATÓRIAS

Informar:

- número total de queries;
- páginas consultadas;
- repositórios únicos encontrados;
- repositórios avaliados;
- distribuição por faixa de estrelas;
- distribuição por categoria;
- candidatos históricos recuperados;
- candidatos históricos não localizados;
- novos candidatos encontrados;
- `ADOPT_NOW`;
- `ADAPT_PATTERN`;
- `SANDBOX_POC`;
- rejeitados por segurança;
- rejeitados por licença;
- rejeitados por duplicação;
- componentes realmente implementados;
- componentes promovidos;
- arquivos criados;
- arquivos alterados;
- agentes operacionais antes e depois;
- skills operacionais antes e depois;
- status de G009;
- status de G011;
- status do teste público real;
- regressões executadas;
- falhas;
- rollback testado;
- ações externas realizadas.

## CRITÉRIOS DE ACEITE

Esta execução só pode ser considerada concluída se:

1. candidatos antigos forem recuperados ou explicitamente marcados como não localizados;
2. RTK for identificado ou permanecer com candidatos documentados;
3. Ruflo for auditado pelo repositório canônico `ruvnet/ruflo`;
4. MiroFish for auditado pelo repositório canônico candidato `666ghj/MiroFish`;
5. Opensquad/Squads100 for auditado sem execução insegura;
6. a pesquisa nova for ordenada por estrelas e paginada;
7. várias categorias forem cobertas;
8. licença e segurança forem avaliadas;
9. existir shortlist objetiva;
10. pelo menos um componente ou padrão útil for implementado quando houver candidato seguro;
11. skills e agentes afetados tiverem prova operacional;
12. G011 for atacado com implementação real ou bloqueio técnico comprovado;
13. o teste público real for executado ou houver evidência técnica concreta de impossibilidade;
14. regressão continuar em `PASS`;
15. nenhuma versão preservada for alterada;
16. nenhuma campanha ou conta privada for tocada;
17. nenhum push for realizado.

## ESTADO FINAL

Declarar somente um:

- `FORJA_OPEN_SOURCE_ADOPTION_READY`
- `FORJA_OPEN_SOURCE_ADOPTION_PARTIALLY_READY`
- `FORJA_OPEN_SOURCE_ADOPTION_NOT_READY`

## RETORNO FINAL

O retorno deve informar, sem esconder falhas:

1. estado final;
2. repositórios encontrados;
3. repositórios avaliados;
4. top candidatos por estrelas em cada categoria;
5. candidatos antigos recuperados;
6. identidade do RTK;
7. decisão sobre Ruflo;
8. decisão sobre MiroFish;
9. decisão sobre Opensquad/Squads100;
10. novos candidatos selecionados;
11. componentes adotados;
12. padrões adaptados;
13. componentes rejeitados e motivo;
14. agentes operacionais antes e depois;
15. skills operacionais antes e depois;
16. resultado de G011;
17. resultado de G009;
18. resultado do teste público;
19. arquivos criados e alterados;
20. testes executados;
21. regressões;
22. rollback;
23. licenças incorporadas;
24. proveniência do código incorporado;
25. confirmação de ausência de campanha alterada;
26. confirmação de ausência de bridge publicado;
27. confirmação de ausência de commit e push;
28. `external_actions: READ_ONLY_PUBLIC_GITHUB_AND_WEB`.

## REGRA FINAL

Não produzir mais uma biblioteca de ideias esquecidas.

Pesquisar, selecionar, adaptar, testar e colocar em operação o que realmente melhorar a FORJA.

Não usar quantidade de agentes, skills ou estrelas como substituto de capacidade operacional.