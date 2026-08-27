# Thesis: trajectory examples + EEG construction math

Date: 23 August 2026. Overleaf `docs/overleaf/thesis/`, local only.

Walter asked for a compact `head(5)` on the trajectory Gold tables, and
whether the Dataset EEG section had lost the paper's original math.

## Trajectories

`tab:trajectory-examples` in `chapters/dataset.tex`: four stacked
`head(5)` blocks (utterances, transitions, conversations,
advertisements), primary `utterance` source. Headers use theory
notation (\(a^{\mathrm{exp}}_4\), \(\hat g_k\), \(\delta_k\),
\(\hat{\mathbf{G}}\), \(N_{\mathrm{shift}}\), \(D\), \(H\),
\(R_{\max}\), \(\delta^{(a)}\), \(g^{(a)}\)). No classifier
posteriors. Genre class names tokenised in the caption.

## EEG math

Paper 5.6's displayed equations (average reference, \(E\), pre/post
windows, \(Y_A\)/\(Y_B\) shapes) were already in Dataset. What had
flattened into prose, and is now displayed again:

- shape rail \(X\to\tilde{X}\to E\to Y_A,Y_B\)
- Welch band maps \(y^{\mathrm{abs}}\), \(y^{\mathrm{rel}}\)
- \(E_{i\ell}\mapsto y_{i\ell}\)
- Dataset A cell \(Y_{A,ic}=\mathrm{med}_{\ell\in c} y_{i\ell}\)
- Dataset B cell \(Y_{B,ik}=y^{\mathrm{post}}-y^{\mathrm{pre}}\)

\(D^{A}_{i}\) and \(D^{B}_{i}\) stay in Methods (inferential, not Gold).
Appendix D now displays FAA / Pope / Kislov instead of inline-only.

Not pushed.
