#!/usr/bin/env python3
"""Emit Workflow scripts: ONE AGENT PER CHUNK, fully independent, contract inlined.

Speed design. Every chunk of every volume is its own agent whose first and only
action is a single Write, so there are no file reads, no exploration round trips,
and no prose-to-sheet dependency. Chunks already on disk are skipped, so a rerun
only fills the gaps. Concurrency comes from the number of workflows, since each
workflow runs two agents at a time.
"""
import json, os, sys, glob
from manifest import TIER1, TIER2, CATALOGUE, FORMULAS

SRC = '/home/user/mh370-apush-project/usabo-compendium/source'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/wf'
NWF = int(sys.argv[2]) if len(sys.argv) > 2 else 40
EXAM = ("the USA Biology Olympiad Open Exam, the USABO Semifinal Exam, and the International "
        "Biology Olympiad")

CONTRACT = r"""HOW THIS FILE IS COMPILED. It is \input into a driver that already has the preamble, so
write BODY CONTENT ONLY. These rules are absolute; each one breaks the build.
- Never write \documentclass, \usepackage, \begin{document}, \end{document}, \newcommand,
  \renewcommand, \def, \label, \ref, \cite, \makeindex, \printindex, \tableofcontents,
  \includegraphics, \multirow, tikzpicture, figure, table, or $$...$$.
- PLAIN ASCII ONLY, no Unicode anywhere. Write $\alpha$, $\beta$, $\Delta G$, $\mu$,
  $\rightarrow$, $\rightleftharpoons$, $\times$, $\approx$, $\leq$, $\geq$, $\pm$,
  $37\degc$, $90\dg$, $\sim$. Never paste the character itself.
- In ordinary text escape: \% \& \_ \# \$. An unescaped % eats the rest of the line.
- Inline math $...$, display math \[...\]. Chemistry may use mhchem: \ce{C6H12O6 + 6O2 ->
  6CO2 + 6H2O}, \ce{Na+}, \ce{HCO3-}.
- Close every environment you open. Never nest one box inside another box.
- Tables: plain tabular only, @{} at both ends, \toprule \midrule \bottomrule, p{Xcm} for
  any cell longer than three words, total width under 12cm. \multicolumn is fine.
- No blank line directly after \begin{itemize} or before \end{itemize}, and none inside
  a \[...\] display.

MACROS AVAILABLE TO YOU
- \section{...} and \subsection{...}
- \nr{unique-label}{Name As It Appears In The Index} places an index entry. Put one on
  every named law, formula, structure, pathway, term, value and rule you state.
- Boxes, each with a title, all used as \begin{X}[title={...}] ... \end{X}:
  keybox (MEMORIZE: the facts and formulas to know cold, grey background),
  thmbox (PRINCIPLE: a law or rule stated precisely),
  defbox (DEFINITIONS: several terms at once),
  calcbox (WORKED: a calculation or data interpretation, arithmetic shown, check at end),
  expbox (EXPERIMENT: a landmark experiment, its design, result, and what it established),
  tipbox (TECHNIQUE: how to attack a question, with the trigger that says to use it),
  warnbox (TRAP: a misconception the exam exploits, wrong belief then correction),
  obsbox (WORTH NOTICING: a pattern, a numerical coincidence, a link between topics).
- \tm{term} bold for a term being introduced. \sn{Escherichia coli} italic for a species.
  \ttitle{Lead-in.} a bold run-in heading inside a box. \pref{key} cross-references
  another volume by key. \dg degrees, \degc degrees Celsius.

HOUSE STYLE, copy this density and tone exactly:

\section{Arcs of the example}

\begin{defbox}[title={DEFINITIONS: bonds and forces}]
\nr{stem-bond-types}{Bond types in biology}
A \tm{covalent bond} shares electrons, $348\ \mathrm{kJ\,mol^{-1}}$ for \ce{C-C}. A
\tm{hydrogen bond} is $20\ \mathrm{kJ\,mol^{-1}}$ and water at $25\degc$ holds about $3.4$
of them per molecule.
\end{defbox}

\begin{keybox}[title={MEMORIZE: the water potential equation}]
\nr{stem-water-potential}{Water potential}
\[
\Psi_w=\Psi_s+\Psi_p,\qquad \Psi_s=-iCRT
\]
with $R=8.31\ \mathrm{J\,mol^{-1}\,K^{-1}}$ and $T$ in kelvin. Water moves from high
$\Psi_w$ to low $\Psi_w$, and most lost marks here are sign errors.
\end{keybox}

\begin{calcbox}[title={WORKED: buffer pH}]
A buffer holds $0.10\ \mathrm{M}$ \ce{CH3COOH} and $0.25\ \mathrm{M}$ \ce{CH3COO-}, with
$pK_a=4.76$.
\[
\mathrm{pH}=4.76+\log_{10}\frac{0.25}{0.10}=4.76+0.40=5.16
\]
\ttitle{Check.} More base than acid, so pH must exceed $pK_a$. \tm{$\surd$}
\end{calcbox}

\begin{warnbox}[title={TRAP: osmolarity is not tonicity}]
\nr{stem-tonicity-trap}{Osmolarity against tonicity}
A $300\ \mathrm{mOsm}$ urea solution is iso-osmotic to a cell and still hypotonic, because
urea crosses the membrane. Tonicity counts only the impermeant solutes.
\end{warnbox}

\begin{tabular}{@{}lp{3.2cm}p{4.4cm}@{}}
\toprule
\textbf{Force} & \textbf{Energy} & \textbf{Where it matters}\\
\midrule
Covalent & $200$--$800\ \mathrm{kJ\,mol^{-1}}$ & Backbones and side chains\\
Hydrogen & $4$--$30\ \mathrm{kJ\,mol^{-1}}$ & Base pairing, $\alpha$ helices\\
\bottomrule
\end{tabular}"""

MEMO_CONTRACT = r"""HOW THIS FILE IS COMPILED. It is \input into a driver that already has the preamble, so
write BODY CONTENT ONLY, and only these three macros, repeated. No prose, no boxes, no
\section, no \parttitle, no \usepackage, no \newcommand.

- \memsec{Sub-area heading} opens a block.
- \mem{Name of the thing}{formula, or empty}{one or two sentence note}
  The second argument is ALREADY display math, so write K_m not $K_m$, and \frac{a}{b}
  directly. When the entry has a formula, put it there: the note is then dropped from the
  printed sheet, so the formula must stand alone with its symbols recognisable. When the
  entry is verbal, pass {} for the formula and make the note a COMPLETE standalone
  statement of the fact, because the note is then all that prints.
- \memtable{\begin{tabular}{@{}...@{}} ... \end{tabular}} for a table of values.

Every \mem name becomes an index entry, so the names are the index of the whole
compendium. Write them as a student would look them up.

PLAIN ASCII ONLY, no Unicode. Escape \% \& \_ \# in the note. Inline math $...$ in the
note is fine. Chemistry may use \ce{...}. Close every environment.

HOUSE STYLE, copy this density exactly:

\memsec{Water and solutions}
\mem{Water potential}{\Psi_w=\Psi_s+\Psi_p}{Solute potential plus pressure potential, in MPa. Pure water at atmospheric pressure is $0$.}
\mem{Solute potential}{\Psi_s=-iCRT}{$i$ ionization factor, $C$ molarity, $R=8.31\ \mathrm{J\,mol^{-1}K^{-1}}$, $T$ in kelvin.}
\mem{Tonicity is not osmolarity}{}{Tonicity counts only impermeant solutes, so a $300\ \mathrm{mOsm}$ urea solution is iso-osmotic yet hypotonic.}
\memtable{\begin{tabular}{@{}lrr@{}}\toprule Ion & Inside (mM) & Outside (mM)\\ \midrule \ce{K+} & $140$ & $5$\\ \ce{Na+} & $12$ & $145$\\ \bottomrule\end{tabular}}
\memsec{Acids and buffers}
\mem{Henderson-Hasselbalch}{\mathrm{pH}=pK_a+\log_{10}\frac{[\mathrm{A^-}]}{[\mathrm{HA}]}}{Maximum buffering at $\mathrm{pH}=pK_a$, useful range $pK_a\pm1$.}"""

CAT_CONTRACT = r"""HOW THIS FILE IS COMPILED. It is \input into a driver that already has the preamble, so
write BODY CONTENT ONLY, and only these two macros, repeated. No prose, no boxes, no
\section, no \usepackage, no \newcommand.

- \catsec{Sub-area heading}
- \thm{Name}{Precise statement, with the conditions under which it holds}{optional line on
  origin, use, or the number worth remembering}

PLAIN ASCII ONLY, no Unicode. Escape \% \& \_ \#. Inline math $...$ and \ce{...} allowed.

HOUSE STYLE, copy this density exactly:

\catsec{Means and classical rules}
\thm{Hardy-Weinberg principle}{In an infinite, randomly mating population with no selection, mutation or migration, allele frequencies $p$ and $q$ stay constant and genotype frequencies are $p^2$, $2pq$, $q^2$.}{The null model of population genetics. Departure from it is the evidence that something is acting.}
\thm{Chargaff's rules}{In double-stranded DNA, $A=T$ and $G=C$, so purines equal pyrimidines. The second rule states that the same near-equality holds within a single strand of most genomes.}{The first rule is what the base-pairing model had to explain.}
\thm{Allen's rule}{Within a warm-blooded species, populations in colder climates have shorter extremities relative to body size, reducing surface area for heat loss.}{Compare Bergmann's rule, which is about body size rather than appendages.}"""

PROSE = """Write one file of a LaTeX biology compendium aimed at {exam}.

{contract}

YOUR TASK
Volume: {title}
This file is chunk {chunk} of {nchunks} of that volume. Other writers are producing the other
chunks in parallel, so cover only the ground listed here and do not repeat or pre-empt theirs.

{firstline}Write one \\section per numbered item below, in this order, covering exactly this ground:
{outline}

DENSITY REQUIRED IN THIS FILE
- {nsec} \\section blocks, each holding {nbox} boxes with connecting prose between them.
- At least {nrs} \\nr named results, every label starting "{stem}-" so it is unique compendium-wide.
- At least {traps} warnbox traps, {calcs} calcbox worked calculations with the arithmetic shown and a
  numerical check, {exps} expbox landmark experiments, and {tabs} tabular tables.
- Concrete numbers throughout: concentrations, potentials, rates, yields, sizes, percentages,
  normal values, and the range where sources disagree. A biology volume without numbers is
  useless for this exam.
- Teach the mechanism, name the exam trap, and give the technique with its trigger.
- {chars} characters of LaTeX.

Your FIRST and ONLY action is a single Write tool call to exactly this path:
{path}
Do not read any file. Do not run any command. Do not inspect the directory. Do not create any
other file. Do not run pdflatex. Write the file, then return JSON only."""

MEMO = """Write one file of a LaTeX biology compendium aimed at {exam}. This file is a bare
memorization sheet: the facts and formulas with nothing explained, which a student revises from
the night before the exam and which also feeds the compendium's master index.

{contract}

YOUR TASK
Volume: {title}
This file is sheet {chunk} of {nchunks} for that volume. Other writers produce the volume's prose
and its other sheet in parallel, so cover only the ground listed here.

Group your entries under \\memsec headings that follow this ground, in this order:
{outline}

DENSITY REQUIRED IN THIS FILE
- At least {mems} \\mem entries, plus {tabs} \\memtable tables of values.
- Every formula, constant, normal value, named law, named structure, pathway step and defined
  term belonging to the ground above must appear. Completeness is this file's whole job: an
  entry that is missing here is missing from the compendium's index.
- {formulaheavy}
- {chars} characters.

Your FIRST and ONLY action is a single Write tool call to exactly this path:
{path}
Do not read any file. Do not run any command. Do not create any other file. Write the file,
then return JSON only."""

CAT = """Write one file of a reference catalogue for a LaTeX biology compendium aimed at {exam}.

{contract}

YOUR TASK
Catalogue volume: {title}
This file is part {chunk} of {nchunks}. Other writers produce the other parts in parallel, so stay
inside the sub-areas listed here.

Cover these sub-areas, one \\catsec each, in order:
{outline}

DENSITY REQUIRED IN THIS FILE
- At least {thms} \\thm entries. Be exhaustive: this volume exists so that nothing named in its
  area is missing, so list the obscure alongside the famous.
- Each statement is one to four sentences, self-contained, precise, and carries its numbers.
  No worked examples, no study advice.
- Within a sub-area, order entries from most to least fundamental.
- {chars} characters.

Your FIRST and ONLY action is a single Write tool call to exactly this path:
{path}
Do not read any file. Do not run any command. Do not create any other file. Write the file,
then return JSON only."""

SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"type": "string"},
        "chars": {"type": "integer"},
        "entries": {"type": "integer", "description": "sections, mem entries or thm entries written"},
        "coverage": {"type": "string", "description": "one line: anything from the outline you could not fit"},
    },
    "required": ["path", "chars", "entries"],
}


def numbered(items, start=1):
    return '\n'.join('%d. %s' % (i, s) for i, s in enumerate(items, start))


def split(items, n):
    out, i, total = [], 0, len(items)
    for k in range(n):
        size = (total - i + (n - k - 1)) // (n - k)
        out.append(items[i:i + size])
        i += size
    return out


def exists(path):
    return os.path.exists(path) and os.path.getsize(path) > 8000


def volume_jobs(num, title, stem, key, subtitle, oa, ob, formula=False):
    items = list(oa) + list(ob)
    jobs = []
    groups = split(items, 3)
    offset = 1
    for i, g in enumerate(groups, 1):
        path = '%s/sections/%s-%d.tex' % (SRC, stem, i)
        first = ('The first line of this file must be exactly:\n'
                 '\\parttitle[%s]{%s}{%s}\n\n' % (key, title, subtitle)) if i == 1 else \
                'This file starts straight into its first \\section, with no \\parttitle.\n\n'
        if not exists(path):
            jobs.append({"label": '%s-s%d' % (stem, i), "path": path,
                         "prompt": PROSE.format(exam=EXAM, contract=CONTRACT, title=title, chunk=i,
                                                nchunks=3, firstline=first,
                                                outline=numbered(g, offset), nsec=len(g),
                                                nbox='4 to 8', nrs=45, traps=3, calcs=3 if formula else 2,
                                                exps=1 if formula else 2, tabs=4, stem=stem,
                                                chars='30000 to 40000', path=path)})
        offset += len(g)
    mgroups = split(items, 2)
    for i, g in enumerate(mgroups, 1):
        path = '%s/memo/%s-%d.tex' % (SRC, stem, i)
        if not exists(path):
            jobs.append({"label": '%s-m%d' % (stem, i), "path": path,
                         "prompt": MEMO.format(exam=EXAM, contract=MEMO_CONTRACT, title=title,
                                               chunk=i, nchunks=2, outline=numbered(g, 1 if i == 1 else len(mgroups[0]) + 1),
                                               mems=115, tabs=5, chars='24000 to 32000', path=path,
                                               formulaheavy=('Nearly every entry here has a formula, so the second '
                                                             'argument is filled in almost always, with the symbols '
                                                             'defined in the note.') if formula else
                                                            ('Fill the formula argument wherever a quantitative '
                                                             'relationship exists, and use the note for the rest.'))})
    return jobs


def cat_jobs(num, title, stem, key, subtitle, ca, cb):
    jobs = []
    n = 1
    for outline in (ca, cb):
        for g in split(list(outline), 2):
            path = '%s/catalogue/%s-c%d.tex' % (SRC, stem, n)
            if not exists(path):
                jobs.append({"label": '%s-c%d' % (stem, n), "path": path,
                             "prompt": CAT.format(exam=EXAM, contract=CAT_CONTRACT, title=title,
                                                  chunk=n, nchunks=4, outline=numbered(g),
                                                  thms=110, chars='55000 to 70000', path=path)})
            n += 1
    return jobs


SCRIPT = """export const meta = {{
  name: {name},
  description: {desc},
  phases: [{{ title: 'Write' }}],
}}
const SCHEMA = {schema}
const JOBS = {jobs}
const out = await parallel(JOBS.map(j => () => agent(j.prompt, {{ label: j.label, phase: 'Write', schema: SCHEMA }})))
return out.map((r, i) => ({{ label: JOBS[i].label, ok: !!r, result: r }}))
"""


def emit(name, desc, jobs):
    path = os.path.join(OUT, name + '.js')
    with open(path, 'w') as fh:
        fh.write(SCRIPT.format(name=json.dumps(name), desc=json.dumps(desc),
                               schema=json.dumps(SCHEMA), jobs=json.dumps(jobs, indent=1)))
    return path, len(jobs)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, '*.js')):
        os.remove(f)
    alljobs = []
    for v in TIER1 + TIER2:
        alljobs += volume_jobs(*v)
    for v in FORMULAS:
        alljobs += volume_jobs(*v, formula=True)
    for v in CATALOGUE:
        alljobs += cat_jobs(*v)
    # interleave so each workflow mixes prose, sheets and catalogue rather than
    # queueing all the long files behind each other
    alljobs = [alljobs[i] for i in sorted(range(len(alljobs)), key=lambda i: (i % NWF, i))]
    buckets = [[] for _ in range(NWF)]
    for i, j in enumerate(alljobs):
        buckets[i % NWF].append(j)
    plan = []
    for i, b in enumerate(buckets, 1):
        if b:
            plan.append(emit('w%02d' % i, 'Compendium content batch %d of %d' % (i, NWF), b))
    for p, n in plan:
        print('%s %d' % (os.path.basename(p), n))
    print('%d workflows, %d chunk jobs, %d concurrent agents' % (len(plan), sum(n for _, n in plan), 2 * len(plan)))
