# CAMPUS LIFE — Roadmap and First Playable MVP

## 1. Purpose and current repository context

This roadmap sequences the CAMPUS LIFE concept into evidence-gathering milestones. The repository currently contains no Unity game project or game implementation; these documents are planning artifacts only. No Unity, C#, networking, or other implementation is included here.

The roadmap assumes a small team and a provider-neutral design. Dates, staffing, cost, supported device matrix, online capacity, and launch markets have not been established; milestones are exit-criteria based rather than calendar promises. Each stage should be re-estimated after its risks and dependencies are measured.

## 2. MVP objective

Prove that a player can safely and reliably enter a compact persistent online campus, express a character and starting role, complete one short server-validated activity / job, earn a durable reward exactly once, and recover the same state after reconnect—on representative Android and iOS devices.

The MVP is a **first playable**, not a content-complete launch or commercial release. It should demonstrate the core online loop and the architecture's highest-risk boundaries without prematurely building every planned feature.

## 3. First playable scope

### Required

- Unity 6 LTS client foundation using C#, URP, and Unity Input System.
- One compact Izmir-inspired campus slice and a small connected town route. Only the buildings necessary for the loop need to be accessible; the full 5–10 building target is a release scope, not an MVP prerequisite.
- Basic touch movement, camera, interaction, loading, connection / reconnect, and accessible settings.
- Account/session flow using a selected provider adapter; use test accounts and appropriate privacy controls.
- Modular character selection with a representative starter set and durable appearance persistence.
- Student, Academic, and Business Owner / Patron roles represented in data and UX; implement only the role activity needed to validate the first loop. Avoid claiming all role content is complete.
- One short, server-validated campus activity or student part-time job with an idempotent earned-currency reward.
- Authoritative character / inventory / currency persistence using a transactional data model and audit trail for economic mutations.
- A basic region / zone boundary with server-authorized join / leave and bounded entity replication.
- English, Turkish (`tr-TR`), and German (`de-DE`) localization foundation; localized core navigation, onboarding, safety, and activity text; defined fallback and missing-key checks.
- Privacy, mute / block / report entry points and a gated / closed test social experience. Do not enable open chat until moderation operations are ready.
- Basic diagnostics and a documented playtest device / network matrix.

### Explicitly excluded from first playable

- Full 5–10 building content set (unless needed for the loop), multiple campuses, a large open world, or global scale.
- Two-sided item / currency player trading.
- Player ownership, business operations, property rentals, or rent setting.
- IAP, paid currency, real-world student verification, voice chat, unrestricted user content, and public open chat.
- Claims of capacity, uptime, anti-cheat guarantees, security certification, revenue, or retention.

## 4. Roadmap stages and exit criteria

### Stage 0 — Product and risk validation

**Focus:** align on audience, safety, language, setting, target markets, and what “persistent online” means operationally.

**Deliverables:** approved product assumptions; fictional / licensed setting decision; age-rating and privacy review plan; device matrix proposal; moderation and support operating model; choice criteria for networking, hosting, identity, and persistence vendors.

**Exit criteria:** named decision owners and validation evidence for target audience, age / market constraints, launch locale scope, student eligibility policy, and acceptable online test scope. Do not proceed to public social testing without safety ownership.

### Stage 1 — Offline interaction and mobile slice

**Focus:** prove camera, touch movement, character presentation, interaction UX, and one representative campus environment on physical devices.

**Deliverables:** greybox campus-to-town route; representative interior; character customization prototype; interaction and accessibility conventions; Unity Localization configuration and sample translated UI in all three locales; profiling baseline.

**Exit criteria:** a tester can navigate and complete a local interaction on representative Android and iOS devices; no critical control, load, or localization layout blockers remain; initial performance / memory budgets are recorded from measurement.

### Stage 2 — Online vertical slice

**Focus:** validate the largest technical risk: authoritative multiplayer in one bounded zone.

**Deliverables:** authenticated test session; authoritative zone join / movement / leave; basic replication and interest rules; reconnect and state query; structured diagnostics; service boundary and persistence prototype.

**Exit criteria:** multiple test clients can join the same bounded zone under the agreed test conditions; server-authoritative state is demonstrated; disconnect / reconnect does not invent or lose confirmed durable state; performance and cost observations are documented without extrapolating beyond evidence.

### Stage 3 — Persistent role and reward loop

**Focus:** deliver the first playable loop end-to-end.

**Deliverables:** modular character persistence; initial role selection and role data; one server-validated campus activity or student job; earned currency and ledger; a small NPC service / building interaction; idempotent reward handling; localization and safety controls in the critical flow.

**Exit criteria:** retries, app suspension, disconnect, and duplicate completion attempts do not duplicate reward; a returning player sees canonical character and balance; the loop is understandable and completable on supported test devices; no unresolved critical safety or data-integrity issue.

### Stage 4 — Closed playtest and hardening

**Focus:** test usability, reliability, content scope, and operational readiness with a controlled cohort.

**Deliverables:** playtest onboarding and consent; reporting and support process; crash / network / performance dashboards; localized content review; device and network test results; incident and rollback exercises; prioritized defect list.

**Exit criteria:** product owners accept measured performance and reliability against targets they set; moderation and support can handle the test population; no critical data-loss, economy-integrity, or safety blockers remain. Any open-chat test requires a specific approved moderation plan.

### Stage 5 — Release candidate foundations

**Focus:** expand only after the MVP loop is stable; prepare launch operations and content.

**Candidate work:** complete the 5–10 accessible launch buildings, additional role activities and jobs, more NPC routines, richer accessibility, account lifecycle / deletion flows, policy and platform reviews, disaster recovery, support tools, and scale / cost testing.

**Exit criteria:** launch scope, staffing, operating costs, age / market policies, privacy and retention, languages, service-level objectives, capacity tests, store requirements, and incident ownership are approved. This stage is not a launch commitment.

## 5. Feature sequencing by system

| System | First playable | Later / gated |
|---|---|---|
| World | One campus slice, bounded region / zone, required interiors only | Full 5–10 accessible buildings; additional regions / instances |
| Character | Curated modular starter appearance, save / reload | Broader catalog, advanced body customization, expanded wardrobe |
| Roles | Role selection / representation; one validated role loop | Complete Student / Academic / Patron progression and switching |
| Jobs | One server-validated short task and reward | Multiple jobs, schedules, employer variety, deeper progression |
| Buildings | Stable IDs, access and interaction; small number of required locations | Full launch set, richer schedules and services |
| NPC businesses | One simple server-owned service / purchase interaction if required | Routine simulation, dynamic stock, business expansion |
| Chat / safety | Safety controls and test-only gated social capability | Public / proximity / group chat after moderation readiness |
| Economy | One earned currency, narrow sinks, ledger and reconciliation | Broader economy; trade only after abuse / dispute readiness |
| Trading | None | Server-validated two-sided reserved / escrow-like atomic trade |
| Monetization | None | Optional, server-validated platform purchases after policy / fairness review |
| Localization | `en`, `tr-TR`, `de-DE` core flows and QA foundation | Complete content coverage and ongoing language operations |
| Security / ops | Auth boundaries, least privilege, basic diagnostics and audit | Mature incident response, scaling, support and recovery operations |

## 6. Dependencies and decision gates

1. **Audience / age / market decision** gates social features, data handling, purchase policy, and test cohort.
2. **Setting and rights review** gates use of specific real-world names, campus identity, signage, and cultural assets.
3. **Device matrix and art direction** gate visual budgets, asset approach, and acceptable scene density.
4. **Online proof and operating-cost evidence** gate the number of regions, expected population, and hosting design.
5. **Moderation staffing and policy** gate public chat, group features, and user-generated content.
6. **Economy integrity and support tooling** gate player trading, property, rentals, and player-run businesses.
7. **Platform / legal review** gates IAP, student verification, retention, and launch availability.
8. **Localization review capacity** gates launch content completeness in English, Turkish, and German.

Do not resolve these dependencies by assuming a specific cloud provider, player capacity, age rating, or verification vendor.

## 7. Risks and mitigation

| Risk | Early evidence / mitigation |
|---|---|
| Multiplayer scope and ongoing service cost exceed capacity | Prove one zone; measure server cost and failure behavior before adding scale |
| Realism and building count overwhelm mobile budgets | Greybox, profile on devices, constrain interior and asset scope |
| Chat safety requires more operations than available | Keep open chat out of first playable; define report, moderation, escalation, and retention before enabling |
| Duplicate rewards or lost economic state | Transactional ledger, idempotency, retry / reconnect tests, reconciliation |
| Trading creates scams, disputes, or exploit paths | Defer until atomic state machine, reservations, support, and adversarial tests exist |
| IAP becomes pay-to-win or is incorrectly fulfilled | Defer; use server validation, platform adapters, refund / revocation handling, fairness review |
| Student status collects sensitive data or excludes players | Use in-game eligibility for MVP; evaluate real-world verification separately |
| Three-language support is nominal rather than usable | Translate core flows professionally; test missing keys, Turkish glyphs, German expansion, and moderation language coverage |
| Team treats design as implemented functionality | Keep this roadmap as a plan; track implementation evidence and actual repository state separately |

## 8. Quality gates and evidence

At each stage, keep a small evidence record in the project process (not necessarily in this repository): build / device tested, test conditions, measured outcomes, known limitations, decision owner, and unresolved blockers. Suggested measurements include:

- Client: cold start, time-to-play, frame-time distribution, memory, crash-free test sessions, battery / thermal observations.
- Network: join and reconnect outcomes, latency / loss conditions, replication bandwidth, command rejection, server resource use.
- Persistence / economy: reward idempotency, ledger balance checks, restore after interruption, terminal job / trade states.
- UX / safety: tutorial completion and comprehension, report / block discoverability, moderation queue and response readiness.
- Localization: missing keys, UI clipping, language correctness, date / number formatting, accessibility / font support.

Set measurable acceptance thresholds before claiming success. A prototype passing a happy-path test does not establish production scale, anti-cheat efficacy, security assurance, or launch readiness.

## 9. Release and change control

Freeze first playable scope at the end of Stage 0 / early Stage 1. Additions must identify the user value, implementation and operations cost, safety / privacy impact, mobile impact, and what is removed or delayed. Keep technical providers swappable at service boundaries until the online vertical slice supplies evidence to select them. No production service, purchase flow, real-world verification, or broad public social feature should be enabled solely because it appears in the design.
