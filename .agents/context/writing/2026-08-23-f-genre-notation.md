# Notation: \(f_{\mathrm{genre}}\), not \(f_\theta\)

Date: 23 August 2026

The genre classifier is \(f_{\mathrm{genre}}:\mathcal{U}\rightarrow\mathcal{G}\),
with \(\hat g_k=f_{\mathrm{genre}}(u_k)\). Do not write \(f_\theta\).

Reason: the manuscripts already have other maps (\(f_{\mathrm{embed}}\) on
the catalogue). A generic \(\theta\) collides with those and with EEG
theta. Long form, not \(f_g\).

Family to keep aligned:

| Symbol | Map |
|---|---|
| \(f_{\mathrm{genre}}\) | utterance \(\to\) genre |
| \(f_{\mathrm{embed}}\) | document / query \(\to\) \(\mathbb{R}^{1536}\) |

Paper theory block in `publication/main.tex` (Definition 1) is the
canonical occurrence. Thesis Related Work now has the same block
(23 Aug local port, \(f_{\mathrm{genre}}\)). Old Overleaf backups keep
\(f_\theta\); do not edit those.

Code identifiers (`PRIMARY_SOURCE`, `GenreClassifier`) stay as they are.
