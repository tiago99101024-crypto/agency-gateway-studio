# FORJA TASK

## Render completo em HTML para Ello Joias

Estado esperado ao final:

`ELLO_JOIAS_HTML_DASHBOARD_READY`

## Objetivo

Transformar todo o onboarding público já concluído da cliente `ello.joias.cb` em uma visualização HTML completa, navegável, clara e utilizável no navegador por uma pessoa não técnica.

Não refazer o onboarding.
Não pesquisar novamente sem necessidade.
Não resumir apenas o handoff.
Não criar um HTML genérico com três cartões.
Ler e consolidar o conteúdo real do cliente, do book, dos 15 artefatos obrigatórios, das fontes, do manifesto, do histórico e do handoff.

## Ambiente

Raiz da FORJA:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03`

Cliente:

`ello.joias.cb`

Raiz operacional da cliente:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\ello.joias.cb`

Handoff existente:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\ELLO_JOIAS_PUBLIC_ONBOARDING_HANDOFF.md`

## Entrega principal obrigatória

Criar um arquivo HTML autocontido e abrível com duplo clique:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\ello.joias.cb\exports\html\index.html`

Também criar uma cópia de conveniência em:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\exports\clients\ello.joias.cb\index.html`

O HTML deve funcionar offline, sem servidor, sem CDN e sem dependências externas obrigatórias.

CSS e JavaScript devem estar embutidos ou em arquivos locais na mesma pasta.

## Regra de fidelidade

O painel deve ser gerado a partir dos arquivos reais do cliente.

Não inventar:

- preços;
- materiais;
- garantias;
- endereço;
- CNPJ;
- estoque;
- margem;
- ticket;
- reputação;
- anúncios;
- dados de Shopee;
- resultados comerciais.

Cada informação deve preservar sua classificação original:

- `CONFIRMED`;
- `PROBABLE`;
- `HYPOTHESIS`;
- `STALE`;
- `CONFLICT`;
- `NOT_FOUND`;
- `BLOCKED`;
- `NEEDS_CLIENT_CONFIRMATION`.

A interface deve deixar visualmente impossível confundir fato confirmado com hipótese.

## Estrutura obrigatória do HTML

### 1. Cabeçalho executivo

Mostrar:

- Ello Joias;
- `@ellojoiascb`;
- Campo Bom/RS;
- `client_id`;
- versão do book;
- nota `78/100`;
- classificação `USABLE_WITH_REVIEW`;
- data da última atualização;
- quantidade de fontes;
- quantidade de fatos confirmados, hipóteses, conflitos, itens antigos e lacunas;
- estado do onboarding.

### 2. Navegação lateral ou superior fixa

Links internos para todas as seções.

Deve haver busca textual dentro do painel.

Deve haver filtros por:

- status da informação;
- categoria;
- fonte;
- confiança;
- atualidade.

### 3. Resumo executivo

Apresentar em linguagem humana:

- o que a empresa parece ser;
- como vende;
- para quem vende;
- qual posicionamento aparece;
- principais forças;
- principais fragilidades;
- o que já pode orientar estratégia;
- o que ainda depende da cliente.

### 4. Identidade da empresa

Mostrar:

- nome;
- perfil oficial;
- cidade;
- modelo de negócio;
- canais encontrados;
- canais não encontrados;
- NAP;
- identidade resolvida;
- controles de homônimos;
- conflitos de identidade;
- confiança por campo.

### 5. Produtos e materiais

Tabela detalhada com:

- categoria;
- produto ou SKU quando disponível;
- material confirmado;
- material não confirmado;
- pedra ou componente;
- preço;
- origem da evidência;
- data da evidência;
- status;
- observação.

Separar explicitamente:

- brincos;
- colares;
- pulseiras;
- prata;
- semijoias;
- silicone;
- zircônia;
- materiais não determinados.

### 6. Ofertas e condições comerciais

Exibir:

- oferta atual observada de 12 brincos por R$ 29,99;
- frete grátis via Shopee como condição observada, sem ampliar a promessa;
- oferta antiga de dois pares por R$ 39,99 marcada como `STALE`;
- lacunas de pagamento, frete, troca, garantia, estoque, margem e logística;
- riscos de anunciar oferta sem confirmação.

### 7. Posicionamento e marca

Mostrar:

- posicionamento inferido;
- proposta de valor observada;
- atributos da marca;
- tom;
- linguagem;
- palavras recorrentes;
- elementos visuais;
- embalagem;
- estilo de fotografia;
- análise cromática e tipográfica, preservando `PARTIAL`;
- limites da análise visual atual.

### 8. Conteúdo e redes sociais

Exibir:

- formatos usados;
- temas recorrentes;
- CTAs;
- frequência quando suportada;
- posts públicos analisados;
- ofertas;
- conteúdo de produto;
- conteúdo de significado;
- embalagem;
- Reels;
- possíveis lacunas editoriais.

Sempre incluir links clicáveis para fontes públicas quando existirem.

### 9. Público e ICP

Apresentar os segmentos encontrados:

- uso próprio;
- presente;
- sensível a preço;
- orientada por estilo;
- cliente local.

Para cada segmento, mostrar:

- necessidade;
- motivação;
- objeção;
- gatilho de compra;
- produto provável;
- canal;
- nível de evidência;
- hipótese que precisa ser validada.

Não transformar ICP inferido em dado confirmado.

### 10. Jornada de compra

Visualizar:

`Instagram → link da bio → Shopee → pagamento → entrega`

Mostrar também:

- pontos de atrito;
- etapas não comprovadas;
- tracking ausente;
- URL da Shopee não recuperada;
- possíveis vazamentos de conversão;
- pontos onde a cliente precisa fornecer acesso ou confirmação.

### 11. Mercado, concorrentes e benchmarks

Tabela comparativa dos sete concorrentes locais ou regionais e três benchmarks nacionais.

Para cada um, quando houver evidência:

- nome;
- cidade;
- canal;
- categoria;
- posicionamento;
- faixa de preço;
- oferta;
- conteúdo;
- diferenciais;
- fragilidades;
- fonte;
- nível de confiança.

Não preencher células sem dados. Usar `Não encontrado`.

### 12. Reputação

Mostrar:

- sinais positivos observados;
- tamanho da amostra;
- ausência de reputação independente consolidada;
- fontes encontradas;
- limitações;
- riscos de extrapolação.

### 13. Presença local, SEO e GBP

Mostrar:

- cidade confirmada por geotag;
- GBP não encontrado;
- endereço não encontrado;
- NAP incompleto;
- impactos possíveis;
- ações recomendadas;
- campos que precisam de confirmação.

### 14. Meta Ad Library e mídia paga

Mostrar:

- nenhum anúncio atribuível encontrado;
- classificação `NOT_FOUND`;
- diferença entre não encontrar e provar inexistência;
- pré-requisitos antes de campanha;
- dados necessários para tráfego;
- riscos de anunciar antes de validar margem, estoque, garantia, logística e oferta.

### 15. Fontes e evidências

Criar uma seção completa com todas as fontes reais utilizadas.

Para cada fonte:

- título;
- URL;
- tipo;
- oficial ou alternativa;
- data de coleta;
- confiança;
- status;
- fatos sustentados;
- hash ou identificador local quando disponível;
- motivo de descarte quando rejeitada.

Permitir filtrar e ordenar.

### 16. Fatos, hipóteses, conflitos e informações antigas

Criar quatro visões distintas:

- fatos confirmados;
- hipóteses;
- conflitos;
- informações antigas.

Cada item deve exibir:

- texto;
- categoria;
- fonte;
- confiança;
- data;
- versão;
- observação;
- necessidade de revisão humana.

### 17. Riscos e lacunas

Organizar por prioridade:

- crítica;
- alta;
- média;
- baixa.

Incluir no mínimo:

- material incompleto por SKU;
- garantia inconsistente;
- link da Shopee não recuperado;
- ausência de presença local verificável;
- estoque;
- margem;
- logística;
- política de troca;
- dados de vendas;
- tracking;
- acessos e autorizações.

### 18. Perguntas para a cliente

Mostrar checklist interativo com as perguntas reais já geradas.

Permitir marcar como:

- pendente;
- respondida;
- não se aplica;
- precisa de documento.

Persistir as marcações localmente no navegador usando `localStorage`, sem alterar o book canônico.

Permitir exportar as respostas e marcações como JSON local.

### 19. Plano de 30 dias

Criar uma linha do tempo ou quadro dividido em:

- dias 1 a 7;
- dias 8 a 15;
- dias 16 a 23;
- dias 24 a 30.

Incluir:

- fichas por SKU;
- política comercial;
- validação da Shopee;
- NAP e GBP;
- tracking;
- criativos;
- prova social;
- preparação de mídia;
- critérios para liberar campanha.

### 20. Arquivos do cliente

Listar e criar links locais relativos para:

- book atual;
- versões anteriores;
- fontes;
- relatórios;
- manifesto de hashes;
- handoff;
- artefatos obrigatórios;
- exportações.

Os links devem funcionar dentro da estrutura local quando possível.

Quando o navegador bloquear um link local, mostrar o caminho completo copiável.

### 21. Histórico e versões

Mostrar:

- v1;
- v2;
- alterações entre versões;
- fatos adicionados;
- fatos removidos;
- fatos corrigidos;
- conflitos resolvidos;
- informações marcadas como antigas.

Se não houver dados suficientes para algum delta, declarar isso.

### 22. Saúde e integridade

Mostrar:

- testes que passaram;
- scan de secrets;
- scan de PII;
- isolamento;
- deduplicação;
- idempotência;
- rollback;
- manifesto de hashes;
- estado final da execução.

## Experiência visual

O painel deve ter aparência profissional, limpa e sóbria.

Não usar aparência infantil, template genérico ou excesso de cores.

Requisitos:

- responsivo para desktop e celular;
- modo claro e escuro;
- impressão limpa;
- botão `Imprimir ou salvar em PDF`;
- botão `Copiar caminho da pasta`;
- botão `Abrir Instagram`;
- botão `Exportar resumo em JSON`;
- botão `Mostrar somente pendências`;
- botão `Mostrar somente confirmados`;
- busca instantânea;
- tabelas ordenáveis;
- acordeões para conteúdo longo;
- badges de status;
- legenda de confiança;
- barra visual da nota 78/100;
- nenhuma dependência de internet para renderizar a interface.

## Segurança

Escapar todo conteúdo vindo de arquivos.

Impedir execução de HTML ou scripts presentes em fontes, relatórios ou textos coletados.

Não embutir secrets.

Não embutir PII não autorizada.

Não fazer chamadas externas automáticas.

Links externos só devem abrir após ação do usuário.

## Integração com a CLI

Adicionar ou concluir suporte para:

`forja.cmd book ello.joias.cb --html`

E também:

`forja.cmd export ello.joias.cb --format html`

Os dois comandos devem gerar ou atualizar o mesmo painel HTML.

Adicionar opção de abertura:

`forja.cmd book ello.joias.cb --html --open`

No Windows, `--open` deve abrir o `index.html` no navegador padrão somente após geração bem-sucedida.

Não quebrar os comandos existentes.

## Atualização incremental

O HTML não deve ser manual e descartável.

Criar renderer reutilizável para qualquer cliente da FORJA.

A renderização deve ler o estado atual do cliente e ser regenerável após:

- `onboard`;
- `update`;
- `resume`;
- `correct`.

Quando o book evoluir, o HTML deve refletir a nova versão sem perder as marcações locais de checklist armazenadas no navegador.

## Testes obrigatórios

Executar e registrar:

1. geração do HTML da Ello Joias;
2. abertura offline;
3. ausência de erros JavaScript;
4. funcionamento de busca;
5. funcionamento de filtros;
6. ordenação de tabelas;
7. modo claro e escuro;
8. impressão;
9. exportação JSON;
10. checklist em `localStorage`;
11. sanitização contra script injection;
12. links internos;
13. links externos sem abertura automática;
14. caminhos locais copiáveis;
15. regeneração idempotente;
16. atualização após nova versão do book;
17. renderer genérico em fixture de segundo cliente;
18. regressão completa da FORJA.

## Artefatos finais obrigatórios

Criar:

1. `index.html` principal;
2. assets locais, caso necessários;
3. renderer reutilizável;
4. schema ou view-model do dashboard;
5. testes;
6. relatório de geração;
7. screenshot local do painel em desktop, quando o ambiente permitir;
8. screenshot local em largura móvel, quando o ambiente permitir;
9. handoff:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\ELLO_JOIAS_HTML_DASHBOARD_HANDOFF.md`

## Restrições

Não alterar campanhas.
Não acessar conta privada.
Não enviar mensagens.
Não iniciar pedido.
Não fazer login.
Não publicar no bridge.
Não fazer push.
Não substituir o book canônico pelo HTML.
Não apagar artefatos existentes.
Não mover a raiz da cliente.

## Resultado final obrigatório

Responder com:

1. estado final;
2. caminho exato do HTML principal;
3. caminho da cópia de conveniência;
4. comando para abrir pelo CLI;
5. se abriu offline;
6. se todos os dados reais foram carregados;
7. número de seções renderizadas;
8. número de fontes renderizadas;
9. número de fatos, hipóteses, conflitos, itens antigos e lacunas;
10. testes executados;
11. falhas honestas;
12. arquivos criados e alterados;
13. caminho do handoff;
14. confirmação de que nenhum dado foi inventado;
15. confirmação de que nenhum push foi realizado.

Estados aceitos:

- `ELLO_JOIAS_HTML_DASHBOARD_READY`
- `ELLO_JOIAS_HTML_DASHBOARD_READY_WITH_LIMITATIONS`
- `ELLO_JOIAS_HTML_DASHBOARD_BLOCKED`
