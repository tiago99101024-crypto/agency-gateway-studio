# FORJA | ASTRO BURGER | RELATÓRIO DO DONO E PAINEL INTERNO DE INTELIGÊNCIA

## STATUS DA TAREFA

Esta é uma tarefa operacional sobre dados oficiais já coletados.

Não é auditoria geral da FORJA.

Não é nova pesquisa pública.

Não é pedido para criar hipóteses soltas.

O Bruxo deve orquestrar os agentes e skills necessários para transformar dados oficiais em duas entregas humanas, comprovadas e úteis.

## AMBIENTE

Raiz ativa:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03`

Cliente:

`astro.burger`

Raiz do cliente:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\astro.burger`

Base oficial principal:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\astro.burger\intelligence\instagram-official-api`

Base pública complementar:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\astro.burger\intelligence\instagram-deep-dive`

Book atual:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\astro.burger\production-book`

Estado oficial confirmado:

`ASTRO_BURGER_INSTAGRAM_OFFICIAL_API_INTELLIGENCE_VALIDATED`

Dados oficiais já confirmados:

- Página Astro Burger: `958316537374249`
- Instagram: `@astroburger.nh`
- Instagram ID: `17841477868657087`
- 78 mídias oficiais
- 154 registros de Insights de mídia
- 425 comentários
- 0 Stories disponíveis no momento da coleta
- anúncios em leitura disponíveis
- 11 contas de anúncios acessíveis
- reconciliação pública x oficial concluída
- book atual em v10

## REGRA PRINCIPAL DE FONTE

Usar esta prioridade:

1. API oficial Meta e Instagram
2. dados próprios do cliente já conectados
3. dados públicos reconciliados
4. hipóteses explícitas

Nunca usar a pesquisa pública para substituir dado oficial disponível.

Nunca preencher lacuna oficial com estimativa silenciosa.

## OBJETIVO

Criar duas entregas diferentes.

### Entrega 1

Um relatório em Markdown para o dono do Astro Burger.

Ele deve explicar os dados e os principais Insights em linguagem humana, clara, simples e comercial.

### Entrega 2

Um painel HTML interno para a equipe da FORJA.

Ele deve mostrar, de forma cirúrgica, quem é o público, quando engaja, quais conteúdos funcionam, quais anúncios funcionam, o que precisa ser ajustado e o que ainda não pode ser comprovado.

## ORQUESTRAÇÃO PELO BRUXO

O Bruxo deve coordenar no mínimo:

- agente de inteligência conectada
- agente de Instagram e conteúdo
- agente de mídia paga
- agente de ICP e comportamento
- agente de análise de comentários
- agente de jornada e conversão
- agente de evidências e qualidade
- renderer Markdown
- renderer HTML

Cada agente deve gerar output real e rastreável.

Não considerar agente operacional apenas por existir como prompt.

## ISOLAMENTO DA CONTA DE ANÚNCIOS

A autorização possui 11 contas de anúncios acessíveis.

Antes de usar dados de mídia paga:

1. identificar a conta correta do Astro Burger por associação com Página, Instagram, Business, nome, campanhas e criativos;
2. registrar a evidência da associação;
3. excluir todas as outras contas da análise;
4. nunca somar ou misturar dados de outros clientes;
5. se houver ambiguidade real, marcar mídia paga como `AWAITING_HUMAN_AD_ACCOUNT_SELECTION` e não produzir números misturados.

## ENTREGA 1 | RELATÓRIO PARA O DONO EM MARKDOWN

Arquivo obrigatório:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\astro.burger\deliverables\owner\RELATORIO_INTELIGENCIA_INSTAGRAM_ASTRO_BURGER.md`

Criar também uma cópia em:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\exports\clients\astro.burger\RELATORIO_INTELIGENCIA_INSTAGRAM_ASTRO_BURGER.md`

### Estilo obrigatório

- linguagem humana
- português do Brasil
- sem linguajar de IA
- sem dizer “a IA identificou”
- sem client_id
- sem source_id
- sem IDs técnicos
- sem nomes de endpoints
- sem tokens
- sem hashes no corpo principal
- sem frases genéricas de agência
- sem travessão
- sem promessas não comprovadas
- sem transformar hipótese em fato

### Cabeçalho humano

Usar:

`Astro Burger`

`Relatório de inteligência do Instagram`

`O que os dados mostram e como usar isso para vender mais`

Data localizada em `America/Sao_Paulo`.

### Estrutura obrigatória

1. Resumo em uma página
2. O que foi analisado
3. O tamanho real da base analisada
4. Quem está acompanhando e interagindo
5. Onde esse público está
6. Idade e gênero, somente quando oficiais e disponíveis
7. Dias e horários de maior atividade
8. Dias e horários que geram mais alcance
9. Dias e horários que geram mais interação
10. Reels, imagens e carrosséis
11. Conteúdos que mais chamam atenção
12. Produtos que mais despertam interesse
13. Ganchos e chamadas que funcionam
14. Dúvidas, elogios e objeções nos comentários
15. O que os anúncios mostram
16. O que hoje está dificultando a venda
17. O que deve ser feito agora
18. Plano de 30 dias
19. O que ainda não podemos afirmar
20. Dados que ainda precisam ser conectados

### Linguagem do relatório

Trocar termos técnicos por explicações humanas.

Exemplos:

- não usar apenas `reach`; usar `pessoas alcançadas`
- não usar apenas `engagement`; usar `interações`
- não usar `benchmark`; usar `referência de comparação`
- não usar `hook`; usar `abertura do conteúdo`
- não usar `CTA`; usar `chamada para ação`
- não usar `dataset`; usar `base analisada`

Quando um termo técnico for necessário, explicar em uma frase curta.

### Honestidade obrigatória

O dono precisa enxergar claramente:

- o que está comprovado
- o que é um sinal
- o que ainda não está disponível
- o que depende de pedidos, faturamento, GA4 ou delivery

Não esconder limitações.

Não transformar a ausência de uma métrica em falha da marca.

## ENTREGA 2 | PAINEL HTML INTERNO

Arquivo principal obrigatório:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\astro.burger\intelligence\decision-dashboard\index.html`

Cópia obrigatória:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\exports\clients\astro.burger\intelligence\index.html`

Criar também:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\astro.burger\intelligence\decision-dashboard\technical.html`

### Objetivo do HTML

O painel deve servir para decidir:

- o que postar
- quando postar
- o que anunciar
- para quem falar
- como falar
- qual produto mostrar
- qual oferta testar
- quais dúvidas resolver
- quais canais corrigir
- quais dados ainda faltam

### Estilo obrigatório

- visual humano
- leitura rápida
- sem cara de painel técnico cru
- sem linguagem de IA
- sem excesso de badges
- sem IDs técnicos na tela principal
- sem timestamp ISO
- sem status internos no topo
- sem termos em inglês quando houver equivalente claro
- responsivo
- offline
- imprimível
- pesquisável
- acessível

### Cabeçalho humano

`Astro Burger`

`Painel de inteligência de público, conteúdo e vendas`

`Novo Hamburgo`

`Dados oficiais do Instagram e da Meta`

Data e hora localizadas em `America/Sao_Paulo`.

## SEÇÕES OBRIGATÓRIAS DO HTML

### 1. Visão rápida

Mostrar em linguagem simples:

- tamanho da base oficial
- período analisado
- mídias analisadas
- comentários analisados
- alcance disponível
- seguidores disponíveis
- anúncios considerados
- principal oportunidade
- principal risco

### 2. Quem é o público

Separar claramente:

- seguidores
- pessoas alcançadas organicamente
- pessoas alcançadas por anúncios
- pessoas que interagiram
- pessoas que comentaram
- compradores, somente se houver fonte própria conectada

Nunca misturar esses públicos.

### 3. Idade e gênero

Usar apenas dados oficiais disponíveis.

Exibir:

- distribuição por faixa etária
- distribuição por gênero
- tamanho da amostra
- fonte exata
- período
- limitações

Se a API não devolver esses dados, mostrar:

`A Meta não disponibilizou idade e gênero nesta coleta.`

Não estimar por foto, nome, texto, comentário ou perfil.

### 4. Localização

Usar quando disponível:

- país
- estado
- cidade
- região
- origem geográfica de anúncios
- origem geográfica de pedidos, quando conectada

#### Bairros

Tentar obter bairros apenas por fontes legítimas:

- pedidos e endereços agregados
- CRM
- plataforma de delivery
- GA4 ou outra fonte que realmente forneça localização suficiente
- relatórios de mídia quando o breakdown estiver oficialmente disponível

Regras para bairros:

- nunca inferir bairro por username, comentário, geotag isolada ou nome de pessoa
- nunca mostrar endereço individual
- nunca mostrar bairro com menos de 5 registros
- agrupar bairros com baixa amostra em `Outros`
- informar a fonte
- informar o período
- se indisponível, mostrar `Bairros ainda não disponíveis com segurança`

### 5. Quando o público está ativo

Separar:

- atividade real de seguidores, quando a Meta fornecer
- horários de publicação
- horários de maior alcance
- horários de maior interação
- horários de maior compartilhamento
- horários de maior salvamento
- horários de maior clique
- horários de maior conversão, somente com vendas conectadas

Usar `America/Sao_Paulo`.

Mostrar:

- dia da semana
- hora
- faixa de três horas
- tamanho da amostra
- mediana
- média de apoio
- confiança
- outliers

Não chamar horário de publicação de horário em que seguidores estão online.

### 6. Conteúdo que funciona

Comparar de forma normalizada:

- Reels
- imagem
- carrossel
- collab
- pessoas aparecendo
- produto isolado
- preparo
- humor
- ranking
- pergunta
- prova social
- preço
- oferta
- sazonalidade
- signos
- Novo Hamburgo
- primeira compra

Calcular quando disponível:

- interação por alcance
- comentários por alcance
- compartilhamentos por alcance
- salvamentos por alcance
- cliques por alcance
- seguidores gerados por alcance
- retenção de vídeo
- conclusão de vídeo

Não ranquear apenas por curtidas absolutas.

### 7. Produtos e ofertas

Mostrar:

- produtos com maior alcance
- produtos com maior interação
- produtos com mais comentários
- produtos com mais compartilhamentos
- produtos com mais salvamentos
- produtos presentes em anúncios
- produtos com sinal de intenção de compra
- produtos sem evidência suficiente

Preservar as regras comerciais:

- mídia paga somente em Novo Hamburgo
- primeira compra com pedido mínimo de R$ 40
- benefício de frete limitado a R$ 15
- nunca comunicar entrega grátis de forma absoluta

### 8. Comentários e linguagem do público

Analisar os 425 comentários oficiais.

Classificar:

- intenção de compra
- elogio
- dúvida
- localização
- entrega
- preço
- cardápio
- horário
- disponibilidade
- reclamação
- produto desejado
- marcação de amigos
- humor
- objeção
- spam

Mostrar:

- temas mais frequentes
- perguntas repetidas
- objeções repetidas
- palavras usadas pelo público
- respostas da marca
- oportunidades perdidas
- exemplos anonimizados

Não exibir nome, perfil ou identificador pessoal desnecessário.

### 9. Tom de voz

Mostrar:

- tom atual
- o que funciona
- o que está escondendo o produto
- palavras e construções que aproximam
- exageros
- excesso de metáfora espacial
- nível adequado de humor
- como falar de produto
- como falar de preço
- como falar de entrega
- como falar de urgência
- como chamar para o pedido
- como responder comentários

A recomendação deve ser direta, local e apetitosa.

A temática espacial deve permanecer como assinatura, não como cortina sobre o hambúrguer.

### 10. Anúncios

Usar somente a conta correta do Astro Burger.

Mostrar quando disponível:

- campanhas
- investimento
- alcance
- impressões
- frequência
- cliques
- visualizações de vídeo
- custo por resultado
- criativos
- posicionamentos
- datas
- orgânico versus impulsionado
- posts vinculados
- páginas de destino

Nunca alterar nada.

Se a conta correta não puder ser identificada com segurança, mostrar a pendência sem misturar dados.

### 11. Jornada até a venda

Mostrar:

- Instagram
- anúncio
- link
- UTM
- página de pedidos
- Pixel
- GA4
- pedido
- receita
- recompra

Para cada etapa, classificar:

- conectado
- parcialmente conectado
- não conectado
- não reconciliável ainda

Não afirmar que um post vendeu sem pedido ou receita reconciliados.

### 12. Decisões práticas

Criar três blocos:

#### Fazer agora

Ações que podem ser executadas com os dados atuais.

#### Testar nos próximos 14 dias

Hipóteses com critério de sucesso e descarte.

#### Depende de conexão ou confirmação

Ações que exigem GA4, delivery, pedidos, margem, estoque, autorização ou decisão humana.

### 13. Calendário operacional

Gerar agenda de quatro semanas com:

- dia
- horário
- formato
- produto
- tema
- abertura
- chamada para ação
- objetivo
- métrica principal
- critério de sucesso

Não produzir calendário genérico.

### 14. O que ainda não sabemos

Mostrar de forma humana:

- pedidos
- faturamento
- margem
- ticket médio
- recompra
- vendas por produto
- bairros, se não houver fonte válida
- dados demográficos indisponíveis
- relação conteúdo x venda

## CRUZAMENTOS OBRIGATÓRIOS

Cruzar, quando houver cobertura real:

- formato x alcance
- formato x interação por alcance
- tema x compartilhamento
- tema x salvamento
- produto x comentário
- produto x anúncio
- horário x alcance
- horário x interação
- dia x alcance
- dia x interação
- orgânico x pago
- pessoa x produto isolado
- preço x sem preço
- oferta x conteúdo comum
- collab x não collab
- Novo Hamburgo x conteúdo genérico
- comentário x intenção de compra

## ARQUIVOS ESTRUTURADOS

Criar junto ao HTML:

- `audience-summary.json`
- `audience-age-gender.csv`
- `audience-location.csv`
- `audience-neighborhoods.csv`
- `engagement-by-hour.csv`
- `engagement-by-day.csv`
- `content-performance.csv`
- `product-performance.csv`
- `comment-intelligence.csv`
- `ads-performance.csv`
- `journey-coverage.json`
- `recommendations.json`
- `evidence-matrix.json`
- `limitations.md`
- `source-manifest.json`
- `hash-manifest.json`

Quando um dado não existir, criar o arquivo com estado explícito e motivo. Não inventar linhas.

## COMANDOS

Implementar ou usar:

`forja.cmd intelligence astro.burger --owner-report --open`

`forja.cmd intelligence astro.burger --internal-dashboard --open`

`forja.cmd intelligence astro.burger --refresh`

O `--refresh` deve reutilizar a autorização DPAPI existente, sem pedir novo login quando a autorização continuar válida.

## TESTES OBRIGATÓRIOS

- isolamento da conta correta de anúncios
- zero mistura entre clientes
- zero segredo em arquivos
- zero token no HTML ou Markdown
- zero PII desnecessária
- idade não inferida
- gênero não inferido
- bairros não inferidos
- amostra mínima de bairro aplicada
- dados ausentes declarados
- fonte por métrica
- período por métrica
- fuso correto
- normalização por alcance
- mediana
- outliers
- HTML offline
- zero requisições externas automáticas
- responsividade
- impressão
- navegação por teclado
- links internos
- Markdown legível
- ausência de linguajar de IA
- ausência de IDs técnicos no relatório do dono
- preservação do book v10
- regressões gerais da FORJA

## NÃO FAZER

- não criar nova campanha
- não alterar campanha
- não alterar orçamento
- não publicar conteúdo
- não responder comentários
- não enviar mensagem
- não alterar perfil
- não alterar Página
- não iniciar pedido
- não exibir token
- não pedir token novamente sem necessidade
- não fazer commit
- não fazer push
- não publicar bridge
- não misturar as 11 contas de anúncios
- não inventar bairros
- não inventar idade
- não inventar gênero
- não chamar hipótese de dado

## ESTADOS FINAIS

Usar somente um:

`ASTRO_BURGER_OWNER_REPORT_AND_INTERNAL_INTELLIGENCE_READY`

ou:

`ASTRO_BURGER_OWNER_REPORT_AND_INTERNAL_INTELLIGENCE_USABLE_WITH_LIMITATIONS`

ou:

`ASTRO_BURGER_OWNER_REPORT_AND_INTERNAL_INTELLIGENCE_BLOCKED_BY_DATA_QUALITY`

## RETORNO FINAL OBRIGATÓRIO

Informar:

1. estado final
2. caminho do relatório Markdown do dono
3. caminho da cópia exportada
4. caminho do HTML interno
5. caminho do HTML técnico
6. conta de anúncios usada e evidência de associação, sem segredo
7. período analisado
8. quantidade de mídias
9. quantidade de Insights
10. quantidade de comentários
11. idade disponível ou indisponível
12. gênero disponível ou indisponível
13. cidades disponíveis ou indisponíveis
14. bairros disponíveis ou indisponíveis
15. melhores horários comprovados
16. melhores dias comprovados
17. formatos mais eficientes
18. temas mais eficientes
19. produtos mais eficientes
20. principais objeções
21. tom recomendado
22. ações imediatas
23. testes de 14 dias
24. dados ainda faltantes
25. arquivos gerados
26. testes executados
27. confirmação de zero segredo
28. confirmação de zero alteração externa
29. `external_actions`
