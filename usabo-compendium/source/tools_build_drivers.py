#!/usr/bin/env python3
"""Generate every driver .tex from the manifest: one per volume, plus the two master indexes."""
import os
from manifest import TIER1, TIER2, CATALOGUE, FORMULAS

SRC = os.path.dirname(os.path.abspath(__file__))

TIERS = [
    ("TIER ONE. THE CORE SYLLABUS", "01-Core-Syllabus", TIER1,
     "Part one teaches the topic and works the methods. Part two is the bare memorization sheet for the\n"
     "same material, every fact and formula stated once with no commentary. The index at the back covers both."),
    ("TIER TWO. BEYOND THE SYLLABUS", "02-Beyond-the-Syllabus", TIER2,
     "Part one teaches the topic in the depth the Semifinal Exam and the IBO reach for. Part two is the\n"
     "bare memorization sheet for the same material. The index at the back covers both."),
    ("THE FORMULA VOLUMES", "01-Formula-Volumes", FORMULAS,
     "Part one derives every formula, states its conditions, and works the calculations. Part two is the\n"
     "bare formula sheet for the same material. The index at the back covers both."),
]

HEAD = r"""\input{preamble}
\input{partnames}
\input{memomacros}
\input{sheetstyle}
\makeindex[title={Index of This Volume},columns=2,intoc]
\begin{document}
\begin{titlepage}\thispagestyle{empty}
\vspace*{0.14\textheight}
\noindent{\color{%RULE%}\rule{\textwidth}{5pt}}\\[3pt]
\noindent{\color{bioline}\rule{\textwidth}{1pt}}\\[26pt]
\noindent{\sffamily\bfseries\fontsize{11}{14}\selectfont\color{bionum}%TIERLABEL%}\\[12pt]
\noindent\begin{minipage}{\textwidth}\raggedright
{\sffamily\bfseries\fontsize{28}{32}\selectfont\color{bioink}%
 \hyphenchar\font=-1\hyphenpenalty=10000\exhyphenpenalty=10000 %TITLE%\par}\end{minipage}\\[16pt]
\noindent{\color{biogreen}\rule{\textwidth}{1.4pt}}\\[10pt]
\noindent\begin{minipage}{\textwidth}\raggedright
{\fontsize{10.5}{14}\selectfont\color{biogreen}%
%BLURB%\par}\end{minipage}
\vfill
\noindent{\color{bioline}\rule{\textwidth}{1pt}}\\[3pt]
\noindent{\color{%RULE%}\rule{\textwidth}{5pt}}
\end{titlepage}
\tableofcontents
\clearpage
"""

TAIL = "\\clearpage\n\\printindex\n\\end{document}\n"

CAT_BLURB = ("Every named entry in this area, each with its precise statement, its conditions, and a line on\n"
             "where it is used. This is a reference to look things up in and to train recognition with, not a\n"
             "chapter to read straight through.")


def slug(title):
    out = title.replace(' ', '-')
    for ch in ",:'()":
        out = out.replace(ch, '')
    while '--' in out:
        out = out.replace('--', '-')
    return out


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fh:
        fh.write(text)


def volume_filename(num, title):
    return '%s-%s.tex' % (num, slug(title))


def build_volumes():
    made = []
    for label, folder, entries, blurb in TIERS:
        rule = 'tierbeyond' if folder.startswith('02') else 'tiercore'
        for num, title, stem, key, subtitle, oa, ob in entries:
            body = (HEAD.replace('%TITLE%', title).replace('%TIERLABEL%', label)
                        .replace('%BLURB%', blurb).replace('%RULE%', rule))
            body += '\\memtier{Part One. Learn It}\n'
            for c in (1, 2, 3):
                body += '\\InputIfFileExists{sections/%s-%d}{}{}\n' % (stem, c)
            body += '\\memtier{Part Two. Memorize It}\n'
            for c in (1, 2):
                body += '\\InputIfFileExists{memo/%s-%d}{}{}\n' % (stem, c)
            body += TAIL
            p = os.path.join(SRC, 'topics', folder, volume_filename(num, title))
            write(p, body)
            made.append(os.path.relpath(p, SRC))
    for num, title, stem, key, subtitle, ca, cb in CATALOGUE:
        body = (HEAD.replace('%TITLE%', title).replace('%TIERLABEL%', 'THE REFERENCE CATALOGUE')
                    .replace('%BLURB%', CAT_BLURB).replace('%RULE%', 'tiercat'))
        for c in ('a1', 'a2', 'b1', 'b2'):
            body += '\\InputIfFileExists{catalogue/%s-%s}{}{}\n' % (stem, c)
        body += TAIL
        p = os.path.join(SRC, 'topics', '03-Reference-Catalogue', volume_filename(num, title))
        write(p, body)
        made.append(os.path.relpath(p, SRC))
    return made


def build_partnames():
    lines = ['% Part display names, so a cross reference into a part that is not in this volume degrades',
             '% to the part\'s name in italics instead of a dangling question mark.',
             '\\makeatletter']
    for entries in (TIER1, TIER2, FORMULAS, CATALOGUE):
        for num, title, stem, key, subtitle, a, b in entries:
            safe = title.replace('&', 'and')
            lines.append('\\expandafter\\def\\csname pname@%s\\endcsname{%s}' % (key, safe))
    lines += [
        '\\newcommand{\\partnameof}[1]{%',
        '  \\ifcsname pname@#1\\endcsname\\csname pname@#1\\endcsname\\else this book\\fi}',
        '\\renewcommand{\\pref}[1]{\\@ifundefined{r@part:#1}{\\emph{\\partnameof{#1}}}{Part~\\ref{part:#1}}}',
        '\\renewcommand{\\prefn}[1]{\\@ifundefined{r@part:#1}{\\emph{\\partnameof{#1}}}{\\ref{part:#1}}}',
        '\\renewcommand{\\nrrow}[2]{\\@ifundefined{r@nr:#1}{#2}{#2\\dotfill\\pageref{nr:#1}}\\\\}',
        '\\makeatother', '']
    write(os.path.join(SRC, 'partnames.tex'), '\n'.join(lines))
    return 'partnames.tex'


INDEX_HEAD = r"""\input{preamble}
\input{partnames}
\input{memomacros}
\input{sheetstyle}
\makeindex[title={%IDXTITLE%},columns=2,intoc]
\begin{document}
\begin{titlepage}\thispagestyle{empty}
\vspace*{0.10\textheight}
\noindent{\color{%RULE%}\rule{\textwidth}{5pt}}\\[3pt]
\noindent{\color{bioline}\rule{\textwidth}{1pt}}\\[30pt]
\noindent{\sffamily\bfseries\fontsize{13}{16}\selectfont\color{%RULE%}%KICKER%}\\[14pt]
\noindent\begin{minipage}{\textwidth}\raggedright
{\sffamily\bfseries\fontsize{30}{36}\selectfont\color{bioink}%
\hyphenpenalty=10000\exhyphenpenalty=10000 %TITLE%\par}\end{minipage}\\[20pt]
\noindent{\color{bioline}\rule{\textwidth}{1pt}}\\[14pt]
\noindent\begin{minipage}{\textwidth}\raggedright
{\fontsize{12}{17}\selectfont\color{biogreen} %BLURB%\par}\end{minipage}
\vfill
\noindent{\sffamily\footnotesize\color{bionum}%FOOT%\par}
\noindent{\color{bioline}\rule{\textwidth}{0.6pt}}
\end{titlepage}
{\hypersetup{linkcolor=bioink}\renewcommand{\contentsname}{Contents, in topic order}\tableofcontents}
\pagestyle{fancy}
"""


def build_master_indexes():
    body = (INDEX_HEAD.replace('%IDXTITLE%', 'Alphabetical Index of Everything')
            .replace('%RULE%', 'tiercore').replace('%KICKER%', 'USABO, IBO AND BEYOND')
            .replace('%TITLE%', 'The Index of Everything')
            .replace('%BLURB%', 'Every fact, term, structure, pathway, organism and named result in the whole '
                                'compendium, stated once and nothing explained. The body runs in topic order, tier '
                                'by tier and volume by volume; the alphabetical index of every name is at the back.')
            .replace('%FOOT%', 'Generated from the same sources as the volumes, so the two can never disagree. '
                               'Worked explanation is left out on purpose: this is what to know, the volumes are '
                               'where it is taught.'))
    body += '\\memtier{Tier One. The Core Syllabus}\n'
    for num, title, stem, key, subtitle, a, b in TIER1:
        body += '\\mempart{%s}\n' % title.replace('&', 'and')
        for c in (1, 2):
            body += '\\InputIfFileExists{memo/%s-%d}{}{}\n' % (stem, c)
    body += '\\memtier{Tier Two. Beyond the Syllabus}\n'
    for num, title, stem, key, subtitle, a, b in TIER2:
        body += '\\mempart{%s}\n' % title.replace('&', 'and')
        for c in (1, 2):
            body += '\\InputIfFileExists{memo/%s-%d}{}{}\n' % (stem, c)
    body += '\\memtier{The Reference Catalogue}\n'
    for num, title, stem, key, subtitle, a, b in CATALOGUE:
        body += '\\mempart{%s}\n' % title.replace('&', 'and')
        for c in ('a1', 'a2', 'b1', 'b2'):
            body += '\\InputIfFileExists{catalogue/%s-%s}{}{}\n' % (stem, c)
    body += TAIL
    write(os.path.join(SRC, 'main-index-concepts.tex'), body)

    body = (INDEX_HEAD.replace('%IDXTITLE%', 'Alphabetical Index of Every Formula')
            .replace('%RULE%', 'tiercat').replace('%KICKER%', 'USABO, IBO AND BEYOND')
            .replace('%TITLE%', 'The Index of Every Formula')
            .replace('%BLURB%', 'Every equation, law, constant and normal value in biology worth knowing for '
                                'these exams, stated once with its symbols defined and nothing derived. The body runs '
                                'in subject order, subject by subject; the alphabetical index is at the back.')
            .replace('%FOOT%', 'Generated from the same sources as the formula volumes, so the two can never '
                               'disagree. The derivations and the worked calculations are in the volumes.'))
    body += '\\memtier{Every Formula, Subject by Subject}\n'
    for num, title, stem, key, subtitle, a, b in FORMULAS:
        body += '\\mempart{%s}\n' % title.replace('&', 'and')
        for c in (1, 2):
            body += '\\InputIfFileExists{memo/%s-%d}{}{}\n' % (stem, c)
    body += TAIL
    write(os.path.join(SRC, 'main-index-formulas.tex'), body)
    return ['main-index-concepts.tex', 'main-index-formulas.tex']


def volume_map():
    """(output folder, pdf basename, driver path) for every volume, for the build and staging scripts."""
    rows = []
    for label, folder, entries, blurb in TIERS:
        for num, title, stem, key, subtitle, a, b in entries:
            fn = volume_filename(num, title)
            rows.append((folder, fn[:-4], os.path.join('topics', folder, fn)))
    for num, title, stem, key, subtitle, a, b in CATALOGUE:
        fn = volume_filename(num, title)
        rows.append(('03-Reference-Catalogue', fn[:-4], os.path.join('topics', '03-Reference-Catalogue', fn)))
    return rows


if __name__ == '__main__':
    made = build_volumes()
    print(build_partnames())
    print('\n'.join(build_master_indexes()))
    print('%d volume drivers written' % len(made))
