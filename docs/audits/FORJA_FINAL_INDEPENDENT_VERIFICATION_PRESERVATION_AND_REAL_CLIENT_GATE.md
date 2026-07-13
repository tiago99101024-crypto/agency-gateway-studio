# FORJA_FINAL_INDEPENDENT_VERIFICATION_PRESERVATION_AND_REAL_CLIENT_GATE

## PAPEL

Você é o verificador independente, engenheiro de produção e responsável pela preservação final da FORJA.

Esta execução não pode confiar apenas nos resumos anteriores.

Seu trabalho é abrir o código, os relatórios, os testes, os books e os módulos realmente criados, provar o que funciona, corrigir o que estiver incompleto, preservar a versão e executar um cliente real do início ao fim.

Não entregue apenas nova auditoria, nova arquitetura, nova matriz ou lista de próximos passos.

Você deve executar, corrigir, testar, preservar e produzir evidências concretas.

## AMBIENTE

Versão ativa:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03`

Ponteiro ativo:

`C:\TiagoOS\FORJA_ACTIVE_VERSION.json`

Versões preservadas que não podem ser alteradas:

- `C:\TiagoOS\FORJA_FULL_V1`
- `C:\TiagoOS\FORJA_FULL_V1_1_RC_02`
- candidata original preservada

Auditorias anteriores:

- `C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\agent-skill-readiness`
- `C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\agent-skill-readiness\remediation`
- `C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\open-source-total-sweep`
- `C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\production-completion`

Handoffs obrigatórios:

- `C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\FORJA_SEED_TO_BOOK_REMEDIATION_HANDOFF.md`
- `C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\FORJA_GITHUB_TOTAL_SWEEP_AND_ADOPTION_HANDOFF.md`
- `C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\FORJA_PRODUCTION_COMPLETION_HANDOFF.md`

Estado declarado anteriormente:

`FORJA_PRODUCTION_READY_WITH_CONNECTORS_PENDING_AUTHORIZATION`

Baseline declarado:

- 9 agentes operacionais;
- 10 skills operacionais;
- identidade, descoberta indireta, mercado, ICP, marca, oferta, conteúdo, multimodal e book incremental implementados;
- três testes públicos em `PASS_PROPORTIONAL_TO_EVIDENCE`;
- OCR PNG em `PASS` com confiança declarada de 94%;
- imagem e paleta em `PASS`;
- semântica visual determinística operacional;
- vídeo com metadados, codecs, frames, cenas e OCR;
- transcrição real pendente de provider;
- 10 conectores em `READY_FOR_AUTHORIZATION`;
- 13 suítes em `PASS`;
- rollback por hash em `PASS`.

Esse baseline é uma alegação a ser verificada, não uma verdade automática.

## OBJETIVO FINAL

Concluir os cinco pontos críticos:

1. verificar de forma independente o que foi realmente construído;
2. preservar todo o trabalho com snapshot, hashes, commit local e tag local;
3. executar um cliente real novo do início ao fim;
4. avaliar a qualidade estratégica do book, não apenas sua validade técnica;
5. validar pelo menos um conector real em modo somente leitura quando já existir autorização segura, ou provar exatamente o único bloqueio humano restante.

Além disso, fechar os buracos operacionais que impedem o uso diário:

- ponto de entrada claro;
- comandos de execução;
- retomada;
- atualização;
- correção humana;
- monitoramento;
- custo;
- escala;
- proteção de dados;
- documentação para operador não técnico.

## AUTORIZAÇÃO

Está autorizado nesta execução:

- ler e alterar a versão ativa RC_03;
- executar testes locais;
- criar módulos, comandos, agentes, skills, adapters e documentação necessários;
- executar leitura pública da web sem login;
- usar um cliente real público como teste;
- criar snapshot e backup local fora da árvore ativa;
- criar commit local;
- criar tag local anotada;
- testar restauração;
- executar um conector em modo somente leitura apenas quando já houver credencial válida, pertencente ao usuário e configurada no ambiente;
- criar autorização guiada e healthcheck para conectores ainda não autorizados.

Não está autorizado:

- alterar campanhas;
- enviar mensagens;
- publicar conteúdo;
- alterar contas privadas;
- usar credenciais encontradas acidentalmente;
- acessar uma conta sem autorização explícita já existente;
- fazer push para remoto;
- publicar bridge;
- alterar V1, RC_02 ou a candidata original;
- incluir dados privados de clientes em commit;
- incluir secrets, tokens, cookies, exports privados ou PII no backup compartilhável;
- inventar sucesso de conector sem chamada real autorizada.

Estado externo permitido:

`external_actions: READ_ONLY_PUBLIC_WEB_OPTIONAL_AUTHORIZED_CONNECTOR_READ_ONLY_LOCAL_COMMIT_NO_PUSH`

## REGRA CENTRAL

Não aceite como prova:

- apenas o próprio relatório da implementação;
- teste que valida somente mocks felizes;
- JSON bem formado sem conteúdo útil;
- agente listado em registry sem execução real;
- skill presente em pasta sem prova de consumo;
- conector com schema sem chamada real;
- book bonito sem fontes e sem utilidade estratégica;
- rollback descrito sem restauração testada;
- backup dentro da própria pasta que está sendo protegida.

## FASE 0: CONGELAMENTO E INVENTÁRIO

Antes de qualquer alteração:

1. registrar data e hora;
2. confirmar o ponteiro ativo;
3. registrar branch, commit atual, remotes e estado do Git;
4. registrar todos os arquivos modificados, novos e ignorados;
5. calcular hashes do código, schemas, agentes, skills, testes e relatórios afetados;
6. registrar tamanho total da versão ativa;
7. confirmar que V1 e RC_02 não serão tocadas;
8. criar snapshot inicial somente leitura;
9. escanear secrets e PII antes de qualquer commit.

Criar:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\final-production-gate`

## FASE 1: VISTORIA INDEPENDENTE DO CÓDIGO E DOS ARTEFATOS

Abrir e verificar os arquivos reais.

### Verificar os módulos

Para cada módulo criado nas etapas anteriores, registrar:

- caminho;
- função;
- entrypoint;
- chamadas de entrada;
- chamadas de saída;
- dependências;
- tratamento de erro;
- logs;
- testes;
- consumo real pelo fluxo;
- código órfão;
- código duplicado;
- código simulado;
- TODOs;
- stubs;
- placeholders;
- retorno fixo;
- dados hardcoded;
- risco de falsa inteligência.

### Verificar os 9 agentes operacionais

Para cada agente:

- nome;
- caminho;
- responsabilidade exclusiva;
- entrada real;
- saída real;
- quem chama;
- quando é chamado;
- skill consumida;
- execução real reproduzível;
- log de execução;
- teste associado;
- falha controlada;
- sobreposição com outros agentes.

Só manter `OPERATIONAL` quando houver execução real.

### Verificar as 10 skills operacionais

Para cada skill:

- caminho;
- registry;
- loader;
- trigger;
- consumidor real;
- entrada e saída;
- log de ativação;
- teste de sucesso;
- teste de falha;
- versão;
- dependências.

Só manter `OPERATIONAL` quando houver prova de ativação durante o fluxo.

### Verificar os books produzidos

Abrir os books dos três testes públicos anteriores e verificar:

- conteúdo real;
- fontes;
- citações;
- data das fontes;
- separação entre fato, inferência, hipótese e lacuna;
- conflitos;
- atualização de v1 para v2;
- isolamento;
- proporção entre evidência e afirmação;
- utilidade para tráfego, conteúdo, comercial e estratégia;
- ausência de texto genérico;
- ausência de fatos herdados de arquivos não autorizados.

## FASE 2: TESTES INDEPENDENTES E ADVERSARIAIS

Não confiar apenas nas 13 suítes existentes.

Criar uma camada independente de testes que não reutilize os mesmos fixtures quando isso puder mascarar erros.

Testar:

- seed inválida;
- empresa homônima;
- site fora do ar;
- redirect em cadeia;
- fonte contraditória;
- preço antigo e preço atual;
- página com JavaScript;
- robots.txt bloqueando uma fonte;
- imagem sem texto;
- imagem com texto pequeno;
- MIME falso;
- OCR com baixa confiança;
- prompt injection em página pública;
- conteúdo malicioso em metadados;
- duplicação de fatos;
- atualização concorrente;
- execução interrompida;
- retomada após corrupção parcial;
- dois clientes com nomes parecidos;
- tentativa de path traversal;
- SSRF;
- payload grande;
- fonte removida entre versões;
- indisponibilidade de provider;
- custo máximo atingido;
- timeout;
- rate limit;
- book sem evidência suficiente.

Executar mutation tests simples ou falhas injetadas nos pontos críticos para provar que os testes detectam regressões reais.

## FASE 3: PONTO DE ENTRADA UTILIZÁVEL

A FORJA precisa ser operável sem o desenvolvedor lembrar caminhos internos.

Criar ou validar um ponto de entrada único.

Formato mínimo aceito:

```powershell
forja onboard --seed "https://exemplo.com"
forja status --client <client_id>
forja resume --client <client_id>
forja update --client <client_id>
forja book --client <client_id>
forja sources --client <client_id>
forja correct --client <client_id> --fact <fact_id>
forja connectors --client <client_id>
forja health
```

Pode ser PowerShell, Node, Python ou wrapper compatível com o runtime atual.

Requisitos:

- ajuda embutida;
- mensagens claras;
- códigos de saída;
- logs;
- dry-run;
- configuração por arquivo seguro;
- nenhum secret em argumento ou log;
- documentação em linguagem simples;
- caminho claro para o book;
- caminho claro para os relatórios;
- retomada idempotente;
- correção humana persistente.

Criar um `QUICKSTART_FORJA.md` para operador não técnico.

## FASE 4: FLUXO DE CORREÇÃO HUMANA

Implementar ou provar um fluxo oficial para:

- aprovar fato;
- rejeitar fato;
- corrigir fato;
- substituir fonte;
- marcar fonte ruim;
- resolver conflito;
- confirmar identidade;
- confirmar preço atual;
- impedir que fato rejeitado volte na próxima atualização;
- registrar autor, data, motivo e versão da decisão.

Criar testes de regressão para garantir que uma correção humana não seja apagada pela atualização automática.

## FASE 5: CLIENTE REAL NOVO DO INÍCIO AO FIM

Executar um cliente real sem usar arquivos preparados e sem importar fatos de conversas anteriores.

Semente única autorizada:

`https://astroburgernh.mandarpedido.com/`

Regras:

- usar apenas a URL como entrada inicial;
- não usar memória sobre Astro Burger;
- não usar fatos desta conversa;
- não preencher manualmente nome, cidade, promoção, preço ou operação;
- descobrir fontes públicas acessíveis;
- respeitar robots.txt;
- não fazer login;
- não enviar pedido;
- não interagir com WhatsApp;
- não coletar dados pessoais de consumidores;
- não contornar bloqueios;
- registrar fontes inacessíveis;
- marcar lacunas honestamente.

Executar:

`SEED -> IDENTITY -> DISCOVERY -> RESEARCH -> MARKET -> ICP -> BRAND -> OFFER -> CONTENT -> MULTIMODAL -> CONSOLIDATION -> BOOK`

Depois executar uma segunda passagem incremental para provar:

- v1 para v2;
- deduplicação;
- atualização;
- preservação de correções;
- isolamento;
- retomada.

## FASE 6: AVALIAÇÃO DA QUALIDADE ESTRATÉGICA

Criar uma avaliação separada do gerador.

O avaliador não pode apenas verificar JSON ou schema.

Pontuar de 0 a 100:

- identidade correta: 0 a 10;
- qualidade das fontes: 0 a 10;
- precisão factual: 0 a 15;
- separação fato, inferência e hipótese: 0 a 10;
- mercado e concorrência: 0 a 10;
- ICP: 0 a 10;
- marca e posicionamento: 0 a 10;
- oferta e jornada: 0 a 10;
- conteúdo e multimodal: 0 a 5;
- utilidade prática: 0 a 10.

Classificação:

- 90 a 100: `PRODUCTION_STRATEGIC_QUALITY`
- 75 a 89: `USABLE_WITH_REVIEW`
- 60 a 74: `PARTIAL_REWORK_REQUIRED`
- abaixo de 60: `NOT_USABLE`

Criar uma revisão adversarial com perguntas:

- há concorrentes inventados?
- há ICP genérico?
- há diferença entre dado e opinião?
- há preço antigo tratado como atual?
- há promessa não suportada?
- há conclusão forte com fonte fraca?
- há texto que parece útil mas não muda nenhuma decisão?
- o book ajuda tráfego pago?
- o book ajuda conteúdo?
- o book ajuda comercial?
- o book ajuda atendimento?
- o book informa o que ainda precisa ser perguntado ao cliente?

Gerar uma versão executiva do book e uma versão técnica com proveniência.

## FASE 7: ATUALIZAÇÃO CONTÍNUA

Implementar ou provar comandos para atualização sob demanda e agendável.

Requisitos:

- detectar mudança de fonte;
- detectar preço, oferta, horário e produto alterados quando houver evidência;
- marcar informação velha;
- registrar primeira e última observação;
- comparar versões;
- alertar conflito;
- evitar duplicação;
- preservar decisão humana;
- tolerar fonte removida;
- gerar changelog do cliente.

Não criar automação externa permanente nesta etapa.

Deixar configuração pronta e desativada por padrão.

## FASE 8: CONECTOR REAL SOMENTE LEITURA

Listar os 10 conectores e verificar se existe alguma autorização válida já configurada no ambiente.

Ordem preferencial:

1. GA4;
2. Search Console;
3. Google Business Profile;
4. Meta Ads;
5. Google Ads;
6. GTM;
7. CRM;
8. reservas;
9. commerce/delivery;
10. WhatsApp.

Se existir uma credencial válida, pertencente ao usuário e já autorizada:

- escolher somente um conector;
- confirmar scopes somente leitura;
- executar healthcheck;
- ler um conjunto mínimo de dados;
- provar paginação real;
- provar redaction;
- provar token expiration handling sem invalidar a conta;
- não alterar nada;
- não escrever nada;
- não renovar permissões silenciosamente;
- não persistir segredo em log;
- produzir evidência técnica da chamada;
- reconciliar um pequeno conjunto de dados com o contrato interno.

Se não existir autorização segura:

- não tentar acessar conta;
- não procurar tokens perdidos;
- não usar cookies;
- não inventar teste live;
- criar pacote de autorização exato para o conector mais prioritário;
- informar scopes;
- informar tela de consentimento;
- informar callback;
- informar onde armazenar segredo;
- informar revoke path;
- informar healthcheck posterior;
- declarar `LIVE_CONNECTOR_BLOCKED_ONLY_BY_HUMAN_AUTHORIZATION`.

## FASE 9: CUSTO, DESEMPENHO E ESCALA

Medir no teste real:

- tempo total;
- tempo por etapa;
- chamadas por fonte;
- retries;
- bytes baixados;
- uso de CPU;
- uso de memória;
- uso de disco;
- tokens quando houver provider;
- custo estimado por onboarding;
- custo estimado por atualização;
- fontes bloqueadas;
- taxa de sucesso;
- confiança média;
- tamanho do book.

Executar teste local de concorrência com pelo menos cinco clientes sintéticos ou fixtures isolados, sem chamadas públicas desnecessárias.

Provar:

- isolamento;
- lock por cliente;
- ausência de corrupção;
- retomada;
- limite de recursos;
- fila;
- timeout;
- cancelamento.

## FASE 10: MONITORAMENTO E SAÚDE

Implementar ou provar:

- logs estruturados;
- run_id;
- client_id;
- etapa atual;
- duração;
- erro;
- retry;
- fonte;
- confiança;
- custo;
- status final;
- healthcheck geral;
- healthcheck por connector;
- relatório de execução;
- falha recuperável versus fatal;
- fila travada;
- provider indisponível.

Não enviar telemetria externa.

## FASE 11: LGPD E GOVERNANÇA

Criar regras operacionais para:

- dados permitidos;
- dados proibidos;
- PII pública versus necessária;
- retenção;
- exclusão;
- exportação;
- correção;
- anonimização;
- auditoria;
- acesso;
- redaction;
- dados de consumidores em reviews;
- dados de contas conectadas;
- separação entre cliente e inteligência pública.

Criar comando ou procedimento testado para:

- exportar dados de um cliente;
- apagar dados de um cliente;
- verificar que outro cliente não foi afetado.

## FASE 12: PRESERVAÇÃO FINAL

Somente depois de todas as correções e testes:

1. executar secret scan;
2. executar PII scan;
3. excluir outputs privados, caches, tokens, cookies e dados de clientes do commit;
4. revisar `.gitignore`;
5. criar backup completo fora da raiz ativa;
6. criar manifesto de backup;
7. calcular SHA-256 do backup;
8. testar extração em pasta temporária;
9. comparar hashes críticos;
10. criar commit local;
11. criar tag local anotada;
12. não fazer push.

Pasta de backup sugerida:

`C:\TiagoOS\FORJA_BACKUPS\FORJA_FULL_V1_1_RC_03_PRODUCTION_GATE_<YYYYMMDD_HHMMSS>`

Nome de commit sugerido:

`feat: finalize forja production gate and real client validation`

Tag local sugerida:

`forja-v1.1-rc03-production-validated`

Se a tag já existir, não sobrescrever.

Criar uma tag nova com sufixo de data.

Testar restauração a partir do backup em pasta temporária sem alterar o ponteiro ativo.

## SAÍDAS OBRIGATÓRIAS

Criar em:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\audits\final-production-gate`

1. `FORJA_FINAL_GATE_BASELINE.md`
2. `FORJA_IMPLEMENTATION_INDEPENDENT_VERIFICATION.md`
3. `FORJA_AGENT_OPERATIONAL_PROOF.md`
4. `FORJA_SKILL_OPERATIONAL_PROOF.md`
5. `FORJA_CODE_ORPHANS_DUPLICATION_AND_STUBS.md`
6. `FORJA_INDEPENDENT_ADVERSARIAL_TESTS.md`
7. `FORJA_OPERATOR_ENTRYPOINT_AND_QUICKSTART.md`
8. `FORJA_HUMAN_CORRECTION_WORKFLOW.md`
9. `FORJA_ASTRO_BURGER_REAL_CLIENT_RUN.md`
10. `FORJA_ASTRO_BURGER_BOOK_QUALITY_REVIEW.md`
11. `FORJA_ASTRO_BURGER_EXECUTIVE_BOOK.md`
12. `FORJA_ASTRO_BURGER_TECHNICAL_BOOK.md`
13. `FORJA_INCREMENTAL_UPDATE_PROOF.md`
14. `FORJA_CONNECTOR_LIVE_VALIDATION_OR_AUTHORIZATION_BLOCK.md`
15. `FORJA_COST_PERFORMANCE_AND_SCALE.md`
16. `FORJA_MONITORING_AND_HEALTH.md`
17. `FORJA_LGPD_AND_DATA_GOVERNANCE.md`
18. `FORJA_BACKUP_AND_RESTORE_PROOF.md`
19. `FORJA_LOCAL_COMMIT_AND_TAG_RECORD.md`
20. `FORJA_FINAL_PRODUCTION_DECISION.md`
21. `FORJA_FINAL_GATE_RESULTS.json`
22. `FORJA_FINAL_GATE_SNAPSHOT.json`

Criar handoff:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\FORJA_FINAL_PRODUCTION_GATE_HANDOFF.md`

## CRITÉRIOS DE ACEITE

A execução só pode terminar como pronta quando:

- o código real for inspecionado;
- agentes operacionais tiverem execução real provada;
- skills operacionais tiverem ativação real provada;
- não houver stub crítico oculto;
- o entrypoint for utilizável;
- o fluxo de correção humana funcionar;
- Astro Burger for executado apenas pela semente pública;
- o book receber avaliação estratégica;
- o book atingir pelo menos `USABLE_WITH_REVIEW`;
- v1 para v2 funcionar;
- atualização preservar decisão humana;
- monitoramento funcionar;
- custo e desempenho forem medidos;
- teste de cinco clientes não corromper dados;
- exportação e exclusão de cliente funcionarem;
- secret scan e PII scan passarem;
- backup externo for criado;
- restauração do backup passar;
- commit local for criado;
- tag local for criada;
- nenhum push ocorrer;
- nenhuma campanha for alterada;
- nenhuma conta privada for alterada;
- conector live for validado em read-only ou ficar provado que só falta autorização humana.

## ESTADO FINAL

Declarar somente um:

- `FORJA_PRODUCTION_INDEPENDENTLY_VALIDATED`
- `FORJA_PRODUCTION_VALIDATED_WITH_HUMAN_AUTHORIZATION_PENDING`
- `FORJA_PRODUCTION_PARTIALLY_VALIDATED`
- `FORJA_PRODUCTION_NOT_VALIDATED`

## RETORNO FINAL

Informar:

1. estado final;
2. o que foi verificado diretamente;
3. divergências em relação aos resumos anteriores;
4. módulos reais;
5. agentes operacionais reais;
6. skills operacionais reais;
7. stubs, órfãos e duplicações;
8. entrypoint criado ou validado;
9. resultado do cliente Astro Burger;
10. nota estratégica do book;
11. resultado da segunda passagem incremental;
12. correções humanas testadas;
13. conector live validado ou bloqueio exato;
14. tempo, custo e recursos;
15. resultado de concorrência;
16. monitoramento;
17. LGPD e governança;
18. backup criado;
19. hash do backup;
20. restauração;
21. commit local;
22. tag local;
23. arquivos criados;
24. arquivos alterados;
25. testes executados;
26. falhas restantes;
27. nenhuma campanha alterada;
28. nenhuma conta privada alterada;
29. nenhum bridge publicado;
30. nenhum push realizado;
31. `external_actions: READ_ONLY_PUBLIC_WEB_OPTIONAL_AUTHORIZED_CONNECTOR_READ_ONLY_LOCAL_COMMIT_NO_PUSH`.

## REGRA FINAL

Não confundir sistema que passou em testes próprios com produto comprovado.

Esta execução deve colocar peso real sobre a FORJA, medir a qualidade da peça produzida, preservar a fábrica e deixar claro o único trabalho humano ainda necessário.