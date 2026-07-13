# FORJA_PRODUCTION_COMPLETION_AND_REAL_VALIDATION

## PAPEL

Você é o engenheiro responsável por concluir a FORJA para uso real.

Esta execução NÃO é uma nova auditoria ampla.

Esta execução NÃO deve terminar em uma lista de ideias.

Você deve implementar, integrar, ativar, testar e validar tudo que ainda for tecnicamente possível sem credenciais privadas.

O objetivo é transformar o estado atual `PARTIALLY_READY` em um sistema utilizável para:

1. receber uma semente mínima pública;
2. investigar o cliente;
3. pesquisar mercado, concorrentes, ICP, oferta, marca, conteúdo e presença digital;
4. analisar texto, imagens, documentos e vídeos quando disponíveis;
5. gerar um book vivo de inteligência;
6. atualizar esse book incrementalmente;
7. receber dados conectados após autorização do cliente;
8. preservar proveniência, incerteza, histórico, isolamento e segurança.

## AMBIENTE

Versão ativa:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03`

Ponteiro ativo:

`C:\TiagoOS\FORJA_ACTIVE_VERSION.json`

Versões preservadas:

- `C:\TiagoOS\FORJA_FULL_V1`
- `C:\TiagoOS\FORJA_FULL_V1_1_RC_02`
- candidata original preservada

Auditoria de agentes e skills:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\agent-skill-readiness`

Remediação seed-to-book:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\agent-skill-readiness\remediation`

Varredura e adoção open source:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\open-source-total-sweep`

Handoffs obrigatórios:

- `C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\FORJA_SEED_TO_BOOK_REMEDIATION_HANDOFF.md`
- `C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\FORJA_GITHUB_TOTAL_SWEEP_AND_ADOPTION_HANDOFF.md`

## ESTADO ATUAL CONHECIDO

- `FORJA_OPEN_SOURCE_ADOPTION_PARTIALLY_READY`
- 165 repositórios únicos varridos
- 27 repositórios auditados profundamente
- reader público seguro implementado
- análise real de PNG e paleta implementada
- 4 agentes operacionais
- 5 skills operacionais
- E2E local, incremental, isolamento, retomada, idempotência, regressão e rollback em `PASS`
- Instagram público direto bloqueado por `robots.txt`
- G011 parcialmente resolvido
- OCR ainda aberto
- vídeo ainda aberto
- semântica visual ainda aberta
- G009 parcial
- conectores live ainda sem autorização/configuração
- nenhuma campanha, conta privada ou bridge alterado

## REGRA CENTRAL

Não fazer outra varredura ampla no GitHub.

Usar os artefatos já produzidos.

Pesquisa externa adicional só é permitida quando necessária para fechar um bloqueio técnico específico.

Não ativar agentes ou skills apenas para aumentar contagem.

Ativar somente os componentes que participam de uma capacidade real e possuem teste operacional.

Não declarar pronto por documentação.

Não declarar bloqueado antes de tentar todas as rotas seguras previstas neste documento.

## AUTORIZAÇÕES

Está autorizado nesta execução:

- alterar arquivos dentro da versão ativa;
- criar agentes, skills, adapters, schemas, contratos, fixtures, testes e documentação;
- instalar dependências seguras em ambiente isolado da FORJA;
- criar `venv`, lockfile e cache local dentro da versão ativa ou laboratório;
- usar ferramentas públicas somente leitura;
- consultar páginas públicas respeitando `robots.txt`, rate limits e termos aplicáveis;
- executar OCR local;
- executar processamento local de imagens, documentos, áudio e vídeo;
- usar modelos locais já disponíveis;
- criar providers para modelos externos sem usar credenciais reais;
- executar testes públicos read-only sem login;
- criar mocks e sandboxes para conectores;
- promover componentes locais após teste e rollback.

Não está autorizado:

- burlar `robots.txt`;
- contornar autenticação;
- usar contas privadas;
- usar credenciais reais sem nova autorização do Tiago;
- alterar campanhas;
- publicar no bridge;
- enviar mensagens;
- criar contas;
- coletar PII de consumidores para inteligência;
- executar instaladores externos não auditados;
- executar hooks, MCPs ou daemons desconhecidos;
- alterar V1, RC_02 ou candidata original;
- criar commit ou push nesta etapa.

Estado externo permitido:

`external_actions: READ_ONLY_PUBLIC_WEB_AND_LOCAL_IMPLEMENTATION`

## FASE 0 — BASELINE E RECUPERAÇÃO

Antes de alterar qualquer arquivo:

1. ler os dois handoffs obrigatórios;
2. ler os relatórios finais da auditoria, remediação e open source adoption;
3. confirmar os componentes promovidos;
4. confirmar 4 agentes operacionais e 5 skills operacionais;
5. confirmar G009 e G011;
6. registrar hashes dos arquivos que poderão ser alterados;
7. criar snapshot de rollback;
8. confirmar que as versões preservadas estão intactas;
9. criar pasta desta execução.

Pasta sugerida:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\production-completion`

Não repetir as 100 páginas de pesquisa no GitHub.

## FASE 1 — PUBLIC SOURCE DISCOVERY DE PRODUÇÃO

Concluir o motor público para aceitar uma semente mínima:

- nome da empresa;
- Instagram;
- Facebook;
- Google Business Profile ou Google Maps;
- site;
- URL de reserva;
- cardápio;
- arquivo;
- pasta;
- qualquer combinação desses itens.

### Resolver identidade

Implementar e provar:

- normalização de nomes;
- aliases;
- cidade e região;
- telefone;
- domínio;
- endereço;
- links cruzados;
- identidade visual;
- score de correspondência;
- conflito entre empresas homônimas;
- revisão humana quando a identidade não for segura.

Nenhuma fonte pode entrar no book sem passar pela resolução de identidade.

### Descoberta de fontes

Implementar descoberta automática e fallback para:

- site oficial;
- páginas internas;
- Google Business Profile ou resultados públicos equivalentes;
- Facebook público;
- Instagram indexado publicamente;
- sistemas de reserva;
- cardápios públicos;
- plataformas de delivery;
- diretórios locais;
- avaliações públicas;
- notícias e matérias;
- anúncios públicos e bibliotecas acessíveis;
- documentos públicos;
- PDFs;
- imagens;
- vídeos públicos acessíveis;
- links encontrados nas fontes oficiais.

### Instagram bloqueado

Quando o Instagram direto estiver bloqueado:

- não burlar;
- não usar login oculto;
- não usar scraping evasivo;
- registrar `DIRECT_SOURCE_BLOCKED_BY_ROBOTS`;
- continuar por fontes oficiais alternativas;
- usar resultados públicos indexados quando permitidos;
- usar links cruzados do site, Facebook, Google, reservas e anúncios;
- completar o book proporcionalmente ao que for acessível;
- deixar a lacuna explícita.

A semente não pode falhar só porque uma plataforma bloqueou acesso direto.

### Segurança do reader

Manter e ampliar:

- allowlist de protocolos;
- bloqueio de redes privadas e localhost;
- limite de tamanho;
- timeout;
- rate limiting;
- user-agent identificável;
- respeito a `robots.txt`;
- sanitização de HTML;
- defesa contra prompt injection em conteúdo coletado;
- hash e snapshot;
- MIME validation;
- redirect validation;
- logs de proveniência;
- deduplicação de URLs e conteúdo.

## FASE 2 — PESQUISA DE MERCADO, ICP E BENCHMARK

Concluir capacidades operacionais para gerar, com evidência:

- categoria;
- nicho;
- subnicho;
- localização;
- raio de atuação provável;
- mercado local;
- demanda observável;
- sazonalidade;
- concorrentes diretos;
- concorrentes indiretos;
- benchmark local;
- benchmark de comunicação;
- faixa de preço observável;
- canais usados pelo mercado;
- tendências relevantes;
- objeções;
- dores;
- desejos;
- ocasiões de compra;
- ICPs prováveis;
- segmentos prioritários;
- jornada aparente;
- critérios de escolha;
- hipóteses de ticket e margem somente quando sustentadas;
- lacunas que exigem cliente ou conta conectada.

### Regra de ICP

Não gerar persona decorativa.

Cada ICP deve conter:

- evidências usadas;
- fontes;
- nível de confiança;
- localização;
- necessidade;
- ocasião;
- barreiras;
- comportamento de busca;
- canal provável;
- oferta compatível;
- hipótese a validar;
- fatos ausentes.

Separar:

- `EVIDENCE_BACKED_ICP`
- `PROBABLE_ICP`
- `HYPOTHETICAL_ICP`

## FASE 3 — BRAND, OFFER E CONTENT INTELLIGENCE

Concluir agentes e skills operacionais para:

### Brand intelligence

- nome atual;
- aliases;
- logotipo;
- paleta dominante e secundária;
- contraste;
- tipografia aparente;
- estilo fotográfico;
- estilo de vídeo;
- elementos recorrentes;
- tom de voz;
- vocabulário;
- claims;
- posicionamento aparente;
- consistência visual;
- inconsistências;
- riscos de marca;
- kit de identidade observada.

### Offer intelligence

- produtos;
- serviços;
- categorias;
- preços;
- promoções;
- validade;
- condições;
- disponibilidade;
- CTA;
- canais de compra;
- reservas;
- upsell;
- cross-sell;
- provas;
- diferenciais alegados;
- diferenciais comprovados;
- conflitos históricos.

Não transformar post antigo em condição atual.

### Content intelligence

- canais;
- formatos;
- frequência;
- temas;
- ganchos;
- CTAs;
- estilo de legenda;
- sinais públicos de engajamento;
- comentários agregados;
- conteúdo com maior resposta observável;
- conteúdo fraco;
- padrões de horário quando houver timestamp e amostra suficiente;
- melhor horário estimado somente com base explícita;
- lacunas de conteúdo;
- oportunidades.

Não declarar “melhor horário” com amostra insuficiente.

## FASE 4 — MULTIMODAL COMPLETO

Fechar G011 no máximo tecnicamente possível.

### OCR

Implementar pipeline local para:

- PNG;
- JPG/JPEG;
- WEBP;
- PDF com imagem;
- screenshots;
- cardápios;
- peças publicitárias;
- documentos digitalizados.

Requisitos:

- idioma português e inglês quando disponível;
- confiança por bloco;
- bounding boxes quando suportado;
- preservação do original;
- hash;
- normalização;
- detecção de texto duplicado;
- fallback entre texto embutido e OCR;
- marcação `LOW_OCR_CONFIDENCE`;
- testes com fixtures reais e sintéticas.

Usar dependências isoladas e versões fixadas.

### Semântica visual

Implementar provider interface para análise semântica de imagem.

Usar nesta ordem:

1. provider multimodal já disponível no runtime;
2. modelo local já instalado;
3. provider externo configurável, mas desativado sem credencial;
4. fallback determinístico limitado.

A saída deve separar:

- observação objetiva;
- inferência;
- confiança;
- elementos não detectados;
- limitações do provider.

Analisar:

- tipo de peça;
- produto exibido;
- pessoas;
- ambiente;
- texto;
- CTA;
- composição;
- hierarquia;
- cores;
- logo;
- possíveis inconsistências;
- adequação de formato;
- sem declarar emoções, demografia ou atributos sensíveis sem base.

### Vídeo

Implementar pipeline para:

- metadados;
- duração;
- resolução;
- fps;
- codec;
- áudio;
- extração de frames;
- seleção de keyframes;
- detecção de cenas;
- OCR em frames;
- transcrição local quando ferramenta segura estiver disponível;
- timestamps;
- união entre fala, texto e frames;
- resumo estruturado;
- hooks;
- CTAs;
- produtos;
- cenas;
- limitações.

Se não existir transcritor local viável, concluir toda a arquitetura, fixtures, interface e fallback, e marcar somente a transcrição real como `PROVIDER_REQUIRED`.

Não deixar o módulo de vídeo inexistente.

## FASE 5 — BOOK VIVO DE INTELIGÊNCIA

Concluir o compilador de book para produzir ao menos:

- JSON canônico;
- Markdown legível;
- snapshot versionado;
- manifest;
- provenance ledger;
- conflitos;
- gaps;
- readiness por área;
- histórico de alterações.

### Estrutura mínima

1. identificação;
2. localização;
3. fontes oficiais;
4. presença digital;
5. mercado;
6. concorrentes;
7. benchmark;
8. ICPs;
9. jornadas;
10. produtos e serviços;
11. preços e ofertas;
12. posicionamento;
13. diferenciais;
14. identidade visual;
15. tom de voz;
16. conteúdo;
17. mídia pública;
18. avaliações agregadas;
19. processo comercial aparente;
20. reservas e conversão aparente;
21. tracking conhecido;
22. operação;
23. capacidade;
24. riscos;
25. gargalos;
26. oportunidades;
27. conflitos;
28. lacunas;
29. hipóteses;
30. decisões humanas;
31. proveniência;
32. confiança;
33. histórico.

### Estados de fatos

- `CONFIRMED`
- `PROBABLE`
- `PARTIAL`
- `CONFLICTED`
- `HISTORICAL`
- `UNVERIFIED`
- `UNKNOWN`
- `NOT_FOUND`
- `BLOCKED`

### Regras

- cada fato relevante aponta para fonte;
- repetição derivada não equivale a fontes independentes;
- fatos históricos não substituem fatos atuais;
- hipóteses não aparecem como fatos;
- lacunas não bloqueiam áreas não relacionadas;
- nova fonte atualiza somente áreas afetadas;
- nenhum histórico é apagado;
- rollback por snapshot deve funcionar.

## FASE 6 — AGENTES E SKILLS OPERACIONAIS

Não buscar 62 agentes operacionais por vaidade.

Mapear as capacidades obrigatórias para agentes reais.

O conjunto mínimo operacional deve cobrir:

1. seed intake;
2. identity resolution;
3. public discovery;
4. safe reading e crawling;
5. market research;
6. competitor research;
7. ICP intelligence;
8. brand intelligence;
9. offer intelligence;
10. content intelligence;
11. multimodal intelligence;
12. book compilation;
13. provenance e validation;
14. connected intelligence;
15. orchestration pelo Bruxo.

Pode consolidar várias capacidades em um agente quando isso reduzir duplicação.

Para cada agente e skill promovido:

- registry;
- loader;
- consumer;
- input schema;
- output schema;
- teste unitário;
- teste de integração;
- log de ativação;
- erro controlado;
- rollback;
- evidência de consumo real no E2E.

Skills não consumidas devem permanecer registradas como inativas, não falsamente operacionais.

Agentes redundantes devem ser marcados para consolidação ou descontinuação, sem apagá-los nesta execução.

## FASE 7 — CONNECTED INTELLIGENCE PRONTO PARA AUTORIZAÇÃO

Fechar G009 em tudo que não depende de credencial real.

Implementar arquitetura, contratos, adapters, schemas, fixtures, dry-run, validação e testes para:

### Meta

- Meta Business discovery autorizado;
- contas de anúncio;
- campanhas;
- conjuntos;
- anúncios;
- criativos;
- métricas;
- públicos quando permitidos;
- Instagram Insights;
- Facebook Page Insights;
- scopes necessários;
- paginação;
- rate limits;
- token health;
- data freshness;
- erro de permissão;
- normalização para o book.

### Google

- Google Ads;
- GA4 Data API;
- GTM;
- Google Business Profile;
- Search Console quando útil;
- scopes;
- properties/accounts discovery;
- paginação;
- métricas;
- dimensões;
- data freshness;
- erros;
- normalização.

### CRM e comercial

- adapter genérico REST;
- webhook intake;
- CSV/XLSX/JSON import;
- mapeamento de campos;
- deduplicação;
- leads;
- estágios;
- vendas;
- ticket;
- recorrência;
- perdas;
- origem;
- timestamps;
- PII protection;
- schemas de integração.

### WhatsApp

- WhatsApp Cloud API contract;
- templates e mensagens apenas como leitura nesta etapa;
- conversas agregadas;
- status;
- origem;
- eventos;
- redaction;
- não enviar mensagens;
- não expor conteúdo pessoal no book.

### Reservas, delivery e e-commerce

- adapter genérico;
- LeadsFood ou sistema equivalente quando houver contrato conhecido;
- eventos de início, envio, confirmação, cancelamento e comparecimento;
- pedidos;
- receita;
- produtos;
- ticket;
- UTM;
- reconciliação;
- idempotência.

### Autorização e secrets

Implementar:

- connector registry;
- status por conector;
- `NOT_CONFIGURED`;
- `READY_FOR_AUTHORIZATION`;
- `AUTHORIZED`;
- `DEGRADED`;
- `REVOKED`;
- referência a secret sem armazenar valor no book;
- least privilege;
- scope manifest;
- healthcheck;
- dry-run;
- revoke path;
- audit log;
- autorização humana obrigatória.

Não usar credenciais reais.

Ao final, os conectores devem estar em `READY_FOR_AUTHORIZATION`, não apenas “documentados”.

## FASE 8 — VALIDAÇÃO REAL COM SEMENTES PÚBLICAS

Executar três testes limpos, sem pasta previamente preparada e sem fatos fornecidos manualmente.

### Teste A — semente por site

Escolher um negócio público real com site acessível.

### Teste B — semente por Google Business Profile ou Google Maps

Escolher um negócio público real com fonte pública acessível.

### Teste C — semente por Instagram

Usar:

`https://www.instagram.com/americahouseoficial/`

Criar namespace de teste separado e limpo.

Não ler o namespace `pilot.real.001` durante a primeira execução.

Quando o Instagram estiver bloqueado, continuar pela descoberta indireta segura.

### Regras dos três testes

- nenhum fato manual;
- nenhuma conta privada;
- nenhum login;
- nenhuma evasão;
- nenhum uso de memória externa do operador;
- fontes registradas;
- book proporcional à evidência;
- incertezas explícitas;
- OCR e multimodal usados quando houver mídia acessível;
- mercado, concorrentes e ICP gerados;
- isolamento entre os três clientes;
- retomada após interrupção simulada;
- atualização incremental com uma quarta fonte;
- rollback por hash;
- idempotência;
- comparação entre book inicial e atualizado.

## FASE 9 — TESTE CONNECTED INTELLIGENCE SEM CREDENCIAL

Executar E2E com fixtures realistas e sanitizadas para:

- Meta;
- Google Ads;
- GA4;
- GTM;
- GBP;
- CRM;
- WhatsApp;
- reservas;
- e-commerce ou delivery.

Provar:

- ingestão;
- validação;
- paginação simulada;
- rate limit simulado;
- token expirado;
- permissão insuficiente;
- duplicata;
- evento atrasado;
- evento fora de ordem;
- reconciliação;
- atualização incremental;
- isolamento;
- redaction;
- book enriquecido;
- revoke path;
- rollback.

## FASE 10 — REGRESSÃO, HARDENING E PROMOÇÃO

Executar:

- testes unitários;
- integração;
- E2E;
- segurança;
- prompt injection;
- SSRF;
- path traversal;
- MIME spoofing;
- oversized payload;
- malformed JSON;
- corrupted image;
- corrupted PDF;
- corrupted video;
- PII redaction;
- cross-client contamination;
- interruption recovery;
- idempotência;
- rollback;
- regressão completa da FORJA.

Promover para o runtime ativo somente componentes em `PASS`.

Não promover dependência experimental sem fallback.

Não alterar versões preservadas.

Não criar commit ou push.

## SAÍDAS OBRIGATÓRIAS

Criar em:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\production-completion`

1. `FORJA_PRODUCTION_BASELINE.md`
2. `FORJA_PUBLIC_DISCOVERY_IMPLEMENTATION.md`
3. `FORJA_IDENTITY_RESOLUTION_IMPLEMENTATION.md`
4. `FORJA_MARKET_ICP_BENCHMARK_IMPLEMENTATION.md`
5. `FORJA_BRAND_OFFER_CONTENT_IMPLEMENTATION.md`
6. `FORJA_OCR_IMPLEMENTATION.md`
7. `FORJA_VISUAL_SEMANTICS_IMPLEMENTATION.md`
8. `FORJA_VIDEO_INTELLIGENCE_IMPLEMENTATION.md`
9. `FORJA_CLIENT_BOOK_COMPILER_IMPLEMENTATION.md`
10. `FORJA_OPERATIONAL_AGENT_SKILL_MAP.md`
11. `FORJA_CONNECTED_INTELLIGENCE_IMPLEMENTATION.md`
12. `FORJA_CONNECTOR_AUTHORIZATION_MANIFEST.json`
13. `FORJA_PUBLIC_REAL_SEED_TEST_RESULTS.md`
14. `FORJA_CONNECTED_FIXTURE_E2E_RESULTS.md`
15. `FORJA_SECURITY_HARDENING_RESULTS.md`
16. `FORJA_PRODUCTION_REGRESSION_RESULTS.md`
17. `FORJA_PRODUCTION_READINESS.json`
18. `FORJA_PRODUCTION_COMPLETION_SNAPSHOT.json`
19. `FORJA_PENDING_HUMAN_AUTHORIZATIONS.md`
20. `FORJA_PRODUCTION_COMPLETION_REPORT.md`

Criar handoff:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\FORJA_PRODUCTION_COMPLETION_HANDOFF.md`

## CRITÉRIOS DE ACEITE

### Public onboarding

Só pode ser `READY` se:

- aceita semente mínima;
- resolve identidade;
- descobre fontes alternativas;
- respeita bloqueios;
- pesquisa mercado;
- pesquisa concorrentes;
- produz ICPs classificados;
- analisa marca;
- analisa oferta;
- analisa conteúdo;
- usa OCR;
- usa multimodal real ou provider operacional;
- gera book completo proporcional;
- registra proveniência;
- atualiza incrementalmente;
- passa nos três testes públicos.

### Multimodal

Só pode ser `READY` se:

- imagem e paleta funcionam;
- OCR funciona;
- PDF visual funciona;
- semântica visual possui provider operacional;
- vídeo possui pipeline funcional;
- limitações aparecem explicitamente.

Pode ser `PARTIAL` somente quando a única pendência depender de credencial ou modelo externo não disponível.

### Connected intelligence

Pode ser declarado `READY_FOR_AUTHORIZATION` sem credenciais reais somente se:

- adapters existem;
- contracts existem;
- schemas validam;
- fixtures passam;
- dry-run passa;
- scopes estão definidos;
- errors estão tratados;
- revoke path existe;
- book enrichment passa;
- nenhuma credencial está embutida.

### Agentes e skills

Somente contar como operacional se houver:

- ativação real;
- consumo real;
- teste real;
- output válido;
- erro controlado;
- presença no E2E.

## ESTADO FINAL

Declarar somente um:

- `FORJA_PRODUCTION_READY_FOR_PUBLIC_CLIENT_ONBOARDING`
- `FORJA_PRODUCTION_READY_WITH_CONNECTORS_PENDING_AUTHORIZATION`
- `FORJA_PRODUCTION_PARTIALLY_READY`
- `FORJA_PRODUCTION_NOT_READY`

O melhor estado esperado sem credenciais privadas é:

`FORJA_PRODUCTION_READY_WITH_CONNECTORS_PENDING_AUTHORIZATION`

Não usar esse estado se os três testes públicos, OCR, book e conectores por fixture não passarem.

## RETORNO FINAL OBRIGATÓRIO

Informar:

1. estado final;
2. arquivos criados;
3. arquivos alterados;
4. agentes operacionais antes e depois;
5. skills operacionais antes e depois;
6. capacidades públicas implementadas;
7. resultado dos três testes públicos;
8. fontes encontradas por teste;
9. qualidade dos books;
10. OCR;
11. imagem;
12. semântica visual;
13. vídeo;
14. G011 final;
15. conectores implementados;
16. conectores em `READY_FOR_AUTHORIZATION`;
17. G009 final;
18. fixtures conectadas;
19. segurança;
20. regressão;
21. rollback;
22. lacunas restantes;
23. quais lacunas dependem exclusivamente de credencial ou autorização humana;
24. confirmação de que nenhuma campanha foi alterada;
25. confirmação de que nenhuma conta privada foi acessada;
26. confirmação de que nada foi publicado no bridge;
27. confirmação de ausência de commit e push;
28. confirmação de que V1, RC_02 e candidata original permanecem intactas;
29. `external_actions: READ_ONLY_PUBLIC_WEB_AND_LOCAL_IMPLEMENTATION`.

## REGRA FINAL

Não volte com “ainda precisa implementar” sem ter tentado implementar.

Não volte com “precisa pesquisar” sem ter usado os 165 repositórios já varridos.

Não volte com mais uma arquitetura sem runtime.

Implemente, conecte, ative, teste e prove.

O que depender exclusivamente de credencial privada deve terminar em `READY_FOR_AUTHORIZATION` com fluxo, contrato, fixture, dry-run, scopes, healthcheck e revoke path já prontos.