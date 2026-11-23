# Bullet craft: resume register, limits, and gates

Read this before rewriting any bullet. A resume line is a claim that has no
surrounding prose to qualify it. A reader has about six seconds for it, and
an interviewer will later ask the candidate to explain it for ten minutes.
Each rule below comes from one of those two readers.

## Contents
- Register
- Sentence shape (enforced by the gate script)
- The verb ceiling
- Banlist
- Metrics
- Tagline parts
- Technical proficiencies
- ATS parsing
- The four gates

---

## Register

- Past tense for prior roles (and completed deliverables). No first person
  (`I`, `my`, `we`, `our`). No articles where a line reads fine without them,
  but don't drop so many that it turns into telegraphese.
- Put the mechanism before the outcome: what was done, how it was done, then
  the number. "Rebuilt Jest and Playwright suites from ~40% to an 80%
  CI-enforced baseline" beats "Improved quality by raising coverage to 80%."
- Use concrete nouns. Name the system, the framework, the metric. "Signup
  interception logic" says something. "Data-integrity solutions" doesn't.
- One idea per bullet. When a bullet needs "and also," make two bullets or
  cut one.
- Target length is one to two rendered lines. A three-line bullet is fine
  only when it carries the resume's strongest story.

## Sentence shape (enforced by the gate script)

`check_variant.py` checks these rules on `\item` lines only, so it doesn't
flag `pdftitle` metadata or comment dividers.

- **No em-dash asides in bullets.** Use a comma, a colon, or a second
  sentence instead. (`---` and `—` are both caught.)
- **At most one semicolon per bullet.**
- **At most one participial clause per bullet.** One ", enabling X" or
  ", reducing Y" tail is the limit. Stacked `-ing` tails are the most
  recognizable AI-generated resume pattern.
- **Plain declarative sentences with finite verbs.** Each bullet opens with
  a past-tense verb, not a noun phrase or a gerund (any explicit noun-opening
  exceptions can be allowed in `NOUN_OPENING_ALLOWLIST` in `check_variant.py`).

## The verb ceiling

A bullet's verb may never be stronger than the ceiling in
`evidence-bank.md`. From weakest to strongest, the ladder is:

`contributed to` → `supported` → `built / implemented / shipped` → `owned` →
`led` → `architected / designed`

- **architected / designed** only applies to systems or components the
  candidate personally designed from scratch, as recorded in
  `evidence-bank.md`. It never applies to a broader team or company platform
  someone else designed.
- **led** only applies where the evidence bank explicitly records leadership
  of a project, workstream, or incident.
- **Parenthetical attribution** keeps a strong verb honest by stating the
  ceiling beside it: `(senior-led platform initiative)`, `(staff-led backend
  token exchange)`. It reads as senior candor, and it holds up in deep-dive
  rounds. Use it rather than weakening the verb, if the verb is true for the
  candidate's own slice.
- Under keyword pressure, verbs drift upward. The JD is not permission.

## Banlist

Never use: `spearheaded`, `leveraged`, `utilized`, `responsible for`,
`orchestrated` (unless it means literal workflow orchestration), `seamless`,
`robust`, `cutting-edge`, `passionate`, `world-class`, `synergy`,
`proven track record`, `results-driven`, `dynamic`, `innovative`,
`best-in-class`, `drove impact`, `move the needle`.

`architected` is not on the banlist. It is ceiling-gated (see above).

This is the canonical list in the skill. `check_variant.py`'s `BANLIST`
matches it, with inflections added, so edit the two together. The script
checks the summary, tagline, and bullets, and it flags `orchestrated` as a
WARN because of literal orchestration exceptions.

Don't repeat a buzzword across the tagline, the summary, and the skills
list. Each gets one appearance, or the page reads as a template with
a variable in it.

## Metrics

The resume's weight rests on its concrete numbers, and a tailoring pass must
not lose any of the base resume's metrics.

<!-- CUSTOMIZE: List your base resume's key metrics here for quick reference,
and note any optional metrics from your evidence bank that aren't on the base
resume. Note: check_variant.py automatically extracts all numbers/metrics from
your base .tex file and verifies none are dropped in the variant. -->

- Never re-round a figure. The resume, the cover letter, and LinkedIn all
  carry the same number.
- Never trade a number for a keyword. When a rewrite would lose a number,
  the rewrite loses.
- The open-gap list in the evidence bank stays open. Don't estimate into it.

## Tagline parts

The tagline sits under `\sectionhead{<Role Title>}` and has three parts
separated by `\,$\vert$\,`:
1. **A stack part**, e.g. `Full-Stack (React · TypeScript · GraphQL)` or
   `Frontend (React · TypeScript)` or `Backend & APIs (Go · PostgreSQL · Kafka)`
2. **Two posting-matched parts** chosen from the approved list below.

<!-- CUSTOMIZE: Update the craft and domain parts below to match your
discipline and edit TAGLINE_PARTS in scripts/check_variant.py to match. -->

**Craft parts** (prefer these):
- AI-Assisted Development
- Test Automation & Quality (or `Test Automation & CI/CD` when the posting
  stresses CI)
- Web Performance & Accessibility (or `Web Performance & Reliability`,
  `Web Performance`, `Web Performance & Architecture`)
- End-to-End Product Features
- Frontend Platform & DX
- Product Experimentation (or `A/B Experimentation & Funnels` for a growth
  or funnel req)
- Observability & Reliability
- Code Review & Mentorship
- API & Service Development
- Accessibility & UI Quality
- Feature-Flag Rollouts
- Growth & Experimentation
- Frontend Platform
- Onboarding & Multi-Step Forms
- Distributed Systems & Scalability
- Cloud Infrastructure & DevOps
- Data Pipelines & Analytics

`check_variant.py`'s `TAGLINE_PARTS` matches this list; edit the two
together.

**Domain parts** (at most one, only when the posting is that team):
- Payments Product Engineering

Use the listed form rather than a near-duplicate. A part in the posting's
own words is fine when it's true and fits the line: propose it in the change
set, and add it here and to `TAGLINE_PARTS` once approved. A JD domain no
true part covers is a coverage gap to report, not a reason to invent a part.

## Technical proficiencies

- Contents come only from the evidence bank's verified stack surface ("Stack
  and years"): the base resume's items, plus any verified skills-list-only
  entries recorded in the bank. Within that surface, re-order rows and items
  toward the JD, swap one item for another to hold the page, and relabel a
  row. A technology outside the surface goes to the user as a base-resume
  change.
- Every row still has to fit its line. A row that starts wrapping costs page
  1 a line.
- Keep the taxonomy right. TypeScript and Java are languages. Node.js is a
  runtime. React and Angular are frameworks or libraries. GraphQL is a query
  language. DynamoDB and PostgreSQL are databases.

## ATS parsing

- Keywords count only if they show up in `pdftotext` output. A keyword in a
  graphic, a ligature-broken word, or a mis-ordered column does nothing.
- Use the JD's exact spelling for real keywords (e.g. `React.js` vs
  `React`) when both are honest. Parsers are literal.
- Keep section names standard: `Education`, `Technical Proficiencies`,
  `Professional Experience`. The summary sits under the title block with no
  heading of its own.
- Tech names must not hyphenate across line breaks (`Play-wright` extracts
  as two fragments). The base preamble's `\hyphenation{...}` list covers
  the current names; extend it when a variant adds one.
- Every keyword has to live in a true line. The summary and tagline are
  where a real keyword lands without distorting a bullet.

## The four gates

A variant ships only after passing all four. Gates 3 and 4 are mechanical,
and `check_variant.py` runs them (the page-1 check is a WARN heuristic, so
look at the page break when it fires). It also backs up gate 1 with lists
taken from the evidence bank (`SKILLS_ONLY`, `OFF_SURFACE`, `DO_NOT_WRITE`,
and custom scope regexes). Gates 1 and 2 are judgment, applied during
drafting: once each, while the change set is built.

1. **Scope gate.** Every verb sits at or under its ceiling. Every
   parenthetical attribution the base carries survives.
2. **Evidence gate.** Every claim traces to a line in the evidence bank.
   Every base metric is still present, unrounded.
3. **Shape gate.** Sentence-shape rules and banlist pass on all `\item`
   lines.
4. **Render gate.** Within the page limit (default 2 pages). The sub-heading
   is one line. Page 1 ends on a whole bullet. The JD's top keywords are
   present in the extracted text.
