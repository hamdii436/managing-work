# CAMPUS LIFE — Game Design Document

## 1. Product summary

**CAMPUS LIFE** is a realistic, social 3D university and coastal-town life simulation for Android and iOS. Players create a character, choose a life path, attend university activities, work, visit local businesses, and socialize in a persistent shared world inspired by Izmir's Aegean coastal atmosphere.

The intended first release centers on one compact seaside campus and a town containing 5–10 accessible buildings. The experience favors readable routines, player expression, and safe social play over combat, competitive advantage, or a large map. The target technology is Unity 6 LTS, C#, URP, and the Unity Input System. These are product constraints and architectural targets, not evidence that a Unity project or implementation already exists in this repository.

### Product pillars

1. **A welcoming campus routine:** classes, campus activities, work, errands, and downtime fit into short mobile sessions.
2. **A place worth inhabiting:** the campus and nearby town feel coherent, lived-in, and distinctly coastal without requiring a sprawling world.
3. **Social play with boundaries:** players can meet and cooperate while having usable privacy, blocking, reporting, and moderation controls.
4. **Fair, trustworthy progression:** earned currency and server-validated trades support customization and convenience, never paid competitive power.
5. **Mobile-first quality:** stable performance, clear touch controls, efficient networking, and reliable state recovery take precedence over map scale.

## 2. Audience, platforms, and session shape

- **Platforms:** Android and iOS phones and tablets; touch is the primary input. Controller support is optional and should not compromise touch usability.
- **Audience:** players seeking a low-pressure social simulation, including students and young adults. Age rating, privacy obligations, and required parental controls must be determined for target markets before release.
- **Session design:** activities should have useful outcomes in brief sessions, with longer optional social and role-play sessions. No essential progression should require uninterrupted long sessions.
- **Online requirement:** the shared persistent experience requires a network connection. The client must clearly communicate connection and recovery states; it must not pretend an unconfirmed online action succeeded.
- **Languages:** English (`en`), Turkish (`tr-TR`), and German (`de-DE`) are required in-game languages. Use Unity Localization for UI strings and supported localized assets, with an explicit locale fallback policy. Player-generated text is not automatically translated by this requirement.

## 3. World and setting

### Launch world

The initial playable area is one compact Izmir-inspired university campus connected to a small coastal town. It should communicate local character through environmental art, signs, architecture, food, sound, and routine, without claiming to reproduce a specific real institution or neighborhood unless separately licensed and approved.

The town contains 5–10 accessible buildings. Each building should have a clear purpose and a bounded, performant interior. A launch candidate set is:

- University buildings: teaching / student commons and administration or library.
- Town services: cafe, small grocery or market, and a health or public-service location.
- Work and leisure: one additional employer / workshop and one social or recreation venue.
- Remaining slots can be deferred or used for another high-value service, subject to scope and performance validation.

The exact count, interiors, opening hours, and launch building set are production decisions to validate against content capacity. Buildings outside the accessible set can be represented as non-enterable scenery and should not imply unavailable gameplay.

### World structure

Organize the environment into authored regions or cells with explicit boundaries, spawn points, visibility rules, and streaming budgets. The campus and town may share a seamless-feeling map, but the service may place players into authoritative zone instances based on location and capacity policy. Moving between regions is a server-recognized transition: the client requests it, and the server validates and confirms it.

The MVP should use only the cells needed for the campus route and a small town slice. Region streaming and zone instances are foundations for performance and operations, not a promise of an unlimited seamless world. Target device memory, loading time, zone population, and operating cost need measurement before capacity is advertised.

## 4. Player experience and loop

### Core loop

1. Enter the world and choose a destination or activity.
2. Participate in a class, campus activity, role task, part-time job, or local business interaction.
3. Earn an approved reward or social / collection progress.
4. Spend earned currency on cosmetic items, food, services, or other clearly described non-power rewards.
5. Meet other players, customize the character, and plan the next activity.

Every loop should have a clear start, expected duration, reward, and exit or interruption path. Network loss, disconnect, or application suspension must not duplicate a reward or leave a trade in an ambiguous state.

### First-session goals

- Understand movement, interaction, settings, and basic safety controls.
- Create or choose a character appearance and select a starting role.
- Reach the campus hub and complete one short, understandable activity.
- Learn how to find a job / service or a public social area.
- Find blocking, reporting, and chat controls without having to leave the current context.

The first-session funnel and tutorial length are hypotheses to test with players, not fixed targets.

## 5. Roles and progression

Players select a starting life path. Roles grant access to themed activities and progression, not exclusive ownership of essential services or combat-like power.

### Student

- Attends class and campus events, undertakes student part-time jobs, and progresses through campus-related activities.
- Eligibility for the university student group must be explicitly defined. The recommended launch approach is a game-earned student status tied to the Student role, with any real-world verification deferred until its privacy, accessibility, abuse, and support costs are approved.
- Student-only spaces and groups should have clear rules and age-appropriate safety controls.

### Academic

- Participates in university-flavored activities such as teaching, research-themed tasks, and scheduled campus events.
- In the MVP, this should be a role experience and NPC-supported activity, not a claim of real academic credentials or authority.

### Business Owner / Patron

- Patron activities are a launch-friendly way to visit and support NPC-run businesses.
- Player ownership, hiring, inventory management, rent setting, and player-operated storefronts are future features. They require economy sinks, dispute handling, moderation policies, anti-collusion controls, and an operations plan before implementation.
- Do not market the launch role as actual ownership if it only provides patron or business-themed activities.

### Progression

Use character level / general progression and role-specific reputation or milestones only where they produce understandable, bounded rewards. Avoid irreversible role selection in the MVP; provide a documented switch or respec policy before launch. Rewards should be cosmetic, expressive, or activity-unlocking and must not create pay-to-win advantages.

## 6. Character creation and customization

Character creation should support a welcoming range of appearances and styles. Build modular customization from curated, compatible options: body / face presets or supported sliders, hair, skin tone, clothing, accessories, and color variants. Avoid implying medical, biometric, or identity verification from appearance.

- Provide a usable default character and allow later edits.
- Validate combinations against rig, clipping, animation, and device-memory constraints.
- Store durable selections as server-owned catalog identifiers and validated parameters, not arbitrary client paths or assets.
- Separate gameplay-relevant identity / account data from visible appearance where practical.
- Use clear previews and localized labels; do not make customization availability dependent on paid purchases.
- MVP scope: a small but representative starter set, one safe edit flow, and persistence across sessions. A full wardrobe, detailed body morphs, and user-authored assets are later work.

## 7. Activities, jobs, and businesses

### Campus activities

Short, repeatable, server-validated activities can include class attendance, campus errands, events, and social gathering. MVP activities should be simple enough to complete and reward consistently under disconnects and retries.

### Student part-time jobs

Jobs provide structured activities and an earned-currency source. The first playable should include one or two bounded job loops (for example, a short service or campus task) with a clear employer, objective, time / completion rule, and reward. The server validates prerequisites, progress, completion, and payout. Avoid relying on client timers or client-reported completion as proof.

### NPC businesses and buildings

NPC businesses can provide goods, services, and atmosphere with server-owned prices and stock / availability rules. Buildings have stable IDs, access policies, interaction points, and content definitions. For launch, properties are world locations, not player-owned assets.

Future systems may add routine schedules, dynamic stock, rentals, and player-owned businesses. These require explicit offline behavior, economic balancing, moderation and fraud handling, and safe fallbacks when a business owner is absent.

## 8. Social systems and safety

The social experience should default to public, bounded interactions and provide agency:

- Public / proximity / group chat scope must be visible and easy to change.
- Include mute, block, report, and privacy controls; blocking should suppress contact and applicable visibility / interaction according to a documented policy.
- Apply server-side rate limits, spam controls, and moderation workflows. Client filtering alone is insufficient.
- Define retention, access, escalation, and deletion policies for reports and chat data before production.
- Do not expose sensitive account or verification information through presence, profiles, or chat.
- The game supports English, Turkish, and German UI. Moderation must account for the language of submitted text; translated UI does not mean text is translated or adequately moderated in every language. Machine translation, if later added, needs privacy review, quality disclosure, and a clear opt-in / fallback policy.
- Chat and user-generated content are not MVP launch blockers for the first online playable unless specifically needed for testing. If included in a test, keep it gated, moderated, and limited to an approved audience.

## 9. Economy, trading, and monetization

### Currency and rewards

Use a small, understandable set of currencies. The MVP should have one earned soft currency and a deliberately narrow set of sinks. All balances, rewards, prices, and transfers are authoritative server state. Economy changes need an audit trail and reconciliation path.

### Player trading

Two-sided item / currency trading is a requested system direction, but is not necessary for the first playable. When implemented, it must use server-validated offers and an escrow-like atomic trade flow: both parties review the same final terms, both confirm, the server revalidates inventory / balances, and the server commits once or releases the reservation. Expiration, cancellation, disconnect, retries, and duplicate requests must have deterministic outcomes. Never transfer items based on a client animation or message.

### Monetization

Optional IAP may support cosmetic items or clearly bounded convenience that does not confer competitive or progression dominance. No loot-box-like randomized paid rewards are assumed. Purchases must be verified server-side with the relevant platform receipt / transaction validation, idempotent fulfillment, refund / revocation handling, and clear price disclosure. Keep earned and paid entitlements distinguishable for support and audit.

Paid currency must not be required for essential roles, safety features, core activities, or reasonable progression. Any convenience item needs a pay-to-win review and platform-policy review before release.

## 10. Accessibility, localization, and UX

- Support touch-safe targets, readable text scaling, clear interaction feedback, audio / visual options, and reduced-motion considerations where feasible.
- Provide remappable or configurable touch layouts only if they can be tested across supported aspect ratios and accessibility needs.
- Use Unity Localization for UI string tables, locale selection, localized asset references, and a defined fallback (English is the proposed development fallback; final behavior must be confirmed).
- Ship `en`, `tr-TR`, and `de-DE` locale data with professional review of high-value flows, safety, purchase, and error messages. Do not rely solely on machine translation for launch-critical language.
- Keep date, time, number, and currency formatting locale-aware while retaining canonical server values.
- Apply language-aware safety review to localized UI and any supported player-generated content moderation. Player text is not automatically translated.

## 11. Product assumptions and validation

The following are assumptions, not established facts:

- Izmir-inspired fictional setting is appropriate and does not require specific real-world institutional / location permissions.
- Initial audience and age rating permit the planned social features under target-market rules.
- A persistent online world is economically and operationally viable for the intended team.
- One campus and 5–10 accessible buildings can meet the desired variety within the art, QA, localization, and performance budgets.
- The first launch can defer player-owned businesses and open player trading without undermining the core loop.
- The Student role can be represented through in-game eligibility rather than external verification.
- English fallback and the exact behavior when a locale is incomplete are acceptable.

Validate these through market / legal review, player research, device profiling, moderation operations planning, and a representative online prototype. Do not state population, uptime, security, retention, or monetization outcomes as guaranteed until measured.

## 12. Out of scope for first playable

Global multi-region scale, a large open world, real university accreditation, player-owned businesses or rentals, unrestricted user-generated assets, complex academic simulation, large-scale live events, guild systems, voice chat, real-money player trading, and broad paid progression are not part of the first playable. Revisit only after core safety, performance, service operation, and economy foundations are validated.
