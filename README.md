# `resume-tailor` — Truth-Preserving LaTeX Resume Tailoring Skill for Claude Code

A Claude Code skill that produces an ATS-parseable, company-specific LaTeX resume variant from a job posting—re-pointing the title block, tagline, and summary, re-ordering and selectively re-framing bullets, compiling to PDF, and verifying the result through a deterministic mechanical gate (`check_variant.py`).

## Why This Skill Exists

Most AI resume tailoring fails in four predictable ways:
1. **Scope creep:** "Contributed to" quietly becomes "architected", or owning a feature frontend becomes owning the platform architecture.
2. **Keyword stuffing:** Job description nouns get jammed into sentences until a human hiring manager can tell at a glance.
3. **Metric loss:** A concrete, defensible number gets dropped to make room for a vague phrase that matched the posting.
4. **Variant drift:** An outdated phrasing, internal codename, or retired claim rides in from an older tailored variant.

`resume-tailor` is designed to prevent all four:
- **Locked Evidence Bank (`references/evidence-bank.md`):** Every factual claim, metric, and attribution ceiling is recorded in one file. Nothing goes on the resume unless it traces to the evidence bank.
- **Explicit Gap Triage:** Requirements are triaged into **Placed** (backed by verified evidence), **Ask** (plausibly part of a project in the bank, surfaced as a direct question to the user), or **Gap** (recorded as `# gap: <keyword>` in `keywords.txt`, never stretched into a fake bullet).
- **Approval Gate Before File Writes:** In normal single-posting mode, the agent proposes an exact `old → new` diff grouped by section plus a coverage report and waits for your approval before touching a `.tex` file.
- **Mechanical Verification (`scripts/check_variant.py`):** Compiles the `.tex` twice with `pdflatex` and runs hard gates on page count, single-line tagline no-wrap, page-1 bullet breaks, ATS text-layer extraction (`pdftotext`), placed keywords, sentence shape, AI-cliché banlist, metric survival against the base resume, and scope lists (`SKILLS_ONLY`, `OFF_SURFACE`, `DO_NOT_WRITE`).

---

## Repository Structure

```text
resume-tailor/
├── README.md                          # Overview, prerequisites, and quickstart
├── HOW_TO_CUSTOMIZE.md                # 3-step customization guide
├── LICENSE                            # MIT License
├── templates/
│   └── Candidate_Name_Resume.tex      # Clean, ATS-verified LaTeX base resume template
└── resume-tailor/                     # The Claude Code skill directory (copy/symlink to ~/.claude/skills/)
    ├── SKILL.md                       # Main skill workflow and non-negotiable rules
    ├── config.example.json            # Tracked config template (copied/generated to config.json)
    ├── references/
    │   ├── bullet-craft.md            # Register, sentence shape, verb ceiling, banlist, ATS rules, 4 gates
    │   ├── evidence-bank.md           # Template for verified claims, attribution ceilings, and stack tiers
    │   ├── recent-applications.md     # Sibling application index by role type for reusing proven bullets
    │   └── fetching.md                # Fallback steps when a job posting URL blocks automated fetches
    └── scripts/
        ├── init_profile.py            # Auto-generates config.json & evidence-bank.md from your base .tex
        ├── check_variant.py           # Mechanical compiler + ATS/scope/metric/shape verification gate
        └── find_posting.py            # Optional lookup helper for local job-search-pipeline caches
```

---

## Prerequisites

- **Python 3.10+** (standard library only; no third-party Python packages required)
- **LaTeX (`pdflatex`)** and **Poppler utilities (`pdfinfo`, `pdftotext`)**:
  - **Ubuntu / Debian (or WSL):**
    ```bash
    sudo apt-get install texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended poppler-utils
    ```
  - **macOS (Homebrew):**
    ```bash
    brew install --cask mactex-no-gui
    brew install poppler
    ```
  - **Windows (PowerShell via `winget` or `scoop`):**
    ```powershell
    winget install MiKTeX.MiKTeX oschwartz10612.Poppler
    # Or with Scoop: scoop install latex poppler
    ```
    *(Note: In MiKTeX Console, set "Install missing packages on-the-fly" to **Yes** so `pdflatex` can run non-interactively.)*

---

## Quickstart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AdnapEngineering/resume-tailor.git
   cd resume-tailor
   ```

2. **Bootstrap your configuration in one command (see [`HOW_TO_CUSTOMIZE.md`](HOW_TO_CUSTOMIZE.md)):**
   - Copy `templates/Candidate_Name_Resume.tex` to `~/Documents/resumes/<Your_Name>_Resume.tex` and fill in your resume.
   - Run `init_profile.py` to auto-generate `resume-tailor/config.json` and a pre-filled `resume-tailor/references/evidence-bank.md` straight from your `.tex` bullets:
     ```bash
     python3 resume-tailor/scripts/init_profile.py \
       --resume ~/Documents/resumes/<Your_Name>_Resume.tex \
       --write-evidence-bank --force
     ```
     *(On Windows PowerShell, use `python` instead of `python3`.)*
   - Review `resume-tailor/config.json` (`skills_only`, `off_surface`, `do_not_write`) and add your scope ceilings in `resume-tailor/references/evidence-bank.md`.

3. **Verify your setup and test the mechanical gate:**
   ```bash
   python3 resume-tailor/scripts/check_variant.py --check-setup
   python3 resume-tailor/scripts/check_variant.py ~/Documents/resumes/<Your_Name>_Resume.tex
   ```

4. **Install the skill into Claude Code:**
   - **Linux / macOS / WSL:**
     ```bash
     mkdir -p ~/.claude/skills
     ln -s "$(pwd)/resume-tailor" ~/.claude/skills/resume-tailor
     ```
   - **Windows (PowerShell):**
     ```powershell
     New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
     New-Item -ItemType Junction -Path "$HOME\.claude\skills\resume-tailor" -Target "$PWD\resume-tailor"
     ```

5. **Use it in Claude Code:**
   Share any job posting URL or paste a job description:
   > *"Tailor my resume for this posting: https://boards.greenhouse.io/..."*
   > *"Does my resume match this JD?"*
   > *"Audit my existing Acme variant against its job_description.txt"*

---

## What `check_variant.py` Enforces

When you (or the agent) run:

```bash
python3 ~/.claude/skills/resume-tailor/scripts/check_variant.py \
  ~/Documents/resumes/toApply/Acme/Your_Name_resume.tex \
  --base ~/Documents/resumes/Your_Name_Resume.tex \
  --keywords ~/Documents/resumes/toApply/Acme/keywords.txt
```

It checks:

| Gate | Type | What It Verifies |
| :--- | :--- | :--- |
| **`render`** | Hard FAIL / WARN | No unescaped `%` after a number in LaTeX source; `pdflatex` compiles cleanly (2 passes); PDF page count `<= MAX_PAGES`; page 1 ends on a complete bullet (WARN if split). |
| **`no-wrap`** | Hard FAIL | The centered 3-part tagline under `\sectionhead{<Role Title>}` renders on a single line in the extracted PDF text. |
| **`ats`** | Hard FAIL / WARN | Date ranges use ASCII hyphens (`-`), not Unicode en/em-dashes (`–`/`—`) that break Workday imports; zero garbled `(cid:N)` or `U+FFFD` glyphs; `mailto:` email address is printed as visible text; every placed keyword in `keywords.txt` extracts via `pdftotext` (while reporting `# gap:` and `# ask:` lines). |
| **`shape`** | Hard FAIL / WARN | On `\item` lines: no em-dash asides (`---` or `—`), at most 1 semicolon, at most 1 participial clause (`, <verb>ing`), no first-person pronouns (`I`, `my`, `we`, `our`), zero hits from `BANLIST`, opens with a past-tense verb (WARN), and doesn't end on pure process/collaboration (WARN). |
| **`scope`** | Hard FAIL / WARN | No `SKILLS_ONLY` terms in bullets or summary; no `OFF_SURFACE` terms anywhere on the page; no `DO_NOT_WRITE` phrases; no `CUSTOM_SCOPE_FAILS` violations; `"Senior"` not used in summary opener when the role title isn't Senior; parenthetical attributions `(senior-led...)` / `(staff-led...)` preserved from the base resume. |
| **`spelling`** | Hard FAIL | Brand and technology names match owner casing (`GitHub`, `TypeScript`, `GraphQL`, `PostgreSQL`, `LaunchDarkly`, `Datadog`, etc.). |
| **`evidence`** | Hard FAIL / WARN | Every metric present in the canonical `--base` `.tex` survives unrounded in the variant; any new metric not in `--base` or `evidence-bank.md` triggers a WARN. |

---

## License

[MIT](LICENSE)
