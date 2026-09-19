# Writing contract for the USABO / IBO Biology Compendium

You are writing one file of a LaTeX compendium. The preamble, the macros and the
volume drivers already exist and you must not touch them. Your file is `\input`
into a driver, so it has **no preamble, no `\documentclass`, no `\begin{document}`,
no `\usepackage`**. Write body content only.

## Hard rules, every one of which breaks the build if ignored

1. No `\usepackage`, no `\documentclass`, no `\begin{document}`, no `\newcommand`,
   no `\def`, no `\renewcommand`, no `\makeindex`, no `\printindex`, no `\tableofcontents`.
2. Use only the macros and environments listed below. Nothing else is defined.
3. Escape these characters in ordinary text: `%` as `\%`, `&` as `\&`, `_` as `\_`,
   `#` as `\#`, `$` as `\$`. An unescaped `%` silently eats the rest of the line.
4. Plain ASCII only. No Unicode: no curly quotes, no en dashes, no Greek letters as
   characters, no degree sign, no arrows, no `×`, no `≈`, no `→`. Use `$\alpha$`,
   `$\rightarrow$`, `$\times$`, `$\approx$`, `$10\dg$`, `$37\degc$`.
5. Every mathematical or chemical symbol goes in math mode: `$K_m$`, `$V_{\max}$`,
   `$\mathrm{CO_2}$`. Chemistry may also use mhchem: `\ce{CO2 + H2O -> H2CO3}`.
6. Displayed equations use `\[ ... \]`. Never `$$ ... $$`. Never leave a blank line
   inside a displayed equation.
7. Every environment you open must be closed. Never nest a tcolorbox inside another
   tcolorbox. Never put a `\section` inside a box.
8. Tables: `tabular` only, wrapped in nothing (the preamble shrinks them for you),
   with `@{}` at both ends, `\toprule \midrule \bottomrule`, and column specs that
   use `p{Xcm}` for any cell longer than three words. Keep total width under 12cm.
   Never use `\multirow`. `\multicolumn` is allowed.
9. No `\label` or `\ref` except through `\nr` (below). No `\cite`, no bibliography,
   no `\includegraphics`, no image files, no TikZ pictures.
10. No blank line between `\item` entries inside a list, and never a blank line
    immediately after `\begin{itemize}` or before `\end{itemize}`.

## The macros you may use

### In a prose (`sections/`) file

- `\parttitle[key]{Volume Title}{One sentence saying what the volume covers.}`
  Exactly once, as the first line of the file. The `key` is given to you.
- `\section{Heading}` for each major heading. `\subsection{Heading}` below it.
- `\nr{unique-label}{Name As It Should Appear In The Index}` immediately after the
  opening of a box or before the sentence that states a named thing. Labels must be
  unique across the whole compendium, so prefix every one with your volume stem,
  e.g. `\nr{07-respiration-glycolysis-net-yield}{Net yield of glycolysis}`.
  This is what builds the index, so every named law, formula, structure, pathway,
  term, value and rule you state gets one. Aim for 120 or more per prose file.
- Boxes, each taking a title: choose the one whose job matches the content.
  - `\begin{keybox}[title={MEMORIZE: ...}] ... \end{keybox}` grey box, for the facts
    and formulas that must be known cold.
  - `\begin{thmbox}[title={PRINCIPLE: ...}] ... \end{thmbox}` for a law, rule or
    principle stated precisely.
  - `\begin{defbox}[title={DEFINITIONS: ...}] ... \end{defbox}` for vocabulary,
    several terms at a time.
  - `\begin{calcbox}[title={WORKED: ...}] ... \end{calcbox}` grey box, for a worked
    calculation or a worked data interpretation, with the arithmetic shown and a
    numerical check at the end.
  - `\begin{expbox}[title={EXPERIMENT: ...}] ... \end{expbox}` for a landmark
    experiment: design, result, and what it established.
  - `\begin{tipbox}[title={TECHNIQUE: ...}] ... \end{tipbox}` for a method of
    attacking a question, with the trigger that tells you to use it.
  - `\begin{warnbox}[title={TRAP: ...}] ... \end{warnbox}` for a misconception the
    exam exploits, stated as the wrong belief and then the correction.
  - `\begin{obsbox}[title={WORTH NOTICING: ...}] ... \end{obsbox}` for a pattern,
    a coincidence of numbers, or a connection between two topics.
- `\tm{term}` bold for a term being introduced. `\sn{Escherichia coli}` italic for a
  species name. `\ttitle{Lead-in.}` bold coloured run-in heading inside a box.
- `\pref{key}` to cross-reference another volume by its key.
- `itemize`, `enumerate`, `description` lists.

### In a memorization sheet (`memo/`) file

Only these three, repeated. No prose, no boxes, no `\section`.

- `\memsec{Sub-area heading}` to open each block.
- `\mem{Name of the thing}{formula in math, or empty}{one or two sentence note}`
  The second argument is set in display math automatically, so write `K_m` not
  `$K_m$`, and leave it empty as `{}` when the entry is verbal rather than
  mathematical. The third argument is ordinary text and may contain `$...$`.
  When the second argument is non-empty the note is dropped in the bare sheet, so
  the formula must stand alone. When it is empty the note is what is shown, so the
  note must be a complete statement of the fact.
- `\memtable{\begin{tabular}{@{}...@{}} ... \end{tabular}}` for a table of values.

Every `\mem` name is automatically indexed, so the names are the index of the whole
compendium. Aim for 180 or more `\mem` entries per memo file, and make sure every
named thing, every formula, every value and every term from the matching prose file
appears. This file is what a student revises from the night before, so nothing may
be missing and nothing may need the prose to make sense.

### In a catalogue (`catalogue/`) file

Only these two, repeated.

- `\catsec{Sub-area heading}`
- `\thm{Name}{Precise statement, with the conditions under which it holds.}{Optional
  line on where it is used, who found it, or the number worth remembering.}`
  The statement is ordinary text and may contain `$...$` and `\ce{}`.

Aim for 200 or more `\thm` entries per catalogue file. Entries are one to four
sentences: precise, self-contained, no worked examples.

## Content standard

- Write for a student aiming at the USABO Semifinal Exam and the IBO. Assume a strong
  high school background and no more. Explain the mechanism, never just the name.
- Everything must be factually correct and current. Where textbooks disagree or a
  figure varies, say so and give the range.
- Give the numbers. Concentrations, potentials, rates, yields, sizes, normal values,
  percentages: a biology exam asks for them and a volume without them is useless.
- Every formula gets its symbols defined, its units, and the conditions under which
  it holds.
- Prefer a table to a paragraph whenever the content is a comparison.
- Name the exam trap wherever there is one. `warnbox` entries are as valuable as the
  content itself.
- Write in plain declarative English. No filler, no "it is important to note", no
  encouragement, no meta-commentary about the volume itself.
- Never reproduce a real exam question verbatim. Worked examples are your own, with
  your own numbers.
