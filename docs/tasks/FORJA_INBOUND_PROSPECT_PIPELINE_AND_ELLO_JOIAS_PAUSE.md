# FORJA INBOUND PROSPECT PIPELINE AND ELLO JOIAS PAUSE

## Contexto humano

A Ello Joias ainda não deve ser tratada como cliente ativa.

Ela entrou por prospecção receptiva: a empresa procurou Tiago para entender o que ele faz. Não existe, até o momento, confirmação de contratação, escopo, orçamento, reunião, acesso, campanha ou autorização operacional.

A pesquisa pública já realizada deve ser preservada como inteligência pré-comercial. Porém, a empresa deve ficar em segundo plano até existir uma nova ação comercial humana.

Esta tarefa não serve apenas para a Ello Joias. Ela deve criar na FORJA um fluxo reutilizável para qualquer lead ou oportunidade que chegue espontaneamente.

## Objetivo

Implementar um módulo simples de prospecção receptiva separado do cadastro de clientes ativos.

A FORJA deve passar a distinguir claramente:

- prospect recebido;
- prospect em descoberta;
- prospect qualificado;
- reunião agendada;
- proposta enviada;
- negociação;
- cliente ganho;
- oportunidade perdida;
- oportunidade pausada;
- cliente ativo.

O fluxo não pode promover automaticamente uma empresa para cliente ativo apenas porque houve pesquisa, criação de book ou geração de dashboard.

## Estado correto da Ello Joias

Registrar a oportunidade com os seguintes dados, sem inventar o que não foi informado:

- nome: `Ello Joias`;
- identificador de referência: `ello.joias.cb`;
- origem: `INBOUND`;
- natureza: `PROSPECCAO_RECEPTIVA`;
- contexto: `A empresa procurou Tiago para entender os serviços que ele oferece.`;
- estágio comercial: `DISCOVERY_INITIAL`;
- prioridade: `SECONDARY`;
- estado operacional: `PAUSED_UNTIL_NEXT_HUMAN_ACTION`;
- cliente contratado: `false`;
- autorização para campanhas: `false`;
- autorização para contas privadas: `false`;
- autorização para monitoramento contínuo: `false`;
- próxima ação automática: `none`;
- próxima ação humana: `aguardar novo contato, resposta, reunião ou decisão de Tiago`;
- contato de entrada: `UNCONFIRMED` caso o canal não esteja registrado;
- responsável: `Tiago`;
- observação: `O onboarding público e o dashboard já produzidos são inteligência pré-comercial, não prova de contratação.`

Não inventar nome de pessoa, telefone, e-mail, canal de contato, data exata de contato, orçamento, interesse específico ou prazo.

## Preservação obrigatória

Não apagar, mover ou sobrescrever:

- `C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\ello.joias.cb`
- `C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\ELLO_JOIAS_PUBLIC_ONBOARDING_HANDOFF.md`
- `C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\ELLO_JOIAS_HTML_DASHBOARD_HANDOFF.md`
- HTMLs e relatórios já criados.

O material existente deve ser referenciado no registro da oportunidade como `PRE_SALES_INTELLIGENCE`.

O book existente deve permanecer preservado, mas a empresa não deve aparecer como cliente ativa em listas operacionais, filas de atualização, monitoramento recorrente ou dashboards de produção.

## Implementação geral

Criar um módulo reutilizável de prospects dentro da arquitetura atual da FORJA.

Antes de escolher caminhos, inspecionar a estrutura real existente e seguir os padrões do runtime. Não criar uma segunda arquitetura paralela desnecessária.

O sistema deve suportar, no mínimo:

### Entidade de prospect

Campos mínimos:

- `prospect_id`;
- `display_name`;
- `origin`;
- `stage`;
- `priority`;
- `operational_state`;
- `owner`;
- `created_at`;
- `updated_at`;
- `last_human_action_at`;
- `next_human_action`;
- `next_action_due_at` opcional;
- `contact_channel`;
- `contact_person` opcional;
- `reason_for_contact`;
- `contracted`;
- `authorizations`;
- `linked_client_id` opcional;
- `linked_intelligence_artifacts`;
- `notes`;
- `timeline`;
- `tags`;
- `source_of_truth`;
- `confidence`.

### Estágios aceitos

Implementar enumeração clara:

- `INBOUND_NEW`
- `DISCOVERY_INITIAL`
- `QUALIFIED`
- `MEETING_SCHEDULED`
- `PROPOSAL_PREPARATION`
- `PROPOSAL_SENT`
- `NEGOTIATION`
- `WON`
- `LOST`
- `DORMANT`
- `PAUSED`

### Estados operacionais

- `ACTIVE_COMMERCIAL_FOLLOWUP`
- `PAUSED_UNTIL_NEXT_HUMAN_ACTION`
- `AWAITING_PROSPECT_RESPONSE`
- `AWAITING_INTERNAL_DECISION`
- `READY_TO_CONVERT_TO_CLIENT`
- `CLOSED`

### Regras

1. `WON` não pode ocorrer sem ação humana explícita.
2. Converter prospect em cliente ativo exige confirmação humana.
3. Pesquisa pública não equivale a contratação.
4. Dashboard ou book não equivale a autorização operacional.
5. Prospect pausado não entra em atualização automática.
6. Prospect pausado não gera monitoramento, mensagens, pesquisas ou tarefas automáticas.
7. Nenhum prospect pode receber contato automático sem autorização humana explícita.
8. Toda alteração de estágio deve gerar evento na timeline.
9. Toda informação desconhecida deve permanecer `UNCONFIRMED`, nunca inferida.
10. Inteligência pré-comercial deve ser preservada e vinculada, não duplicada.

## CLI

Adicionar comandos simples e humanos, mantendo compatibilidade com a CLI atual:

```bat
forja.cmd prospect add
forja.cmd prospect show <prospect_id>
forja.cmd prospect list
forja.cmd prospect note <prospect_id>
forja.cmd prospect stage <prospect_id> <stage>
forja.cmd prospect pause <prospect_id>
forja.cmd prospect resume <prospect_id>
forja.cmd prospect convert <prospect_id>
forja.cmd prospect timeline <prospect_id>
```

Também aceitar:

```bat
forja.cmd prospect show ello.joias.cb
```

O comando `convert` deve exigir confirmação humana explícita no terminal e registrar quem autorizou, data e estado anterior.

## Visualização HTML

Criar uma visão simples de prospecção, separada do dashboard técnico da cliente.

Ela deve responder:

- quem entrou em contato;
- por que entrou em contato;
- em que estágio está;
- o que já foi pesquisado;
- o que ainda não foi confirmado;
- qual é a próxima ação humana;
- se existe proposta, reunião ou contratação;
- se o caso está ativo ou pausado.

Para Ello Joias, o cabeçalho deve ser humano:

- `Ello Joias`
- `Prospecção receptiva`
- `Em descoberta inicial`
- `Aguardando próxima ação comercial`

Não mostrar `client_id`, hashes, timestamps ISO, nomes de testes ou status internos na área principal.

Criar, preferencialmente:

- `C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\prospects\ello.joias.cb\index.html`
- uma listagem geral em `C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\prospects\index.html`

A localização final pode ser adaptada ao padrão real do projeto, desde que documentada e sem duplicação de arquitetura.

## Registro da Ello Joias

Criar o registro de prospect e vincular:

- onboarding público;
- book v2;
- HTML simples;
- HTML técnico;
- handoffs;
- lista de lacunas;
- perguntas pendentes.

Adicionar uma timeline mínima:

1. empresa procurou Tiago para entender seus serviços, informação reportada pelo usuário;
2. pesquisa pública inicial realizada;
3. dashboard comercial e técnico gerados;
4. caso reclassificado como prospecção receptiva;
5. caso pausado até nova ação humana.

Não registrar data ou horário inventado. Use data de execução apenas como data do registro no sistema e diferencie claramente de `data do contato não confirmada`.

## Separação entre prospect e cliente

A FORJA deve deixar explícito:

```text
PROSPECT != CLIENTE ATIVO
```

Um prospect pode ter:

- pesquisa pública;
- diagnóstico;
- book preliminar;
- reunião;
- proposta;
- notas comerciais.

Mas somente vira cliente ativo após confirmação humana de contratação.

## Lista operacional

A Ello Joias não deve aparecer em:

- clientes ativos;
- fila de atualização automática;
- conectores pendentes de autorização de clientes;
- monitoramento contínuo;
- produção de campanha;
- execução de mídia;
- tarefas recorrentes.

Ela deve aparecer em:

- prospects;
- prospecção receptiva;
- descoberta inicial;
- prioridade secundária;
- aguardando próxima ação humana.

## Testes obrigatórios

Criar e executar testes para provar:

1. cadastro de prospect;
2. listagem;
3. alteração de estágio;
4. pausa e retomada;
5. timeline imutável ou append-only;
6. não promoção automática para cliente;
7. conversão somente com confirmação humana;
8. isolamento entre prospects;
9. vínculo com inteligência pré-comercial;
10. prospect pausado fora das filas automáticas;
11. ausência de contato automático;
12. ausência de pesquisa automática após pausa;
13. HTML offline sem requisições externas;
14. segurança, traversal, PII e secrets;
15. regressão completa da FORJA.

## Saídas obrigatórias

Gerar:

- schema de prospect;
- módulo de runtime;
- comandos CLI;
- registro da Ello Joias;
- timeline;
- HTML individual;
- HTML geral de prospects;
- relatório de testes;
- manifesto de hashes;
- handoff em `.md`.

Handoff sugerido:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs\FORJA_INBOUND_PROSPECT_PIPELINE_AND_ELLO_JOIAS_HANDOFF.md`

## Restrições

- não refazer o onboarding;
- não pesquisar novamente a Ello Joias;
- não enviar mensagem;
- não criar lembrete automático;
- não iniciar follow-up;
- não acessar conta privada;
- não alterar campanha;
- não promover a cliente para ativa;
- não apagar inteligência existente;
- não fazer push;
- não publicar bridge;
- não inventar dados comerciais.

## Estado final esperado

```text
FORJA_INBOUND_PROSPECT_PIPELINE_READY
ELLO_JOIAS_INBOUND_PROSPECT_PAUSED
```

O retorno final deve informar:

1. onde fica o registro da oportunidade;
2. onde fica a lista geral de prospects;
3. estágio e estado operacional da Ello Joias;
4. arquivos criados e alterados;
5. comandos disponíveis;
6. provas de que ela não está em filas de cliente ativo;
7. testes executados;
8. handoff criado;
9. confirmação de que nenhum contato, pesquisa adicional, campanha, commit ou push foi realizado.