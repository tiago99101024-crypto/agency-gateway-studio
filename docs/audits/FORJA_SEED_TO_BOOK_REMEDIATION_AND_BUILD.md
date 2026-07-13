# FORJA_SEED_TO_BOOK_REMEDIATION_AND_BUILD

## PAPEL

Você é o executor técnico responsável por transformar a FORJA de um conjunto parcialmente configurado em um fluxo comprovadamente operacional de:

`SEED -> DISCOVERY -> RESEARCH -> CONSOLIDATION -> BOOK`

Nesta etapa, você deve usar a auditoria já concluída como fonte de verdade.

Não invente gaps.

Não reconstrua tudo do zero.

Não crie agentes ou skills duplicados quando houver componentes locais reutilizáveis.

## AMBIENTE

Versão ativa:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03`

Ponteiro ativo:

`C:\TiagoOS\FORJA_ACTIVE_VERSION.json`

Auditoria concluída em:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\agent-skill-readiness`

Resultado atual:

`FORJA_SEED_TO_BOOK_NOT_READY`

Resumo:

- 62 agentes encontrados;
- 0 agentes comprovadamente operacionais;
- 62 agentes parcialmente operacionais;
- 38 skills configuradas sem prova de ativação;
- 4 gaps `BLOCKER`;
- 8 gaps `HIGH`;
- 9 suítes locais executadas com `PASS`;
- nenhuma prova E2E de `SEED -> DISCOVERY -> RESEARCH -> CONSOLIDATION -> BOOK`.

## OBJETIVO

Corrigir e construir somente o que estiver comprovadamente faltando nos artefatos da auditoria, até existir uma cadeia funcional, testada e rastreável capaz de:

1. receber uma semente mínima;
2. resolver a identidade da empresa;
3. descobrir fontes;
4. executar pesquisa;
5. consolidar fatos com proveniência;
6. gerar um book inicial de inteligência;
7. atualizar esse book incrementalmente;
8. preservar isolamento entre clientes;
9. declarar incertezas;
10. impedir ações externas sem autorização.

## FONTE OBRIGATÓRIA

Leia integralmente os 13 artefatos existentes em:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\agent-skill-readiness`

No mínimo, use:

1. `FORJA_AGENT_INVENTORY.md`
2. `FORJA_SKILL_INVENTORY.md`
3. `FORJA_ORCHESTRATION_MAP.md`
4. `FORJA_RUNTIME_ACTIVATION_AUDIT.md`
5. `FORJA_PUBLIC_INTELLIGENCE_CAPABILITY_MATRIX.md`
6. `FORJA_CONNECTED_INTELLIGENCE_CAPABILITY_MATRIX.md`
7. `FORJA_CLIENT_BOOK_CAPABILITY_MATRIX.md`
8. `FORJA_SEED_TO_BOOK_E2E_READINESS.md`
9. `FORJA_EXTERNAL_REPOSITORY_USAGE_REGISTER.md`
10. `FORJA_GAPS_AND_BUILD_PRIORITIES.md`
11. `FORJA_READINESS_SUMMARY.json`
12. `FORJA_AUDIT_SNAPSHOT.json`
13. `FORJA_AGENT_SKILL_READINESS_AUDIT_HANDOFF.md`

Não aceite apenas o resumo acima.

Use os IDs, evidências, dependências e critérios de aceite registrados nesses artefatos.

## ORDEM DE EXECUÇÃO

### FASE 1: MATRIZ DE REMEDIAÇÃO

Antes de alterar código:

1. extrair os 4 gaps `BLOCKER`;
2. extrair os 8 gaps `HIGH`;
3. relacionar cada gap aos agentes, skills, contratos, testes e componentes existentes;
4. identificar o que pode ser reutilizado;
5. identificar o que precisa ser corrigido;
6. identificar o que realmente precisa ser criado;
7. registrar a ordem de dependência;
8. definir critérios de aceite executáveis.

Criar:

`docs/audits/agent-skill-readiness/remediation/FORJA_REMEDIATION_MATRIX.md`

A matriz deve conter, para cada gap:

- `gap_id`;
- severidade;
- evidência original;
- causa raiz;
- impacto;
- componentes afetados;
- componentes reutilizáveis;
- alteração necessária;
- arquivos previstos;
- testes previstos;
- critério de aceite;
- risco de regressão.

Depois disso, continue a execução sem aguardar nova autorização, desde que todas as mudanças permaneçam locais e dentro das regras desta instrução.

### FASE 2: RUNTIME DE AGENTES E SKILLS

Corrigir o runtime para que exista prova real de:

- registro dos agentes;
- carregamento dos agentes;
- registro das skills;
- ativação das skills;
- roteamento entre agente e skill;
- verificação de dependências;
- detecção de componente ausente;
- health check;
- telemetria local;
- persistência de estado;
- retomada após interrupção.

Não considerar um agente operacional apenas porque o arquivo existe.

Para classificar um agente como `OPERATIONAL`, deve existir prova de:

1. carregamento no runtime;
2. entrada válida;
3. execução;
4. saída validada por contrato;
5. erro controlado;
6. teste reproduzível.

Para classificar uma skill como `OPERATIONAL`, deve existir prova de:

1. descoberta pelo loader;
2. ativação;
3. chamada real por agente ou orquestrador;
4. saída validada;
5. teste reproduzível.

### FASE 3: ORQUESTRADOR SEED-TO-BOOK

Usar o componente local mais adequado como orquestrador.

Confirmar se o Bruxo já possui implementação suficiente.

Se possuir, corrigir e conectar.

Se não possuir, criar somente a camada mínima faltante, sem duplicar responsabilidades já existentes.

O orquestrador deve:

1. receber uma semente mínima;
2. criar ou localizar o namespace do cliente;
3. normalizar a entrada;
4. resolver identidade;
5. selecionar agentes e skills;
6. executar descoberta;
7. executar pesquisa;
8. consolidar evidências;
9. gerar o book;
10. registrar proveniência;
11. registrar confiança;
12. registrar conflitos;
13. registrar lacunas;
14. persistir checkpoint;
15. retomar após falha;
16. evitar loops;
17. impedir mistura entre clientes;
18. impedir ação externa não autorizada.

### FASE 4: CONTRATO DE SEMENTE

Criar ou corrigir um contrato canônico para entrada mínima.

Entradas aceitas:

- nome;
- Instagram;
- Facebook;
- Google Business Profile;
- site;
- URL pública;
- arquivo;
- pasta;
- combinação desses itens.

O contrato deve permitir entrada pequena sem exigir onboarding completo.

Campos mínimos esperados:

- `seed_type`;
- `seed_value`;
- `client_namespace` opcional;
- `authorization_scope`;
- `allowed_actions`;
- `blocked_actions`;
- `requested_depth`;
- `created_at`;
- `request_id`.

### FASE 5: IDENTITY RESOLUTION

Implementar ou corrigir a resolução de identidade.

A saída deve distinguir:

- entidade confirmada;
- entidade provável;
- entidade conflitante;
- entidade não resolvida;
- aliases;
- localização;
- domínio;
- perfis associados;
- evidências usadas;
- nível de confiança.

Não misturar empresas com nomes semelhantes.

### FASE 6: PUBLIC DISCOVERY E RESEARCH

Conectar os componentes já existentes para cobrir, quando houver ferramenta disponível:

- descoberta de site;
- Instagram;
- Facebook;
- Google Business Profile;
- presença digital;
- concorrentes;
- benchmark;
- mercado;
- avaliações;
- produtos;
- serviços;
- preços públicos;
- ofertas públicas;
- identidade visual;
- paleta;
- conteúdo;
- linguagem;
- sinais de engajamento;
- ICP provável;
- jornada pública;
- WhatsApp;
- formulários;
- reservas;
- páginas de conversão.

Não simular acesso externo inexistente.

Quando uma capacidade externa não estiver disponível no runtime, o sistema deve:

1. declarar a limitação;
2. gerar uma tarefa pendente estruturada;
3. continuar nas áreas possíveis;
4. não inventar resultado.

A ausência de uma fonte não deve travar todo o fluxo.

### FASE 7: CONSOLIDAÇÃO E PROVENIÊNCIA

A consolidação deve gerar fatos estruturados com:

- `fact_id`;
- área;
- valor;
- estado;
- confiança;
- `source_id`;
- origem;
- data da fonte;
- data de coleta;
- tipo da fonte;
- se é dado bruto ou derivado;
- conflitos;
- limitações;
- histórico de mudança.

Estados mínimos:

- `CONFIRMED`
- `PROBABLE`
- `PARTIAL`
- `CONFLICTED`
- `HISTORICAL`
- `UNVERIFIED`
- `UNKNOWN`
- `NOT_FOUND`
- `BLOCKED`

Não usar repetição como prova automática.

Não transformar hipótese em fato.

### FASE 8: CLIENT INTELLIGENCE BOOK

Criar ou corrigir o compilador do book para manter, conforme houver evidência:

- identidade;
- localização;
- mercado;
- concorrentes;
- benchmark;
- produtos;
- serviços;
- preços;
- ofertas;
- ICP;
- personas úteis;
- posicionamento;
- diferenciais;
- fragilidades;
- identidade visual;
- paleta;
- tipografia, quando identificável;
- tom de voz;
- conteúdo;
- mídia;
- criativos;
- tracking;
- CRM;
- processo comercial;
- operação;
- capacidade;
- riscos;
- oportunidades;
- conflitos;
- lacunas;
- decisões;
- proveniência;
- nível de confiança;
- histórico.

O book deve ser:

- estruturado;
- versionado;
- incremental;
- consultável;
- atualizável;
- exportável;
- isolado por cliente;
- protegido contra sobrescrita silenciosa.

Gerar no mínimo:

- JSON canônico;
- Markdown legível;
- readiness por área;
- snapshot;
- registro de proveniência.

### FASE 9: ATUALIZAÇÃO INCREMENTAL

Adicionar teste que prove:

1. execução inicial com uma semente;
2. criação do book;
3. entrada de uma nova fonte;
4. atualização somente das áreas afetadas;
5. preservação do histórico;
6. preservação de fatos não afetados;
7. alteração correta da prontidão;
8. ausência de reprocessamento integral desnecessário.

### FASE 10: TESTE E2E LOCAL

Criar um teste local reproduzível:

`SEED -> DISCOVERY -> RESEARCH -> CONSOLIDATION -> BOOK`

O teste deve começar com uma semente mínima.

Não usar os 4.458 arquivos do America House como entrada obrigatória.

Pode usar fixture local controlada para provar a cadeia de runtime.

O teste deve provar:

- seed intake;
- namespace;
- identity resolution;
- roteamento;
- chamada de agentes;
- ativação de skills;
- descoberta;
- pesquisa;
- consolidação;
- proveniência;
- book;
- snapshot;
- retomada;
- atualização incremental;
- isolamento entre dois clientes;
- bloqueio de ações externas.

### FASE 11: TESTE REAL CONTROLADO

Somente se já existir capacidade pública de leitura segura e sem credenciais, executar um smoke real com uma semente pública.

Não acessar contas privadas.

Não fazer login.

Não enviar mensagens.

Não alterar campanhas.

Não publicar nada.

Se a leitura pública externa não estiver autorizada ou disponível, não fingir o teste.

Registrar:

`REAL_PUBLIC_SEED_TEST_NOT_EXECUTED`

com o motivo objetivo.

## REGRAS DE IMPLEMENTAÇÃO

- reutilizar componentes existentes antes de criar novos;
- preservar contratos canônicos já aprovados;
- preservar V1, RC_02 e versões anteriores;
- não mover ou apagar agentes de pesquisa existentes;
- não sobrescrever agentes ou skills sem inventário e backup;
- não retirar arquivos da quarentena;
- não usar credenciais;
- não acessar contas reais;
- não alterar campanhas;
- não publicar no bridge;
- não instalar código externo sem necessidade comprovada;
- não importar repositório do GitHub nesta etapa, salvo se um gap `BLOCKER` não puder ser resolvido localmente e a auditoria já registrar essa necessidade;
- não criar dashboard ou interface;
- não criar agentes decorativos;
- não declarar `PASS` sem teste;
- manter ações externas desativadas.

## GITHUB E VERSIONAMENTO

Nesta execução:

- alterações locais são permitidas;
- criar backups e snapshots antes de alterações críticas;
- não executar push;
- não abrir pull request;
- não publicar release;
- não alterar o repositório remoto;
- não criar commit final sem autorização explícita do Tiago.

Manter:

`external_actions: NONE`

## TESTES

Executar:

1. testes já existentes afetados;
2. testes unitários novos;
3. testes de contratos;
4. testes de loader;
5. testes de registry;
6. testes de ativação de skills;
7. testes de roteamento;
8. testes do orquestrador;
9. teste E2E local;
10. teste incremental;
11. teste de retomada;
12. teste de isolamento;
13. regressão completa.

Todo teste deve registrar:

- comando;
- resultado;
- duração;
- arquivos afetados;
- evidência de saída;
- motivo, quando não executado.

## SAÍDAS OBRIGATÓRIAS

Criar ou atualizar:

1. `docs/audits/agent-skill-readiness/remediation/FORJA_REMEDIATION_MATRIX.md`
2. `docs/audits/agent-skill-readiness/remediation/FORJA_BLOCKER_RESOLUTION_REPORT.md`
3. `docs/audits/agent-skill-readiness/remediation/FORJA_HIGH_GAP_RESOLUTION_REPORT.md`
4. `docs/audits/agent-skill-readiness/remediation/FORJA_RUNTIME_ACTIVATION_PROOF.md`
5. `docs/audits/agent-skill-readiness/remediation/FORJA_AGENT_OPERATIONAL_STATUS.md`
6. `docs/audits/agent-skill-readiness/remediation/FORJA_SKILL_OPERATIONAL_STATUS.md`
7. `docs/audits/agent-skill-readiness/remediation/FORJA_SEED_TO_BOOK_E2E_PROOF.md`
8. `docs/audits/agent-skill-readiness/remediation/FORJA_INCREMENTAL_UPDATE_PROOF.md`
9. `docs/audits/agent-skill-readiness/remediation/FORJA_ISOLATION_AND_RECOVERY_PROOF.md`
10. `docs/audits/agent-skill-readiness/remediation/FORJA_REMEDIATION_TEST_REPORT.md`
11. `docs/audits/agent-skill-readiness/remediation/FORJA_REMEDIATION_SNAPSHOT.json`
12. `docs/handoffs/FORJA_SEED_TO_BOOK_REMEDIATION_HANDOFF.md`

## CRITÉRIO DE ACEITE

Somente declarar `FORJA_SEED_TO_BOOK_READY` quando houver prova de:

1. seed mínima aceita;
2. namespace criado;
3. identidade resolvida;
4. agentes carregados;
5. skills ativadas;
6. orquestração executada;
7. descoberta executada;
8. pesquisa executada;
9. consolidação executada;
10. proveniência registrada;
11. book criado;
12. readiness por área criado;
13. atualização incremental comprovada;
14. retomada comprovada;
15. isolamento entre clientes comprovado;
16. ações externas bloqueadas;
17. regressão aprovada.

Se parte da cadeia funcionar, declarar:

`FORJA_SEED_TO_BOOK_PARTIALLY_READY`

Se a cadeia mínima continuar quebrada, declarar:

`FORJA_SEED_TO_BOOK_NOT_READY`

## RETORNO FINAL

O retorno deve informar:

1. os 4 gaps `BLOCKER` encontrados na auditoria;
2. os 8 gaps `HIGH` encontrados;
3. gaps resolvidos;
4. gaps ainda abertos;
5. causa dos gaps não resolvidos;
6. arquivos criados;
7. arquivos alterados;
8. agentes agora comprovadamente operacionais;
9. agentes ainda parciais;
10. skills agora comprovadamente operacionais;
11. skills ainda sem prova;
12. orquestrador usado;
13. seed contract usado;
14. fluxo E2E executado;
15. atualização incremental executada;
16. isolamento executado;
17. retomada executada;
18. teste real público executado ou não;
19. testes executados;
20. testes com falha;
21. regressões encontradas;
22. estado final;
23. confirmação de ausência de campanha alterada;
24. confirmação de ausência de bridge publicado;
25. confirmação de ausência de commit e push;
26. confirmação de `external_actions: NONE`.

## REGRA FINAL

A meta não é transformar todos os 62 agentes em operacionais por força bruta.

A meta é provar uma cadeia funcional mínima e real usando os componentes certos.

Corrija os gaps comprovados.

Evite duplicação.

Não maquie prontidão.

O resultado precisa executar, persistir, retomar e produzir o book.