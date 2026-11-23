<!--
  An index of applications already built, so a new req can start from the
  closest sibling instead of from the base resume alone.
  If mirrored across resume-tailor/references/ and cover-letter-generator/references/,
  confirm both copies match with:
    python3 resume-tailor/scripts/check_variant.py --mirror ~/.claude/skills
-->

# Recent applications: prior materials to reuse

An index of applications already built, so a new req can start from the
closest sibling instead of from the base alone. Each entry points to the
tracker row (if you use Notion/Airtable/etc.) and the local folder under
`~/Documents/resumes/` (the files actually sent). Unapplied variants sit in
`toApply/<Company>/`, and move up to `<Company>/` once applied.

**The files are the source of truth, not this index.** Variants get revised
after this was written. Open the `.tex` before reusing a line. The evidence
bank still sets the ceiling on every claim. A sent variant is proof that
wording was approved for *that* posting, not that it's true at a looser
reading. Check any reused line against the current evidence bank;
`check_variant.py` fails retired forms in `DO_NOT_WRITE`.

**To find a sibling, read the two tables below and then only that
company's entry (grep its heading); don't read the whole file.**

**When to use this:**
- Step 3 of `resume-tailor` ("read prior variants"): pick siblings from the
  role-type table below instead of scanning every folder.
- Before conceding a gap: see whether the same gap already came up and how
  the user decided to handle it.

**Entry template.** Keep an entry to about six short lines:

    ### <Company>: <posting title> (<domain>; <anything unusual about location>)
    - **Folder / status:** `<Company>/`; tracker <URL> (<status>); letter or none
    - **Title note:** only when choosing between titles or parts, and why
    - **Thesis:** one sentence, plus any summary change
    - **Order and rewrites:** bullet order; rewrites (reused or new); skills-row moves
    - **Not adopted:** JD language left out because it would overclaim
    - **Gaps:** coverage gaps, and any gap decision made

Bullet abbreviations used in "Order" (customize to match your base resume's
bold bullet prefixes):
`Pay` (Enterprise Payments), `Perf` (Web Performance & Architecture),
`Back` (Backend Services), `Growth` (Growth & Experimentation),
`Std` (Engineering Standards), `Auth` (Authentication),
`Obs` (Observability & On-Call), `AI` (AI & Automation),
`Data` (Data Integrity).

## Find the closest sibling by role type

| Role type | Closest prior applications |
|---|---|
| Senior full-stack, product teams | *(Add companies as you apply, e.g. Acme Corp, ExampleApp)* |
| Senior frontend, product surface | *(Add companies as you apply)* |
| Mid-level (SWE II/III, no "Senior" in the title) | *(Add companies as you apply)* |
| Frontend platform / DX / CI / tooling | *(Add companies as you apply)* |
| Backend-leaning / services | *(Add companies as you apply)* |
| Growth / experimentation / activation | *(Add companies as you apply)* |
| AI / LLM workflows | *(Add companies as you apply)* |

## Title and sub-heading choices already made

| Company | `\sectionhead` title | Sub-heading |
|---|---|---|
| ExampleCorp | Senior Full-Stack Software Engineer | Full-Stack (React · TypeScript · GraphQL) \| End-to-End Product Features \| Web Performance & Reliability |

---

## Application entries (newest first)

### ExampleCorp: Senior Full-Stack Software Engineer (B2B SaaS; Remote)
- **Folder / status:** `ExampleCorp/`; applied
- **Thesis:** Lead with end-to-end product ownership and GraphQL/Java backend depth alongside React performance.
- **Order and rewrites:** Pay, Growth, Back, Perf, AI, Std, Data, Auth, Obs; kept base bullets intact.
- **Not adopted:** "Distributed systems architecture" (kept scope to the preference microservice and MFEs).
- **Gaps:** Kubernetes (listed Docker & AWS ECS; recorded Kubernetes as `# gap: Kubernetes`).
