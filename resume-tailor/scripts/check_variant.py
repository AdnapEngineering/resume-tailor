#!/usr/bin/env python3
"""Mechanical gates for a tailored resume variant (gates 3 and 4 in bullet-craft.md).

Reads candidate-specific settings from resume-tailor/config.json (or
~/.config/resume-tailor/config.json, or --config), falling back to
config.example.json defaults so you never have to edit Python code to
customize the skill.

Usage:
  check_variant.py [VARIANT.tex] [--base BASE.tex] [--keywords KW.txt]
                   [--config CONFIG.json] [--no-compile] [--mirror SKILLS_DIR]
                   [--max-pages N] [--check-setup]

  --base         canonical base .tex (defaults to base_resume in config.json)
  --keywords     one JD keyword per line; each must appear in the extracted PDF text.
                 Lines starting with # are skipped; "# gap: X" records a JD keyword
                 with no evidence (a coverage gap), "# ask: X" one that may be real
                 but unrecorded (a question for the candidate), and the report lists both
  --config       path to config.json
  --no-compile   skip pdflatex (use the existing PDF next to the .tex)
  --mirror       skills root containing resume-tailor/ and cover-letter-generator/;
                 verifies the mirrored reference files match
  --max-pages    maximum allowed PDF page count (overrides config.json max_pages)
  --check-setup  verify system tools (pdflatex, pdfinfo, pdftotext), config.json,
                 base_resume, and evidence-bank.md

Exit code 0 = all hard gates pass, 1 = at least one FAIL. WARN lines are for
judgment and don't fail the run.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_CONFIG = {
    "base_resume": "~/Documents/resumes/Candidate_Name_Resume.tex",
    "output_dir": "~/Documents/resumes",
    "variant_filename": "Candidate_Name_resume.tex",
    "max_pages": 2,
    "skills_only": [
        "Python", "Cypress", "Storybook", "Docker", "GitHub Actions", "Astro",
        "Tailwind", "design tokens", "Confluence", "PHP", "Reactive Forms",
        "Module Federation", "SCSS", "Jira", "Linux", "Git", "Copilot", "Kafka",
    ],
    "off_surface": [
        "Vite", "Vitest", "Redux", "Kubernetes", "React Native", "Flutter",
        "Golang", "NestJS", "Spring Boot", "Sentry", "TanStack", "Zustand",
        "Turborepo", "esbuild", "Rollup", "NVDA", "JAWS", "Section 508",
        "VPAT", "MUI", "Material UI", "Shopify", "Relay",
    ],
    "do_not_write": [],
    "custom_scope_fails": [],
    "tagline_parts": [
        "AI-Assisted Development", "Test Automation & Quality", "Test Automation & CI/CD",
        "Web Performance & Accessibility", "Web Performance & Reliability", "Web Performance",
        "Web Performance & Architecture", "End-to-End Product Features", "Frontend Platform & DX",
        "Product Experimentation", "A/B Experimentation & Funnels", "Observability & Reliability",
        "Code Review & Mentorship", "API & Service Development", "Accessibility & UI Quality",
        "Feature-Flag Rollouts", "Growth & Experimentation", "Frontend Platform",
        "Payments Product Engineering", "Onboarding & Multi-Step Forms",
        "Distributed Systems & Scalability", "Cloud Infrastructure & DevOps",
        "Data Pipelines & Analytics",
    ],
    "noun_opening_allowlist": ["Sole technical owner"],
    "excluded_companies": [],
}

MISSPELLED = [
    (r"\bGithub\b", "GitHub"),
    (r"\bGitlab\b", "GitLab"),
    (r"\bJavascript\b", "JavaScript"),
    (r"\bTypescript\b", "TypeScript"),
    (r"\bPagerduty\b", "PagerDuty"),
    (r"\bLaunch [Dd]arkly\b|\bLaunchdarkly\b", "LaunchDarkly"),
    (r"\bDynamo DB\b|\bDynamoDb\b", "DynamoDB"),
    (r"\bGraphql\b|\bGraphQl\b", "GraphQL"),
    (r"\bMixPanel\b", "Mixpanel"),
    (r"\bDataDog\b", "Datadog"),
    (r"\bPostgresql\b", "PostgreSQL"),
]

BANLIST = [
    "spearheaded", "spearheading", "leveraged", "leverage", "leveraging",
    "utilized", "utilize", "utilizing", "responsible for",
    "seamless", "seamlessly", "robust", "cutting-edge", "cutting edge", "passionate",
    "world-class", "synergy", "synergies", "proven track record", "results-driven",
    "dynamic", "innovative", "best-in-class", "drove impact", "move the needle",
]

HEADINGS = re.compile(
    r"^\s*(summary|professional summary|core competencies|professional experience|"
    r"experience|technical proficiencies|technical skills|skills|education|projects)\s*$",
    re.I,
)
IRREGULAR = {
    "built", "led", "ran", "wrote", "cut", "rebuilt", "made", "drove", "took", "set",
    "grew", "caught", "brought", "taught", "won", "held", "kept", "shipped", "split",
    "spun", "began", "chose", "found", "gave", "met", "put", "sent", "shot", "sold",
    "oversaw", "rewrote",
}
METRIC = re.compile(
    r"(?:p\d{2}\s*[A-Za-z]*\s*[−-]\s*\d+(?:\.\d+)?\s*s)"          # p75 LCP −1s
    r"|(?:~?\d+(?:\.\d+)?\s*\\?%\s*(?:→|\\to|\$\\rightarrow\$|->)\s*~?\d+(?:\.\d+)?\s*\\?%)"  # 40%→80%
    r"|(?:\d+(?:\.\d+)?\s*\\?%\s+above\s+target)"                # 40% above target
    r"|(?:~?\d+(?:\.\d+)?s\b)"                                   # ~1s
    r"|(?:~?\d+\s+weekly)"                                        # ~3 weekly tickets
    r"|(?:\d+[–-]\d+-minute)"                                     # 5–10-minute
    r"|(?:\d+[–-]\d+\s+(?:minutes|hours))"                         # 10–15 minutes, 2–3 hours
    r"|(?:~?\d+-hour)"                                           # ~2-hour
    r"|(?:\d+-team)"                                             # 6-team department
    r"|(?:sub-\d+-minute)"                                       # sub-30-minute
    r"|(?:\d+-engineer)"                                         # 10-engineer team
    r"|(?:~?\d{1,3}(?:,\d{3})+\+?)"                              # 4,000+
    r"|(?:~?\d+(?:\.\d+)?\+?\s*\\?%)"                            # 12%, ~60%
    r"|(?:\d+\+(?:/wk)?)"                                        # 500+/wk
)
ASCII_DATES = re.compile(
    r"\b(?:19|20)\d\d\s*[–—]|[–—]\s*(?:\d\d/)?(?:(?:19|20)\d\d\b|Present\b)",
    re.I,
)
PROCESS_END = re.compile(
    r"(?:partner(?:ed|ing) with|collaborat\w+ with|in Scrum sprints)[^;.]{0,70}\.?\s*$",
    re.I,
)
MIRRORED = [("evidence-bank.md", True), ("recent-applications.md", False)]

results = []


def record(level, gate, msg):
    results.append((level, gate, msg))


def load_config(explicit_path=None):
    cfg = dict(DEFAULT_CONFIG)
    candidates = [
        explicit_path,
        os.environ.get("RESUME_TAILOR_CONFIG"),
        os.path.join(SKILL_DIR, "config.json"),
        os.path.expanduser("~/.config/resume-tailor/config.json"),
        os.path.join(SKILL_DIR, "config.example.json"),
    ]
    loaded_from = None
    for p in candidates:
        if p and os.path.exists(os.path.expanduser(p)):
            loaded_from = os.path.expanduser(p)
            with open(loaded_from, encoding="utf-8") as f:
                user_cfg = json.load(f)
            cfg.update({k: v for k, v in user_cfg.items() if not k.startswith("_")})
            break
    cfg["_loaded_from"] = loaded_from
    return cfg


def compile_word_list_regex(words):
    cleaned = [w.strip() for w in (words or []) if w and w.strip()]
    if not cleaned:
        return None
    escaped = "|".join(re.escape(w) for w in cleaned)
    return re.compile(rf"\b({escaped})\b", re.I)


def check_setup(cfg):
    print("=== resume-tailor setup check ===")
    cfg_path = cfg.get("_loaded_from")
    is_example = cfg_path and cfg_path.endswith("config.example.json")
    if cfg_path and not is_example:
        record("PASS", "setup", f"config loaded from {cfg_path}")
    else:
        record(
            "WARN",
            "setup",
            f"no config.json found (using {cfg_path or 'built-in defaults'}); "
            "run `python3 scripts/init_profile.py --resume /path/to/Resume.tex` or copy config.example.json to config.json",
        )

    for tool in ("pdflatex", "pdfinfo", "pdftotext"):
        found = shutil.which(tool)
        record(
            "PASS" if found else "FAIL",
            "setup",
            f"{tool}: {found}" if found else f"{tool} not found on PATH (install texlive & poppler-utils)",
        )

    base = os.path.expanduser(cfg.get("base_resume") or "")
    if base and os.path.exists(base):
        record("PASS", "setup", f"base_resume found: {base}")
    else:
        record("WARN", "setup", f"base_resume not found at '{base}' (update base_resume in config.json)")

    bank = os.path.join(SKILL_DIR, "references", "evidence-bank.md")
    if os.path.exists(bank):
        txt = open(bank, encoding="utf-8").read()
        has_placeholder = "CUSTOMIZE THIS FILE" in txt or "Company A — Role / Team" in txt
        record(
            "WARN" if has_placeholder else "PASS",
            "setup",
            "evidence-bank.md still contains template placeholders"
            if has_placeholder
            else "evidence-bank.md exists and is customized",
        )
    else:
        record("FAIL", "setup", f"missing {bank}")

    return report()


def strip_comments(tex):
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", ln) for ln in tex.splitlines())


def body_of(tex):
    tex = strip_comments(tex)
    m = re.search(r"\\begin\{document\}(.*)\\end\{document\}", tex, re.S)
    return m.group(1) if m else tex


def items_of(body):
    parts = re.split(r"\\item\b", body)[1:]
    out = []
    for p in parts:
        p = re.split(r"\\end\{itemize\}|\\begin\{itemize\}", p)[0]
        out.append(" ".join(p.split()))
    return out


def summary_of(body):
    m = re.search(r"\\sectionhead\{[^}]*\}.*?\\endgroup(.*?)\\sectionhead", body, re.S)
    return " ".join(m.group(1).split()) if m else ""


def skill_rows(body):
    return "\n".join(
        " ".join(r.split())
        for tab in re.findall(r"\\begin\{tabularx\}.*?\\end\{tabularx\}", body, re.S)
        for r in tab.split("\\\\")
    )


def plain(s):
    s = re.sub(r"\\(textbf|textit|emph|texttt|href\{[^}]*\})\{([^}]*)\}", r"\2", s)
    return s


def check_mirror(root):
    for fname, has_header in MIRRORED:
        rt = os.path.join(root, "resume-tailor/references", fname)
        cl = os.path.join(root, "cover-letter-generator/references", fname)
        if not (os.path.exists(rt) and os.path.exists(cl)):
            record("WARN", "mirror", f"one {fname} copy is missing")
            continue
        r_txt = open(rt, encoding="utf-8").read()
        if has_header:
            r_txt = re.sub(r"^<!--.*?-->\s*\n", "", r_txt, count=1, flags=re.S)
        c_txt = open(cl, encoding="utf-8").read()
        if has_header:
            c_txt = re.sub(r"^<!--.*?-->\s*\n", "", c_txt, count=1, flags=re.S)
        same = r_txt == c_txt
        record(
            "PASS" if same else "FAIL",
            "mirror",
            f"{fname} copies match" if same else f"{fname} copies have diverged",
        )


def metric_src(body):
    return (
        body.replace("\\til ", "~")
        .replace("\\til", "~")
        .replace("\\textasciitilde", "~")
        .replace("--", "–")
    )


def norm_metric(m):
    m = m.replace("\\%", "%").replace("\\to", "→").replace("$\\rightarrow$", "→")
    m = m.replace("->", "→").replace("−", "-")
    return re.sub(r"\s+", "", m)


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tex", nargs="?")
    ap.add_argument("--base")
    ap.add_argument("--keywords")
    ap.add_argument("--config")
    ap.add_argument("--no-compile", action="store_true")
    ap.add_argument("--mirror")
    ap.add_argument("--max-pages", type=int)
    ap.add_argument("--check-setup", action="store_true")
    a = ap.parse_args()

    cfg = load_config(a.config)
    if a.check_setup:
        return check_setup(cfg)

    if not a.tex and not a.mirror:
        ap.error("give a VARIANT.tex, --mirror SKILLS_DIR, or --check-setup")
    if a.mirror:
        check_mirror(a.mirror)
    if not a.tex:
        return report()

    max_pages = a.max_pages or int(cfg.get("max_pages") or 2)
    base_path = a.base
    if not base_path:
        cfg_base = os.path.expanduser(cfg.get("base_resume") or "")
        if cfg_base and os.path.exists(cfg_base):
            base_path = cfg_base

    skills_only_re = compile_word_list_regex(cfg.get("skills_only"))
    off_surface_re = compile_word_list_regex(cfg.get("off_surface"))
    tagline_parts = set(cfg.get("tagline_parts") or [])
    noun_allowlist = tuple(cfg.get("noun_opening_allowlist") or [])
    do_not_write = [
        (item["pattern"], item["reason"]) if isinstance(item, dict) else tuple(item)
        for item in (cfg.get("do_not_write") or [])
    ]
    custom_scope_fails = [
        (item["pattern"], item.get("gate", "scope"), item["reason"])
        if isinstance(item, dict)
        else tuple(item)
        for item in (cfg.get("custom_scope_fails") or [])
    ]

    tex_path = os.path.abspath(a.tex)
    d, name = os.path.split(tex_path)
    pdf = os.path.join(d, name[:-4] + ".pdf")
    src = open(tex_path, encoding="utf-8").read()
    body = body_of(src)

    # ---- unescaped % after a figure ----
    m_doc = re.search(r"\\begin\{document\}", src)
    start = src[: m_doc.start()].count("\n") if m_doc else 0
    bare = [
        (start + i + 1, ln.strip())
        for i, ln in enumerate(src.splitlines()[start:])
        if not ln.lstrip().startswith("%") and re.search(r"\d\s?%", ln)
    ]
    record(
        "PASS" if not bare else "FAIL",
        "render",
        "no unescaped % after a figure"
        if not bare
        else "unescaped % (write \\%): " + "; ".join(f"line {n}: {t[:60]}" for n, t in bare[:3]),
    )

    # ---- compile ----
    if not a.no_compile:
        for _ in range(2):
            r = run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", name], d)
        if r.returncode != 0:
            tail = "\n".join(r.stdout.splitlines()[-15:])
            record("FAIL", "render", f"pdflatex failed:\n{tail}")
            return report()
        warns = re.findall(r"Overfull \\hbox.*", r.stdout)
        if warns:
            record("WARN", "render", f"{len(warns)} overfull hbox(es): {warns[0]}")

    if not os.path.exists(pdf):
        record("FAIL", "render", f"no PDF at {pdf}")
        return report()
    if a.no_compile and os.path.getmtime(tex_path) > os.path.getmtime(pdf):
        record(
            "WARN",
            "render",
            "the PDF is older than the .tex, so these results describe "
            "the old version; rerun without --no-compile",
        )

    # ---- pages ----
    info = run(["pdfinfo", pdf], d).stdout
    pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    record(
        "PASS" if pages <= max_pages else "FAIL",
        "render",
        f"{pages} page(s) (limit {max_pages})",
    )
    if pages >= 2:
        p2 = run(["pdftotext", "-layout", "-f", "2", "-l", "2", pdf, "-"], d).stdout.splitlines()
        hdr = next((i for i, l in enumerate(p2) if re.search(r"Page\s+2\s*$", l)), -1)
        first = next((l.strip() for l in p2[hdr + 1 :] if l.strip()), "")
        if first.startswith("•") or "|" in first or first.isupper() or HEADINGS.match(first):
            record("PASS", "render", "page 1 ends on a whole bullet")
        else:
            record(
                "WARN",
                "render",
                f"page 2 may open mid-bullet (check page 1 ends on a whole bullet): '{first[:60]}'",
            )

    text = run(["pdftotext", "-layout", pdf, "-"], d).stdout
    lines = text.splitlines()

    # ---- text layer: what an ATS import actually reads ----
    dash_dates = [" ".join(l.split()) for l in lines if ASCII_DATES.search(l)]
    record(
        "PASS" if not dash_dates else "FAIL",
        "ats",
        "date ranges use ASCII hyphens"
        if not dash_dates
        else f"date range with a Unicode dash (write the \\roleline date with a single '-'): {dash_dates[:3]}",
    )
    garbled = len(re.findall(r"\(cid:\d+\)|\ufffd", text))
    record(
        "PASS" if not garbled else "FAIL",
        "ats",
        "no garbled glyphs in text layer"
        if not garbled
        else f"{garbled} (cid:N)/U+FFFD glyph(s): a font lacks a Unicode map, an ATS reads garbage",
    )
    flat_text = " ".join(text.split()).lower()
    for url in re.findall(r"\\href\{mailto:([^}]*)\}", body):
        if url.lower() not in flat_text:
            record("FAIL", "ats", f"email {url.lower()} is only in a link, not printed text")

    # ---- sub-heading under \sectionhead ----
    tag_raw = ""
    m = re.search(r"\\sectionhead\{([^}]*)\}", body)
    if m:
        role = plain(m.group(1)).strip()
        idx = next((i for i, l in enumerate(lines) if role and role in l), None)
        if idx is None:
            record(
                "WARN",
                "render",
                f"couldn't find role line '{role}' in extracted text; check the sub-heading by eye",
            )
        else:
            tm = re.search(
                r"\\sectionhead\{" + re.escape(m.group(1)) + r"\}(.*?)(?:\\sectionhead\{|\n\s*\n)",
                body,
                re.S,
            )
            tag = ""
            if tm:
                bf = re.search(r"\\bfseries\s+(.*?)\}\\par", tm.group(1), re.S)
                if bf:
                    tag = " ".join(plain(bf.group(1)).split())
                    tag_raw = bf.group(1)
            if not tag:
                record(
                    "WARN",
                    "no-wrap",
                    "couldn't isolate the tagline in the .tex; check the sub-heading by eye",
                )
            else:
                key = lambda t: re.sub(r"[^a-z0-9]", "", re.sub(r"\\[a-zA-Z]+", " ", t).lower())
                after = [" ".join(l.split()) for l in lines[idx + 1 : idx + 6] if l.strip()]
                whole = next((l for l in after if key(l) == key(tag)), None)
                if whole:
                    record("PASS", "no-wrap", "sub-heading renders as 1 line")
                else:
                    record(
                        "FAIL",
                        "no-wrap",
                        f"sub-heading wraps (must be 1 line): {after[:3]}",
                    )
    else:
        record("WARN", "no-wrap", "no \\sectionhead{} found; check the sub-heading by eye")

    # ---- tagline parts & level alignment (SKILL.md step 6) ----
    if tag_raw:
        parts = [
            " ".join(re.sub(r"\\,|\$\\cdot\$", " ", p).replace("\\&", "&").split())
            for p in re.split(r"\$\\vert\$", tag_raw)
        ]
        if len(parts) != 3:
            record("WARN", "tagline", f"tagline has {len(parts)} part(s), not 3: {parts}")
        if tagline_parts:
            unknown = [p for p in parts[1:] if p not in tagline_parts]
            if unknown:
                record(
                    "WARN",
                    "tagline",
                    f"part(s) not in tagline_parts (a near-duplicate, or a new "
                    f"part to add once approved): {unknown}",
                )
    summ0 = plain(summary_of(body))
    if m and summ0.startswith("Senior") and not re.search(r"\b(?:Senior|Sr)\b", m.group(1)):
        record(
            "FAIL",
            "scope",
            f"summary opens 'Senior' under a title without it: '{plain(m.group(1))}'",
        )

    # ---- keywords ----
    if a.keywords:
        flat = re.sub(r"-\s*\n\s*", "", text)  # rejoin hyphenated breaks
        flat = " ".join(flat.split()).lower()
        raw = [k.strip() for k in open(a.keywords, encoding="utf-8") if k.strip()]
        kws = [k for k in raw if not k.startswith("#")]
        gaps = [k.split(":", 1)[1].strip() for k in raw if re.match(r"#\s*gap:", k, re.I)]
        asks = [k.split(":", 1)[1].strip() for k in raw if re.match(r"#\s*ask:", k, re.I)]
        missing = [k for k in kws if k.lower() not in flat]
        record(
            "PASS" if not missing else "FAIL",
            "ats",
            f"{len(kws) - len(missing)}/{len(kws)} JD keywords extract"
            + (f"; missing: {missing}" if missing else "")
            + (f"; declared gaps (not placed): {gaps}" if gaps else ""),
        )
        if asks:
            record(
                "WARN",
                "ats",
                f"open asks (possibly real, unrecorded; resolve before sending): {asks}",
            )

    # ---- sentence shape on \item lines only ----
    items = items_of(body)
    for n, it in enumerate(items, 1):
        t = plain(it)
        t = re.sub(r"^\{\\bfseries [^}]*\}\s*", "", t)  # bold category label
        short = (t[:70] + "…") if len(t) > 70 else t
        if "---" in t or "—" in t:
            record("FAIL", "shape", f"bullet {n}: em-dash aside: {short}")
        semis = len(re.findall(r"(?<!\\);", t))
        if semis > 1:
            record("FAIL", "shape", f"bullet {n}: {semis} semicolons (max 1): {short}")
        parts = len(re.findall(r",\s+[a-z]+ing\b", t))
        if parts > 1:
            record("FAIL", "shape", f"bullet {n}: {parts} participial clauses (max 1): {short}")
        if re.search(r"\bI\b(?![/-])|\b(?:[Mm]y|[Oo]ur|[Ww]e)\b", t):
            record("FAIL", "shape", f"bullet {n}: first person: {short}")
        if PROCESS_END.search(t):
            record("WARN", "shape", f"bullet {n}: ends on process, not an outcome: …{t[-70:]}")
        first = re.sub(r"^[^A-Za-z]*", "", t).split(" ")[0].lower().strip(",.")
        if any(t.startswith(prefix) for prefix in noun_allowlist):
            continue
        if first and not (first.endswith("ed") or first in IRREGULAR):
            record("WARN", "shape", f"bullet {n}: opens with '{first}', not a past-tense verb: {short}")

    # ---- banlist (body prose: not the preamble, comments or the skills table) ----
    prose = re.sub(r"\\begin\{tabularx\}.*?\\end\{tabularx\}", "", body, flags=re.S)
    low = plain(prose).lower()
    hits = [w for w in BANLIST if re.search(r"(?<![a-z-])" + re.escape(w) + r"(?![a-z-])", low)]
    record("PASS" if not hits else "FAIL", "shape", "banlist clean" if not hits else f"banlist hits: {hits}")

    # ---- scope lists ----
    summary = plain(summary_of(body))
    if not summary:
        record("WARN", "scope", "couldn't isolate the summary; check it by eye for skills-only terms")
    flat_body = " ".join(plain(body).split())
    if skills_only_re:
        so = sorted({m.group(0) for t in items + [summary] for m in skills_only_re.finditer(plain(t))})
        record(
            "PASS" if not so else "FAIL",
            "scope",
            "skills-only terms stay in the skills list"
            if not so
            else f"skills-only term(s) in a bullet or the summary: {so}",
        )
    if off_surface_re:
        off = sorted({m.group(0) for m in off_surface_re.finditer(flat_body)})
        if off:
            record("FAIL", "scope", f"not on the verified stack surface (off_surface): {off}")
    for rx, why in do_not_write:
        dm = re.search(rx, flat_body, re.I)
        if dm:
            record("FAIL", "scope", f"'{dm.group(0)}': {why}")
    for rx, gate_name, why in custom_scope_fails:
        cm = re.search(rx, flat_body, re.I)
        if cm:
            record("FAIL", gate_name, f"'{cm.group(0)}': {why}")
    for rx, right in MISSPELLED:
        sm = re.search(rx, flat_body)
        if sm:
            record("FAIL", "spelling", f"'{sm.group(0)}': the owner spells it '{right}'")
    if re.search(r"\borchestrat\w+", flat_body, re.I):
        record("WARN", "shape", "'orchestrated': only for literal workflow orchestration (bullet-craft.md banlist)")

    # ---- metric preservation vs base ----
    if base_path and os.path.exists(base_path):
        bbody = body_of(open(base_path, encoding="utf-8").read())
        base_m = {norm_metric(x) for x in METRIC.findall(metric_src(bbody))}
        var_m = {norm_metric(x) for x in METRIC.findall(metric_src(body))}
        lost = sorted(base_m - var_m)
        new = sorted(var_m - base_m)
        bank_p = os.path.join(SKILL_DIR, "references", "evidence-bank.md")
        if new and os.path.exists(bank_p):
            bank_n = norm_metric(metric_src(open(bank_p, encoding="utf-8").read()))
            new = [x for x in new if x not in bank_n]
        record(
            "PASS" if not lost else "FAIL",
            "evidence",
            f"{len(base_m) - len(lost)}/{len(base_m)} base metrics present"
            + (f"; lost: {lost}" if lost else ""),
        )
        if new:
            record(
                "WARN",
                "evidence",
                f"metrics in neither the base nor the evidence bank (confirm with user): {new}",
            )
        for par in sorted(set(re.findall(r"\((?:senior|staff)-led[^)]*\)", bbody))):
            if par not in body:
                record(
                    "WARN",
                    "scope",
                    f"the base's attribution {par} is gone: keep an equivalent "
                    f"wherever the claim it qualifies still appears",
                )

    # ---- build hygiene (SKILL.md step 8) ----
    if not re.search(r"^%.*(?:Resume\.tex|base|https?://)", "\n".join(src.splitlines()[:6]), re.I | re.M):
        record("WARN", "render", "no lineage comment at the top of the .tex (base path, posting URL, date)")
    jd = os.path.join(d, "job_description.txt")
    if not os.path.exists(jd):
        record("WARN", "ats", "no job_description.txt in the folder")
    elif len(open(jd, encoding="utf-8", errors="replace").read().split()) < 150:
        record("WARN", "ats", "job_description.txt is under 150 words: save the posting verbatim and whole")

    print("\n--- extracted header (eyeball the centered blocks) ---")
    print("\n".join(lines[:14]))
    return report()


def report():
    print("\n--- gates ---")
    for level, gate, msg in results:
        print(f"[{level}] {gate}: {msg}")
    failed = any(l == "FAIL" for l, _, _ in results)
    print("\nRESULT:", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
