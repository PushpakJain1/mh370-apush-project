#!/usr/bin/env python3
"""Stage the two deliverable trees from the built PDFs, and write each README."""
import os, shutil, subprocess, sys
from manifest import TIER1, TIER2, CATALOGUE, FORMULAS
from tools_build_drivers import volume_map, volume_filename

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
STAGE = os.path.join(ROOT, 'stage')

CONCEPTS = 'USABO-Biology-Concepts'
FORMULAE = 'USABO-Biology-Formulas'


def pages(p):
    try:
        out = subprocess.run(['pdfinfo', p], capture_output=True, text=True).stdout
        for line in out.splitlines():
            if line.startswith('Pages:'):
                return int(line.split()[1])
    except Exception:
        pass
    return None


def built(driver):
    base = os.path.basename(driver)[:-4]
    return os.path.join(SRC, 'build', driver.replace('/', '_'), base + '.pdf')


def place(driver, dest_dir, dest_name):
    srcpdf = built(driver)
    if not os.path.exists(srcpdf):
        return None
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, dest_name)
    shutil.copyfile(srcpdf, dest)
    return dest


def stage():
    if os.path.exists(STAGE):
        shutil.rmtree(STAGE)
    cdir = os.path.join(STAGE, CONCEPTS)
    fdir = os.path.join(STAGE, FORMULAE)
    os.makedirs(cdir); os.makedirs(fdir)
    report = {'concepts': [], 'formulas': [], 'missing': []}

    place('main-index-concepts.tex', cdir, '00-Everything-Indexed.pdf') or report['missing'].append('index-concepts')
    place('how-to-learn.tex', cdir, '00-How-to-Learn-All-of-This.pdf') or report['missing'].append('how-to-learn')
    place('main-index-formulas.tex', fdir, '00-Every-Formula-Indexed.pdf') or report['missing'].append('index-formulas')
    place('how-to-use-formulas.tex', fdir, '00-How-to-Use-These-Formulas.pdf') or report['missing'].append('how-to-use')

    for folder, base, driver in volume_map():
        if folder == '01-Formula-Volumes':
            dest = os.path.join(fdir, '01-Volumes')
            bucket = 'formulas'
        else:
            dest = os.path.join(cdir, '01-Volumes', folder)
            bucket = 'concepts'
        got = place(driver, dest, base + '.pdf')
        if got:
            report[bucket].append((folder, base, pages(got)))
        else:
            report['missing'].append(driver)

    for tree, name in ((cdir, CONCEPTS), (fdir, FORMULAE)):
        dst = os.path.join(tree, 'source')
        shutil.copytree(SRC, dst, ignore=shutil.ignore_patterns('build', '__pycache__', '*.pyc'))
    return report


TIER_BLURB = {
    '01-Core-Syllabus': ('01-Core-Syllabus', len(TIER1),
        'the syllabus itself, in dependency order. Each volume teaches one topic in part one and gives the\n'
        'bare memorization sheet for the same material in part two, then its own index.'),
    '02-Beyond-the-Syllabus': ('02-Beyond-the-Syllabus', len(TIER2),
        'the depth past the Open Exam that the Semifinal Exam and the IBO reach for, including the practical\n'
        'exam volume.'),
    '03-Reference-Catalogue': ('03-Reference-Catalogue', len(CATALOGUE),
        'reference volumes. Every named law, pathway, molecule, gene, hormone, experiment, taxon and term in\n'
        'an area, each stated precisely. For looking things up and for training recognition.'),
}


def write_readmes(report):
    cdir = os.path.join(STAGE, CONCEPTS)
    fdir = os.path.join(STAGE, FORMULAE)
    cvol = len(report['concepts']); cpg = sum(p or 0 for _, _, p in report['concepts'])
    fvol = len(report['formulas']); fpg = sum(p or 0 for _, _, p in report['formulas'])
    ipg = pages(os.path.join(cdir, '00-Everything-Indexed.pdf')) or 0
    hpg = pages(os.path.join(cdir, '00-How-to-Learn-All-of-This.pdf')) or 0
    fipg = pages(os.path.join(fdir, '00-Every-Formula-Indexed.pdf')) or 0
    fhpg = pages(os.path.join(fdir, '00-How-to-Use-These-Formulas.pdf')) or 0

    lines = []
    for folder in ('01-Core-Syllabus', '02-Beyond-the-Syllabus', '03-Reference-Catalogue'):
        rows = [r for r in report['concepts'] if r[0] == folder]
        if not rows:
            continue
        lines.append('\n### 01-Volumes/%s' % folder)
        for _, base, pg in rows:
            lines.append('- %s  (%s pages)' % (base, pg))
    head = """# The USABO Biology Compendium: Concepts

Everything the USA Biology Olympiad and the International Biology Olympiad can ask,
taught topic by topic. {cvol} volumes, {cpg} pages, plus the index of everything.

There is a companion zip, **USABO-Biology-Formulas**, holding every equation and
calculation. This zip is the concepts. Nothing here is a single thousand page file you
have to scroll through: the material is split by topic so that one volume is one
sitting's worth of one subject.

## The two files at the top level

- `00-Everything-Indexed.pdf`  ({ipg} pages). Every fact, term, structure, pathway,
  organism and named result in the whole compendium, stated once, with nothing
  explained. The body is ordered by topic, tier by tier and volume by volume, exactly as
  the volumes are, so it reads as one continuous course; the alphabetical index of every
  name is at the back, for when you know the word and want the page. This is the revision
  file and the lookup file, and it is generated from the same sources as the volumes, so
  the two can never disagree.
- `00-How-to-Learn-All-of-This.pdf`  ({hpg} pages). Which file to open, the order to
  learn the topics in, what to memorise against what to derive, and a twelve week plan
  with a four week compression.

## The folder

`01-Volumes` holds everything else, in three tiers.

- `01-Core-Syllabus` is {n1} volumes: {b1}
- `02-Beyond-the-Syllabus` is {n2} volumes: {b2}
- `03-Reference-Catalogue` is {n3} volumes: {b3}

Every volume carries its own index. `source` holds the LaTeX for all of it: compile any
driver from inside that folder with `pdflatex`, run `makeindex` on the `.idx`, then
`pdflatex` twice more, or just run `./build-all.sh`.

## The volumes
""".format(cvol=cvol, cpg=cpg, ipg=ipg, hpg=hpg,
           n1=TIER_BLURB['01-Core-Syllabus'][1], b1=TIER_BLURB['01-Core-Syllabus'][2],
           n2=TIER_BLURB['02-Beyond-the-Syllabus'][1], b2=TIER_BLURB['02-Beyond-the-Syllabus'][2],
           n3=TIER_BLURB['03-Reference-Catalogue'][1], b3=TIER_BLURB['03-Reference-Catalogue'][2])
    open(os.path.join(cdir, 'README.md'), 'w').write(head + '\n'.join(lines) + '\n')

    flines = ['\n### 01-Volumes']
    for _, base, pg in report['formulas']:
        flines.append('- %s  (%s pages)' % (base, pg))
    fhead = """# The USABO Biology Compendium: Formulas

Every equation, constant and calculation biology asks for at olympiad level, derived and
worked. {fvol} volumes, {fpg} pages, plus the index of every formula.

There is a companion zip, **USABO-Biology-Concepts**, holding the topics themselves.
This zip is the mathematics: the same exams that ask what a nephron does also ask you to
compute a clearance, a Hardy-Weinberg frequency, a Nernst potential and a chi-square
statistic, and that is what is in here.

## The two files at the top level

- `00-Every-Formula-Indexed.pdf`  ({fipg} pages). Every equation, law, constant and
  normal value in the whole compendium, stated once with its symbols defined and nothing
  derived. The body is ordered by subject, subject by subject in the same order as the
  volumes, so you can work through one area at a time; the alphabetical index of every
  formula name is at the back, for when you know the name and want the page.
- `00-How-to-Use-These-Formulas.pdf`  ({fhpg} pages). Which formula the exam is asking
  for, how to recognise it from the wording, what to memorise against what to derive,
  and the unit and sanity checks that catch a wrong answer.

## The folder

`01-Volumes` holds everything else: {fvol} volumes, one per quantitative area. Each one
derives every formula in its area, states the conditions under which it holds, and works
the calculations in part one, then gives the bare formula sheet for the same material in
part two.

Every volume carries its own index. `source` holds the LaTeX for all of it.

## The volumes
""".format(fvol=fvol, fpg=fpg, fipg=fipg, fhpg=fhpg)
    open(os.path.join(fdir, 'README.md'), 'w').write(fhead + '\n'.join(flines) + '\n')
    return cvol, cpg, fvol, fpg


if __name__ == '__main__':
    rep = stage()
    c, cp, f, fp = write_readmes(rep)
    print('concepts: %d volumes, %d pages' % (c, cp))
    print('formulas: %d volumes, %d pages' % (f, fp))
    if rep['missing']:
        print('MISSING (%d):' % len(rep['missing']))
        for m in rep['missing']:
            print('  ' + m)
