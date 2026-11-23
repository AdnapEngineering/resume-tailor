<!--
CUSTOMIZE THIS FILE WITH YOUR OWN VERIFIED CLAIMS AND SCOPE CEILINGS.
If you also use a cover-letter skill, you can mirror this file in both skills
and verify they stay in sync with:
  python3 resume-tailor/scripts/check_variant.py --mirror ~/.claude/skills
-->
# Evidence bank — verified claims and their locked attribution

Every factual sentence in a resume variant (or cover letter) comes from this
file. If a claim isn't here, it doesn't go in the document. This exists
because the failure mode under drafting pressure is upgrading language —
"contributed to" becomes "built," "the frontend of X" becomes "X" — and a
hiring manager who probes a resume's claims in a screen will find the gap.

## Contents
- [How to use this](#how-to-use-this)
- [Company A — Role / Team](#company-a--role--team)
- [Company B — Earlier Role](#company-b--earlier-role)
- [Stack and years](#stack-and-years)
- [Company / industry exclusions](#company--industry-exclusions)
- [Open metric gaps — never fill these](#open-metric-gaps--never-fill-these)
- [Angles: one fact, several true framings](#angles-one-fact-several-true-framings)
- [Requirement → evidence map](#requirement--evidence-map)

---

## How to use this

Each entry gives the **claim**, the **attribution ceiling** (the strongest
honest phrasing), and where relevant a **do not write** line showing the
overreach to avoid. Rephrase freely for clarity — but never past the ceiling.
Quoted phrasings are ceilings.

**Dates & Titles:**
- **[Company A]:** `[MM/YYYY - MM/YYYY]`, `[Official Title(s)]`.
- **[Company B]:** `[MM/YYYY - MM/YYYY]`, `[Official Title(s)]`.

---

## Company A — Role / Team

**Project 1: [e.g. Checkout Redesign & Conversion Lift]**
- **Claim:** Shipped the checkout redesign that lifted cart-to-paid conversion
  by 18% across 200,000+ monthly active users, measured via end-to-end
  LaunchDarkly A/B testing and product analytics cohort analysis.
- **Ceiling:** The 18% lift attaches to **the checkout redesign only**, not
  to top-of-funnel signup or pricing, and not to the funnel in general. Treat
  18% as a **relative lift** with no recorded baseline.
- **Do not write:** "grew conversion 18% across the platform," "18 percentage
  points," or "from X% to Y%."

**Project 2: [e.g. Enterprise Platform / Cross-Functional Product]**
- **Claim:** Led frontend for a multi-tenant enterprise billing platform
  ($25M+ ARR) from zero through MVP and GA on an 8-engineer team, owning the
  customer admin portal (React, TypeScript) and internal operations dashboard.
  Authored frontend design docs, defined API contracts with backend engineers,
  and reviewed code for 3 frontend engineers.
- **Ceiling:** "Led frontend" is the ceiling — never "managed" or "led a team
  of 8 engineers." Keep the ARR figure in a parenthetical or separate clause
  so it reads as product scale, not revenue personally closed. Do not use
  internal codenames (e.g. `ProjectTitan`).
- **Do not write:** "Led a team of 8 engineers," "Architected the enterprise
  billing platform," or the internal codename `ProjectTitan`.

**Project 3: [e.g. Backend Service Re-Architecture & Migration]**
- **Claim:** Designed and solo-built a configurable notification-routing
  service (Go, GraphQL and REST, PostgreSQL) replacing a legacy hardcoded
  rules engine; backfilled from MySQL with a zero-downtime staged cutover,
  turning ~5 weekly deploy-bound support tickets into 5-minute self-serve
  config changes.
- **Ceiling:** Solo-owned from design doc through cutover. Do not claim the
  broader database migration or unrelated microservices.
- **Do not write:** "endpoints on PostgreSQL" (PostgreSQL was the storage
  layer behind the Go service).

**Project 4: [e.g. Web Performance & Frontend Architecture]**
- **Claim:** Cut p95 Largest Contentful Paint (LCP) by 1.4s into Google's
  "good" range (Datadog RUM) via bundle splitting, route-level lazy loading,
  and GraphQL query batching. Built 2 domain micro-frontends `(staff-led
  platform initiative)` and upgraded shared UI packages across major React
  versions.
- **Ceiling:** Architected 2 domain micro-frontends; a staff engineer led the
  broader MFE platform initiative. Keep `(staff-led platform initiative)`
  whenever the MFE build is claimed. The p95 LCP baseline is recalled, not
  recorded, so never write "from X.Xs to Y.Ys".
- **Do not write:** "Architected the micro-frontend platform," "Led the
  micro-frontend migration," or "cut LCP from 3.8s to 2.4s."

---

## Company B — Earlier Role

**Project 5: [e.g. Full-Stack Product Engineering / Earlier Role]**
- **Claim:** Architected and deployed 3 customer-facing web applications
  (including a B2B client portal on a TypeScript, Node.js/Express REST API and
  PostgreSQL) as sole technical owner from CI/CD setup through production
  handoff. Grew organic traffic by ~40% and reached 95+ Lighthouse performance
  and accessibility scores.
- **Ceiling:** Sole technical owner for 3 client applications. This is the
  only production Node.js backend experience if Company A used Go.

---

## Stack and years

<!-- CUSTOMIZE: Categorize every technology into one of three tiers:
1. Verified production surface (can appear in summary, bullets, and skills table)
2. Skills-list-only (light exposure, scripting, or personal projects — listed in
   SKILLS_ONLY in check_variant.py so they never creep into work bullets)
3. Off-surface (technologies you have NOT used — listed in OFF_SURFACE in
   check_variant.py so the gate fails if an LLM hallucinates them onto your resume)
-->

**Total experience:** `[X]` years total (`[Y]` years at Company A, `[Z]` years
at Company B).

### 1. Verified production stack (bullets, summary, and skills table)
- **Languages:** TypeScript (`[X]` yrs), JavaScript (`[X]` yrs), HTML5/CSS3 (`[X]` yrs), Go (`~1` yr part-time within Company A tenure — never attach total Company A years to Go), SQL (PostgreSQL, MySQL, Athena).
- **Frontend:** React, Next.js, Apollo Client, responsive layout, lazy loading, WCAG & ARIA accessibility.
- **Backend & Data:** GraphQL (schema design & resolvers), REST APIs, Node.js/Express (Company B only), PostgreSQL, MySQL, DynamoDB, AWS (Lambda, ECS, EC2, S3, Athena).
- **Testing & Observability:** Jest, Playwright, React Testing Library, GitLab CI, LaunchDarkly, Mixpanel, Segment, Datadog (RUM, tracing, dashboards), Splunk, PagerDuty.
- **AI & Tooling:** Claude Code, GitHub Copilot, MCP tooling, agent skill authoring.

### 2. Skills-list-only (`SKILLS_ONLY` in `check_variant.py` — never in bullets or summary)
- `Python (scripting)` — always include `(scripting)` qualifier
- `Cypress`, `Storybook`, `Docker`, `GitHub Actions`, `Astro`, `Tailwind`, `design tokens`, `SCSS`, `Git`, `Jira`, `Confluence`, `Linux`, `Kafka (personal projects)`

### 3. Off-surface (`OFF_SURFACE` in `check_variant.py` — never anywhere on the page)
- `Vite`, `Vitest`, `Redux`, `Kubernetes`, `React Native`, `Flutter`, `Golang`, `NestJS`, `Spring Boot`, `Sentry`, `TanStack`, `Zustand`, `Turborepo`, `esbuild`, `Rollup`, `NVDA`, `JAWS`, `Section 508`, `VPAT`, `WCAG 2.x` (no formal conformance level claimed), `MUI`, `Material UI`, `Shopify`, `Relay`.

---

## Company / industry exclusions

<!-- CUSTOMIZE: Note any companies or industries you skip in step 2 of the workflow,
or write "None." -->
- Default: flag and confirm before building variants for excluded companies
  unless the posting comes directly from the user's pre-approved job
  prospects list.

---

## Open metric gaps — never fill these

Flag them to the user instead of estimating. A resume is a document the
candidate will be asked to defend out loud.

- Exact row count backfilled in the preference-service migration
- Baseline percentage for the 12% onboarding conversion lift
- Exact before/after seconds for the >1s p75 LCP improvement
- Measured MTTR reduction from runbooks/observability (if only a design target exists, keep `"designed for"`)
- Any formal WCAG conformance level (e.g. AA/AAA) if no formal compliance audit was run

---

## Angles: one fact, several true framings

Pick the framing the posting values (step 5). Each angle stays inside the
item's ceiling; none adds a fact.

| Item | Angle → what leads |
|---|---|
| Checkout redesign (18% lift) | **Growth/conversion** → the 18% conversion lift. **Experimentation** → shipped behind a LaunchDarkly A/B test + Mixpanel cohort analysis. **Scale** → 200,000+ monthly active users. |
| Notification-routing service | **Ownership** → designed and solo-built end to end. **Backend/API** → Go, GraphQL and REST endpoints, PostgreSQL data model. **Migration/reliability** → MySQL backfill, staged cutover, zero downtime. **Ops impact** → ~5 weekly deploy-bound tickets → 5-minute config changes. |
| Enterprise billing platform | **Product scope** → led frontend from zero through MVP and GA. **Business scale** → $25M+ ARR. **Technical leadership** → authored frontend design docs, defined API contracts, reviewed 3 frontend engineers. |

---

## Requirement → evidence map

Fast lookup when mapping a JD's bullets to verified material.

| JD asks for | Reach for |
|---|---|
| Growth, activation, funnel, checkout, PLG | 18% cart-to-paid conversion lift; LaunchDarkly A/B testing & Mixpanel analysis |
| Experimentation, A/B testing, product analytics | Checkout A/B test; Mixpanel funnel instrumentation and Segment events |
| Performance, Core Web Vitals | p95 LCP cut by 1.4s into Google's "good" range (Datadog RUM) with mechanism named |
| Micro-frontends, large frontend codebases | Built 2 React MFEs `(staff-led platform initiative)` + major React version upgrades |
| Backend / API design, microservices | Solo-built Go, GraphQL, REST, and PostgreSQL notification-routing service with zero-downtime MySQL cutover |
| Testing, quality standards, CI/CD | Raised test coverage from ~40% to a CI-enforced 80% baseline (Jest, RTL, Playwright) |
| Accessibility (a11y), WCAG | Team accessibility practice: ARIA semantics, VoiceOver, keyboard nav, axe/Lighthouse audits |
| Observability, on-call, incident response | Datadog RUM/tracing/dashboards, PagerDuty alerts, P0 runbooks, primary on-call, root-cause reviews |
| AI-assisted development, developer productivity | Authored agent skills for Claude Code adopted team-wide (cut ~2-hour alert triage to 10–15 minutes); repo guardrails |
