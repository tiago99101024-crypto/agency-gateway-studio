# FORJA SIMPLIFY ELLO JOIAS CLIENT DASHBOARD

## Objetivo

Refazer a apresentação HTML da Ello Joias para uso com cliente final.

A versão atual está tecnicamente completa, porém excessivamente complexa, com linguagem de sistema e pouca clareza comercial.

Não refazer o onboarding.
Não alterar o book canônico.
Não inventar dados.
Não apagar a versão técnica existente.

## Cliente

- Nome humano: Ello Joias
- Instagram: @ellojoiascb
- Cidade confirmada: Campo Bom/RS
- client_id técnico: ello.joias.cb

## Fontes obrigatórias

Usar os dados reais já existentes em:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\ello.joias.cb`

Usar também:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\ELLO_JOIAS_PUBLIC_ONBOARDING_HANDOFF.md`

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\ELLO_JOIAS_HTML_DASHBOARD_HANDOFF.md`

## Resultado esperado

Gerar duas visões separadas:

1. `index.html`
   - visão simples, humana e própria para apresentar à cliente
   - deve abrir por padrão

2. `technical.html`
   - visão técnica completa atual
   - preservar os dados, evidências, hashes, testes e classificações internas

A visão simples deve ter no máximo sete áreas principais:

1. Visão geral
2. Canais digitais
3. Público e clientes
4. Produtos e ofertas
5. Conteúdo e posicionamento
6. Oportunidades e prioridades
7. Perguntas para completar o diagnóstico

## Cabeçalho humano

Remover da área principal qualquer exibição como:

`Cliente: Ello Joias · client_id: ello.joias.cb Coleta: 2026-07-13T19:25:26.846Z`

Substituir por:

- título: `Ello Joias`
- subtítulo: `Diagnóstico inicial de presença digital`
- localização: `Campo Bom/RS`
- data localizada no fuso America/Sao_Paulo, por exemplo: `Atualizado em 13 de julho de 2026 às 16h25`

O `client_id`, timestamp ISO, run_id, hashes e nomes técnicos devem ficar apenas em uma seção recolhida chamada `Detalhes técnicos`.

## Linguagem

Não mostrar termos técnicos crus na visão da cliente:

- `PARTIAL`
- `NOT_FOUND`
- `STALE`
- `PROBABLE`
- `CONFIRMED`
- `client_id`
- `source_id`
- `run_id`

Traduzir para linguagem humana:

- Confirmado
- Precisa confirmar
- Não localizado publicamente
- Informação antiga
- Hipótese de trabalho
- Evidência limitada

## Resumo inicial

Criar quatro blocos simples:

1. O que já existe
2. O que está funcionando
3. O que ainda não conseguimos confirmar
4. Oportunidades mais importantes

Não usar contadores técnicos como elemento principal.
Os números podem aparecer apenas como apoio.

## Matriz de canais digitais

Criar uma tabela simples com estas colunas:

- Canal
- Situação atual
- Evidência encontrada
- O que isso significa
- Próximo passo

Usar somente os dados reais do book.

Os canais mínimos que devem ser avaliados são:

- Instagram
- Shopee
- Google Business Profile
- Google Search e SEO local
- WhatsApp Business
- Facebook
- Site próprio
- TikTok
- Catálogo Meta
- E-mail ou base de clientes, somente se houver evidência

Distinguir obrigatoriamente:

- canal confirmado e ativo
- canal indicado, mas não validado
- canal não localizado
- canal que pode existir, mas depende de confirmação da cliente
- canal recomendado para ativação

Não afirmar que um canal não existe apenas porque não foi encontrado.
Usar `Não localizado publicamente`.

## Explicação sobre endereço

Criar uma caixa chamada `Por que não encontramos o endereço completo?`

Explicar em linguagem simples, com base nas evidências reais:

- Campo Bom/RS foi confirmado por geotag oficial
- não foi encontrado endereço de rua verificável em fonte oficial acessível
- não foi localizado um Google Business Profile inequívoco
- não houve NAP consistente em fontes públicas
- o sistema não deve adivinhar endereço

Adicionar o próximo passo:

`Confirmar com a cliente se existe loja física, retirada, atendimento com horário marcado ou operação exclusivamente online.`

## Explicação sobre telefone

Criar uma caixa chamada `Por que não encontramos um telefone confirmado?`

Explicar:

- o telefone não apareceu em fonte pública oficial verificável
- botões de contato do Instagram podem não ficar visíveis sem login ou podem estar ausentes
- nenhum número deve ser inferido por diretório ou homônimo

Próximo passo:

`Pedir o WhatsApp oficial, confirmar se ele é comercial e validar se deve aparecer no Instagram, Google e materiais de venda.`

## ICP

A seção de ICP não pode aparecer como conclusão definitiva.

Usar o título:

`Público provável neste momento`

Separar em três camadas:

### Sinais observados

Usar apenas evidências existentes:

- compra para uso próprio
- compra para presente
- sensibilidade a preço
- decisão orientada por estilo
- possível componente local e regional

### Hipóteses de trabalho

Mostrar como hipóteses, nunca como fatos:

- faixas etárias
- frequência de compra
- ticket ideal
- preferência entre prata e semijoias
- peso de presente versus uso próprio

### O que falta para fechar o ICP

Listar perguntas objetivas sobre:

- quem mais compra hoje
- idade média
- cidade dos pedidos
- ticket médio
- produtos mais vendidos
- ocasiões de compra
- objeções
- recompra
- canal de origem
- forma de pagamento

Usar um indicador simples:

`ICP provisório, precisa de dados da cliente e histórico de vendas.`

## Prioridades comerciais

A visão da cliente deve destacar apenas as prioridades mais úteis:

1. confirmar link oficial da Shopee
2. confirmar telefone e WhatsApp oficial
3. confirmar se existe endereço, retirada ou loja física
4. organizar ficha técnica por SKU
5. padronizar garantia, troca e materiais
6. criar ou regularizar Google Business Profile quando aplicável
7. melhorar SEO local e presença no Google
8. estruturar rastreamento e catálogo
9. produzir criativos com prova social e produto real

Cada prioridade deve conter:

- motivo
- impacto
- responsável sugerido
- status

## Perguntas para a cliente

Criar uma seção curta, agrupada por tema:

- operação
- produtos
- vendas
- canais
- dados e acessos

Não mostrar 17 lacunas soltas sem contexto.
Transformar lacunas em perguntas humanas e acionáveis.

## Design

A visão simples deve:

- ter aparência leve
- usar títulos curtos
- evitar tabelas gigantes
- evitar excesso de badges
- usar no máximo duas cores de destaque além dos neutros
- ter navegação simples
- funcionar em celular e desktop
- ter modo impressão
- funcionar offline
- não fazer requisições externas automáticas

## Navegação

Adicionar no topo:

- `Visão para cliente`
- `Ver detalhes técnicos`
- `Imprimir ou salvar em PDF`

`Ver detalhes técnicos` deve abrir `technical.html`.

## CLI

Preservar:

`forja.cmd book ello.joias.cb --html --open`

Esse comando deve abrir a visão simples.

Adicionar, caso ainda não exista:

`forja.cmd book ello.joias.cb --html --audience technical --open`

## Arquivos finais

Principal:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\ello.joias.cb\exports\html\index.html`

Técnico:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\ello.joias.cb\exports\html\technical.html`

Cópias:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\exports\clients\ello.joias.cb\index.html`

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\exports\clients\ello.joias.cb\technical.html`

## Testes obrigatórios

Validar:

- nome humano no cabeçalho
- data localizada
- nenhum `client_id` visível na área principal
- nenhum timestamp ISO visível na área principal
- matriz de canais renderizada
- endereço explicado sem invenção
- telefone explicado sem invenção
- ICP marcado como provisório
- link entre visão simples e técnica
- impressão
- responsividade
- zero erros JavaScript
- zero requisições externas automáticas
- book canônico inalterado
- regressões da FORJA em PASS

## Entrega

Ao final retornar:

1. estado final
2. caminhos dos dois HTMLs
3. resumo das mudanças
4. canais exibidos e classificação de cada um
5. confirmação de que endereço e telefone foram explicados sem inferência
6. confirmação de que o ICP foi reescrito como provisório
7. testes executados
8. limitações restantes

Não criar commit.
Não fazer push.
Não alterar campanhas.
Não alterar contas.
Não modificar o book canônico.
