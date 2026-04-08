# Studio Smoke Fixture

Fixture operacional minimo e mais restritivo para reduzir oscilacao do fluxo completo do Studio sem alterar scoring, benchmark, allocation, envelope ou logica central.

## Cliente

Payload usado em `POST /api/clients`:

```json
{
  "nome": "Smoke Winner <suffix>",
  "instagram": "",
  "nicho": "delivery",
  "produto": "pizza artesanal com pedido direto no WhatsApp",
  "cidade": "Sao Paulo",
  "objetivo": "aumentar pedidos diretos no WhatsApp e reduzir comissao do iFood",
  "tom_voz": "direto, comercial, anti-app, quase literal, sem abstracao, com numero concreto, perda explicita, CTA curto e sem sinonimos motivacionais",
  "cores": ["#FF6B35", "#111111", "#F7F3E8"],
  "fontes": ["Montserrat Bold", "Poppins SemiBold"],
  "observacoes_identidade": "Usar uma unica composicao dominante e absolutamente rigida no formato vertical 4:5. Fundo inteiro em preto liso, sem textura e sem gradiente. O numero '27%' deve ocupar sozinho cerca de 28% da altura total da peca, centralizado horizontalmente no topo e encostado visualmente na margem superior. Logo abaixo do 27%, reservar uma area de headline centralizada, em duas linhas no maximo, ocupando cerca de 12% da altura total e sem sair da metade superior. O mockup do celular deve ser o unico elemento imagetico: um unico smartphone reto, frontal, centralizado, ocupando entre 38% e 42% da altura total da peca e entre 46% e 52% da largura. A interface visivel dentro do celular deve mostrar somente uma tela de app de delivery com lista de pedido e valor/comissao, sem mapa, sem foto de comida grande, sem multiplos cards e sem overlays. O rodape deve comportar uma chamada curta para pedido direto no WhatsApp em faixa horizontal unica, ocupando cerca de 12% da altura da peca inteira, com bloco centralizado e sem elementos ao lado. As areas entre headline e celular e nas laterais do celular devem permanecer vazias, servindo como respiro visual. Elementos obrigatorios: fundo preto liso, 27% laranja, headline branca curta, um unico celular central e CTA curto no rodape. Elementos proibidos em hipotese nenhuma: pessoas, maos, comida em destaque, ingredientes, boxes extras, badges, selos, setas, explosoes, icones flutuantes, logos grandes, texturas, padroes, sombras dramaticas, segundos mockups, recortes inclinados, fundos de cozinha, mesas, qualquer segundo foco e qualquer excesso de texto fora do eixo 27% + mensagem principal + CTA."
}
```

## Identidade minima

- Nicho e produto deixam explicita a venda direta fora do app.
- Objetivo forca ganho comercial concreto e mensuravel.
- Tom de voz elimina abstracao, branding generico e motivacional.
- Cores e fontes fortes evitam visual generico.
- Observacao de identidade ancora o criativo em margem, comissao e WhatsApp com um unico foco.

## Asset

Asset-base usado em `POST /api/clients/:id/assets`:

- Arquivo principal: `docs/assets/studio-smoke-phone-base-v2.png`
- Categoria: `imagem`
- Uso padrao: `docs/assets/studio-smoke-phone-base-v2.png`, que segue como referencia operacional principal por ser o melhor estado conhecido entre estabilidade visual e contexto suficiente para o pipeline.
- Uso experimental minimo: `docs/assets/studio-smoke-phone-base-v5.png`, para comparacao direta contra a v2 alterando apenas um detalhe interno da interface: a remocao da linha secundaria de cada item da lista dentro do smartphone.
- Uso experimental intermediario: `docs/assets/studio-smoke-phone-base-v4.png`, para comparacao controlada contra a v2 quando o objetivo for reduzir `visual_overlap` sem empobrecer a leitura do copy.
- Motivo da v2: PNG local deterministico, com fundo preto liso, smartphone frontal central e interface simples, mas ainda rica o bastante para sustentar leitura consistente do pipeline.
- Motivo da v5: preserva a composicao macro da v2 e muda apenas um detalhe interno mensuravel e reversivel, reduzindo microtexto dentro da tela sem retirar o contexto visual principal.
- Motivo da v4: composicao ainda rigida, com menos detalhe que a v2 e mais contexto que a v3, tentando reduzir ambiguidade visual sem cair em abstracao excessiva.
- Referencia historica ruim: `docs/assets/studio-smoke-phone-base-v3.png`, mantida apenas para comparacao; a v3 ficou minima demais, quebrou uma corrida no copy e piorou a estabilidade visual.
- Fallback antigo: `teste_real.png`, apenas se for necessario comparar o efeito do asset-base controlado com um asset mais solto.

## Job

Payload usado em `POST /api/clients/:id/jobs`:

```json
{
  "tipo": "post_estatico",
  "briefing": "Criar post estatico para delivery com promessa comercial direta e sem ambiguidade. Tom comercial, anti-app, com dor clara de margem perdida e incentivo a pedido direto no WhatsApp. A headline precisa obrigatoriamente conter um numero, um verbo de perda, margem ou comissao e o app como agente da perda. Dar preferencia a uma construcao unica e mais estreita na familia 'voce perde X% da margem para o app', evitando trocas como 'com app' ou formulacoes com duas ideias. A chamada final precisa obrigatoriamente trazer verbo de acao curto, pedido direto e WhatsApp. Dar preferencia a CTA na familia 'peca direto no WhatsApp', evitando trocas equivalentes como 'pelo WhatsApp'. O visual deve obedecer uma composicao dominante unica e quase mecanica: fundo preto liso, numero 27% laranja enorme no topo ocupando cerca de 28% da altura, area de headline branca centralizada imediatamente abaixo, um unico smartphone frontal no centro ocupando de 38% a 42% da altura com tela de app de delivery mostrando lista de pedido e comissao, e faixa de CTA no rodape ocupando cerca de 12% da altura. Deixar vazias as laterais do celular e o espaco entre headline e mockup. Nao incluir pessoas, maos, comida em destaque, boxes extras, selos, icones, texturas, fundos contextuais ou qualquer segundo mockup.",
  "formato": "feed_portrait",
  "objetivo_job": "gerar pedidos diretos no WhatsApp hoje",
  "tom_especifico": "urgente, especifico, anti-app, com numero concreto, perda financeira explicita, headline forte contra o app e CTA final direto para pedir no WhatsApp",
  "referencias": [
    "Falar explicitamente de comissao do app, margem perdida e pedido direto no WhatsApp.",
    "A headline deve combinar numero + verbo de perda + margem/comissao + app.",
    "Dar preferencia a uma unica frase curta de perda direta na familia 'voce perde X% da margem para o app'.",
    "Usar verbos de perda concreta na headline, como perder, entregar ou pagar, em vez de beneficios amplos.",
    "A chamada final deve combinar verbo curto + pedido direto + WhatsApp.",
    "Dar preferencia a CTA na familia 'peca direto no WhatsApp'.",
    "O CTA deve chamar para pedir direto no WhatsApp, nao prometer economia, desconto ou ganho amplo.",
    "Se possivel, manter o CTA limpo e sem aditivos desnecessarios.",
    "Evitar trocas equivalentes como 'com app' na headline e 'pelo WhatsApp' no CTA.",
    "Evitar saidas amplas como 'pague menos', 'economize', 'saia ganhando' ou beneficios genericos sem confronto com o app.",
    "Evitar branding generico, promessa vaga, awareness, frases motivacionais e qualquer abstracao.",
    "Usar uma unica composicao visual dominante: 27% ocupando cerca de 28% da altura no topo, headline imediatamente abaixo, smartphone frontal central ocupando 38% a 42% da altura e CTA em faixa no rodape.",
    "A tela visivel do smartphone deve mostrar apenas interface de app de delivery com lista de pedido e comissao, sem mapa, sem foto grande de comida e sem cards extras.",
    "Manter vazias as laterais do celular e o espaco entre headline e smartphone, sem elementos de apoio.",
    "Nao incluir pessoas, maos, comida em destaque, selos, icones decorativos, texturas, boxes extras, fundos contextuais, recortes inclinados ou qualquer segundo foco.",
    "Na peca final, priorizar visualmente o 27%, a mensagem principal e a chamada final."
  ]
}
```

## Sinais de estabilidade

- Headline deve conter numero, perda de margem/comissao e oposicao ao app.
- CTA deve conter verbo curto, pedido direto e WhatsApp, sem virar promessa de economia e sem modificadores extras.
- A promessa deve falar apenas de perda de margem no app e recuperacao de lucro no WhatsApp.
- O visual deve usar um unico quadro dominante com ordem fixa: topo `27%`, headline abaixo, celular central, CTA no rodape.
- O smartphone deve permanecer frontal, centralizado e ocupar de 38% a 42% da altura da peca.
- As laterais do celular e o espaco entre headline e mockup devem permanecer vazios.
- Nenhum segundo foco visual deve competir com o celular e o numero.
- O texto visivel da peca deve permanecer curto, direto e sem competir com o quadro principal.

## Sinal esperado de sucesso

- `POST /api/clients/:id/jobs/:jid/run` retorna `200`
- `manifest.json` existe no diretorio do job
- `output_image.png` existe no diretorio do job
- `quality_gate.json` indica:
  - `approved: true`
  - `score >= 85`
  - `critical_failures: []`
