#!/usr/bin/env python3
"""Emit one Workflow script per batch of volumes. Each volume gets a prose agent then a sheet agent."""
import json, os, sys
from manifest import TIER1, TIER2, CATALOGUE, FORMULAS

SRC = '/home/user/mh370-apush-project/usabo-compendium/source'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/wf'
GUIDE = SRC + '/STYLE-GUIDE.md'

EXAM = ("the USA Biology Olympiad Open Exam, the USABO Semifinal Exam, and the International Biology "
        "Olympiad")

PROSE = """Write one prose teaching volume of a LaTeX biology compendium aimed at {exam}.

STEP 1. Read {guide} in full. It is the binding contract for this file; every rule in it breaks the build if ignored.
STEP 2. Read {example} for the house style. It is a six page stub. Yours is a full volume, twenty times longer.

VOLUME: {title}
The very first line of your file must be exactly:
\\parttitle[{key}]{{{title}}}{{{subtitle}}}

COVER EXACTLY THIS GROUND, one \\section per numbered item, in this order:
{outline}

REQUIREMENTS
- One \\section per outline item, same order, same scope. Do not merge, drop, or reorder items.
- Inside each \\section: 4 to 8 boxes (keybox, thmbox, defbox, calcbox, expbox, tipbox, warnbox, obsbox) with connecting prose between them. Choose the box whose job matches the content.
- At least 120 \\nr{{...}}{{...}} named results across the file. Every label must start with "{stem}-" so it stays unique across the compendium.
- At least 8 warnbox traps, 6 calcbox worked calculations with the arithmetic shown and a numerical check, 4 expbox landmark experiments, and 10 tabular tables.
- Numbers everywhere: concentrations, potentials, rates, yields, sizes, percentages, normal values, and the ranges where sources disagree. A biology volume without numbers is worthless for this exam.
- Name the exam trap wherever one exists. Explain mechanism, never just terminology.
- Plain ASCII only. Escape %, &, _, #. Math in $...$ or \\[...\\]. Chemistry may use \\ce{{...}}.
- Target 70000 to 95000 characters of LaTeX. This is a complete teaching text.

Write the file with the Write tool to exactly this path:
{path}
Then run: grep -c '\\\\section' on it, wc -c on it, and grep -n 'usepackage\\|documentclass\\|begin{{document}}\\|newcommand' on it. If that last grep finds anything, fix the file. Create no other file. Do not run pdflatex.

Return JSON only."""

MEMO = """Write the bare memorization sheet that accompanies one volume of a LaTeX biology compendium aimed at {exam}.

STEP 1. Read {guide} in full, especially the section on memorization sheet files, and read {memoexample} for the house format.
STEP 2. Read the prose volume this sheet must mirror: {source}
Every named result, formula, value, term, table and number in that file must appear in your sheet. The sheet is what a student revises from the night before the exam, so nothing may be missing and no entry may need the prose to make sense.

VOLUME: {title}

REQUIREMENTS
- Use only \\memsec, \\mem and \\memtable. No prose, no boxes, no \\section, no \\parttitle.
- \\memsec headings follow the \\section order of the prose file.
- At least {mems} \\mem entries.
- \\mem{{name}}{{formula}}{{note}}: the second argument is display math already, so write K_m not $K_m$. When the entry has a formula, put it there and the note is dropped from the bare sheet, so the formula must stand alone. When the entry is verbal, pass {{}} and make the note a complete standalone statement of the fact.
- Carry over every table of values as \\memtable with a tabular inside.
- Plain ASCII only. Escape %, &, _, # in the note argument.
- Target {chars} characters.

Write the file with the Write tool to exactly this path:
{path}
Then run: grep -c '\\\\mem{{' on it and wc -c on it. Create no other file.

Return JSON only."""

CAT = """Write one part of a reference catalogue volume for a LaTeX biology compendium aimed at {exam}.

STEP 1. Read {guide} in full, especially the section on catalogue files.

CATALOGUE VOLUME: {title}
YOUR PART: part {ab} of two.

COVER EXACTLY THESE SUB-AREAS, one \\catsec each, in order:
{outline}

REQUIREMENTS
- Use only \\catsec and \\thm. No prose, no boxes, no \\section, no \\parttitle.
- \\thm{{Name}}{{Precise statement with the conditions under which it holds}}{{optional line on origin, use, or the number worth remembering}}
- At least 200 \\thm entries. Be exhaustive: this volume's job is that nothing named in this area is missing.
- Each statement is one to four sentences, self-contained, precise, with the numbers. No worked examples.
- Entries are sorted into the sub-areas above, and within a sub-area ordered from most to least fundamental.
- Plain ASCII only. Escape %, &, _, #. Math in $...$. Chemistry may use \\ce{{...}}.
- Target 90000 to 130000 characters.

Write the file with the Write tool to exactly this path:
{path}
Then run: grep -c '\\\\thm{{' on it and wc -c on it. Create no other file.

Return JSON only."""

SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"type": "string"},
        "chars": {"type": "integer"},
        "entries": {"type": "integer", "description": "count of sections, mem entries, or thm entries"},
        "coverage": {"type": "string", "description": "one line: anything from the outline you could not cover"},
    },
    "required": ["path", "chars", "entries"],
}

EXAMPLE = SRC + '/EXAMPLE-section.tex'


def numbered(items):
    return '\n'.join('%d. %s' % (i + 1, s) for i, s in enumerate(items))


def prose_job(num, title, stem, key, subtitle, oa, ob):
    return {
        "stem": stem,
        "label": stem,
        "prose": PROSE.format(exam=EXAM, guide=GUIDE, example=EXAMPLE, title=title, key=key,
                              subtitle=subtitle, outline=numbered(list(oa) + list(ob)), stem=stem,
                              path='%s/sections/%s.tex' % (SRC, stem)),
        "memo": MEMO.format(exam=EXAM, guide=GUIDE, memoexample=SRC + '/EXAMPLE-memo.tex', source='%s/sections/%s.tex' % (SRC, stem),
                            title=title, mems=180, chars='40000 to 60000',
                            path='%s/memo/%s.tex' % (SRC, stem)),
    }


def cat_jobs(num, title, stem, key, subtitle, ca, cb):
    jobs = []
    for ab, outline in (('a', ca), ('b', cb)):
        jobs.append({
            "stem": '%s-%s' % (stem, ab),
            "label": '%s-%s' % (stem, ab),
            "prose": CAT.format(exam=EXAM, guide=GUIDE, title=title, ab=ab.upper(),
                                outline=numbered(outline),
                                path='%s/catalogue/%s-%s.tex' % (SRC, stem, ab)),
            "memo": None,
        })
    return jobs


SCRIPT = """export const meta = {{
  name: {name},
  description: {desc},
  phases: [{{ title: 'Prose' }}, {{ title: 'Sheet' }}],
}}
const SCHEMA = {schema}
const JOBS = {jobs}
const out = await pipeline(
  JOBS,
  j => agent(j.prose, {{ label: 'write:' + j.label, phase: 'Prose', schema: SCHEMA }}),
  (r, j) => j.memo ? agent(j.memo, {{ label: 'sheet:' + j.label, phase: 'Sheet', schema: SCHEMA }}) : r
)
return out
"""


def emit(name, desc, jobs):
    path = os.path.join(OUT, name + '.js')
    with open(path, 'w') as fh:
        fh.write(SCRIPT.format(name=json.dumps(name), desc=json.dumps(desc),
                               schema=json.dumps(SCHEMA), jobs=json.dumps(jobs, indent=1)))
    return path, len(jobs)


def chunks(seq, n):
    return [seq[i:i + n] for i in range(0, len(seq), n)]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    plan = []
    for i, group in enumerate(chunks([prose_job(*v) for v in TIER1], 7), 1):
        plan.append(emit('usabo-core-%d' % i, 'Core syllabus volumes, batch %d: prose then memorization sheet' % i, group))
    for i, group in enumerate(chunks([prose_job(*v) for v in TIER2], 5), 1):
        plan.append(emit('usabo-beyond-%d' % i, 'Beyond-the-syllabus volumes, batch %d' % i, group))
    for i, group in enumerate(chunks([prose_job(*v) for v in FORMULAS], 7), 1):
        plan.append(emit('usabo-formulas-%d' % i, 'Formula volumes, batch %d: derivations then bare formula sheet' % i, group))
    catj = [j for v in CATALOGUE for j in cat_jobs(*v)]
    for i, group in enumerate(chunks(catj, 7), 1):
        plan.append(emit('usabo-catalogue-%d' % i, 'Reference catalogue parts, batch %d' % i, group))
    for p, n in plan:
        print('%-70s %d jobs' % (p, n))
    print('%d workflows, %d volumes-or-parts' % (len(plan), sum(n for _, n in plan)))
