#!/usr/bin/env python3
"""Emit one Workflow script per batch of volumes.

Each volume gets a prose agent, which writes its volume in three numbered chunk files,
then a sheet agent, which writes the matching memorization sheet in two chunk files.
Chunking means an interrupted agent loses one chunk, not a whole volume, and it keeps
each single Write inside a comfortable response size.
"""
import json, os, sys
from manifest import TIER1, TIER2, CATALOGUE, FORMULAS

SRC = '/home/user/mh370-apush-project/usabo-compendium/source'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/wf'
GUIDE = SRC + '/STYLE-GUIDE.md'
EXAM = ("the USA Biology Olympiad Open Exam, the USABO Semifinal Exam, and the International "
        "Biology Olympiad")

HYGIENE = """- Plain ASCII only: no Unicode at all. Write $\\alpha$, $\\rightarrow$, $\\times$, $\\approx$, $\\leq$, $\\pm$, $37\\degc$, $10\\dg$, never the character itself.
- Escape %, &, _, # and $ in ordinary text. An unescaped %% eats the rest of the line.
- Math in $...$ or \\[...\\], never $$...$$. Chemistry may use \\ce{...}.
- No \\usepackage, \\documentclass, \\begin{document}, \\newcommand, \\label, \\ref, \\includegraphics, tikzpicture, figure, table float, or \\multirow.
- Every environment you open, you close. Never nest one box inside another."""

PROSE = """Write chunk {chunk} of 3 of one prose teaching volume of a LaTeX biology compendium aimed at {exam}.

{step1}
VOLUME: {title}
YOUR CHUNK: this file carries outline items {span} of the volume's {total}. The other chunks are written by you in the same run, in order, so do not repeat or pre-empt their material.

{firstline}COVER EXACTLY THIS GROUND, one \\section per numbered item, in this order:
{outline}

REQUIREMENTS FOR THIS CHUNK
- One \\section per outline item above, same order, same scope. Do not merge, drop or reorder.
- Inside each \\section: 4 to 8 boxes (keybox, thmbox, defbox, calcbox, expbox, tipbox, warnbox, obsbox) with connecting prose between them. Pick the box whose job matches the content.
- At least {nrs} \\nr{{label}}{{Index Name}} named results in this chunk. Every label starts with "{stem}-" so it is unique across the compendium.
- At least {traps} warnbox traps, {calcs} calcbox worked calculations with the arithmetic shown and a numerical check, {exps} expbox landmark experiments, and {tabs} tabular tables in this chunk.
- Numbers everywhere: concentrations, potentials, rates, yields, sizes, percentages, normal values, and the range where sources disagree. A biology volume without numbers is useless for this exam.
- Name the exam trap wherever one exists. Teach mechanism, never terminology alone.
{hygiene}
- Target {chars} characters for this chunk.

Write it with the Write tool to exactly:
{path}

Then write the next chunk, in the same way, to its own path. The three paths are:
{allpaths}

After all three exist, run wc -c on each and grep -c '\\\\section' on each, and grep -n 'usepackage\\|documentclass\\|newcommand' across all three, fixing anything that grep finds. Create no other file. Do not run pdflatex.

Return JSON only, reporting the totals across all three files."""

MEMO = """Write the bare memorization sheet for one volume of a LaTeX biology compendium aimed at {exam}, in two chunk files.

STEP 1. Read {guide} in full, especially the part on memorization sheet files, then read {memoexample} for the house format.
STEP 2. Read all three prose chunks this sheet must mirror:
{sources}
Every named result, formula, value, term, table and number in those files must appear in your sheet. This sheet is what a student revises from the night before the exam: nothing may be missing and no entry may need the prose to make sense.

VOLUME: {title}

REQUIREMENTS
- Use only \\memsec, \\mem and \\memtable. No prose, no boxes, no \\section, no \\parttitle.
- \\memsec headings follow the \\section order of the prose chunks. File 1 covers the first prose chunk and the first half of the second; file 2 covers the rest.
- At least {mems} \\mem entries per file.
- \\mem{{name}}{{formula}}{{note}}: the second argument is already display math, so write K_m not $K_m$. When there is a formula, put it there, because the note is then dropped from the bare sheet and the formula must stand alone. When the fact is verbal, pass {{}} and make the note a complete standalone statement.
- Carry over every table of values as \\memtable with a tabular inside.
{hygiene}
- Target {chars} characters per file.

Write the two files with the Write tool to exactly these paths, in order:
{allpaths}

Then run grep -c '\\\\mem{{' and wc -c on each. Create no other file.

Return JSON only, reporting the totals across both files."""

CAT = """Write part {ab} of a reference catalogue volume for a LaTeX biology compendium aimed at {exam}, in two chunk files.

STEP 1. Read {guide} in full, especially the part on catalogue files.

CATALOGUE VOLUME: {title}
YOUR PART: part {ab} of two. The other part is written by a different agent, so stay inside the sub-areas listed here.

COVER EXACTLY THESE SUB-AREAS, one \\catsec each, in order. File 1 takes sub-areas 1 and 2, file 2 takes sub-areas 3 and 4:
{outline}

REQUIREMENTS
- Use only \\catsec and \\thm. No prose, no boxes, no \\section, no \\parttitle.
- \\thm{{Name}}{{Precise statement, with the conditions under which it holds}}{{optional line on origin, use, or the number worth remembering}}
- At least 110 \\thm entries per file. Be exhaustive: this volume's job is that nothing named in its area is missing.
- Each statement is one to four sentences, self-contained, precise, with the numbers. No worked examples.
- Within a sub-area, order entries from most to least fundamental.
{hygiene}
- Target 55000 to 70000 characters per file.

Write the two files with the Write tool to exactly these paths, in order:
{allpaths}

Then run grep -c '\\\\thm{{' and wc -c on each. Create no other file.

Return JSON only, reporting the totals across both files."""

SCHEMA = {
    "type": "object",
    "properties": {
        "files_written": {"type": "integer"},
        "chars_total": {"type": "integer"},
        "entries_total": {"type": "integer", "description": "sections, mem entries or thm entries across all files"},
        "coverage": {"type": "string", "description": "one line: anything from the outline you could not cover"},
    },
    "required": ["files_written", "chars_total", "entries_total"],
}

STEP1 = ("STEP 1. Read %s in full. It is the binding contract for this file and every rule in it "
         "breaks the build if ignored.\nSTEP 2. Read %s for the house style. It is a six page stub; "
         "a full volume is twenty times longer.\n\n" % (GUIDE, SRC + '/EXAMPLE-section.tex'))


def numbered(items, start=1):
    return '\n'.join('%d. %s' % (i, s) for i, s in enumerate(items, start))


def split3(items):
    n = len(items)
    a = (n + 2) // 3
    b = (n - a + 1) // 2
    return items[:a], items[a:a + b], items[a + b:]


def prose_job(num, title, stem, key, subtitle, oa, ob):
    items = list(oa) + list(ob)
    groups = split3(items)
    paths = ['%s/sections/%s-%d.tex' % (SRC, stem, i) for i in (1, 2, 3)]
    allpaths = '\n'.join('  chunk %d: %s' % (i + 1, p) for i, p in enumerate(paths))
    chunks = []
    offset = 1
    for i, g in enumerate(groups, 1):
        span = '%d to %d' % (offset, offset + len(g) - 1)
        first = ('The very first line of this file must be exactly:\n'
                 '\\parttitle[%s]{%s}{%s}\n\n' % (key, title, subtitle)) if i == 1 else \
                'This file starts straight into its first \\section, with no \\parttitle.\n\n'
        chunks.append(PROSE.format(chunk=i, exam=EXAM, step1=STEP1 if i == 1 else '', title=title,
                                   span=span, total=len(items), firstline=first,
                                   outline=numbered(g, offset), stem=stem, nrs=45, traps=3,
                                   calcs=2, exps=2, tabs=4, hygiene=HYGIENE,
                                   chars='28000 to 38000', path=paths[i - 1], allpaths=allpaths))
        offset += len(g)
    mpaths = ['%s/memo/%s-%d.tex' % (SRC, stem, i) for i in (1, 2)]
    memo = MEMO.format(exam=EXAM, guide=GUIDE, memoexample=SRC + '/EXAMPLE-memo.tex',
                       sources='\n'.join('  ' + p for p in paths), title=title, mems=110,
                       hygiene=HYGIENE, chars='24000 to 32000',
                       allpaths='\n'.join('  file %d: %s' % (i + 1, p) for i, p in enumerate(mpaths)))
    return {"stem": stem, "label": stem, "prose": '\n\n=====\n\n'.join(chunks), "memo": memo}


def cat_jobs(num, title, stem, key, subtitle, ca, cb):
    jobs = []
    for ab, outline in (('a', ca), ('b', cb)):
        paths = ['%s/catalogue/%s-%s%d.tex' % (SRC, stem, ab, i) for i in (1, 2)]
        jobs.append({
            "stem": '%s-%s' % (stem, ab),
            "label": '%s-%s' % (stem, ab),
            "prose": CAT.format(exam=EXAM, guide=GUIDE, title=title, ab=ab.upper(),
                                outline=numbered(outline), hygiene=HYGIENE,
                                allpaths='\n'.join('  file %d: %s' % (i + 1, p) for i, p in enumerate(paths))),
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
    for i, g in enumerate(chunks([prose_job(*v) for v in TIER1], 7), 1):
        plan.append(emit('usabo-core-%d' % i, 'Core syllabus volumes, batch %d' % i, g))
    for i, g in enumerate(chunks([prose_job(*v) for v in TIER2], 5), 1):
        plan.append(emit('usabo-beyond-%d' % i, 'Beyond-the-syllabus volumes, batch %d' % i, g))
    for i, g in enumerate(chunks([prose_job(*v) for v in FORMULAS], 7), 1):
        plan.append(emit('usabo-formulas-%d' % i, 'Formula volumes, batch %d' % i, g))
    catj = [j for v in CATALOGUE for j in cat_jobs(*v)]
    for i, g in enumerate(chunks(catj, 7), 1):
        plan.append(emit('usabo-catalogue-%d' % i, 'Reference catalogue parts, batch %d' % i, g))
    for p, n in plan:
        print('%-46s %d jobs' % (os.path.basename(p), n))
    print('%d workflows, %d jobs' % (len(plan), sum(n for _, n in plan)))
