# Front matter pass (27 August)

Covers `docs/overleaf/thesis/frontmatter/`. Three files pushed, one held
back because Walter was editing it live.

## Pushed

**`dedication.tex`** — the Descartes epigraph read "body, shape,
extension, motion, location are **functions**". The Latin is *chimerae*;
every published translation gives chimeras, illusions, or fictions.
"Functions" is a corruption that leaves the sentence meaningless, and it
is the first prose a committee reads. Corrected to *chimeras*, accented
René, and sourced to *Meditations on First Philosophy*, **II** — the
passage opens Meditation Two, not One.

**Superseded.** Walter has since replaced Descartes with three epigraphs
of his own — Philippians 3:13–14, Nietzsche, and David Goggins. They are
his and are **not to be edited**. One open issue he should decide:
`\dedicationpage` wraps the file in `{\scshape ...}`, so all three set in
small caps on top of his own `\Large\textit{}`. That suits a one-line
dedication and reads poorly over a six-line quote. Left alone.

**`companion.tex`** — claimed the paper "will be published shortly into
a journal", which is not ours to promise pre-review; now "in preparation
for submission". Spelled omissions as "emissions". Second reason was
garbled mid-clause; rewritten and pointed at `sec:disc-trajectories`.

**`abbr.tex`** — still shipped the Dissertate template example, "FTC,
Fundamental Theorem of Calculus", as its only entry. Replaced with 35
initialisms extracted from the chapters and verified present in the body.
LMM, MDE and ROI are deliberately excluded: always spelled out, never
abbreviated. Spelling follows the chapters, which lean British
(neighbour, randomised).

## Second pass, same day (`a8480ac`)

**`personalize.tex`** — title page now reads *Università degli Studi di
Padova* (was the hybrid "University Degli Studi di Padova") and
*Universitat Pompeu Fabra, Telefónica* (was "University of Pompeu
Fabra, Telefonica"). `\@university` is typeset twice by `\maketitle`, so
one edit fixes both lines. The build is XeLaTeX (`mathspec`), so accents
need no escape.

**Companion note promoted to its own page.** It had been inlined inside
`\dedicationpage` as bold running text between two `\vspace*{\fill}`,
which read as an afterthought to the epigraphs. The class already
defined `\companionnotepage` with the same `\chapter*` shape as
`\abstractpage` and never called it. Removed the inline block, added the
`\phantomsection` and TOC entry the other front-matter pages have, and
called it after `\dedicationpage` in `\frontmatter`.

**`chapters/models.tex`, Statistical Framework.** The contrast paragraph
opened cold on "Take one outcome, say Fz theta". Added a lead-in that
derives the need from the unit convention immediately above — the
participant is the inferential unit, so a test accepts one number per
person, and the rule collapsing five condition scores into one is a
researcher degree of freedom unless fixed before the data are seen — and
that hands off to the table. Trimmed the Design and Sample bullets,
which restated `sec:methods:study-design` almost verbatim.

**Do not strip the `\\` paragraph separators in `models.tex`.** There
are 21 and they are the file's own convention for inter-paragraph
spacing, not a slip. They do emit underfull-hbox warnings; `\medskip`
would be the clean equivalent, but that is a whole-thesis restyle.

## Held: `thanks.tex`

Walter wrote the personal half himself on Overleaf during this pass, in
four rapid commits. Do **not** overwrite it. The merge below keeps all of
his content and adds the three paragraphs he cannot write from memory —
supervisors, collaborators, participants — plus grammar fixes and real
paragraph breaks in place of `\\` on blank lines (which yields
underfull-box warnings, not paragraphs).

Still blank at the time of writing:

- the younger-self sentence, which stops at "the strength to have pushed a";
- surnames for **Angela** (montage / channel-set advice, became
  `sec:app-eeg-channel-sets`), **Sebastian** (exploratory EEG restructure),
  **Katerina** (behavioural instruments).

Merged draft, pending his go-ahead:

```latex
%!TEX root = ../dissertation.tex

This work was supervised by Prof.\ Michele Rossi at Padova and co-supervised by
Prof.\ Ioannis Arapakis at Telefónica Research. I am grateful to both for the
freedom to follow the evidence where it went, and for the corrections that kept
the writing honest at the points where I would have preferred it to claim more.

Angela ---, whose reading of the montage literature became the channel-set
sensitivity analysis in \autoref{sec:app-eeg-channel-sets}; Sebastian ---, who
kept asking what the exploratory EEG layer was actually entitled to say; and
Katerina ---, for the behavioural instruments, all shaped this work in ways that
are easier to see in the analysis than in the citations.

Fifty-four people gave up an afternoon to five simulated shopping conversations
so that this study could exist: thirty-six through Prolific, and eighteen in the
laboratory under a thirty-two-channel cap, none of whom learned what was really
being measured until the debriefing. What the experiment returned them is a set
of careful nulls. That is a quieter result than any of us hoped for, and the
thesis rests on their patience regardless.

I am deeply grateful to all the people who have pushed me through this journey
to graduation, especially my father Alessandro Troiani, my sister Elisabeth
Troiani, and my partner Patricia Pérez, whose support during the hardest
stretches of my academic and industrial career has been a constant source of
strength and a reason never to give up, whatever the cost.

To all the great teachers I have had the chance to meet along my academic
trajectory, and especially to Conrado Martínez Parra, my clearest model of what
a teacher can be, who helped me inside and outside the classroom and pushed me
toward my adolescent dream of one day working at CERN. To Carlos Escolano and
Lluís Belanche, for passing on to me this deep curiosity and hunger for large
language models and deep learning.

Lastly, I want to thank my younger self, for somehow finding the strength to
\textbf{[FINISH]}. I hope I can keep up with his hunger, his curiosity, his
military discipline, and his relentless pursuit of excellence, now that I am
beginning a new life as a machine learning infrastructure engineer in San
Francisco. Thank you, Walter.

\vspace{1.5em}
\noindent\textit{To my grandfather, Walter Troiani Pascua.}
```

## Still missing elsewhere

Audit run over all `*.tex` on 27 August.

- **`abstract.tex` contains the literal string `LOREM IPSUM LACKING AN
  ABSTRACT`** and renders into the PDF. Highest-severity remaining item.
- **Related Works** is the emptiest chapter: nine subsections with no
  body (Evaluation, State of the Art, CRS, Language Models and its
  Definition, Information Retrieval, Advertising, Advertisement &
  Monetization of LLMs, Cognitive Neuroscience).
- **Dataset**: Product Catalog and EEG Data are empty.
- **Results**: seven empty subsections, all gated on Goal 1 and the
  combos, so blocked on analysis rather than on writing.
- Inline TODOs at `introduction.tex:86` (list the research questions) and
  `models.tex:96` (whether to mention all biases).
- **Title page** (`personalize.tex`) carries three name errors, not yet
  fixed because they are Walter's call: "University Degli Studi di
  Padova" is an English/Italian hybrid (should be "Università degli Studi
  di Padova"), and the co-supervisor line reads "University of Pompeu
  Fabra, Telefonica" — it is *Universitat* Pompeu Fabra, and Telefónica
  takes an accent.

Good news from the same audit: all 82 citation keys resolve against
`references.bib`. No missing references.

## Note on the class

`\dedicationpage` wraps the epigraph in `\scshape`, so the five-line
quote sets entirely in small caps. That styling suits a one-line
dedication and reads poorly at this length. Not changed — taste call.
