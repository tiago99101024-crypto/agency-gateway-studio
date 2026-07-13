# FORJA_CLIENT_ONBOARDING_ELLO_JOIAS_CB

## TIPO DE EXECUÇÃO

Cliente novo.

Executar onboarding público completo usando a FORJA já validada.

Não refazer auditoria de agentes, skills, arquitetura, segurança ou GitHub.

Não reconstruir o sistema.

Não pesquisar novos frameworks.

Usar o runtime atual, os 9 agentes operacionais, as 10 skills operacionais, a CLI e os contratos existentes.

## AMBIENTE

Raiz ativa:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03`

Ponteiro ativo:

`C:\TiagoOS\FORJA_ACTIVE_VERSION.json`

Handoff final obrigatório:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\FORJA_FINAL_PRODUCTION_GATE_HANDOFF.md`

Estado de referência:

`FORJA_PRODUCTION_VALIDATED_WITH_HUMAN_AUTHORIZATION_PENDING`

## SEMENTE ÚNICA

Instagram informado pelo usuário:

`https://www.instagram.com/ellojoiascb?igsh=MWoxZzlzaGxoa2ZocA%3D%3D&utm_source=qr`

Handle esperado:

`@ellojoiascb`

Não assumir silenciosamente que `cb` significa Campo Bom.

Resolver a cidade, identidade, nome comercial, localização e natureza do negócio com evidência.

## OBJETIVO

Descobrir tudo que for publicamente possível sobre a cliente e criar um book vivo, versionado, rastreável e útil para estratégia, mídia paga, conteúdo, comercial e atendimento.

O sistema deve partir somente da semente acima.

Não pedir briefing antes da primeira execução.

Não depender de pasta manual preparada.

Não usar fatos fornecidos de memória pelo operador.

Não preencher lacunas com invenção.

## AUTORIZAÇÃO

Permitido:

- leitura pública da web;
- Instagram público quando acessível;
- mecanismos de busca;
- resultados indexados;
- sites oficiais;
- Google Maps e Google Business Profile públicos;
- Facebook público;
- TikTok público;
- Pinterest público;
- marketplaces públicos;
- catálogos e lojas virtuais públicas;
- links de bio;
- WhatsApp apenas para identificar o link ou número publicado, sem enviar mensagem;
- Meta Ad Library pública;
- diretórios empresariais públicos;
- avaliações públicas;
- arquivos públicos de imagem, PDF e vídeo;
- criação e atualização do book local;
- screenshots públicos necessários para análise;
- execução de OCR e análise multimodal local;
- gravação de fontes, hashes, snapshots e evidências.

Não permitido:

- login em conta;
- contornar robots.txt;
- técnicas evasivas;
- burlar bloqueios;
- seguir perfil;
- curtir;
- comentar;
- enviar direct;
- enviar WhatsApp;
- fazer pedido;
- iniciar checkout;
- cadastrar lead;
- alterar campanha;
- acessar conta privada;
- acessar Meta Business;
- acessar Google Ads;
- acessar GA4;
- acessar CRM;
- publicar bridge;
- usar credenciais;
- coletar dados pessoais de consumidores;
- criar commit ou push.

Estado:

`external_actions: READ_ONLY_PUBLIC_WEB_AND_LOCAL_CLIENT_BOOK`

## REGRA PARA INSTAGRAM

Se o Instagram bloquear acesso direto:

1. não tentar evasão;
2. registrar o bloqueio;
3. usar descoberta indireta;
4. buscar snippets indexados;
5. buscar links oficiais associados;
6. buscar Facebook, Google Maps, site, catálogo, WhatsApp publicado, marketplaces e diretórios;
7. buscar imagens públicas indexadas;
8. usar somente informações proporcionalmente suportadas;
9. marcar o que não pôde ser verificado.

O Instagram é semente, não deve ser ponto único de falha.

## IDENTIDADE E ENTITY RESOLUTION

Resolver e registrar:

- nome comercial atual;
- variações do nome;
- handle atual;
- handles antigos, quando existirem;
- cidade;
- endereço;
- bairro;
- área de atendimento;
- loja física, online ou híbrida;
- telefone e WhatsApp publicados;
- site;
- link de catálogo;
- Google Business Profile;
- Facebook;
- TikTok;
- Pinterest;
- marketplace;
- CNPJ público somente quando a correspondência for forte e relevante;
- pessoas proprietárias somente quando apresentadas publicamente pela própria marca;
- relação entre perfis encontrados;
- conflitos de identidade;
- grau de confiança por identidade.

Não confundir com empresas homônimas.

## PESQUISA OBRIGATÓRIA

### 1. Negócio e modelo comercial

Descobrir:

- o que vende;
- categorias de produtos;
- joias, semijoias, prata, ouro, folheados, aço, bijuterias ou outras categorias, somente com evidência;
- serviços adicionais;
- ticket aparente;
- faixas de preço públicas;
- formas de pagamento públicas;
- parcelamento;
- Pix;
- entrega;
- retirada;
- envio regional ou nacional;
- atendimento por WhatsApp;
- loja física;
- horários;
- garantias;
- troca;
- manutenção;
- personalização;
- embalagem;
- presente;
- atacado ou varejo;
- pronta entrega ou encomenda;
- jornada de compra;
- gargalos aparentes da jornada.

### 2. Produtos e ofertas

Mapear:

- brincos;
- anéis;
- alianças;
- colares;
- correntes;
- pulseiras;
- pingentes;
- conjuntos;
- relógios;
- peças personalizadas;
- presentes;
- datas comemorativas;
- linhas masculinas e femininas;
- produtos infantis, quando houver;
- lançamentos;
- promoções;
- kits;
- descontos;
- condições;
- validade;
- disponibilidade;
- diferenciais prometidos;
- prova da promessa;
- conflitos de preço;
- ofertas antigas ainda indexadas.

Separar:

- oferta atual confirmada;
- oferta antiga;
- oferta sem data;
- hipótese;
- não encontrado.

### 3. Marca e posicionamento

Analisar:

- proposta de valor;
- posicionamento aparente;
- linguagem;
- tom;
- promessa central;
- diferenciais;
- sinais de preço baixo, acessível, presenteável, premium, artesanal, autoral ou tradicional, apenas quando sustentados;
- arquétipo aparente como hipótese;
- consistência do nome;
- clareza da bio;
- CTA;
- prova social;
- autoridade;
- confiança;
- identidade local;
- coerência entre marca, produto e preço;
- riscos de posicionamento genérico.

### 4. Identidade visual e multimodal

Analisar todo material público acessível:

- logotipo;
- versões do logotipo;
- paleta principal e secundária;
- cores dominantes;
- tipografia aparente;
- fundos;
- fotografia;
- iluminação;
- enquadramento;
- acabamento;
- uso de mãos, modelos, bustos e caixas;
- embalagem;
- vitrine;
- loja física;
- feed;
- Stories e destaques quando acessíveis;
- templates;
- legibilidade;
- hierarquia visual;
- consistência;
- sinais de conteúdo genérico;
- qualidade das imagens;
- coerência entre arte e produto;
- oportunidades de melhoria.

Executar OCR em artes públicas acessíveis.

Não declarar semântica visual avançada quando depender de provider não configurado.

### 5. Conteúdo e presença digital

Mapear:

- frequência aparente de postagem;
- formatos;
- Reels;
- fotos;
- carrosséis;
- Stories;
- destaques;
- demonstração de produto;
- prova social;
- bastidores;
- educação;
- ofertas;
- datas comemorativas;
- UGC;
- rosto da proprietária ou equipe;
- vídeos com fala;
- conteúdo de desejo;
- conteúdo de objeção;
- conteúdo local;
- chamadas para WhatsApp;
- chamadas para loja;
- chamadas para compra;
- qualidade dos ganchos;
- clareza de legenda;
- SEO social;
- GEO local;
- consistência do CTA;
- sinais de posts com maior repercussão quando os dados forem públicos;
- lacunas editoriais.

Não inventar métricas privadas.

### 6. Reputação e prova social

Buscar:

- avaliações no Google;
- comentários públicos;
- elogios recorrentes;
- reclamações recorrentes;
- percepção de atendimento;
- percepção de preço;
- qualidade;
- durabilidade;
- entrega;
- embalagem;
- troca;
- confiança;
- sinais de recorrência;
- depoimentos usados pela própria marca;
- reputação em marketplaces;
- riscos reputacionais.

Não coletar ou expor dados pessoais de consumidores.

### 7. Mercado local

Após resolver a localização, pesquisar:

- mercado de joias e semijoias da cidade;
- comportamento local;
- sazonalidade;
- datas relevantes;
- renda e perfil econômico em fontes públicas confiáveis;
- polos comerciais;
- concorrência física;
- concorrência online regional;
- raio de influência provável;
- oportunidades locais;
- ameaças;
- lacunas de oferta;
- diferenciais possíveis.

Não usar estatísticas nacionais como se fossem locais.

### 8. Concorrentes

Identificar no mínimo:

- 5 concorrentes diretos locais ou regionais;
- 3 concorrentes digitais ou benchmarks nacionais;
- concorrentes por preço;
- concorrentes por estilo;
- concorrentes por confiança;
- concorrentes por conveniência.

Para cada concorrente:

- nome;
- cidade;
- fontes;
- produtos;
- posicionamento;
- preço aparente;
- força digital;
- avaliações;
- diferencial;
- fraqueza aparente;
- ameaça para a cliente;
- oportunidade de diferenciação.

Não selecionar concorrentes apenas por nome parecido.

### 9. ICP e segmentos

Construir segmentos com evidência e hipótese declarada:

- compradora para uso próprio;
- presente;
- namoro;
- noivado;
- casamento;
- datas comemorativas;
- mãe;
- filha;
- adolescente;
- público masculino comprador de presente;
- cliente recorrente;
- cliente sensível a preço;
- cliente orientada por estilo;
- cliente que valoriza atendimento local;
- atacado ou revenda, somente se houver evidência.

Para cada segmento:

- contexto;
- necessidade;
- desejo;
- objeção;
- gatilho de compra;
- produto provável;
- ticket provável como hipótese;
- canal;
- mensagem;
- risco de comunicação.

### 10. Funil e jornada

Mapear:

- descoberta;
- consideração;
- prova;
- contato;
- compra;
- pagamento;
- entrega ou retirada;
- pós-venda;
- recompra;
- indicação.

Avaliar:

- atritos;
- links quebrados;
- ausência de catálogo;
- ausência de preço;
- demora potencial;
- CTA disperso;
- falta de prova;
- falta de política;
- falta de localização;
- falta de rastreamento;
- dependência excessiva de direct ou WhatsApp.

### 11. Mídia paga pública

Verificar:

- presença na Meta Ad Library;
- anúncios ativos públicos;
- formatos;
- ofertas;
- criativos;
- mensagens;
- páginas de destino;
- CTA;
- consistência com o orgânico;
- riscos de promessa;
- possíveis lacunas de rastreamento visíveis.

Não acessar conta de anúncios.

### 12. SEO, GBP e descoberta local

Avaliar:

- consistência NAP;
- nome;
- endereço;
- telefone;
- categoria;
- descrição;
- fotos;
- avaliações;
- respostas;
- horário;
- produtos;
- links;
- ranking aparente;
- presença em buscas locais;
- site;
- indexação;
- termos de busca;
- oportunidades de SEO local;
- perguntas frequentes;
- schema quando houver site.

### 13. Riscos e lacunas

Registrar claramente:

- identidade não confirmada;
- cidade não confirmada;
- produto não confirmado;
- material não confirmado;
- preço antigo;
- oferta sem validade;
- fonte fraca;
- fonte contraditória;
- falta de prova;
- risco jurídico;
- risco de marca;
- risco de promessa;
- risco de reputação;
- risco de tracking;
- risco operacional;
- risco comercial;
- risco de capacidade;
- dependência de informação da cliente.

## CLASSIFICAÇÃO DE CONHECIMENTO

Todo fato deve receber:

- `CONFIRMED`
- `PROBABLE`
- `HYPOTHESIS`
- `CONFLICTED`
- `STALE`
- `NOT_FOUND`
- `BLOCKED_SOURCE`

Toda afirmação precisa de:

- fonte;
- URL;
- data de coleta;
- trecho ou evidência;
- confiança;
- origem oficial, secundária ou fraca;
- validade temporal.

## BOOK OBRIGATÓRIO

Criar book vivo com:

1. resumo executivo;
2. identidade;
3. fontes oficiais;
4. modelo de negócio;
5. produtos;
6. preços e ofertas;
7. posicionamento;
8. marca;
9. identidade visual;
10. conteúdo;
11. reputação;
12. mercado;
13. concorrentes;
14. ICP;
15. jornada;
16. mídia paga pública;
17. SEO e presença local;
18. riscos;
19. conflitos;
20. lacunas;
21. oportunidades;
22. recomendações;
23. fatos confirmados;
24. hipóteses;
25. perguntas para a cliente;
26. fontes e proveniência;
27. histórico de versões.

O book deve ser útil para:

- gestor de tráfego;
- social media;
- copywriter;
- designer;
- comercial;
- atendimento;
- proprietária;
- planejamento estratégico.

## SAÍDAS OPERACIONAIS

Além do book, criar:

1. `ELLO_JOIAS_EXECUTIVE_SUMMARY.md`
2. `ELLO_JOIAS_SOURCE_REGISTER.json`
3. `ELLO_JOIAS_IDENTITY_RESOLUTION.md`
4. `ELLO_JOIAS_PRODUCT_AND_OFFER_MATRIX.md`
5. `ELLO_JOIAS_BRAND_AND_VISUAL_AUDIT.md`
6. `ELLO_JOIAS_CONTENT_AUDIT.md`
7. `ELLO_JOIAS_REPUTATION_AUDIT.md`
8. `ELLO_JOIAS_MARKET_AND_COMPETITOR_MAP.md`
9. `ELLO_JOIAS_ICP_AND_JOURNEY.md`
10. `ELLO_JOIAS_PUBLIC_ADS_AND_TRACKING_AUDIT.md`
11. `ELLO_JOIAS_GAPS_AND_RISKS.md`
12. `ELLO_JOIAS_CLIENT_KICKOFF_QUESTIONS.md`
13. `ELLO_JOIAS_FIRST_30_DAYS_PRIORITIES.md`
14. `ELLO_JOIAS_FACTS_HYPOTHESES_CONFLICTS.json`
15. `ELLO_JOIAS_ONBOARDING_RESULT.json`

Criar handoff em:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\ELLO_JOIAS_PUBLIC_ONBOARDING_HANDOFF.md`

Usar a estrutura canônica de cliente da FORJA.

Não inventar caminho ou `client_id` fora das regras existentes.

Informar no retorno o `client_id` criado e a raiz exata.

## PERGUNTAS PARA A CLIENTE

Gerar perguntas somente depois da pesquisa pública.

As perguntas devem preencher exclusivamente o que não foi possível descobrir, incluindo quando necessário:

- produtos reais;
- materiais;
- margem;
- ticket;
- estoque;
- capacidade;
- prazo;
- entrega;
- troca;
- garantia;
- público atual;
- metas;
- acesso a Meta;
- acesso a Google;
- acesso ao catálogo;
- dados de vendas;
- produtos prioritários;
- sazonalidade;
- restrições;
- concorrentes percebidos;
- histórico de campanhas.

Não perguntar o que já estiver publicamente confirmado.

## PRIMEIROS 30 DIAS

Criar plano inicial priorizado, mas sem executar campanhas.

Separar:

- correções urgentes;
- quick wins;
- conteúdo;
- presença local;
- oferta;
- comercial;
- tracking;
- criativos;
- mídia paga;
- dados que precisam de autorização.

Cada recomendação precisa informar:

- evidência;
- impacto;
- esforço;
- dependência;
- risco;
- prioridade.

## TESTES

Executar:

- validação do seed contract;
- entity resolution;
- deduplicação;
- isolamento;
- retomada;
- idempotência;
- atualização incremental;
- correção humana;
- renderer;
- source confidence;
- stale information;
- conflito de identidade;
- segurança;
- PII;
- path traversal;
- prompt injection;
- rollback por hash.

## CRITÉRIO DE ACEITE

A execução só termina quando:

1. a identidade tiver sido resolvida ou marcada honestamente como parcial;
2. as fontes tiverem sido descobertas;
3. o Instagram bloqueado não impedir o onboarding;
4. existir book útil proporcional à evidência;
5. mercado e concorrentes tiverem sido pesquisados;
6. ICP e jornada tiverem sido construídos;
7. marca, visual e conteúdo tiverem sido analisados;
8. fatos, hipóteses e conflitos estiverem separados;
9. perguntas para a cliente forem geradas somente para lacunas reais;
10. existir plano inicial de 30 dias;
11. nenhum dado for inventado;
12. nenhuma ação externa de escrita for executada;
13. testes e regressões passarem.

## ESTADO FINAL

Declarar somente um:

- `ELLO_JOIAS_PUBLIC_ONBOARDING_READY`
- `ELLO_JOIAS_PUBLIC_ONBOARDING_USABLE_WITH_REVIEW`
- `ELLO_JOIAS_PUBLIC_ONBOARDING_PARTIAL`
- `ELLO_JOIAS_PUBLIC_ONBOARDING_BLOCKED`

## RETORNO FINAL

Informar:

1. estado final;
2. `client_id`;
3. raiz do cliente;
4. identidade resolvida;
5. cidade;
6. modelo de negócio;
7. produtos confirmados;
8. preços e ofertas confirmados;
9. fontes oficiais;
10. fontes alternativas;
11. concorrentes;
12. ICP;
13. posicionamento;
14. identidade visual;
15. conteúdo;
16. reputação;
17. jornada;
18. anúncios públicos;
19. riscos;
20. lacunas;
21. perguntas para a cliente;
22. nota do book de 0 a 100;
23. classificação do book;
24. versão do book;
25. arquivos gerados;
26. testes executados;
27. falhas;
28. confirmação de nenhuma campanha alterada;
29. confirmação de nenhuma mensagem enviada;
30. confirmação de nenhum pedido iniciado;
31. confirmação de nenhum login realizado;
32. confirmação de nenhum commit ou push;
33. `external_actions: READ_ONLY_PUBLIC_WEB_AND_LOCAL_CLIENT_BOOK`.
