"""Offline implementation checks; optional strict check of a real session."""
import argparse
import ast
import json
from pathlib import Path
from prompts import CASES, TEMPLATES, prompt_for
from evaluation import evaluate, summarize
from run_lab import ROOT, PLAN, groups, all_rows

def validate(session=None):
    for f in ROOT.glob('*.py'):ast.parse(f.read_text(encoding='utf-8'))
    nb=json.loads((ROOT/'prompt_engineering_lab.ipynb').read_text(encoding='utf-8'))
    for c in nb['cells']:
        if c['cell_type']=='code':ast.parse(''.join(c['source']))
    try:
        import nbformat
        nbformat.validate(nbformat.from_dict(nb))
    except ImportError:pass
    for t in CASES:
        assert set(TEMPLATES[t])=={'v1','v2','v3'}
        for v in TEMPLATES[t]:
            for c in CASES[t]:assert prompt_for(t,v,c)
    # Authored fixtures below validate the checker. They are NOT model outputs.
    assert evaluate('sentiment',CASES['sentiment'][0],'positive')==[]
    assert 'label_format' in evaluate('sentiment',CASES['sentiment'][0],'Positive.')
    assert 'wrong_sentiment' in evaluate('sentiment',CASES['sentiment'][0],'negative')
    for case in CASES['extraction']:
        assert evaluate('extraction',case,json.dumps(case['expected']))==[]
    assert evaluate('extraction',CASES['extraction'][0],'```json\n{}\n```')==['invalid_json']
    wrong=dict(CASES['extraction'][0]['expected']);wrong['order_date']='2026-03-15'
    assert 'wrong_order_date' in evaluate('extraction',CASES['extraction'][0],json.dumps(wrong))
    assert 'word_count' in evaluate('product',CASES['product'][0],json.dumps({'title':'wireless mouse','description':'wireless mouse','price':'$29.99'}))
    fake=[{'status':'ok','response':'positive','failures':[]}]*13+[{'status':'error','response':None,'failures':['api_error']}]*2
    assert abs(summarize(fake)['consistency_pct']-100*13/15)<1e-9
    assert summarize([])['consistency_pct'] is None
    assert summarize(fake)['exact_match_pct']==100*13/15
    assert len((ROOT/'lab_summary.md').read_text(encoding='utf-8').strip().split('\n\n'))==1
    print('PASS: offline code, notebook structure, 9 prompts, cases, evaluator and one-paragraph summary. No model calls performed by this check.')
    if session:
        folder=ROOT/'results'/session
        g=groups(all_rows(folder));issues=[]
        expected=[(p,t,v,'base',n) for p,v,n in PLAN for t in CASES]+[('variations',t,'v3',c['id'],5) for t,cs in CASES.items() for c in cs[1:]]
        for k in expected:
            rs=g.get(k,[])
            if len(rs)!=k[4] or {r['run'] for r in rs}!=set(range(1,k[4]+1)):issues.append(f'Incomplete/duplicate batch: {k}')
            if any(r['status']!='ok' for r in rs):issues.append(f'API errors: {k}')
            if any(not r.get('response_id') for r in rs if r['status']=='ok'):issues.append(f'Missing API provenance: {k}')
            if k[0]=='final' and (summarize(rs)['consistency_pct'] or 0)<=80:issues.append(f'Final threshold not met: {k[1]}')
        import csv
        review=folder/'manual_review.csv'
        if not review.exists():issues.append('Product manual review missing')
        else:
            with review.open(encoding='utf-8-sig') as f:
                product=list(csv.DictReader(f))
            final=[r for r in product if r['phase']=='final']
            if len(final)!=15 or sum(r['factual_pass'].lower() in ('yes','true','1') and r['style_pass'].lower() in ('yes','true','1') for r in final)<13:
                issues.append('Product final human review must confirm >=13/15 (yes in both columns)')
        print(json.dumps({'empirical_submission_ready':not issues,'issues':issues},ensure_ascii=False,indent=2))
        return not issues
    print('Empirical readiness: NOT RUN. Run with --session after actual experiments; manually review narrative and GitHub submission.')
    return True

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--session');a=p.parse_args()
    raise SystemExit(0 if validate(a.session) else 1)
