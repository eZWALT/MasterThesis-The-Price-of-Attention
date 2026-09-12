# Work item 2 — §4.2.2 Behavioural Data draft (Grok 4.6)

## Summary
- Length: 516 words (544 if table cells are counted); matches neighbours: yes (trajectories 552 words plus a pipeline figure and an example-row table; EEG Description 274 words plus a grain table and a pipeline figure). No thesis file was edited.
- Every count with its source file
  - \(N=54\), \(L=18\), \(C=36\): `analysis/walter/behavioural/outputs/gold/build_report.json` (`n_people`, `n_lab`, `n_crowd`); same roster already in `chapters/dataset.tex` `\subsec:dataset:ingestion`.
  - 270 condition / ratings rows: `build_report.json` `n_conditions`; `condition_features.csv` (270 rows); \(54\times 5\).
  - 54 person rows: `build_report.json` `n_people`; `person_features.csv` (54 rows).
  - 216 advertisement / recall rows: `build_report.json` `n_advertisements`; `advertisement_features.csv` (216 rows); \(54\times 4\).
  - 54 contrast rows (wide): `build_report.json` `n_contrasts_all`; `contrast_scores.csv` (54 rows). Identical on disk to `combo_threeway_D.csv`.
  - 270 joined chat / 90 laboratory: `build_report.json` `n_combo_all`, `n_combo_lab`; `combo_threeway.csv`, `combo_threeway_lab.csv`.
  - 18 joined laboratory contrasts: `build_report.json` `n_contrasts_lab`; `combo_threeway_lab_D.csv`.
  - 2,160 turn / process rows: `build_report.json` `n_messages`; `messages.csv`.
  - 22 post-condition items and 3 cued-recall items: `chapters/appendix_c.tex` (`tab:post-condition-*`, `tab:recall-items`); 15 `llm_*` + 5 `personality_*` + 2 `behaviour_*`.
  - Reversal \(8-x\) once: `analysis/walter/behavioural/build_gold.py` `invert()` / `REVERSE_ITEMS`.
  - Freeze date 8 September 2026: Gold mtime `2026-09-08 08:27` on `condition_features.csv` and `build_report.json`; Results already calls this the 8 September freeze.
- Open questions for Walter (≤ 5)
  1. Include `figures/gold_tables.pdf` here, at the §4.2 opener, or leave it out? The file is already in the thesis tree but is not cited; it shows all three families and prints filenames on the cards.
  2. Cued memory and trust after re-exposure are stored on recall (216 rows), not on ratings (270), because \(a^{\emptyset}\) has no product. Confirm that split.
  3. `advertisement_features.csv` has format, timing, and product, not \(g^{(a)}\). The draft points genre to the trajectory advertisement table. Confirm.
  4. Keep `\label{tab:beh-gold}`? EEG has a grain table; trajectories puts counts only in prose.
  5. Keep the turns (\(2{,}160\)) sentence? It is a behavioural Gold view on the catalog figure but was not in the required list. Bronze path `src/project/logs/tracked/{lab,crowd}/` is in a `% NUMBERS` comment only.

## Draft (verbatim copy of the .tex)

```latex
\subsection{Behavioural Data}
\label{subsec:dataset:behavioural}

The behavioural battery is scored from the same Bronze JSONL as the trajectories, at the participant \(\times\) condition grain, and its Gold tables were frozen on 8 September 2026.
\\

The pass uses the same Bronze / Silver / Gold contract as the other two families. Bronze is the tracked JSONL; Silver is an in-memory flatten, parse, and a single reverse-coding; Gold is the named views that analysis reads. Each zone refines the one before it and never writes back to it. Both arms completed the instruments, so this family runs at \(N=54\). How the items become the outcomes is fixed in \autoref{sec:behavioral-measures}.
\\

Bronze is the tracked laboratory and crowd session log.
% NUMBERS: src/project/logs/tracked/{lab,crowd}/ ; prefer *export*.jsonl
When a folder holds both an events file and an export-tagged file, the export is the one that is read.
A session file holds the 22 post-condition items after each of the five conversations, the cued-recall block after the fifth, the BFI-10, the demographics form, and the interaction log of messages, timings, and served advertisements.
The roster is the finished set of \autoref{subsec:dataset:ingestion}: the same folder-tag exclusions, with unfocused sessions kept.
\\

Silver parses that JSONL, in memory, into a flat participant \(\times\) condition item table: the 22 post-condition items on every condition, and the three cued-recall items on each advertisement condition.
Reverse-coded Likert items are inverted once as \(8-x\) and are not inverted again when the outcome means are formed.
The join key is \texttt{experiment\_id}, together with \texttt{condition} at this grain.
Silver is not inferential: no later chapter reads an intermediate item file.
\\

Gold writes the views in \autoref{tab:beh-gold}.
% NUMBERS: analysis/walter/behavioural/outputs/gold/condition_features.csv
Ratings (condition outcomes) are one row per participant \(\times\) condition (\(54\times 5=270\)): the four primary outcomes (trust, credibility, perceived manipulation, notice) and the four secondary qualities (helpfulness, convincingness, relevance, neutrality).
The raw items remain on the same rows beside those means.
% NUMBERS: analysis/walter/behavioural/outputs/gold/person_features.csv
Person features are one row per participant (\(54\)): the five BFI-10 traits, the demographics, and the arm.
% NUMBERS: analysis/walter/behavioural/outputs/gold/contrast_scores.csv
Contrast scores are one row per participant (\(54\)), each holding one person-level difference \(D_i\) per planned contrast \eqref{eq:person-contrast}, stored wide as columns on that row.
% NUMBERS: analysis/walter/behavioural/outputs/gold/advertisement_features.csv
Advertisement features (recall) are one row per served advertisement (\(54\times 4=216\)): format, timing, the served product, cued memory, and trust after re-exposure.
\(a^{\emptyset}\) has no row, because there is no product to re-show.
The advertisement genre \(g^{(a)}\) lives on the trajectory advertisement table (\autoref{subsubsec:dataset:trajectories-conversation}).
% NUMBERS: analysis/walter/behavioural/outputs/gold/messages.csv
A message-grain process table (turns: length and latency; \(2{,}160\) rows) sits beside the ratings and is not an outcome table.
\\

% NUMBERS: analysis/walter/behavioural/outputs/gold/combo_threeway.csv
% NUMBERS: analysis/walter/behavioural/outputs/gold/combo_threeway_lab.csv
% NUMBERS: analysis/walter/behavioural/outputs/gold/combo_threeway_D.csv
% NUMBERS: analysis/walter/behavioural/outputs/gold/combo_threeway_lab_D.csv
The association analyses read joined views of the same grains: ratings joined to the trajectory and EEG condition tables (\(270\) rows; laboratory-only \(90\)), and the contrast scores joined the same way (\(54\) rows; laboratory-only \(18\)).
EEG columns are empty on crowd rows.
Joins are views, not a fourth grain; the key remains \texttt{experiment\_id} and \texttt{condition}.
\\

\begin{table}[htbp]
\centering
\caption{Gold behavioural views from the 8 September 2026 freeze.
Laboratory joined rows are the cells in which EEG is filled.}
\label{tab:beh-gold}
\begin{tabular}{@{}llr@{}}
\toprule
\textbf{View} & \textbf{Grain} & \textbf{Rows} \\
\midrule
ratings & participant \(\times\) condition & 270 \\
BFI + demo & participant & 54 \\
contrasts & participant & 54 \\
recall & participant \(\times\) advertisement & 216 \\
joined chat, laboratory & participant \(\times\) condition & 90 \\
joined contrasts, laboratory & participant & 18 \\
\bottomrule
\end{tabular}
\end{table}
\FloatBarrier

The Gold builder \texttt{build\_gold.py} is the only script that writes these tables.
% NUMBERS: analysis/walter/behavioural/build_gold.py
The frozen Gold tables are the only source of behavioural numbers in \autoref{chp:results} and \autoref{chp:discussion}.
An independent analysis of the same Bronze by a second analyst was used for cross-checking and is not quoted.
\\
```
