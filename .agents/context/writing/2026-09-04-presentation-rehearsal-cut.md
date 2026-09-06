# Defence rehearsal cut (4 September 2026)

Walter rehearsed the live Beamer deck
(`docs/overleaf/presentation/`,
`https://git.overleaf.com/69b05745e534a779b65aae63`).
The clock overrun is real. This note is the lock from that
rehearsal. The Overleaf `main.tex` was **not** edited in the
same pass; apply on the next slide edit after showing the tex.

## Clock

The introduction (money argument + literature outlook) is the
part that works. Budget **about five minutes** for it. The rest
of the spoken path has to fit so the whole talk stays inside
**20 minutes**. Do not steal intro time to keep theory.

## Spoken-path cuts / adds

**Off the spoken path: intent theory.**
That is `Theoretical Work (2)` (true intent \(t_k\), genre
\(g_k\), \(\hat{\mathbf{G}}\), Xu cluster figure,
human-free benchmark closer). It is the slide that costs the
clock without paying the 20-minute talk. Move it to the
appendix (the genre-trajectory appendix already has “Intent is
not observable. Genre is.”) or drop it from the main path.
Do **not** strip trajectory Results; those stay. Definitions
1–6 stay appendix / thesis.

`Theoretical Work (1)` (\(\Pi\) vs \(a_k\), \(\lambda\) and
timing) was not named in the rehearsal cut. Leave it unless
he says that one goes too.

**On the spoken path: retrieval pipeline.**
`images/arch/retrieval_pipeline.png` already sits in the
presentation tree. Put that frame **immediately before**
`The Experimental Platform` (`system_architecture.png`).
“Next or before the system” from the rehearsal; before is the
default so the stack is retrieval → Atlas box.

This **overrides** the 28 August skeleton line that the
retrieval funnel stays off the clock
(`2026-08-28-presentation-skeleton.md`). The pipeline image
is now Methods. Still do **not** walk GPU 0 / GPU 1 / FAISS
internals or the prefill/decode sketches (`inference.png`).
Catalog preprocessing (`ads_data_pipeline.png`) stays
appendix.

## Why

Rehearsal: intent theory + a long Methods tail overruns 20
minutes. Dropping the genre-theory beat and showing how the
ad actually gets into the reply (retrieval, then the system)
leaves the five-minute intro intact and still reaches Results.

## Fast-talk flag

`\fasttalktrue` is a separate switch (High-Level Goals,
Experimental Platform, Artifacts, main-path section cards).
This rehearsal cut is for the **full** spoken path, not only
the fast flag. After the slides move, decide whether Platform
stays full-only (the new retrieval frame may carry that
beat).

## Do not

- Rewrite his `%` comments.
- Put Defs 1–6 back on the main path.
- Cut the intro to save time.
- Treat this note as already-applied Overleaf.
