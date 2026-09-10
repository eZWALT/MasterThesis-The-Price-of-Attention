import pandas as pd
from pathlib import Path
from statsmodels.formula.api import mixedlm

ROOT = Path(r'C:\Users\katly\Documents\GitHub\MasterThesis-The-Price-of-Attention')
cond = pd.read_csv(ROOT / 'analysis/walter/behavioural/outputs/gold/condition_features.csv')
person = pd.read_csv(ROOT / 'analysis/walter/behavioural/outputs/gold/person_features.csv')

# Keep the per-person demographic info and join to repeated condition rows.
df = cond.merge(person[['participant_id', 'demo_age', 'demo_sex', 'demo_education', 'demo_familiarity', 'demo_frequency']], on='participant_id', how='left')

# Keep only rows with a valid condition and outcome data.
base = ['credibility', 'helpfulness', 'convincingness', 'relevance', 'neutrality', 'behaviour_pushing', 'behaviour_manipulate']
# Some columns may have been renamed in gold; keep canonical score columns if present.
for c in base:
    if c not in df.columns:
        print('missing', c)

# demographic candidates to test
mods = ['demo_sex', 'demo_education', 'demo_familiarity', 'demo_frequency']

for outcome in base:
    print(f'\n=== OUTCOME: {outcome} ===')
    for mod in mods:
        d = df[['participant_id', 'condition', outcome, mod]].dropna(subset=['participant_id', 'condition', outcome, mod]).copy()
        vc = d[mod].value_counts()
        keep = vc[vc >= 3].index.tolist()
        if len(keep) < 2:
            print(f'  {mod}: skipped (too sparse)')
            continue
        d = d[d[mod].isin(keep)].copy()
        d[mod] = d[mod].astype(str)
        d['condition'] = d['condition'].astype(str)
        # one baseline reference per factor
        ref = {
            'demo_sex': 'Male',
            'demo_education': "Bachelor's Degree",
            'demo_familiarity': 'Familiar',
            'demo_frequency': '1–5 times per day',
        }.get(mod)
        if ref is None or ref not in d[mod].unique():
            ref = sorted(d[mod].unique())[0]
        formula = f'{outcome} ~ C(condition) * C({mod}, Treatment(reference="{ref}"))'
        try:
            model = mixedlm(formula, d, groups=d['participant_id'])
            res = model.fit()
            inter = []
            for k, p in res.pvalues.items():
                if ':' in k and mod in k:
                    inter.append((k, float(p)))
            if not inter:
                inter = [(k, float(v)) for k, v in res.pvalues.items() if 'condition' in k and mod in k]
            if inter:
                best = sorted(inter, key=lambda x: x[1])[:5]
                print(f'  {mod}: ', '; '.join(f'{k} p={p:.4f}' for k,p in best))
            else:
                print(f'  {mod}: no interaction terms')
        except Exception as e:
            print(f'  {mod}: model failed: {type(e).__name__}: {e}')
