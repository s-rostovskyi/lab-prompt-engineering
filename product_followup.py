"""Independent product-only revision batches; retain original evidence and reviews."""
import argparse
import concurrent.futures
import csv
import json
from pathlib import Path
from prompts import CASES, TEMPLATES
from run_lab import ROOT, call_openai, all_rows, groups, PLAN
from evaluation import summarize
from product_prompt_revision import VERSION, PRODUCT_PROMPT, CLAIM_SCREEN
import hashlib
from prompts import prompt_for

def revision_rows(folder):
    p=folder/'product_revision_responses.jsonl'
    return [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines()] if p.exists() else []

def screen(row, case):
    if row['status']!='ok':return
    try:obj=json.loads(row['response'])
    except (ValueError,TypeError):return
    if not isinstance(obj,dict) or not isinstance(obj.get('description'),str):return
    text=obj['description'].lower()
    for phrase in CLAIM_SCREEN:
        if phrase in text and phrase not in case['input']['name'].lower():
            row['failures'].append('unsupported_claim:'+phrase)
    if 'this description' in text:row['failures'].append('meta_description')

def write_review(folder, rows):
    p=folder/'product_revision_manual_review.csv'
    fields=['phase','task','version','case_id','run','response','factual_pass','style_pass','notes']
    old={}
    if p.exists():
        with p.open(encoding='utf-8-sig',newline='') as f:
            for r in csv.DictReader(f):old[tuple(r[k] for k in fields[:5])]=r
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for row in rows:
            r={k:str(row[k]) if k=='run' else row[k] for k in fields[:6]}
            prior=old.get(tuple(r[k] for k in fields[:5]),{})
            # Never retain a review if its actual response changed.
            for k in fields[6:]:r[k]=prior.get(k,'') if prior.get('response')==r['response'] else ''
            w.writerow(r)

def report(folder):
    rows=revision_rows(folder);original=all_rows(folder)
    write_review(folder,rows)
    table=['| Batch | Version | Case | Attempted | API success | Contract % |',
           '|---|---|---|---:|---:|---:|']
    relevant=[r for r in original if r['phase']=='final' and r['task']=='product']+rows
    for key,rs in sorted(groups(relevant).items()):
        m=summarize(rs)
        table.append(f'| {key[0]} | {key[2]} | {key[3]} | {m["attempted"]} | {m["api_success"]} | {m["consistency_pct"]:.1f} |')
    text='# Product prompt revision: v3r1\n\n'
    text+='The original v3 final batch remains in raw_responses.jsonl and manual_review.csv. The reviewed batch exposed unsupported appearance, reliability, comfort and performance claims. One response contained 29 words. The original automatic screen missed several of these claims. This revision adds explicit exclusions and neutral shopping examples; its effectiveness must be measured with new calls.\n\n'
    text+='\n'.join(table)+'\n\n'
    text+='The original and revised automatic percentages use different claim screens; they must not be interpreted as directly comparable factual accuracy. Compare both batches using the same manual rubric. Screens remain incomplete, so human review is required.\n\n'
    for r in rows:
        if r['failures']:text+=f'- {r["phase"]}, {r["case_id"]}, run {r["run"]}: '+', '.join(r['failures'])+'\n'
    (folder/'product_revision_report.md').write_text(text,encoding='utf-8')

def validate(folder):
    issues=[];base_groups=groups(all_rows(folder))
    expected=[(p,t,v,'base',n) for p,v,n in PLAN for t in CASES]
    expected += [('variations',t,'v3',c['id'],5) for t,cs in CASES.items() for c in cs[1:]]
    # Preserve completeness requirements for every original batch. Revised product
    # replaces only the original product threshold, never its historical evidence.
    for key in expected:
        rs=base_groups.get(key,[])
        if len(rs)!=key[4] or {r['run'] for r in rs}!=set(range(1,key[4]+1)):
            issues.append('Incomplete or duplicate original batch: '+str(key))
        if any(r['status']!='ok' or not r.get('response_id') for r in rs):issues.append('Original API/provenance failure: '+str(key))
        if key[0]=='final' and key[1]!='product' and (summarize(rs)['consistency_pct'] or 0)<=80:
            issues.append('Original final threshold not met: '+key[1])
    rows=revision_rows(folder);g=groups(rows)
    revised=[('revision_advanced','product',VERSION,'base',15),('revision_final','product',VERSION,'base',15)]
    revised += [('revision_variations','product',VERSION,c['id'],5) for c in CASES['product'][1:]]
    for key in revised:
        rs=g.get(key,[])
        if len(rs)!=key[4] or {r['run'] for r in rs}!=set(range(1,key[4]+1)):
            issues.append('Incomplete or duplicate revision batch: '+str(key))
        if any(r['status']!='ok' or not r.get('response_id') for r in rs):issues.append('Revision API/provenance failure: '+str(key))
        if len({r['prompt_sha256'] for r in rs})>1:issues.append('Prompt changed within batch: '+str(key))
    final=g.get(('revision_final','product',VERSION,'base',15),[])
    review_path=folder/'product_revision_manual_review.csv';review={}
    if review_path.exists():
        with review_path.open(encoding='utf-8-sig',newline='') as f:
            for r in csv.DictReader(f):
                if r['phase']=='revision_final' and r['case_id']=='base' and r['version']==VERSION:
                    review.setdefault(r['run'],[]).append(r)
    passing=0
    for r in final:
        matches=review.get(str(r['run']),[])
        if len(matches)!=1 or matches[0]['response']!=r['response']:continue
        human=matches[0]
        if r['status']=='ok' and not r['failures'] and all(human[k].strip().lower()=='yes' for k in ('factual_pass','style_pass')):passing+=1
    if len(final)!=15 or passing<13:issues.append(f'Revised product needs >=13/15 passing BOTH automatic and human checks; currently {passing}/15')
    print(json.dumps({'experiment_checks_pass':not issues,'revised_product_combined_pass':passing,'issues':issues,
      'remaining_manual_submission_checks':['Complete evidence-based narrative and variation analysis','Save notebook with real outputs','Upload repository materials']},indent=2))
    return not issues

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--session',required=True)
    p.add_argument('--stage',choices=['advanced','variations','final'])
    p.add_argument('--validate',action='store_true')
    a=p.parse_args()
    if Path(a.session).name!=a.session:p.error('Session must be a directory name')
    folder=ROOT/'results'/a.session
    if not (folder/'config.json').exists():p.error('Existing session/config.json not found')
    if a.validate:raise SystemExit(0 if validate(folder) else 1)
    if not a.stage:p.error('Choose --stage or --validate')
    from dotenv import load_dotenv
    load_dotenv(ROOT/'.env')
    from openai import OpenAI
    client=OpenAI(timeout=60,max_retries=0)
    config=json.loads((folder/'config.json').read_text(encoding='utf-8'))
    if config.get('system')!='You are a helpful assistant.' or config.get('max_completion_tokens')!=700:p.error('Session API settings differ from this runner')
    phase='revision_'+a.stage
    if any(r['phase']==phase for r in revision_rows(folder)):p.error('Revision batch already started. Retain evidence; do not append duplicate attempts.')
    TEMPLATES['product'][VERSION]=PRODUCT_PROMPT
    previous=revision_rows(folder)
    case_map={c['id']:c for c in CASES['product']}
    for r in previous:
        expected_hash=hashlib.sha256(prompt_for('product',VERSION,case_map[r['case_id']]).encode()).hexdigest()
        if r['prompt_sha256']!=expected_hash:p.error('Revision prompt changed after a batch. Use a new revision identifier instead of mixing prompts.')
    required=['revision_advanced'] if a.stage=='variations' else ['revision_advanced','revision_variations'] if a.stage=='final' else []
    for prerequisite in required:
        rs=[r for r in previous if r['phase']==prerequisite]
        if len(rs)!=15 or any(r['status']!='ok' for r in rs):p.error('Complete prerequisite first: '+prerequisite)
    cases=CASES['product'][1:] if a.stage=='variations' else CASES['product'][:1]
    n=5 if a.stage=='variations' else 15
    with concurrent.futures.ThreadPoolExecutor(max_workers=config['workers']) as pool:
        tasks=[(case,pool.submit(call_openai,client,'product',VERSION,case,phase,n,i,config['model'],config['temperature'])) for case in cases for i in range(1,n+1)]
        with (folder/'product_revision_responses.jsonl').open('a',encoding='utf-8') as f:
            for case,future in tasks:
                r=future.result();screen(r,case)
                f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush()
    report(folder)
    print(f'{phase}: saved {len(tasks)} attempts in product_revision_responses.jsonl. Original logs and manual reviews unchanged.')

if __name__=='__main__':main()
