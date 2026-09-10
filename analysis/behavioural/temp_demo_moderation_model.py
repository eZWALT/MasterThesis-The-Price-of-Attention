import json
from pathlib import Path
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(r'C:\Users\katly\Documents\GitHub\MasterThesis-The-Price-of-Attention')
TRACKED = ROOT / 'src/project/logs/tracked'

# Assemble participant x condition data from tracked logs
rows = []
for arm in ['lab', 'crowd']:
    arm_dir = TRACKED / arm
    for subj_dir in sorted(arm_dir.iterdir()):
        if not subj_dir.is_dir():
            continue
        seen = set()
        files = []
        for pat in ['*export*.jsonl', 'export.jsonl', 'export_*.jsonl', '*events*.jsonl']:
            files.extend(subj_dir.glob(pat))
        for f in files:
            rp = str(f.resolve())
            if rp not in seen:
                seen.add(rp)
                try:
                    with open(f, 'r', encoding='utf-8') as fh:
                        for line in fh:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                rec = json.loads(line)
                            except json.JSONDecodeError:
                                continue
                            event = rec.get('event')
                            data = rec.get('data') or {}
                            pid = rec.get('participant_id') or data.get('participant_id') or subj_dir.name
                            if event == 'demographics_post_submitted':
                                rows.append({
                                    'participant_id': pid,
                                    'demo_sex': data.get('demo_sex'),
                                    'demo_education': data.get('demo_education'),
                                    'demo_familiarity': data.get('demo_familiarity'),
                                    'demo_frequency': data.get('demo_frequency'),
                                    'condition': None,
                                    'outcome': None,
                                })
                            elif event == 'post_condition_survey_submitted':
                                resp = data.get('responses') or {}
                                cond = data.get('condition')
                                if cond is not None and 'llm_reliable' in resp:
                                    rows.append({
                                        'participant_id': pid,
                                        'demo_sex': None,
                                        'demo_education': None,
                                        'demo_familiarity': None,
                                        'demo_frequency': None,
                                        'condition': cond,
                                        'outcome': float(resp.get('llm_reliable')),
                                    })
                except Exception:
                    pass

# Convert rows to participant-level record with repeated condition outcomes
people = {}
for r in rows:
    pid = r['participant_id']
    p = people.setdefault(pid, {
        'participant_id': pid,
        'demo_sex': None,
        'demo_education': None,
        'demo_familiarity': None,
        'demo_frequency': None,
        'conditions': []
    })
    if r['demo_sex'] is not None:
        p['demo_sex'] = r['demo_sex']
    if r['demo_education'] is not None:
        p['demo_education'] = r['demo_education']
    if r['demo_familiarity'] is not None:
        p['demo_familiarity'] = r['demo_familiarity']
    if r['demo_frequency'] is not None:
        p['demo_frequency'] = r['demo_frequency']
    if r['condition'] is not None and r['outcome'] is not None:
        p['conditions'].append({'condition': r['condition'], 'outcome': r['outcome']})

records = []
for pid, p in people.items():
    for cond in p['conditions']:
        records.append({
            'participant_id': pid,
            'condition': cond['condition'],
            'outcome': cond['outcome'],
            'demo_sex': p['demo_sex'],
            'demo_education': p['demo_education'],
            'demo_familiarity': p['demo_familiarity'],
            'demo_frequency': p['demo_frequency'],
        })

df = pd.DataFrame(records)
print(f'N rows: {len(df)}')
print(f'N participants: {df["participant_id"].nunique()}')
print('Conditions:', sorted(df['condition'].unique()))

# Helper for moderation analysis

def run_mod(var_name):
    d = df[['participant_id', 'condition', 'outcome', var_name]].dropna(subset=['condition', 'outcome', var_name]).copy()
    vc = d[var_name].value_counts()
    keep = vc[vc >= 3].index.tolist()
    if len(keep) < 2:
        print(f'\n=== {var_name} ===\nToo sparse; skipped.')
        return
    d = d[d[var_name].isin(keep)].copy()
    d[var_name] = pd.Categorical(d[var_name])
    formula = f'outcome ~ C(condition) * C({var_name}) + C(participant_id)'
    model = smf.ols(formula, data=d).fit()
    print(f'\n=== {var_name} ===')
    print(f'rows={len(d)}, participants={d["participant_id"].nunique()}')
    # Only print the interaction p-value(s) relevant to the condition x demo moderation.
    interaction_terms = []
    for name, pval in model.pvalues.items():
        if 'condition' in name and var_name in name and ':' in name:
            interaction_terms.append((name, pval))
    if interaction_terms:
        for name, pval in sorted(interaction_terms, key=lambda x: x[1])[:10]:
            print(f'{name}: p = {pval:.4f}')
    else:
        print('No explicit interaction terms found in coefficient table.')
    # Show mean outcome by condition within the demographic groups
    means = d.groupby(['condition', var_name], as_index=False)['outcome'].mean().sort_values(['condition', var_name])
    print('\nCondition means by group:')
    print(means.head(20).to_string(index=False))

for var in ['demo_sex', 'demo_education', 'demo_familiarity', 'demo_frequency']:
    run_mod(var)
    print('\n---')
