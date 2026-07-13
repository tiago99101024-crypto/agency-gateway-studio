# FORJA_AGENT_SKILL_READINESS_AND_GAP_AUDIT

## PAPEL

Você é um auditor técnico da FORJA.

Nesta execução você NÃO deve construir, corrigir, instalar, ativar, mover, apagar, sobrescrever ou refatorar nada.

Seu trabalho é provar, com evidência local, o que já existe, o que está realmente operacional, o que está apenas documentado, o que está quebrado e o que ainda falta para a FORJA executar um onboarding investigativo completo a partir de uma semente mínima.

## CONTEXTO

Versão ativa:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03`

Ponteiro ativo:

`C:\TiagoOS\FORJA_ACTIVE_VERSION.json`

Versões preservadas:

- `C:\TiagoOS\FORJA_FULL_V1`
- `C:\TiagoOS\FORJA_FULL_V1_1_RC_02`
- candidata original preservada

Namespace piloto existente:

`pilot.real.001`

Raiz do piloto:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients\pilot.real.001`

Marca e arquitetura preferidas:

- FORJA como marca guarda-chuva
- Agência Forja como frente operacional
- Bruxo como possível orquestrador principal
- não usar “Agency Gateway” como nome central de produto

## OBJETIVO REAL DO SISTEMA

A FORJA deve receber uma semente mínima, por exemplo:

- nome da empresa;
- Instagram;
- Facebook;
- Google Business Profile;
- site;
- qualquer URL pública;
- arquivo;
- pasta;
- combinação mínima dessas entradas.

A partir disso, os agentes e skills devem executar um onboarding investigativo progressivo, sem depender de o cliente preencher um formulário completo.

A saída deve ser uma pasta viva, versionada, rastreável e atualizável de inteligência do cliente.

## FLUXO QUE PRECISA SER PROVADO

### ETAPA 1 — PUBLIC INTELLIGENCE ONBOARDING

Com uma semente mínima, o sistema precisa conseguir:

1. resolver a identidade correta da empresa;
2. localizar canais oficiais;
3. descobrir fontes públicas;
4. coletar evidências públicas;
5. pesquisar mercado;
6. mapear concorrentes;
7. produzir benchmark;
8. identificar produtos e serviços;
9. identificar preços e ofertas quando públicos;
10. estimar ICPs com evidência e confiança explícita;
11. analisar posicionamento;
12. analisar diferenciais e fragilidades;
13. analisar identidade visual;
14. extrair paleta de cores;
15. mapear linguagem e tom de voz;
16. analisar conteúdo;
17. analisar formatos, frequência, temas e sinais de engajamento;
18. estimar melhores dias e horários apenas quando houver base;
19. mapear jornada aparente;
20. mapear WhatsApp, reservas, formulários e caminhos públicos;
21. registrar riscos, conflitos, lacunas e limitações;
22. gerar um book inicial de inteligência.

### ETAPA 2 — CONNECTED INTELLIGENCE ONBOARDING

Após autorização do cliente, o sistema precisa conseguir integrar ou receber dados de:

- Meta Business;
- contas de anúncio;
- Instagram;
- Facebook;
- Google Ads;
- GA4;
- GTM;
- Google Business Profile;
- CRM;
- WhatsApp;
- sistemas de reservas;
- plataformas de delivery;
- e-commerce;
- planilhas;
- relatórios comerciais;
- APIs próprias do cliente;
- outras fontes autorizadas.

A partir disso, precisa enriquecer o mesmo book com:

- mídia;
- criativos;
- públicos;
- investimentos;
- leads;
- vendas;
- reservas;
- ticket;
- recorrência;
- funil;
- tracking;
- qualidade de dados;
- processo comercial;
- gargalos;
- capacidade;
- reconciliação entre mídia e resultado comercial.

### ETAPA 3 — CONTINUOUS CLIENT INTELLIGENCE

Toda nova fonte deve atualizar apenas as áreas afetadas.

O sistema não deve:

- reiniciar a investigação;
- apagar histórico;
- substituir fatos silenciosamente;
- transformar lacuna em fato;
- declarar completude artificial.

## ESCOPO DA AUDITORIA

Auditar todo o conjunto relacionado à versão ativa, incluindo quando existirem:

- agentes;
- subagentes;
- orquestradores;
- skills;
- commands;
- hooks;
- workflows;
- schemas;
- contratos;
- prompts;
- manifests;
- registries;
- loaders;
- routers;
- MCPs;
- integrações;
- conectores;
- adaptadores;
- crawlers;
- scrapers;
- browser automation;
- mecanismos de pesquisa;
- ingestão de arquivos;
- análise multimodal;
- módulos de mídia;
- módulos de mercado;
- módulos de ICP;
- módulos de marca;
- módulos de tracking;
- módulos comerciais;
- book compiler;
- persistência;
- versionamento;
- proveniência;
- snapshots;
- testes;
- fixtures;
- smoke tests;
- regressão;
- documentação;
- handoffs;
- configuração de runtime;
- variáveis de ambiente;
- dependências;
- entrypoints;
- scripts de inicialização;
- permissões;
- feature flags;
- mecanismos de ativação.

Também localizar referências relevantes fora da raiz ativa somente quando apontadas por manifests, ponteiros, documentação ou configuração existente.

Não fazer varredura destrutiva.

Não modificar arquivos.

## PERGUNTAS QUE DEVEM SER RESPONDIDAS

### 1. AGENTES

Para cada agente encontrado:

- nome;
- caminho;
- função declarada;
- função real observada;
- entrypoint;
- dependências;
- skills usadas;
- ferramentas usadas;
- inputs;
- outputs;
- contratos;
- schemas;
- testes;
- status real;
- evidência do status;
- duplicidades;
- conflitos;
- gaps.

Classificar cada agente como:

- `OPERATIONAL`
- `PARTIALLY_OPERATIONAL`
- `CONFIGURED_NOT_TESTED`
- `DOCUMENTED_ONLY`
- `BROKEN`
- `DUPLICATED`
- `DEPRECATED`
- `ORPHANED`
- `NOT_FOUND`

### 2. SKILLS

Para cada skill:

- nome;
- caminho;
- objetivo;
- agente consumidor;
- mecanismo de carregamento;
- ativação;
- dependências;
- testes;
- status real;
- evidência;
- conflitos;
- duplicidades;
- gaps.

Classificar cada skill com os mesmos estados.

### 3. ORQUESTRAÇÃO

Provar:

- qual componente recebe a semente inicial;
- qual componente resolve a identidade;
- qual componente decide quais agentes chamar;
- como as skills são selecionadas;
- como erros são tratados;
- como resultados parciais são persistidos;
- como o fluxo retoma após interrupção;
- como novos dados atualizam somente áreas afetadas;
- como o sistema evita loops;
- como o sistema evita agentes duplicados;
- como o sistema evita que um agente invente dados;
- como as decisões humanas entram;
- como o sistema controla ações externas.

Confirmar se o Bruxo é realmente o orquestrador ou apenas uma ideia/documentação.

### 4. PUBLIC INTELLIGENCE

Verificar se existe capacidade real para:

- pesquisa web;
- descoberta de perfis;
- descoberta de site;
- Google Business Profile;
- pesquisa de concorrentes;
- benchmark;
- análise de avaliações;
- análise de presença digital;
- pesquisa local;
- análise de identidade visual;
- extração de paleta;
- análise de conteúdo;
- análise de engajamento;
- pesquisa de ICP;
- pesquisa de mercado;
- detecção de produtos e ofertas;
- captura de fontes e proveniência;
- deduplicação;
- classificação de atualidade;
- geração de book.

Não aceitar documentação como prova de execução.

### 5. CONNECTED INTELLIGENCE

Verificar o estado real de:

- Meta;
- Google Ads;
- GA4;
- GTM;
- Google Business Profile;
- CRM;
- WhatsApp;
- reservas;
- delivery;
- e-commerce;
- APIs genéricas;
- importação de planilhas;
- importação de relatórios.

Separar:

- integração implementada;
- integração configurável;
- integração apenas desenhada;
- integração bloqueada por credencial;
- integração inexistente.

Não acessar credenciais reais.

Não autenticar contas.

Não executar chamadas externas.

### 6. BOOK DE INTELIGÊNCIA

Verificar se existe um compilador real capaz de produzir e manter:

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
- identidade visual;
- paleta;
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
- confiança;
- histórico.

Verificar se o book é:

- estruturado;
- versionado;
- incremental;
- consultável;
- atualizável;
- exportável;
- separado por cliente;
- protegido contra contaminação entre clientes.

### 7. TESTE SEED-TO-BOOK

Verificar se já existe teste que prove:

`SEED -> DISCOVERY -> RESEARCH -> CONSOLIDATION -> BOOK`

O teste deve partir apenas de uma semente mínima.

Exemplo:

`Instagram ou Google Business Profile de uma empresa`

Não considerar como prova um teste que depende de:

- milhares de arquivos pré-carregados;
- pasta preparada manualmente;
- fatos fornecidos previamente;
- respostas humanas que substituem investigação;
- dados simulados sem correspondência com o fluxo real.

### 8. ATIVAÇÃO

Verificar o que significa “agentes e skills ativados” no runtime atual.

Provar:

- onde são registrados;
- como são carregados;
- quando são ativados;
- se carregam automaticamente;
- se exigem comando manual;
- se existem flags desligadas;
- se existem dependências ausentes;
- se existe configuração conflitante;
- se o runtime realmente enxerga todos.

### 9. REPOSITÓRIOS E COMPONENTES EXTERNOS

Nesta execução, não instalar nada.

Apenas identificar:

- quais repositórios já foram importados;
- quais foram apenas avaliados;
- quais estão isolados;
- quais estão bloqueados;
- quais foram adaptados;
- quais componentes externos são realmente usados;
- quais dependências externas sustentam partes críticas;
- quais áreas ainda precisariam de pesquisa em GitHub.

Não recomendar repositório apenas por popularidade.

Toda recomendação futura deve partir de um gap comprovado.

## REGRAS DE SEGURANÇA

- não alterar campanhas;
- não publicar;
- não acessar contas;
- não usar credenciais;
- não retirar arquivos de quarentena;
- não mover originais protegidos;
- não alterar versões preservadas;
- não criar commit;
- não executar push;
- não instalar dependências;
- não copiar código externo;
- não ativar scripts desconhecidos;
- não criar MCPs;
- não criar novos agentes;
- não corrigir nada nesta fase;
- manter `external_actions: NONE`.

## MÉTODO

1. Ler o ponteiro ativo.
2. Confirmar a raiz ativa.
3. Inventariar componentes.
4. Resolver relações entre componentes.
5. Identificar entrypoints e runtime.
6. Verificar testes existentes.
7. Executar somente testes locais seguros e já existentes quando não exigirem rede, credenciais ou escrita destrutiva.
8. Registrar evidência objetiva.
9. Montar matriz de prontidão.
10. Montar gap analysis.
11. Não construir solução ainda.

## SAÍDAS OBRIGATÓRIAS

Criar em uma pasta de auditoria apropriada da versão ativa:

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

Criar também uma passagem de bastão:

`FORJA_AGENT_SKILL_READINESS_AUDIT_HANDOFF.md`

## FORMATO DO GAP ANALYSIS

Para cada gap:

- `gap_id`;
- área;
- descrição;
- evidência;
- impacto;
- severidade;
- dependências;
- componente afetado;
- se deve ser corrigido, substituído ou criado;
- se existe solução local reutilizável;
- se exige pesquisa em GitHub;
- teste necessário;
- critério de aceite.

Severidades:

- `BLOCKER`
- `HIGH`
- `MEDIUM`
- `LOW`

## CRITÉRIO DE PRONTIDÃO

O sistema só pode ser declarado pronto para clientes reais se houver prova de:

1. entrada por semente mínima;
2. resolução de identidade;
3. descoberta de fontes;
4. pesquisa de mercado;
5. pesquisa de concorrentes;
6. construção de ICP;
7. inteligência de marca;
8. inteligência de oferta;
9. inteligência de conteúdo;
10. consolidação com proveniência;
11. book inicial criado;
12. atualização incremental;
13. isolamento entre clientes;
14. retomada após interrupção;
15. incerteza explícita;
16. ausência de ações externas não autorizadas.

## RESULTADO FINAL

Declarar apenas um dos estados:

- `FORJA_SEED_TO_BOOK_READY`
- `FORJA_SEED_TO_BOOK_PARTIALLY_READY`
- `FORJA_SEED_TO_BOOK_NOT_READY`

O retorno final deve informar:

1. quantidade de agentes encontrados;
2. agentes operacionais;
3. agentes parciais;
4. agentes quebrados;
5. quantidade de skills encontradas;
6. skills operacionais;
7. skills parciais;
8. skills quebradas;
9. orquestrador real;
10. runtime real;
11. capacidades públicas prontas;
12. capacidades conectadas prontas;
13. capacidades ausentes;
14. gaps bloqueadores;
15. gaps altos;
16. o que pode ser reutilizado;
17. o que precisa ser corrigido;
18. o que precisa ser construído;
19. o que exige pesquisa em GitHub;
20. se existe prova `SEED_TO_BOOK`;
21. estado final de prontidão;
22. arquivos criados;
23. testes executados;
24. testes não executados e motivo;
25. confirmação de ausência de alterações externas;
26. confirmação de ausência de commit e push;
27. confirmação de `external_actions: NONE`.

## REGRA FINAL

Não diga que está pronto porque existem muitos arquivos, agentes ou skills.

Não diga que está incompleto apenas porque não encontrou um componente pelo nome esperado.

Prove a cadeia completa.

Inventarie primeiro.

Construa somente depois de identificar os gaps reais.
