#!/usr/bin/env python3
"""Bootstrap your customized resume-tailor config.json and evidence-bank.md from your base .tex resume.

Usage:
  python3 resume-tailor/scripts/init_profile.py --resume ~/Documents/resumes/Your_Name_Resume.tex

What it does:
  1. Parses your base .tex resume to extract your tagline parts, summary,
     Technical Proficiencies rows, companies/roles/dates, bullets, and metrics.
  2. Writes resume-tailor/config.json with your base_resume path, output_dir,
     variant_filename, and pre-populated skills_only / tagline_parts lists
     (Detecting which skills appear ONLY in your skills table vs. in your bullets).
  3. Optionally writes a pre-filled draft of resume-tailor/references/evidence-bank.md
     with every company, role, bullet, metric, and stack list from your resume so you
     only need to fill in your scope notes ("Ceiling" / "Do not write").
"""
import argparse
import json
import os
import re
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def strip_comments(tex):
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", ln) for ln in tex.splitlines())


def plain(s):
    s = re.sub(r"\\(textbf|textit|emph|texttt|href\{[^}]*\})\{([^}]*)\}", r"\2", s)
    s = s.replace("\\%", "%").replace("\\&", "&").replace("\\til ", "~").replace("\\til", "~")
    s = re.sub(r"\\mbox\{([^}]*)\}", r"\1", s)
    s = s.replace("--", "–").replace("``", '"').replace("''", '"')
    return " ".join(s.split())


def parse_resume(tex_path):
    raw = open(tex_path, encoding="utf-8").read()
    body_m = re.search(r"\\begin\{document\}(.*)\\end\{document\}", strip_comments(raw), re.S)
    body = body_m.group(1) if body_m else strip_comments(raw)

    # Tagline parts
    tagline_parts = []
    sec_m = re.search(r"\\sectionhead\{([^}]*)\}(.*?)(?:\\sectionhead\{|\n\s*\n)", body, re.S)
    role_title = plain(sec_m.group(1)) if sec_m else "Software Engineer"
    if sec_m:
        bf = re.search(r"\\bfseries\s+(.*?)\}\\par", sec_m.group(2), re.S)
        if bf:
            parts = [
                " ".join(re.sub(r"\\,|\$\\cdot\$", " ", p).replace("\\&", "&").split())
                for p in re.split(r"\$\\vert\$", bf.group(1))
            ]
            tagline_parts = parts[1:] if len(parts) > 1 else parts

    # Summary
    sum_m = re.search(r"\\sectionhead\{[^}]*\}.*?\\endgroup(.*?)\\sectionhead", body, re.S)
    summary = plain(sum_m.group(1)) if sum_m else ""

    # Skills table
    skills_by_cat = []
    all_skill_tokens = []
    for tab in re.findall(r"\\begin\{tabularx\}[^\n]*\n(.*?)\\end\{tabularx\}", body, re.S):
        for r in tab.split("\\\\"):
            if "&" not in r:
                continue
            cat, items_str = r.split("&", 1)
            cat_clean = plain(cat).strip()
            items_clean = plain(items_str).strip()
            if cat_clean and items_clean:
                skills_by_cat.append((cat_clean, items_clean))
                for tok in re.split(r",\s*", re.sub(r"\([^)]*\)", "", items_clean)):
                    tok = tok.strip()
                    if tok and len(tok) > 1:
                        all_skill_tokens.append(tok)

    # Companies and bullets
    companies = []
    comp_splits = re.split(r"\\company\{([^}]*)\}\{([^}]*)\}", body)
    # comp_splits[0] is before first company; then triples of (name, loc, content)
    for i in range(1, len(comp_splits), 3):
        c_name = plain(comp_splits[i])
        c_loc = plain(comp_splits[i + 1])
        c_content = comp_splits[i + 2]
        c_content = re.split(r"\\sectionhead\{", c_content)[0]
        roles = [
            (plain(m.group(1) + m.group(2)), plain(m.group(3)))
            for m in re.finditer(r"\\roleline\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}", c_content)
        ]
        bullets = []
        for p in re.split(r"\\item\b", c_content)[1:]:
            p = re.split(r"\\end\{itemize\}|\\begin\{itemize\}|\\roleline", p)[0]
            label_m = re.match(r"\s*\{\\bfseries\s*([^}]*)\}\s*(.*)", p, re.S)
            if label_m:
                bullets.append((plain(label_m.group(1)).rstrip(":"), plain(label_m.group(2))))
            else:
                bullets.append(("Bullet", plain(p)))
        companies.append({"name": c_name, "location": c_loc, "roles": roles, "bullets": bullets})

    # Auto-detect skills that appear in the skills table but never in summary or bullets
    prose_text = summary + " " + " ".join(b for c in companies for _, b in c["bullets"])
    skills_only_detected = []
    verified_detected = []
    for tok in all_skill_tokens:
        # check if token appears in prose
        if re.search(r"\b" + re.escape(tok) + r"\b", prose_text, re.I):
            verified_detected.append(tok)
        else:
            skills_only_detected.append(tok)

    return {
        "role_title": role_title,
        "tagline_parts": tagline_parts,
        "summary": summary,
        "skills_by_cat": skills_by_cat,
        "companies": companies,
        "verified_detected": verified_detected,
        "skills_only_detected": skills_only_detected,
    }


def build_evidence_bank_draft(parsed, tex_path):
    lines = [
        "# Evidence bank — verified claims and their locked attribution",
        "",
        f"Auto-drafted from `{tex_path}` by `scripts/init_profile.py`.",
        "Review each bullet below and fill in any **Ceiling** or **Do not write** boundaries so the AI never overclaims your scope.",
        "",
        "---",
        "",
    ]
    for comp in parsed["companies"]:
        role_str = "; ".join(f"{r} ({d})" for r, d in comp["roles"])
        lines.append(f"## {comp['name']} ({comp['location']})")
        if role_str:
            lines.append(f"**Roles:** {role_str}")
        lines.append("")
        for label, text in comp["bullets"]:
            lines.append(f"**{label}**")
            lines.append(f"- **Claim:** {text}")
            lines.append("- **Ceiling:** *(TODO: note the maximum honest verb/scope, e.g. 'owned frontend only' or 'solo-built end to end')*")
            lines.append("- **Do not write:** *(TODO: note any overreach or internal codename to avoid)*")
            lines.append("")
        lines.append("---")
        lines.append("")

    lines.extend([
        "## Stack and years",
        "",
        "### 1. Verified stack from your Technical Proficiencies table",
    ])
    for cat, items in parsed["skills_by_cat"]:
        lines.append(f"- **{cat}:** {items}")
    lines.extend([
        "",
        "### 2. Skills-list-only (`skills_only` in `config.json` — never in bullets or summary)",
        "- *(Move light/scripting/personal-project tools here and into `skills_only` in `config.json`)*",
        "",
        "### 3. Off-surface (`off_surface` in `config.json` — never anywhere on the page)",
        "- *(List common JD technologies you have zero experience with in `off_surface` in `config.json`)*",
        "",
        "---",
        "",
        "## Open metric gaps — never fill these",
        "",
        "- *(List any unrecorded baselines or numbers you don't have so the AI never estimates them)*",
        "",
        "---",
        "",
        "## Requirement → evidence map",
        "",
        "| JD asks for | Reach for |",
        "|---|---|",
    ])
    for comp in parsed["companies"]:
        for label, text in comp["bullets"]:
            short = (text[:90] + "…") if len(text) > 90 else text
            lines.append(f"| {label} | {short} ({comp['name']}) |")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Bootstrap config.json and evidence-bank.md from your base .tex resume.")
    ap.add_argument("--resume", required=True, help="Path to your canonical base .tex resume")
    ap.add_argument("--write-evidence-bank", action="store_true", help="Also generate a pre-populated references/evidence-bank.md from your resume bullets")
    ap.add_argument("--force", action="store_true", help="Overwrite existing config.json / evidence-bank.md")
    a = ap.parse_args()

    tex_path = os.path.abspath(os.path.expanduser(a.resume))
    if not os.path.exists(tex_path):
        print(f"Error: resume file not found at {tex_path}", file=sys.stderr)
        sys.exit(1)

    parsed = parse_resume(tex_path)
    out_dir, base_name = os.path.split(tex_path)
    # Convention: First_Last_Resume.tex -> First_Last_resume.tex for variants
    if base_name.endswith("_Resume.tex"):
        var_name = base_name[:-11] + "_resume.tex"
    else:
        var_name = base_name[:-4] + "_variant.tex"

    example_cfg_path = os.path.join(SKILL_DIR, "config.example.json")
    cfg = json.load(open(example_cfg_path, encoding="utf-8")) if os.path.exists(example_cfg_path) else {}
    cfg.pop("_comment", None)
    cfg["base_resume"] = tex_path
    cfg["output_dir"] = out_dir
    cfg["variant_filename"] = var_name

    # Merge any tagline parts from their base resume into tagline_parts
    existing_parts = list(cfg.get("tagline_parts") or [])
    for p in parsed["tagline_parts"]:
        if p and p not in existing_parts:
            existing_parts.insert(0, p)
    cfg["tagline_parts"] = existing_parts

    cfg_out = os.path.join(SKILL_DIR, "config.json")
    if os.path.exists(cfg_out) and not a.force:
        print(f"Note: {cfg_out} already exists (pass --force to overwrite).")
    else:
        with open(cfg_out, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
            f.write("\n")
        print(f"✓ Wrote {cfg_out}")
        print(f"  - base_resume:      {tex_path}")
        print(f"  - variant_filename: {var_name}")
        print(f"  - skills in table but not bullets (candidate skills_only): {parsed['skills_only_detected'][:10]}")

    if a.write_evidence_bank:
        bank_out = os.path.join(SKILL_DIR, "references", "evidence-bank.md")
        if os.path.exists(bank_out) and not a.force:
            print(f"Note: {bank_out} already exists (pass --force to overwrite).")
        else:
            draft = build_evidence_bank_draft(parsed, tex_path)
            with open(bank_out, "w", encoding="utf-8") as f:
                f.write(draft)
            print(f"✓ Drafted {bank_out} from your resume's {sum(len(c['bullets']) for c in parsed['companies'])} bullets")

    print("\nNext steps:")
    print("  1. Review resume-tailor/config.json (edit skills_only, off_surface, and do_not_write)")
    print("  2. Fill in the Ceiling / Do not write notes in resume-tailor/references/evidence-bank.md")
    print("  3. Verify your setup: python3 resume-tailor/scripts/check_variant.py --check-setup")


if __name__ == "__main__":
    main()
