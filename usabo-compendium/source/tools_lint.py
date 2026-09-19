#!/usr/bin/env python3
"""Check every written content file for the breakages agents actually make, and fix the safe ones."""
import os, re, sys, glob

SRC = os.path.dirname(os.path.abspath(__file__))
FIX = '--fix' in sys.argv

FORBIDDEN = [
    (r'\\documentclass', 'documentclass'),
    (r'\\usepackage', 'usepackage'),
    (r'\\begin\{document\}', 'begin document'),
    (r'\\end\{document\}', 'end document'),
    (r'\\newcommand', 'newcommand'),
    (r'\\renewcommand', 'renewcommand'),
    (r'\\makeindex', 'makeindex'),
    (r'\\printindex', 'printindex'),
    (r'\\tableofcontents', 'tableofcontents'),
    (r'\\includegraphics', 'includegraphics'),
    (r'\\begin\{tikzpicture\}', 'tikzpicture'),
    (r'\\multirow', 'multirow'),
    (r'\$\$', 'double dollar display math'),
    (r'\\begin\{figure\}', 'figure float'),
    (r'\\begin\{table\}', 'table float'),
]

ENVS = ['keybox', 'thmbox', 'defbox', 'warnbox', 'tipbox', 'obsbox', 'calcbox', 'expbox',
        'itemize', 'enumerate', 'description', 'tabular', 'align', 'align*', 'equation',
        'gather', 'minipage', 'center']


def nonascii(text):
    return sorted({c for c in text if ord(c) > 126})


UNI_FIX = {
    '\u2013': '--', '\u2014': '---', '\u2018': "`", '\u2019': "'", '\u201c': "``",
    '\u201d': "''", '\u2026': '\\ldots{}', '\u00b0': '$^{\\circ}$', '\u00d7': '$\\times$',
    '\u2192': '$\\rightarrow$', '\u2190': '$\\leftarrow$', '\u2194': '$\\leftrightarrow$',
    '\u21cc': '$\\rightleftharpoons$', '\u2248': '$\\approx$', '\u2264': '$\\leq$',
    '\u2265': '$\\geq$', '\u2260': '$\\neq$', '\u00b1': '$\\pm$', '\u00b5': '$\\mu$',
    '\u03b1': '$\\alpha$', '\u03b2': '$\\beta$', '\u03b3': '$\\gamma$', '\u03b4': '$\\delta$',
    '\u03b5': '$\\epsilon$', '\u03b8': '$\\theta$', '\u03bb': '$\\lambda$', '\u03bc': '$\\mu$',
    '\u03c0': '$\\pi$', '\u03c1': '$\\rho$', '\u03c3': '$\\sigma$', '\u03c6': '$\\phi$',
    '\u03c8': '$\\psi$', '\u03c9': '$\\omega$', '\u0394': '$\\Delta$', '\u03a9': '$\\Omega$',
    '\u03a8': '$\\Psi$', '\u2032': "'", '\u00a0': ' ', '\u2033': "''", '\u2212': '-',
    '\u00bd': '$\\tfrac12$', '\u00e9': '\\\'e', '\u2082': '$_2$', '\u2083': '$_3$',
    '\u00ad': '', '\u2022': '$\\bullet$', '\u2264': '$\\leq$', '\u221e': '$\\infty$',
}


def check(path):
    raw = open(path, encoding='utf-8', errors='replace').read()
    problems = []
    fixed = raw
    for pat, name in FORBIDDEN:
        hits = len(re.findall(pat, raw))
        if hits:
            problems.append('%s x%d' % (name, hits))
    bad = nonascii(raw)
    if bad:
        unmapped = [c for c in bad if c not in UNI_FIX]
        problems.append('non-ascii %d chars%s' % (len(bad), (' UNMAPPED ' + repr(''.join(unmapped))) if unmapped else ''))
        for c, rep in UNI_FIX.items():
            fixed = fixed.replace(c, rep)
    for env in ENVS:
        o = len(re.findall(r'\\begin\{%s\}' % re.escape(env), raw))
        c = len(re.findall(r'\\end\{%s\}' % re.escape(env), raw))
        if o != c:
            problems.append('env %s %d open / %d close' % (env, o, c))
    if raw.count('\\[') != raw.count('\\]'):
        problems.append('display math %d open / %d close' % (raw.count('\\['), raw.count('\\]')))
    for i, line in enumerate(raw.splitlines(), 1):
        if re.search(r'(?<!\\)%', line) and not line.lstrip().startswith('%'):
            problems.append('line %d: bare %% comment' % i)
            break
    if FIX and fixed != raw:
        open(path, 'w', encoding='utf-8').write(fixed)
        problems.append('[unicode fixed]')
    return problems


def stats(path):
    raw = open(path, encoding='utf-8', errors='replace').read()
    return {
        'chars': len(raw),
        'sections': len(re.findall(r'\\section\{', raw)),
        'nr': len(re.findall(r'\\nr\{', raw)),
        'mem': len(re.findall(r'\\mem\{', raw)),
        'thm': len(re.findall(r'\\thm\{', raw)),
        'boxes': len(re.findall(r'\\begin\{(?:key|thm|def|warn|tip|obs|calc|exp)box\}', raw)),
        'tables': len(re.findall(r'\\begin\{tabular\}', raw)),
    }


if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(SRC, 'sections', '*.tex')) +
                   glob.glob(os.path.join(SRC, 'memo', '*.tex')) +
                   glob.glob(os.path.join(SRC, 'catalogue', '*.tex')))
    tot = {'chars': 0, 'nr': 0, 'mem': 0, 'thm': 0, 'boxes': 0, 'tables': 0, 'sections': 0}
    bad = 0
    for f in files:
        st = stats(f)
        for k in tot:
            tot[k] += st[k]
        pr = check(f)
        rel = os.path.relpath(f, SRC)
        flag = ''
        if 'sections/' in rel and (st['chars'] < 45000 or st['nr'] < 80):
            flag = ' THIN'
        if 'memo/' in rel and (st['chars'] < 25000 or st['mem'] < 120):
            flag = ' THIN'
        if 'catalogue/' in rel and (st['chars'] < 50000 or st['thm'] < 140):
            flag = ' THIN'
        if pr or flag:
            bad += 1
            print('%-34s %6dc s=%-3d nr=%-4d mem=%-4d thm=%-4d box=%-3d tab=%-3d %s%s'
                  % (rel, st['chars'], st['sections'], st['nr'], st['mem'], st['thm'],
                     st['boxes'], st['tables'], '; '.join(pr), flag))
    print('\n%d files, %d flagged' % (len(files), bad))
    print('totals: %(chars)d chars, %(sections)d sections, %(nr)d named results, %(mem)d mem entries, %(thm)d catalogue entries, %(boxes)d boxes, %(tables)d tables' % tot)
