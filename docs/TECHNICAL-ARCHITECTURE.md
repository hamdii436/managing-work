# CAMPUS LIFE — Technical and Online Architecture

## 1. Status and design intent

This document defines a proposed architecture for the CAMPUS LIFE product. Repository inspection found no Unity project or existing game implementation; these are design decisions and interfaces to validate, not descriptions of working systems. The target client stack is Unity 6 LTS, C#, URP, and the Unity Input System.

The architecture prioritizes server authority for valuable state, clear service boundaries, safe recovery, mobile performance, and small first-release scope. Select specific networking, hosting, identity, persistence, moderation, analytics, and purchase providers only after a prototype and operational / privacy review. Do not couple game rules to a vendor SDK.

## 2. High-level topology

```text
Unity mobile client
  ├─ Presentation: UI, localization, input, character visuals, audio
  ├─ Game client: prediction / interpolation, local interaction requests
  └─ Network boundary: authenticated session, snapshots, commands
                    │
                    ▼
Online gateway / session service
  ├─ Identity and session authorization
  ├─ Zone / region routing and presence
  ├─ Authoritative zone simulation and activity rules
  ├─ Social / chat and moderation boundary
  └─ Economy and entitlement commands
                    │
                    ▼
Persistence boundary
  ├─ Relational store: durable accounts, character state, ledger, trades
  ├─ Cache / ephemeral store: presence, routing, rate limits (if needed)
  └─ Audit / operational event pipeline with controlled access
                    │
                    ▼
External adapters: platform purchase validation, notification / support,
optional moderation or analytics providers
```

This is a logical decomposition. The first deployment may use a small number of services or a modular server process rather than many microservices. Split services only when independent scaling, ownership, or failure isolation justify the operational cost.

### Trust boundaries

- Treat all client-supplied movement, interaction, inventory, currency, job progress, trade state, and purchase claims as untrusted.
- Authenticate every online command and authorize it against the current account, character, region, role, and state.
- Clients may predict presentation for responsiveness; the server decides durable results.
- Validate input shape, ranges, ownership, request rate, and state transition on the server. Use idempotency keys for retryable mutations.
- Never include secrets, privileged service credentials, or authoritative economic logic in the client build.
- Use TLS for service connections and secure platform-supported local storage for refresh credentials. Avoid persisting unnecessary personal data on the device.

## 3. Unity client structure

Use explicit modules / assemblies with dependencies pointing inward to domain contracts:

- **Presentation:** UI, camera, animation, localization, and accessibility.
- **Input:** Unity Input System actions mapped to platform-friendly controls; input produces intents, not direct durable state changes.
- **World client:** region presentation, local interaction affordances, entity interpolation, and asset streaming.
- **Feature clients:** character, roles / activities, buildings, jobs, social, chat, economy, and entitlements; each calls a narrow application interface.
- **Network adapter:** transport-specific implementation behind typed request / response and event interfaces.
- **Configuration / diagnostics:** non-secret environment configuration, version compatibility, and privacy-reviewed telemetry.

Use ScriptableObjects or equivalent authored data for static presentation catalogs only. Server-owned prices, rewards, access rules, and entitlement effects must be validated by authoritative service configuration. The client should handle loading, suspended / resumed application lifecycle, reconnect, and explicit unknown-result states. A timeout after a mutation means “result unknown” until queried, not “failed” or “succeeded.”

## 4. Multiplayer, zones, and persistence

### Authority and replication

The authoritative simulation owns player position validation, interaction eligibility, role activity outcomes, world-visible state, and valuable changes. The client sends bounded intents; the server validates and emits canonical results. Use server snapshots / deltas and client interpolation for remote movement. Prediction, if added, must be limited to reversible presentation and reconciled with server state.

Define transport-independent contracts for login, zone join / leave, movement input, interaction, activity start / progress / completion, chat submission, trade, and inventory query. Version contracts and reject unsupported incompatible clients with a user-readable update path.

### Regions and instances

Represent the campus and town as authored cells / regions with stable IDs, portals or transition points, asset bundles / addressable content, and budgets. The routing layer assigns a player to an authoritative zone instance. The server validates transitions and controls visibility / relevance to limit bandwidth. Each region has spawn, occupancy, and recovery rules.

Do not assume one server process per cell or a specific player capacity. Benchmark representative devices, network conditions, server CPU / memory, and costs before selecting instance size or advertised concurrency. For early online playtests, a small number of bounded instances is preferable to a speculative global shard design.

### Reconnect and durable state

Persist critical mutations transactionally. Session reconnect restores the last confirmed durable character, inventory, and currency state; transient position may use a safe checkpoint or current zone spawn. Define periodic checkpoints for noncritical state only where loss is acceptable. On zone failure, reconnect through routing and query authoritative state before replaying a command. Deduplicate commands by account / session scope and idempotency key.

## 5. Provider-neutral service boundaries

Use domain interfaces and adapters for:

- Identity and authentication / session issuance.
- Zone allocation, presence, and matchmaking / routing.
- Persistent character and world repositories.
- Economy ledger and trade orchestration.
- Chat delivery, moderation, report case management, and rate limiting.
- Platform purchase verification and entitlement fulfillment.
- Observability, support exports, and privacy-reviewed analytics.

Each boundary should declare data ownership, authorization, retries, timeout behavior, idempotency, and failure semantics. Keep provider-specific payloads inside adapters. Avoid introducing distributed transactions across providers; use a transactional outbox / inbox or equivalent reconciliation pattern for cross-service events. External integrations must have timeouts, bounded retries, and an explicit degraded state.

## 6. Data model and persistence

Use a relational database as the system of record for durable account-linked state, subject to provider evaluation. A proposed logical model includes:

| Entity | Important data / invariant |
|---|---|
| Account | Internal ID, provider identity references, status, consent / policy state; minimal personal data |
| Character | Account owner, appearance catalog selections, role, progression, last safe region |
| Inventory | Item instance / catalog ID, quantity, ownership, location / reservation state |
| Currency account | Currency type and derived balance; no client-writable balance |
| Economy ledger | Immutable transaction ID, debit / credit entries, reason, actor / source, idempotency key, timestamp |
| Activity / job | Definition version, eligibility, server progress state, completion and reward transaction |
| Trade | Participants, offer revisions, reservations, confirmations, expiry, terminal state |
| Entitlement | Platform transaction reference, product, validation and fulfillment status, revocation / refund state |
| Building / business | Stable definition ID, access and availability configuration; player ownership is future scope |
| Safety case | Report / moderation references, restricted access, retention and deletion metadata |

Use database constraints and transactions for invariants. Currency is derived from ledger entries or maintained as a transactionally updated balance with ledger reconciliation; never silently repair discrepancies. Store timestamps consistently in UTC and use stable IDs. Version authored definitions and preserve enough version metadata to interpret existing character / activity records after content updates.

Retention, account deletion, export, backup, disaster recovery, and access controls must be defined with privacy / legal stakeholders. Avoid collecting real name, precise location, or student records unless an approved feature requires them.

## 7. Economy, inventory, and two-sided trade

### Ledger

Every currency change has a unique transaction, reason code, source, and balanced debit / credit entries. Reward and purchase handlers use idempotency keys so reconnects and retries cannot grant twice. Define legitimate sources and sinks; alert on impossible balances, duplicate sources, and reconciliation drift. Admin adjustments require authenticated, least-privilege tooling and an audit record.

### Trade state machine

Two-sided trades are a later-phase feature, not part of the first playable. The intended flow:

1. A participant proposes item and currency terms; the server checks ownership, availability, allowed item types, and bounds.
2. The server reserves offered assets and assigns an offer revision / expiry.
3. Both participants receive and explicitly confirm the same final revision.
4. Any offer edit invalidates prior confirmations.
5. At commit, the server rechecks participants, reservations, limits, and current state, then atomically transfers both sides and records ledger / inventory events.
6. Cancellation, timeout, disconnect, invalidation, or server error releases reservations exactly once or leaves the operation recoverable for reconciliation.

Use explicit states such as `Draft`, `Open`, `Confirmed`, `Committed`, `Cancelled`, `Expired`, and `NeedsReconciliation`; legal transitions must be enforced server-side. Duplicate commit requests return the original result. Clients only render authoritative status. An escrow-like reservation is not custody of real-world money; no real-money player-to-player transfer is in scope.

## 8. Character, roles, buildings, and jobs

### Character

The server stores validated catalog IDs and allowed parameter values. Catalog updates need compatibility rules for retired or replaced assets. Appearance is cosmetic state; the client resolves IDs to locally available content. Reject unknown, incompatible, or unauthorized content references.

### Roles

Role definitions specify eligibility, activities, progression, access, and reward tables. The server evaluates role requirements and role changes. Student membership should be an in-game status for MVP unless real-world verification is separately approved. Never expose verification documents or sensitive eligibility data to peers.

### Buildings and businesses

Represent each building with a stable ID, region, access rules, interaction anchors, content references, and optional operating schedule. Server logic determines whether an interaction or service is available. NPC business routines are authored schedules / state machines with bounded deterministic behavior; clients render their replicated state. Player ownership, rentals, and player-run economy are future scope and require dedicated financial / safety design.

### Jobs and activities

Job definitions are versioned server-side rules. Start requests validate role, location, cooldown, and prerequisites. Progress is driven by validated server-observed actions or a bounded activity protocol; a client timer alone is insufficient. Completion is idempotent, persisted with the reward transaction, and queryable after reconnect.

## 9. Chat, privacy, and moderation

Chat should have a separate authorization and data lifecycle from general gameplay:

- Define channel scopes (for example public, proximity, and group) and validate membership / distance server-side.
- Apply per-account and per-channel rate limits, message length limits, abuse controls, and anti-spam heuristics.
- Enforce mute / block preferences consistently for delivery and presence according to documented product behavior.
- Provide report flow with context controls, case access restrictions, escalation, and retention limits.
- Moderate supported languages (`en`, `tr-TR`, `de-DE`) with appropriate language-aware rules and operational review. Localization of UI alone does not provide moderation coverage.
- Treat user text as untrusted content; safely render it and avoid executable formatting / links unless explicitly allowed.
- Do not automatically translate player-generated text. Translation would be a separately scoped, disclosed feature with privacy review, user controls, quality handling, and moderation implications.
- Document when messages are stored, who can access them, how reports affect retention, how users block others, and how account deletion applies.

Text chat is not required for the first playable online MVP. A test that enables chat must include operational moderation and clear participant expectations; do not ship open chat without staffed or otherwise validated safety operations.

## 10. Monetization and platform purchases

Purchases are not needed for the first playable. When introduced:

- The client initiates purchase through the platform SDK and forwards an opaque transaction reference to the server.
- Server-side validation uses the appropriate platform mechanism and verifies product, environment, transaction state, and account binding.
- Fulfillment is idempotent; persist validation and entitlement grant before acknowledging success to the client.
- Handle pending transactions, duplicate notifications, restore flows, refunds, chargebacks, revocations, and delayed platform responses.
- Use platform adapters behind an entitlement interface. Do not trust a client-provided “purchase succeeded” flag.
- Keep products cosmetic or non-dominant convenience. Review platform rules, consumer disclosures, tax / regional requirements, and pay-to-win risk before release.

## 11. Localization implementation design

Use Unity Localization package concepts for locale assets and string tables:

- Configure `en`, `tr-TR`, and `de-DE` as supported locales.
- Resolve device locale to a supported locale with a visible in-game override; persist the user selection on the account or local preferences as product policy allows.
- Define fallback behavior for missing translations. Proposed fallback: English, with a development / QA warning for missing keys; confirm user-facing fallback before release.
- Localize UI strings, onboarding, errors, safety / moderation copy, activity names, item names / descriptions, and purchase disclosures. Use localized asset references for images / audio when the content differs by locale.
- Keep stable localization keys and avoid building user-facing sentences by concatenating fragments. Use locale-aware plural, date, number, and currency formatting.
- Include localization QA in build gates: missing-key scan, pseudo-localization / layout expansion review, Turkish character support, German text expansion, and device font coverage.
- Translate moderation rules and report controls consistently; player-generated content is not automatically translated or localized by this system.

## 12. Mobile performance and reliability

Set measurable budgets after selecting minimum supported devices; do not claim a universal frame rate or concurrency target without measurement. Profile release builds on representative low-, mid-, and high-tier Android / iOS devices.

Design controls include:

- URP quality tiers, sensible resolution scaling, controlled real-time lights / shadows, baked lighting where appropriate, and shader variant management.
- LODs, occlusion, GPU / CPU profiling, draw-call and material discipline, texture compression by platform, and memory-aware asset streaming.
- Region / cell loading with bounded activation and unload behavior; avoid loading every interior or cosmetic asset at once.
- Pool frequently reused effects / entities, cap transient objects, and avoid per-frame allocations in hot paths.
- Interest-managed replication, compact state updates, interpolation, bounded message rates, and graceful degradation under poor mobile networks.
- Handle app background / resume, network handover, battery / thermal pressure, and low-memory callbacks without corrupting durable state.
- Measure cold start, time-to-play, memory, frame-time percentiles, battery / thermal behavior, bandwidth, reconnect success, and server cost in realistic scenarios.

Define budgets and acceptance thresholds from a device matrix and playtest telemetry, then add automated / manual regression checks. Do not optimize against editor-only performance.

## 13. Security, operations, and observability

### Security baseline

- Server-authoritative valuable state; input validation and authorization at every command boundary.
- Short-lived sessions, secure transport, credential handling through platform-supported facilities, and least-privilege service identities.
- Rate limiting, abuse detection, replay / duplicate protection, and safe error responses that do not leak internal data.
- Secret management outside source control and client packages; rotate credentials and audit privileged actions.
- Dependency and build provenance review; signed / controlled release artifacts and environment separation.
- Threat model account takeover, cheating, economy abuse, trade scams, spam, harassment, purchase fraud, and service denial before public launch.

No system can be described as “secure” solely from this design. Security posture depends on implementation, configuration, testing, operational response, and ongoing review.

### Observability and operations

Use privacy-reviewed structured logs, metrics, and traces with correlation IDs. Monitor authentication failures, zone transitions, disconnects, command rejection rates, job payouts, ledger reconciliation, trade terminal states, moderation queue health, purchase validation, latency, crashes, and resource utilization. Avoid logging message contents, secrets, or unnecessary personal data by default.

Establish alert ownership, severity levels, incident response, maintenance / rollback procedures, backups and restore drills, and player support escalation before a public launch. Staff access to moderation and economy tools must be scoped, audited, and tested.

## 14. Delivery and validation risks

| Risk | Mitigation / evidence required |
|---|---|
| Persistent multiplayer exceeds team or operating budget | Prove a single bounded zone, reconnect, and cost model before expanding |
| Mobile world performance or memory is poor | Profile early on physical devices; constrain cells, interiors, and visual scope |
| Chat causes unmanaged harm or operational burden | Keep chat out of MVP or gate it behind a reviewed moderation operation |
| Economy duplication or trade disputes | Ledger, idempotency, reconciliation, escrow-like reservations, adversarial tests |
| Localization quality / layout defects | Translation review, missing-key checks, pseudo-localization, device QA |
| Student verification creates privacy / access barriers | Use in-game status for MVP; require separate legal and product approval for verification |
| IAP policy or refund behavior is mishandled | Defer purchases; validate through server adapter and platform-policy review |
| Scope grows beyond 5–10 buildings | Freeze the MVP content set and gate additions on measurable quality |

## 15. MVP boundary

The first playable online MVP should prove one short end-to-end loop: authenticated player enters a bounded campus zone, creates / selects a persisted modular character, chooses an in-game role, completes a simple validated activity or student job, receives an idempotent earned reward, reconnects to the same authoritative character state, and can access safety / privacy controls.

Include only the world cells, buildings, role content, and localization required to prove that loop. Exclude open chat, two-sided trading, player-owned businesses / rentals, IAP, real-world student verification, voice, and scale claims unless a later scope review explicitly approves them.
