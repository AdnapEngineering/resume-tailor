# How to Customize `resume-tailor` (3 Steps)

You **do not** need to edit any Python scripts or `SKILL.md` to customize this skill. Everything specific to your career lives in just **two files** after you create your base LaTeX resume:

1. **`resume-tailor/config.json`** — your file paths, page limit, `skills_only` list, `off_surface` (never-used tech) list, and `do_not_write` rules.
2. **`resume-tailor/references/evidence-bank.md`** — your verified project facts and scope ceilings.

Even better, **`scripts/init_profile.py` generates both files for you automatically** by parsing your base `.tex` resume.

---

## Step 1: Create Your Base LaTeX Resume

Copy the included template to your resumes directory and edit it with your experience:

```bash
mkdir -p ~/Documents/resumes/toApply
cp templates/Candidate_Name_Resume.tex ~/Documents/resumes/Your_Name_Resume.tex
```

> **Tip:** Already have a resume in Markdown, PDF, or Word? Open Claude Code and ask:
> *"Convert my existing resume into `~/Documents/resumes/Your_Name_Resume.tex` following the macros and layout of `templates/Candidate_Name_Resume.tex`."*

---

## Step 2: Auto-Generate `config.json` and `evidence-bank.md`

Run the bootstrap script against your new `.tex` resume:

```bash
python3 resume-tailor/scripts/init_profile.py \
  --resume ~/Documents/resumes/Your_Name_Resume.tex \
  --write-evidence-bank \
  --force
```

What this script does automatically:
- Parses your `.tex` resume's companies, roles, dates, bullets, metrics, tagline parts, and Technical Proficiencies table.
- Writes **`resume-tailor/config.json`** pre-configured with your `base_resume` path, `output_dir`, `variant_filename`, and tagline parts.
- Writes **`resume-tailor/references/evidence-bank.md`** pre-populated with every company, role, bullet, and skill row from your resume, plus a starter Requirement → Evidence table.

---

## Step 3: Review `config.json` and Fill In Your Scope Ceilings

### A. Quick review of `resume-tailor/config.json`

Open `resume-tailor/config.json` and adjust three simple lists:

```json
{
  "base_resume": "/home/you/Documents/resumes/Your_Name_Resume.tex",
  "output_dir": "/home/you/Documents/resumes",
  "variant_filename": "Your_Name_resume.tex",
  "max_pages": 2,
  "skills_only": ["Python", "Docker", "Cypress", "Kafka"],
  "off_surface": ["Kubernetes", "Golang", "Spring Boot", "React Native", "Redux"],
  "do_not_write": [
    {
      "pattern": "\\bProjectTitan\\b",
      "reason": "internal codename; write \"enterprise billing platform\""
    }
  ]
}
```

- **`skills_only`**: Technologies you have light, scripting-only, or personal-project exposure to. They are allowed in your **Technical Proficiencies** table, but `check_variant.py` will **FAIL** if the AI tries to slip them into a work-experience bullet or the summary.
- **`off_surface`**: Common technologies in job descriptions that you have **never** used. If the AI hallucinates any of these anywhere on the resume, `check_variant.py` **FAILS**.
- **`do_not_write`**: Internal company codenames or scope overreaches (like `"led a team of"` when you were an IC tech lead) that must never appear.

### B. Fill in your scope ceilings in `resume-tailor/references/evidence-bank.md`

Open `resume-tailor/references/evidence-bank.md` (which `init_profile.py` pre-filled with your bullets) and replace the `*(TODO: ...)*` notes on each bullet with:
- **Ceiling:** The strongest honest verb and boundary (e.g., *"Owned the frontend build and rollout; a staff backend engineer designed token exchange"*).
- **Do not write:** Overreaches to avoid (e.g., *"Do not claim ownership of the backend authentication service"*).

> **Tip:** You can also have Claude Code interview you to fill this in:
> *"Read `resume-tailor/references/evidence-bank.md` and interview me one company at a time to fill in the Ceiling and Do-Not-Write lines, plus my `skills_only` and `off_surface` lists in `resume-tailor/config.json`."*

---

## Verify Your Setup

Run the built-in setup and gate check:

```bash
# 1. Check that pdflatex/pdfinfo/pdftotext, config.json, and evidence-bank.md are ready
python3 resume-tailor/scripts/check_variant.py --check-setup

# 2. Compile and gate your base resume against itself
python3 resume-tailor/scripts/check_variant.py ~/Documents/resumes/Your_Name_Resume.tex
```

Once both pass, symlink the skill into Claude Code:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/resume-tailor" ~/.claude/skills/resume-tailor
```
