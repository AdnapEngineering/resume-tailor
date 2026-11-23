# How to Customize `resume-tailor`

This skill is built around one principle: **an AI should re-order and re-point your real experience toward a job posting, never upgrade your scope, stuff keywords, or drop concrete metrics.**

To make that work reliably, the skill separates **tailoring mechanics** (how bullets are shaped, how LaTeX is compiled, how ATS text layers are checked) from **your personal ground truth** (your base `.tex` resume, your evidence bank, and your scope boundaries).

Follow the 5 steps below to customize the skill for your own background.

---

## Customization Checklist

| Step | File to Edit | What You're Customizing |
| :--- | :--- | :--- |
| **1. Base Resume** | `~/Documents/resumes/<First_Last>_Resume.tex` | Your canonical LaTeX resume (copied from `templates/Candidate_Name_Resume.tex`). |
| **2. Evidence Bank** | `resume-tailor/references/evidence-bank.md` | Every verified claim, metric, attribution ceiling, and 3-tier technology stack surface. |
| **3. Mechanical Gate** | `resume-tailor/scripts/check_variant.py` | The `CANDIDATE CUSTOMIZATION SECTION` at the top of the script (`SKILLS_ONLY`, `OFF_SURFACE`, `DO_NOT_WRITE`, `CUSTOM_SCOPE_FAILS`, `TAGLINE_PARTS`). |
| **4. Craft & Taglines** | `resume-tailor/references/bullet-craft.md` | Your approved tagline parts, key metrics list, and writing register. |
| **5. Skill Paths & History** | `resume-tailor/SKILL.md` & `references/recent-applications.md` | Your resume filename/path in `SKILL.md` and your role-type table in `recent-applications.md`. |

---

## Step 1: Set Up Your Canonical Base Resume (`.tex`)

The gate script (`check_variant.py`) parses your LaTeX resume using a few specific structural macros so it can isolate the title block, verify the centered tagline doesn't wrap onto two lines, extract your summary and skills table, and check every `\item` bullet.

1. Create your resumes folder and copy the included template:
   ```bash
   mkdir -p ~/Documents/resumes/toApply
   cp templates/Candidate_Name_Resume.tex ~/Documents/resumes/Your_Name_Resume.tex
   ```
2. Edit `~/Documents/resumes/Your_Name_Resume.tex` with your own contact details, summary, technical proficiencies, work history, and education.
3. **Keep these structural conventions intact** (or update the regexes in `check_variant.py` if you use a custom `.cls`):
   - **Title & Tagline:** The first `\sectionhead{...}` holds your target role title, immediately followed by a `\begingroup\centering ... {\normalsize\bfseries <Part 1> \,$\vert$\, <Part 2> \,$\vert$\, <Part 3>}\par \endgroup` block.
   - **Summary:** Sits directly between the tagline's `\endgroup` and the next `\sectionhead{Technical Proficiencies}`.
   - **Skills Table:** Uses a `tabularx` environment (`\begin{tabularx} ... \end{tabularx}`).
   - **ASCII Hyphens in Dates:** Write date ranges in `\roleline` with a single ASCII hyphen (`08/2023 - 06/2026`), **not** `--` (which renders as a Unicode en-dash that Workday and several ATS parsers drop when splitting start/end dates).
   - **Hyphenation List:** Add any multi-syllable technologies in your stack to `\hyphenation{...}` in the preamble so LaTeX never hyphenates a keyword across a line break (e.g. `Play-wright` or `Post-greSQL`).

---

## Step 2: Populate `resume-tailor/references/evidence-bank.md`

Under drafting pressure, LLMs naturally upgrade language—"contributed to" becomes "architected", "built the frontend for X" becomes "built X", and partial exposure becomes deep production ownership. `evidence-bank.md` stops this.

Open `resume-tailor/references/evidence-bank.md` and replace the example sections with your own history:

### A. Projects, Claims, and Attribution Ceilings
For every project or bullet on your resume (plus extra stories that didn't fit on the base resume), record:
- **Claim:** What you actually did, with exact metrics and tools.
- **Ceiling:** The strongest honest verb and scope boundary. If a project was part of a larger effort led by a staff/principal engineer, specify the parenthetical attribution the resume must keep—for example: `(senior-led platform initiative)` or `(staff-led backend design)`.
- **Do not write:** Specific overreaches or internal company codenames that must never appear.

### B. Three-Tier Stack Surface (`Stack and years`)
Divide your technical and domain keywords into three explicit tiers:
1. **Verified production stack:** Tools you have used in production and can discuss for 10 minutes in a technical screen. Allowed in the tagline, summary, work bullets, and skills table.
2. **Skills-list-only (`SKILLS_ONLY`):** Tools where you have light exposure, scripting-only use, or personal-project experience. Allowed **only** in the Technical Proficiencies table (with an honest qualifier like `Python (scripting)` or `Kafka (personal projects)` if appropriate), never in a work-experience bullet or the summary.
3. **Off-surface (`OFF_SURFACE`):** Common tools in your target job postings that you have **never** used. Listing them explicitly ensures the AI treats them as coverage gaps (`# gap: <keyword>`) instead of hallucinating them onto your resume.

### C. Open Metric Gaps & Requirement → Evidence Map
- **Open metric gaps:** List numbers you *don't* have (e.g. an unrecorded baseline percentage, an unmeasured MTTR) so the AI knows never to estimate them.
- **Requirement → evidence map:** A quick lookup table mapping common JD phrases (`Growth / activation`, `API design`, `CI/CD & testing`, `Observability`) to your specific stories.

---

## Step 3: Configure the Mechanical Gate (`resume-tailor/scripts/check_variant.py`)

Open `resume-tailor/scripts/check_variant.py` and edit the **`CANDIDATE CUSTOMIZATION SECTION`** at the top of the file (lines 34–138) so the script mechanically enforces your `evidence-bank.md`:

### 1. `MAX_PAGES`
Set `MAX_PAGES = 2` (or `1` if you maintain a strict one-page resume). You can also override this per run with `--max-pages`.

### 2. `SKILLS_ONLY`
Update the regex alternation with your Tier-2 skills from `evidence-bank.md`:
```python
SKILLS_ONLY = re.compile(
    r"\b(Python|Cypress|Storybook|Docker|GitHub Actions|Kafka)\b",
    re.I,
)
```
If any of these appear inside a `\item` bullet or the summary paragraph, `check_variant.py` will exit with `[FAIL] scope: skills-only term(s) in a bullet or the summary`.

### 3. `OFF_SURFACE`
Update the regex alternation with your Tier-3 (unverified / zero-experience) technologies:
```python
OFF_SURFACE = re.compile(
    r"\b(Kubernetes|Golang|Spring Boot|React Native|Flutter|Redux)\b",
    re.I,
)
```
If any of these appear *anywhere* in the document (including the skills table), the gate fails immediately.

### 4. `DO_NOT_WRITE`
Add tuples of `(regex_pattern, explanation)` for internal project codenames, retired phrasings from older resume drafts, or scope overreaches you never want to claim:
```python
DO_NOT_WRITE = [
    (r"\bProjectTitan\b", 'internal codename; write "enterprise billing platform"'),
    (r"\bled a team of\b|\bmanag(?:ed|ing) (?:a team|\d+)\b",
     'team ceiling is "led frontend", never people management'),
]
```

### 5. `CUSTOM_SCOPE_FAILS`
Add tuples of `(regex_pattern, gate_name, failure_message)` for rules specific to your tenure or metrics. Three common patterns are included as examples:
- **Preventing tenure inflation on a secondary language:** e.g. failing if `"4 years"` or `"6 years"` is attached to a language you only wrote for 1 year.
- **Preventing relative lifts from turning into percentage points:** e.g. failing if `"12%"` is rewritten as `"12 percentage points"` or `"12 pp"`.
- **Enforcing a qualifier on a skill:** e.g. requiring `Python` to always appear as `Python (scripting)`.

### 6. `TAGLINE_PARTS`
Keep `TAGLINE_PARTS` synchronized with the approved Craft and Domain parts in `references/bullet-craft.md`. The gate warns if a tailored sub-heading introduces an unapproved tagline phrase.

### 7. `NOUN_OPENING_ALLOWLIST`
Every resume bullet is checked to ensure it starts with a past-tense finite verb (`Built`, `Led`, `Architected`, `Shipped`, etc.). If you have a specific bullet that intentionally starts with a noun phrase (e.g. `"Sole technical owner for..."`), keep its prefix in `NOUN_OPENING_ALLOWLIST`.

---

## Step 4: Customize `resume-tailor/references/bullet-craft.md`

Open `resume-tailor/references/bullet-craft.md` and review:
1. **Metrics (`## Metrics`):** Replace the comment block with a quick summary of the numbers on your base resume and any optional numbers from your evidence bank. (Note: `check_variant.py --base` automatically parses all numbers matching `METRIC` from your base `.tex` file and fails if any are dropped in a variant.)
2. **Tagline parts (`## Tagline parts`):** List the 10–20 two-to-four-word craft and domain phrases that accurately describe your work (e.g. `API & Service Development`, `Distributed Systems & Scalability`, `Web Performance & Reliability`, `Product Experimentation`). Make sure every phrase you list here is also in `TAGLINE_PARTS` in `scripts/check_variant.py`.

---

## Step 5: Update Paths in `SKILL.md` and `recent-applications.md`

1. **`resume-tailor/SKILL.md`:**
   - Replace `Candidate_Name_Resume.tex` / `Candidate_Name_resume.tex` (in **Where things are**, **Step 8**, and **Auditing an existing variant**) with your own filename (e.g. `Jane_Doe_Resume.tex` for the base and `Jane_Doe_resume.tex` for tailored variants).
   - In **Step 6 (Title block / Summary)**, adjust any stack-part defaults or summary-sentence notes so they reflect your primary stack and years of experience.
2. **`resume-tailor/references/recent-applications.md`:**
   - Update the **Bullet abbreviations** list at the top to match the bold category prefixes (`{\bfseries Category:}`) on your base resume.
   - Update the rows of the **Find the closest sibling by role type** table to match the categories of jobs you apply for (e.g. `Senior Backend / Distributed Systems`, `Full-Stack Product`, `Platform / Infrastructure`).
   - Clear the `ExampleCorp` placeholder entry once you log your first real application.

---

## Testing Your Customized Setup

Once you have customized the files above, run the gate script against your base resume to verify everything compiles and passes cleanly:

```bash
# 1. Verify system tools (pdflatex, pdfinfo, pdftotext) are installed
which pdflatex pdfinfo pdftotext

# 2. Run check_variant.py on your base resume against itself
python3 resume-tailor/scripts/check_variant.py \
  ~/Documents/resumes/Your_Name_Resume.tex \
  --base ~/Documents/resumes/Your_Name_Resume.tex
```

You should see `[PASS]` across `render`, `ats`, `no-wrap`, `shape`, `scope`, and `evidence`, ending with `RESULT: PASS`. (Two expected `[WARN]` lines will appear when running directly on your base resume folder if there is no `job_description.txt` or lineage header comment in the base directory.)

### Installing into Claude Code

Copy or symlink the `resume-tailor` folder into `~/.claude/skills/`:

```bash
ln -s "$(pwd)/resume-tailor" ~/.claude/skills/resume-tailor
```
