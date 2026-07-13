# FORJA ASTRO BURGER INSTAGRAM DEEP INTELLIGENCE AND SALES PLAYBOOK

## Objetivo

Executar uma investigação pública, profunda e prática do Instagram oficial do Astro Burger, usando o Instagram como fonte principal e cruzando com todas as demais fontes públicas relevantes.

O resultado deve permitir responder com evidência:

- como o perfil está posicionado;
- quais conteúdos realmente chamam atenção;
- quais formatos, temas, ofertas, produtos, pessoas, ganchos e CTAs apresentam melhor desempenho público;
- em quais dias e horários os posts historicamente publicados obtiveram maior engajamento observável;
- como a marca fala;
- como deveria falar para vender mais;
- quais objeções, dúvidas e desejos aparecem nos comentários;
- onde a jornada de compra perde pessoas;
- quais canais e ativos faltam;
- quais ações devem ser tomadas nos próximos 7, 30 e 90 dias.

Esta tarefa não é uma auditoria do sistema FORJA. É uma execução real de inteligência de cliente.

## Ambiente obrigatório

Raiz ativa:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03`

Cliente:

`astro.burger`

Raiz esperada do cliente:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\astro.burger`

Usar o book, fontes, correções, runs, handoffs e artefatos existentes como baseline.

Não apagar, mover ou sobrescrever o material atual.

## Regra principal de investigação

Não encerrar ao primeiro bloqueio do Instagram.

A investigação deve usar uma escada obrigatória de profundidade:

1. dados e fontes já armazenados no cliente;
2. navegador real e navegação pública manual no Instagram;
3. perfil, bio, botões, destaques, posts fixados, feed, Reels e comentários acessíveis;
4. abertura física dos links da bio e registro de redirecionamentos;
5. Google Search, Google Maps, Facebook, site, sistema de pedidos, diretórios e resultados indexados;
6. Meta Ad Library pública;
7. fontes alternativas públicas e confiáveis;
8. registro explícito do que foi bloqueado, não localizado ou não verificável.

Não usar login privado, não contornar controles, não usar credenciais não autorizadas e não violar restrições de acesso.

Diferenciar rigorosamente:

- `CONFIRMED`;
- `PROBABLE`;
- `HYPOTHESIS`;
- `CONFLICT`;
- `STALE`;
- `NOT_PUBLICLY_FOUND`;
- `ACCESS_BLOCKED`;
- `PRIVATE_INSIGHTS_REQUIRED`.

Nunca converter `ACCESS_BLOCKED` em `NOT_FOUND`.

## Identificação do Instagram oficial

Antes de coletar métricas:

1. resolver o handle oficial usando o book existente, site, nome, links e outras fontes;
2. confirmar a ligação entre o perfil e o Astro Burger de Novo Hamburgo;
3. registrar evidências da identidade;
4. rejeitar homônimos.

Se o handle oficial já estiver no cliente, validá-lo novamente.

## Escopo mínimo de coleta do Instagram

Coletar o máximo publicamente acessível.

Meta preferencial:

- últimos 12 meses;
- até 500 publicações públicas;
- todos os posts acessíveis se o total for menor;
- Reels, carrosséis e imagens;
- posts fixados marcados separadamente;
- comentários públicos acessíveis;
- destaques públicos acessíveis;
- dados atuais do perfil.

Se o volume acessível for menor, registrar o motivo e a cobertura real.

## Perfil e presença

Registrar:

- nome exibido;
- username;
- categoria;
- bio completa;
- promessa principal;
- localização declarada;
- seguidores e seguindo, quando públicos;
- quantidade de publicações;
- foto de perfil;
- link da bio;
- todos os redirecionamentos do link;
- telefone, WhatsApp, e-mail e endereço, quando públicos;
- botões de ação;
- destaques, títulos e conteúdos acessíveis;
- posts fixados;
- coerência entre bio, destaques, posts fixados e jornada de compra;
- clareza de área atendida;
- clareza das regras de frete, pedido mínimo, cupom e promoções.

## Ledger obrigatório de publicações

Criar um registro estruturado por publicação com, quando publicamente visível:

- permalink;
- id público ou fingerprint estável;
- data e hora de publicação;
- fuso convertido para `America/Sao_Paulo`;
- formato: imagem, carrossel ou Reel;
- fixado ou não;
- legenda completa;
- primeira frase;
- gancho;
- CTA;
- hashtags;
- menções;
- geotag;
- produto principal;
- categoria de produto;
- oferta;
- preço;
- cupom;
- condição de frete;
- pedido mínimo;
- presença de pessoa;
- presença de rosto;
- UGC;
- bastidor;
- close de produto;
- embalagem;
- prova social;
- humor;
- tendência ou áudio;
- duração, quando Reel e publicamente disponível;
- visualizações ou plays, quando visíveis;
- curtidas, quando visíveis;
- comentários, quando visíveis;
- compartilhamentos e salvamentos apenas se publicamente visíveis, sem inferência;
- perguntas nos comentários;
- objeções;
- elogios;
- reclamações;
- respostas da marca;
- tempo público de resposta, quando timestamps permitirem;
- classificação de confiança;
- fonte e timestamp da coleta.

Gerar pelo menos:

- `instagram_posts.csv`;
- `instagram_posts.json`;
- `instagram_comments_sample.csv`;
- `instagram_collection_manifest.json`.

## Análise de engajamento público

A FORJA não possui direito de chamar dados públicos de `horário em que os seguidores estão online`.

Sem Instagram Insights, produzir duas saídas distintas:

### A. Horários históricos observados

Analisar o desempenho público dos posts conforme o horário em que foram publicados.

Calcular, quando os dados permitirem:

- mediana de curtidas;
- mediana de comentários;
- mediana de visualizações para Reels;
- taxa pública aproximada por seguidores, somente se o número de seguidores atual puder ser usado com ressalva;
- índice composto de engajamento público;
- desempenho por dia da semana;
- desempenho por hora;
- desempenho por faixas de 3 horas;
- desempenho por formato;
- desempenho por tema;
- desempenho por produto;
- desempenho por gancho;
- desempenho por CTA;
- desempenho com preço versus sem preço;
- desempenho com oferta versus conteúdo não promocional;
- desempenho com pessoa versus apenas produto;
- desempenho de UGC, bastidor, humor, prova social e close de produto;
- diferença entre posts fixados e orgânicos comuns;
- outliers positivos e negativos.

Usar mediana como referência principal. Não depender apenas de média.

Separar posts muito recentes quando ainda não maturaram.

Marcar nível de confiança:

- `HIGH`: amostra robusta e consistente;
- `MEDIUM`: amostra razoável;
- `LOW`: menos de cinco itens comparáveis;
- `INSUFFICIENT`: menos de três itens ou métricas indisponíveis.

### B. Agenda recomendada para teste

Criar uma agenda de testes, não uma falsa certeza.

Entregar:

- três melhores janelas históricas observadas;
- três janelas alternativas;
- dias de maior e menor desempenho observável;
- separação por Reels, carrossel e imagem;
- grade de testes por quatro semanas;
- hipótese de publicação para almoço, tarde, jantar e noite;
- recomendação de teste A/B de horários;
- métricas mínimas para validar ou rejeitar cada janela.

Usar sempre a expressão `horário histórico observado` quando não houver Insights privados.

## Conteúdo e criatividade

Classificar todo o conteúdo em pilares reais.

Exemplos esperados, sem forçar categorias inexistentes:

- produto;
- promoção;
- primeira compra;
- entrega;
- montagem;
- bastidores;
- equipe;
- prova social;
- humor;
- desejo e close de comida;
- novidade;
- ocasião de consumo;
- fome noturna;
- casal, amigos ou família;
- localização;
- conveniência;
- preço e valor percebido;
- confiança e qualidade.

Para cada pilar, informar:

- frequência;
- desempenho mediano;
- força comercial;
- saturação;
- lacunas;
- exemplos de posts;
- recomendação de manter, ajustar, reduzir ou criar.

Analisar:

- qualidade dos primeiros dois segundos dos Reels;
- clareza visual;
- iluminação;
- enquadramento;
- apetite visual;
- leitura de texto na tela;
- excesso de texto;
- consistência da identidade;
- uso de pessoas;
- ritmo;
- demonstração do produto;
- força do CTA;
- coerência entre anúncio, perfil e página de pedido.

Quando a semântica visual avançada não estiver disponível, separar análise determinística de interpretação que exige provider.

## Tom de voz e comportamento comercial

Extrair o tom atual da marca com exemplos curtos e parafraseados.

Avaliar:

- humano ou genérico;
- local ou impessoal;
- divertido ou formal;
- direto ou prolixo;
- orientado a desejo ou desconto;
- clareza das regras;
- excesso de emojis;
- consistência;
- personalidade;
- repetição;
- risco de promessa enganosa;
- aderência ao público local.

Criar um guia aplicável de tom de voz com:

- personalidade verbal;
- palavras que a marca deve usar;
- palavras e enquadramentos que deve evitar;
- exemplos de abertura;
- exemplos de CTA;
- respostas para dúvidas;
- respostas para elogios;
- respostas para reclamações;
- respostas para preço, frete, atraso, cupom e pedido mínimo;
- linguagem para Novo Hamburgo;
- regras para Instagram, WhatsApp e anúncios.

Preservar a regra conhecida da campanha:

- atuação de mídia paga apenas em Novo Hamburgo;
- promoção de primeira compra com pedido mínimo de R$ 40;
- benefício de frete limitado a no máximo R$ 15;
- nunca comunicar `entrega grátis` de forma absoluta quando a limitação puder afetar a promessa.

## Comentários, audiência e ICP

Analisar comentários públicos acessíveis para identificar:

- dúvidas frequentes;
- linguagem usada pelo público;
- produtos mais desejados;
- menções a bairro ou cidade;
- reclamações;
- elogios;
- intenção de compra;
- marcações entre amigos;
- ocasiões de consumo;
- objeções de preço;
- objeções de entrega;
- confiança;
- expectativa de prazo;
- resposta da marca.

O ICP deve ser dividido em:

- `CONFIRMED_BY_PUBLIC_EVIDENCE`;
- `PROVISIONAL`;
- `NEEDS_PRIVATE_DATA`.

Não declarar idade, renda, gênero ou comportamento como fato sem evidência.

Criar segmentos de trabalho apenas quando sustentados por sinais públicos.

Para cada segmento:

- ocasião;
- dor;
- desejo;
- gatilho de compra;
- objeção;
- produto provável;
- mensagem;
- canal;
- risco da hipótese;
- dado necessário para confirmação.

## Jornada de compra e conversão

Abrir fisicamente a jornada pública:

Instagram → link da bio → página de pedido → carrinho ou etapa anterior ao pedido.

Não concluir pedido e não enviar WhatsApp.

Registrar:

- quantidade de cliques e etapas;
- clareza do cupom;
- pedido mínimo;
- regra de frete;
- cidade atendida;
- horário de funcionamento;
- categorias;
- produtos;
- preços;
- disponibilidade;
- fricções;
- mensagens contraditórias;
- ausência de prova social;
- problemas mobile;
- tracking público observável;
- parâmetros UTM;
- redirecionamentos;
- abandono provável;
- melhorias priorizadas.

## Canais e presença digital

Mapear com evidência:

- Instagram;
- Facebook;
- Google Business Profile;
- Google Search e SEO local;
- site ou página de pedidos;
- WhatsApp;
- TikTok;
- YouTube;
- Meta Ad Library;
- marketplaces ou delivery;
- avaliações públicas;
- base própria, somente como `NEEDS_CONFIRMATION` se não for pública;
- Pixel, GA4, GTM e CAPI apenas quando houver evidência pública ou autorização.

Para cada canal, classificar:

- ativo e confirmado;
- indicado, mas não validado;
- não localizado publicamente;
- acesso bloqueado;
- deveria ser estruturado;
- não prioritário.

## Concorrência e benchmark

Selecionar concorrentes reais de Novo Hamburgo e região, priorizando operações comparáveis.

Meta:

- cinco a dez concorrentes locais ou regionais;
- três benchmarks nacionais úteis.

Para cada um:

- perfil;
- proposta;
- tom;
- produtos;
- formatos;
- frequência;
- sinais públicos de engajamento;
- ofertas;
- jornada;
- diferenciais;
- riscos de copiar;
- aprendizados adaptáveis.

Não comparar apenas número bruto de seguidores.

## Meta Ad Library

Pesquisar anúncios atribuíveis ao Astro Burger.

Registrar:

- anúncios encontrados;
- datas;
- formatos;
- mensagens;
- ofertas;
- CTAs;
- páginas vinculadas;
- variações;
- ausência de anúncios, quando realmente não encontrados;
- bloqueios de acesso.

Não alterar campanhas.

## Diagnóstico comercial

Entregar respostas diretas para:

1. O que o Astro Burger já faz bem?
2. O que está prejudicando alcance?
3. O que está prejudicando conversão?
4. O perfil explica claramente onde vende e como pedir?
5. As promoções estão claras e juridicamente seguras?
6. Quais produtos devem aparecer mais?
7. Quais formatos devem aumentar?
8. Quais formatos devem reduzir?
9. Quais horários históricos apresentaram melhor resposta pública?
10. Quais horários ainda precisam ser testados?
11. Como a marca deve falar?
12. Como deve responder comentários e mensagens?
13. Que conteúdo vende sem depender apenas de desconto?
14. Quais objeções precisam ser tratadas?
15. Quais provas sociais faltam?
16. O que precisa mudar na bio, destaques e posts fixados?
17. Onde a jornada de compra perde pessoas?
18. Que dados privados são necessários para concluir o ICP e o calendário?

## Playbook obrigatório de venda e conteúdo

Gerar um playbook prático com:

- posicionamento recomendado;
- promessa central;
- três mensagens principais;
- cinco pilares editoriais;
- matriz de funil;
- calendário de 30 dias;
- frequência recomendada;
- grade de horários de teste;
- dez ideias de Reels;
- dez ideias de Stories;
- cinco carrosséis;
- cinco conteúdos de prova social;
- cinco conteúdos de objeção;
- cinco ofertas sem banalizar preço;
- cinco roteiros UGC;
- dez ganchos;
- dez CTAs;
- respostas para comentários e dúvidas;
- guia de tom de voz;
- padrão de legenda;
- padrão de texto na tela;
- recomendações para bio;
- destaques recomendados;
- posts fixados recomendados;
- protocolo de oferta da primeira compra;
- protocolo para não prometer frete ilimitado;
- plano de testes de quatro semanas;
- métricas públicas e privadas necessárias.

## Dados privados pendentes

Criar uma lista curta e priorizada do que só pode ser concluído com autorização:

- Instagram Insights;
- alcance;
- impressões;
- seguidores ativos por hora;
- compartilhamentos;
- salvamentos;
- visitas ao perfil;
- cliques no link;
- mensagens iniciadas;
- dados demográficos;
- origem geográfica;
- campanhas;
- pedidos;
- ticket;
- margem;
- recompra;
- produtos mais vendidos;
- cancelamentos;
- tempo de entrega;
- conversão por canal.

Explicar exatamente como cada dado mudaria a decisão.

## Atualização do book

Atualizar o cliente de forma incremental.

Requisitos:

- preservar todas as versões anteriores;
- criar nova versão;
- deduplicar fatos;
- registrar conflitos;
- não sobrescrever correções humanas;
- anexar evidências;
- classificar confiança;
- manter histórico.

## Saídas obrigatórias

Criar uma pasta dedicada:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\astro.burger\intelligence\instagram-deep-dive`

Gerar no mínimo:

1. `README.md`
2. `executive-summary.md`
3. `instagram-profile-audit.md`
4. `instagram_posts.csv`
5. `instagram_posts.json`
6. `instagram_comments_sample.csv`
7. `engagement-by-day-hour.csv`
8. `engagement-by-format.csv`
9. `engagement-by-theme.csv`
10. `top-posts.md`
11. `low-performing-posts.md`
12. `tone-of-voice-guide.md`
13. `public-audience-and-icp.md`
14. `journey-and-conversion-audit.md`
15. `channel-matrix.md`
16. `competitor-benchmark.md`
17. `meta-ad-library.md`
18. `sales-and-content-playbook.md`
19. `30-day-content-calendar.csv`
20. `private-data-needed.md`
21. `collection-limitations.md`
22. `instagram_collection_manifest.json`
23. `hash-manifest.json`
24. `index.html`
25. `technical.html`

## HTML principal

Criar uma visão humana e operacional, sem jargão técnico no topo.

Cabeçalho esperado:

`Astro Burger`

`Diagnóstico completo do Instagram e plano para vender mais`

`Novo Hamburgo/RS`

`Atualizado em <data e hora localizadas>`

A visão principal deve mostrar:

- resumo;
- o que funciona;
- o que precisa mudar;
- horários históricos observados;
- agenda recomendada de testes;
- conteúdos vencedores;
- produtos e ofertas;
- tom de voz;
- audiência pública;
- jornada;
- canais;
- concorrentes;
- plano de 30 dias;
- dados privados necessários.

Detalhes técnicos, amostras, fontes, confiança e limitações devem ficar em `technical.html`.

## CLI

Implementar ou adaptar, sem quebrar comandos existentes:

`forja.cmd instagram astro.burger --deep --open`

`forja.cmd instagram astro.burger --deep --technical --open`

`forja.cmd instagram astro.burger --refresh-public`

O primeiro comando deve abrir o HTML humano.

## Testes obrigatórios

Executar e provar:

- resolução de identidade;
- cobertura da coleta;
- timestamps e fuso;
- deduplicação;
- tratamento de posts fixados;
- maturação de posts recentes;
- mediana e outliers;
- confiança por tamanho de amostra;
- separação entre dados públicos e Insights privados;
- bloqueio versus não encontrado;
- jornada sem concluir pedido;
- preservação de regras de frete e pedido mínimo;
- isolamento do cliente;
- atualização incremental;
- correção humana;
- HTML offline;
- zero requisições externas automáticas no HTML;
- zero erros JavaScript;
- responsividade;
- impressão;
- path traversal;
- prompt injection;
- PII;
- secrets;
- rollback por hash;
- regressões da FORJA.

## Restrições

Não:

- enviar mensagens;
- iniciar pedido;
- concluir carrinho;
- fazer login em conta privada;
- acessar Insights sem autorização;
- alterar campanhas;
- alterar perfil;
- responder comentários;
- publicar conteúdo;
- criar automações externas;
- fazer commit;
- fazer push;
- publicar no bridge;
- inventar métricas.

## Estados finais aceitos

Somente um:

`ASTRO_BURGER_INSTAGRAM_DEEP_INTELLIGENCE_READY`

`ASTRO_BURGER_INSTAGRAM_DEEP_INTELLIGENCE_USABLE_WITH_LIMITATIONS`

`ASTRO_BURGER_INSTAGRAM_DEEP_INTELLIGENCE_BLOCKED`

O retorno final deve informar:

- handle confirmado;
- período coberto;
- número de posts coletados;
- número de Reels, carrosséis e imagens;
- comentários amostrados;
- métricas públicas disponíveis;
- horários históricos observados;
- nível de confiança;
- melhores formatos;
- melhores temas;
- tom atual;
- tom recomendado;
- ICP confirmado, provisório e pendente;
- principais gargalos;
- plano de 30 dias;
- dados privados necessários;
- versão nova do book;
- caminhos de todos os artefatos;
- testes;
- limitações;
- ações externas realizadas.
