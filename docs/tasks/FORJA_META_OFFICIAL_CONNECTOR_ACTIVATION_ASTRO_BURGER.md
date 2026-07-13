# FORJA META OFFICIAL CONNECTOR ACTIVATION FOR ASTRO BURGER

## Purpose

Fix the concrete production gap identified after the Astro Burger Instagram official API attempt.

Current state:

`ASTRO_BURGER_INSTAGRAM_OFFICIAL_API_NOT_CONFIGURED`

The FORJA currently has contracts, scopes, fixtures, dry-run and healthcheck for Meta, but it does not have a live Graph API adapter, a secure local authorization resolver or a client-level connection binding for `astro.burger`.

This task is not another audit. Implement the missing connector path, activate it safely with explicit human authorization, validate the correct assets and then execute the official Instagram collection and reconciliation.

## Environment

Active root:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03`

Client:

`astro.burger`

Client root:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\astro.burger`

Existing public Instagram analysis:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\astro.burger\intelligence\instagram-deep-dive`

Existing official API attempt:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\astro.burger\intelligence\instagram-official-api`

Current book version:

`v7`

Preserve all existing versions and artifacts.

## Non-negotiable security rules

- Never put credentials in Git, Markdown, JSON, CSV, HTML, logs, screenshots, terminal history or reports.
- Never print an access credential or application secret.
- Never place credentials in ordinary environment files inside the repository.
- Use an operating-system-protected local secret store.
- On Windows, prefer the existing approved FORJA secret abstraction. If none exists, implement a current-user, current-machine protected store using Windows-native protection such as DPAPI or an equivalent OS credential facility.
- The stored secret must be unreadable as plaintext on disk.
- All reports must contain only redacted connection metadata.
- Do not scan unrelated folders for credentials.
- Do not attempt to extract credentials from a browser, cookies, history or another application.
- A user must explicitly approve or provide the authorization through a secure local flow.

## Required implementation

### 1. Live Meta Graph adapter

Implement a real, read-only adapter for the Meta Graph and Instagram professional account APIs.

The adapter must support:

- API version configuration without hardcoding an obsolete version;
- authenticated GET requests;
- pagination until completion;
- retries with bounded exponential backoff;
- rate-limit reporting;
- timeout and cancellation;
- structured errors with code and subcode;
- request identifiers when returned;
- redacted logging;
- response provenance and SHA-256 manifests;
- zero write methods for this connector activation task.

Do not use fixtures, mocks or fabricated payloads as live proof.

### 2. Secure local authorization resolver

Implement a resolver with a logical reference such as:

`secret://connectors/meta/astro.burger`

The client configuration may contain only this logical reference and non-sensitive metadata.

Implement two safe authorization paths:

1. `authorize`
   - opens a local user-driven authorization flow in the browser;
   - validates state and callback;
   - stores the resulting authorization only in the protected local secret store;
   - does not expose the authorization in command output.

2. `import-existing`
   - accepts an already existing authorization through a hidden secure local prompt;
   - does not echo input;
   - does not record the value in shell history;
   - writes only the encrypted/protected form to the secret store;
   - validates it immediately;
   - discards plaintext from memory as soon as practical.

Do not require the user to paste sensitive values into ChatGPT, a Markdown file, a source file or a normal command argument.

### 3. Client-level connection binding

Create a redacted connection profile for `astro.burger` containing only:

- connector name;
- logical secret reference;
- expected business name;
- expected Instagram username;
- expected Facebook Page when validated;
- expected professional Instagram account when validated;
- scopes granted;
- authorization status;
- expiry metadata;
- last validation time;
- last successful collection time;
- revoke instructions;
- zero secret values.

The connection must be isolated from every other client.

### 4. Validation flow

Implement:

`forja.cmd connectors astro.burger --name instagram --status`

`forja.cmd connectors astro.burger --name instagram --authorize`

`forja.cmd connectors astro.burger --name instagram --import-existing`

`forja.cmd connectors astro.burger --name instagram --validate`

`forja.cmd connectors astro.burger --name instagram --revoke`

Validation must confirm, from the official API:

- authorization validity;
- expiration when available;
- granted permissions;
- accessible Pages and businesses;
- linked professional Instagram accounts;
- exact username;
- profile identity;
- media access;
- account insight access;
- media insight access;
- comment access;
- Story access when available;
- ads read access when separately authorized.

Never proceed silently with the wrong Page, wrong Instagram account, test asset or unrelated business.

If multiple matching assets exist, present a redacted numbered selection and require explicit human choice.

### 5. Automatic continuation after successful authorization

After successful validation of the correct Astro Burger asset, automatically execute the official Instagram collection and reconciliation already specified by the existing v7 handoff.

The flow must collect all accessible official data, paginate fully, preserve raw redacted evidence, reconcile against the public inventory and create a new incremental book version.

Do not ask the user to run a second unrelated prompt after connection succeeds.

### 6. Source priority correction

Update the FORJA intelligence source policy to enforce this order:

1. official connected data;
2. client-owned operational data;
3. public data;
4. hypotheses.

A public-only Instagram report must never again be labelled as internally complete when an official connection is available but not wired.

Preserve the previous public score as a score for public evidence only.

## Required outputs

Create or update, without secrets:

- live Meta Graph adapter;
- secure local resolver;
- authorization CLI;
- client connection binding;
- validation report;
- redacted permissions matrix;
- authorized assets report;
- collection status;
- reconciliation outputs;
- source-priority policy;
- tests;
- handoff.

Primary result folder:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\storage\clients-live\clients\astro.burger\intelligence\instagram-official-api`

Final handoff folder:

`C:\TiagoOS\FORJA_FULL_V1_1_RC_03\docs\handoffs`

## Required tests

Test at minimum:

- secure storage round trip;
- no plaintext secret on disk;
- no secret in CLI output;
- no secret in logs;
- no secret in generated artifacts;
- wrong asset;
- expired authorization;
- missing permission;
- multiple assets;
- pagination;
- rate limit;
- retry;
- timeout;
- cancellation;
- revoke;
- reauthorization;
- client isolation;
- path traversal;
- PII redaction;
- idempotence;
- resume;
- rollback;
- reconciliation;
- HTML offline;
- regression suites.

Live API tests must be marked as live only when a real authorization and real response are used.

## Do not do

- Do not alter campaigns.
- Do not alter budgets.
- Do not publish content.
- Do not reply to comments.
- Do not send messages.
- Do not change profile or Page settings.
- Do not start an order.
- Do not commit or push.
- Do not publish any credential.
- Do not use browser credential extraction.
- Do not claim live validation from fixtures.

## Final states

Use exactly one:

`ASTRO_BURGER_META_CONNECTOR_IMPLEMENTED_AWAITING_SECURE_HUMAN_AUTHORIZATION`

Use when the adapter, resolver, client binding and secure authorization flow are complete, but the user has not yet completed the local authorization step.

`ASTRO_BURGER_META_CONNECTOR_AUTHORIZED_WRONG_ASSET`

Use when authorization works but the returned asset is not Astro Burger.

`ASTRO_BURGER_META_CONNECTOR_AUTHORIZED_PARTIAL_SCOPE`

Use when the correct asset is validated but some required read permissions are unavailable.

`ASTRO_BURGER_INSTAGRAM_OFFICIAL_API_INTELLIGENCE_VALIDATED`

Use only when the correct account is validated, real official data are collected, reconciled, tested and rendered.

## Final response

Report:

1. final state;
2. files created and changed;
3. adapter status;
4. secure resolver status;
5. authorization path used;
6. client binding status;
7. authorization validity;
8. permissions;
9. validated Page and Instagram account;
10. media count;
11. insight coverage;
12. comments and Stories coverage;
13. ads-read status;
14. reconciliation coverage;
15. new book version;
16. tests;
17. any single human action still required;
18. confirmation that no secret was exposed;
19. confirmation that nothing external was modified;
20. `external_actions`.