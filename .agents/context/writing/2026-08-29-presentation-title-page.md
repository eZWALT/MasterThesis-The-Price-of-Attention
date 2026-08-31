# Defence title page (29 August 2026)

Live source: `docs/overleaf/presentation/`
(`https://git.overleaf.com/69b05745e534a779b65aae63`). Theme files
`beamerinnerthemeUnipd.sty` and `beamerfontthemeUnipd.sty`; copy in
`main.tex` (`\title` / `\subtitle` / `\author` / `\institute` / `\date`).

The spoken-deck flow pass is a separate note:
`2026-08-29-presentation-flow-pass.md` (rollback `d5d42ab`).

## What the page is

UniPD lockup on top (white `unipd_logo.png`). Centered title and
subtitle, short hairline, then a two-column people row, then UPC +
Telefónica in a footer band.

- Title: **The Price of Attention** (about 25 pt).
- Subtitle break after *Responses*, not after *to*.
- Left: `Walter J. Troiani Vargas` / `September 2026`.
  Flush near the left margin (`0.035\paperwidth`). Do not put
  “Master's thesis defence” back on the date.
- Right, colons not middots, short names:
  `Advisor: M. Rossi (UniPD)` /
  `Co-advisor: I. Arapakis (Telefónica)`.
- Footer: `images/logos/upc_lockup.png` (square disk with **white**
  9-dot + “UPC”, rectangular BarcelonaTech wordmark in white; no FIB)
  and `images/misc/logo-telefonica.png` (Walter's upload, official
  blue). Sources for the lockup: `images/misc/logo-upc-2.png` (disk)
  and `images/misc/logo-upc.png` (wordmark only).

People type sits **below** the title/subtitle and is smaller than
both (name ~11 pt, date and advisors ~7.5 pt). OCR of the previous
pass read the name in the same visual band as the advisors
(`Walter J. Troiani Vargas Advisor: M. Rossi…`) because the name
was 13 pt and started at `0.09\paperwidth` — it looked like a
centered cluster, not a left credit.

## What not to do

- Do not put a `tabular` inside `\institute` (beamer rewrites it;
  that is what broke the first two-column pass).
- Do not leave `\centering` on while using `\hfill` minipages.
  Center logo + title + hairline in a group; end the group; then
  `\noindent` the people row.
- Do not fill the UPC disk holes with black — they were transparent
  and read as black on the red field. White fill.
- Do not put UniPD in the footer row with UPC and Telefónica.
  Three marks: UniPD top, the other two bottom.
- Do not copy the bachelor UPC+FIB banner 1:1.

## Related

- Flow / spoken arc: `2026-08-29-presentation-flow-pass.md`
- Skeleton: `2026-08-28-presentation-skeleton.md`
