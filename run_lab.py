"""Run independent batches, retain original API responses, build honest reports."""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import random
import time
import uuid
from prompts import CASES, TEMPLATES, prompt_for
from evaluation import evaluate, summarize

ROOT=Path(__file__).resolve().parent
PLAN=[('initial','v1',1),('baseline','v1',5),('baseline','v1',10),('baseline','v1',15),
      ('iteration1','v2',15),('advanced','v3',15),('final','v3',15)]

def call_openai(client, task, version, case, phase, batch_n, index, model, temperature):
    prompt=prompt_for(task,version,case)
    record={'phase':phase,'task':task,'version':version,'case_id':case['id'],
      'batch_n':batch_n,'run':index,'requested_model':model,'temperature':temperature,
      'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
      'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest()}
    start=time.monotonic()
    for attempt in range(4):
        try:
            response=client.chat.completions.create(model=model,temperature=temperature,
                max_completion_tokens=700,store=False,
                messages=[{'role':'system','content':'You are a helpful assistant.'},{'role':'user','content':prompt}])
            choice=response.choices[0]
            text=choice.message.content or ''
            failures=evaluate(task,case,text)
            if choice.finish_reason != 'stop': failures.append('finish_'+str(choice.finish_reason))
            record.update(status='ok',response=text,failures=failures,
                response_id=response.id,actual_model=response.model,
                system_fingerprint=getattr(response,'system_fingerprint',None),
                finish_reason=choice.finish_reason,usage=response.usage.model_dump() if response.usage else None)
            break
        except Exception as exc:
            code=getattr(exc,'status_code',None)
            transient=code in (429,500,502,503,504) or type(exc).__name__ in ('APIConnectionError','APITimeoutError')
            if transient and attempt < 3:
                time.sleep(2**attempt+random.random());continue
            # Never persist exception text, which may contain sensitive request details.
            record.update(status='error',response=None,failures=['api_error'],error_type=type(exc).__name__,http_status=code)
            break
    record.update(attempts=attempt+1,elapsed_seconds=round(time.monotonic()-start,3))
    return record

def run_batch(phase,version,n, *, client,folder,model,temperature,workers=3,variations=False):
    jobs=[]
    for task,cases in CASES.items():
        for case in (cases[1:] if variations else cases[:1]):
            for index in range(1,n+1): jobs.append((task,case,index))
    records=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(call_openai,client,t,version,c,phase,n,i,model,temperature) for t,c,i in jobs]
        with (folder/'raw_responses.jsonl').open('a',encoding='utf-8') as handle:
            for future in concurrent.futures.as_completed(futures):
                row=future.result();records.append(row)
                handle.write(json.dumps(row,ensure_ascii=False)+'\n');handle.flush()
    print(f'{phase} / {version} / {n}: {sum(r["status"]=="ok" for r in records)}/{len(records)} API responses')
    return records

def all_rows(folder):
    path=folder/'raw_responses.jsonl'
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()] if path.exists() else []

def groups(rows):
    result={}
    for r in rows:
        key=(r['phase'],r['task'],r['version'],r['case_id'],r['batch_n'])
        result.setdefault(key,[]).append(r)
    return result

def report(folder=None):
    rows=all_rows(folder) if folder else []
    grouped=groups(rows)
    table=['| Phase | Task | Version | Case | N | API success | Format % | Contract consistency % | Exact match % | Unique |',
           '|---|---|---|---|---:|---:|---:|---:|---:|---:|']
    metrics=[]
    expected=[(p,t,v,'base',n) for p,v,n in PLAN for t in CASES]
    expected += [('variations',t,'v3',c['id'],5) for t,cs in CASES.items() for c in cs[1:]]
    for key in expected:
        rs=grouped.get(key,[]);m=summarize(rs);metrics.append({'phase':key[0],'task':key[1],'version':key[2],'case_id':key[3],'batch_n':key[4],**m})
        values=[f'{m[k]:.1f}' if m[k] is not None else 'NOT RUN' for k in ('format_pct','consistency_pct','exact_match_pct')]
        table.append('| '+' | '.join(map(str,[*key,f'{m["api_success"]}/{key[4]}',*values,m['unique_responses'] if rs else 'NOT RUN']))+' |')
    text='# Failure Analysis Report\n\n'
    text+=('Data source: `'+str(folder.relative_to(ROOT)).replace('\\','/')+'/raw_responses.jsonl`.\n\n' if folder else 'Status: NOT RUN. No real API calls have been made; no results have been fabricated.\n\n')
    text+='\n'.join(table)+'\n\n## Methodology\n\nEach 5/10/15-run batch and the final v3 batch are independent. All versions use the same model, temperature 0.7, system message and output limit. JSON mode is disabled to compare prompts without API format enforcement. Contract consistency is the percentage of attempted calls passing the task checks, not verbatim agreement. API errors remain in the denominator. Format checks structure; exact match is the frequency of the most common response. Sentiment and extraction are checked against authored reference answers. Product checks provide only an automated minimum; facts, tone and persuasiveness require human review. Strictly >80% requires 13/15. Small batches do not establish production reliability.\n\n## Observed failures\n\n'
    for key,rs in sorted(grouped.items()):
        m=summarize(rs)
        text+=f'### {" / ".join(map(str,key))}\n\n'+json.dumps(m['failure_counts'],ensure_ascii=False)+'\n\n'
        for r in rs:
            if r['failures']:
                excerpt=json.dumps(r['response'],ensure_ascii=False)
                text+=f'- Run {r["run"]}: {", ".join(r["failures"])}. Actual output: `{excerpt}`\n'
    if not rows:text+='No observations are available. Hypotheses: v1 may return explanations instead of labels, invent product features, use arbitrary formatting or invent a year. These are anticipated risks, not observed results.\n'
    text+='\n## v1 vs v3\n\n'
    improvements=[]
    for task in CASES:
        a=summarize(grouped.get(('baseline',task,'v1','base',15),[]))
        b=summarize(grouped.get(('final',task,'v3','base',15),[]))
        if a['consistency_pct'] is not None and b['consistency_pct'] is not None:
            delta=b['consistency_pct']-a['consistency_pct'];improvements.append(f'{task}: {a["consistency_pct"]:.1f}% → {b["consistency_pct"]:.1f}% ({delta:+.1f} percentage points)')
        else:improvements.append(f'{task}: NOT RUN; improvement has not been established')
    text+='\n'.join('- '+x for x in improvements)+'\n\n## Variations and manual analysis\n\nReview original responses and manual_review.csv. For each variation, document what works, observed failures and the next change to test independently. Compare v1 at 5/10/15 runs: do larger batches reveal new failure types? Review baseline before confirming or revising v2, and iteration1 before confirming or revising v3. Keep prompts fixed within a batch. Provisional v2/v3 are based on course materials and hypotheses, not unavailable observations.\n'
    (ROOT/'failure_analysis_report.md').write_text(text,encoding='utf-8')
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results'/'metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
    if folder:
        import csv
        review=folder/'manual_review.csv'
        old={}
        if review.exists():
            with review.open(encoding='utf-8-sig',newline='') as f:
                for r in csv.DictReader(f):old[(r['phase'],r['task'],r['version'],r['case_id'],r['run'])]=r
        with review.open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f);w.writerow(['phase','task','version','case_id','run','response','factual_pass','style_pass','notes'])
            for r in rows:
                if r['task']=='product':
                    prior=old.get(tuple(str(r[k]) for k in ('phase','task','version','case_id','run')), {})
                    w.writerow([r[k] for k in ('phase','task','version','case_id','run','response')]+[prior.get(k,'') for k in ('factual_pass','style_pass','notes')])
    summary='I prepared zero-shot prompts, explicit output constraints, few-shot examples and a step-by-step extraction procedure for the three TechFlow tasks. '
    if rows:
        summary+='The measured comparison between the 15-run baseline and final batches is: '+'; '.join(improvements)+'. Observed failures and actual responses are recorded in the report and raw log; product descriptions still require human factual and style review. The experiment evaluates combined techniques and does not isolate few-shot effects from structure. '
    else:
        summary+='OpenAI API calls have not yet been performed, so failures, improvements and the most effective technique have not been established empirically; v2/v3 remain testable hypotheses. '
    summary+='In the next iteration, I will test these hypotheses against the failure log, compare techniques separately, expand difficult-feedback cases and use a new independent sample before drawing conclusions about production reliability.'
    (ROOT/'lab_summary.md').write_text(summary+'\n',encoding='utf-8')
    return metrics

def main():
    if '--report-only' not in __import__('sys').argv:
        from dotenv import load_dotenv
        load_dotenv(ROOT/'.env')
    p=argparse.ArgumentParser()
    p.add_argument('--stage',choices=['all','initial','baseline','iteration1','advanced','variations','final'],default='all')
    p.add_argument('--session',help='Existing session directory name for staged continuation')
    p.add_argument('--report-only',action='store_true')
    p.add_argument('--model',default=os.getenv('OPENAI_MODEL','gpt-4o-mini'))
    p.add_argument('--temperature',type=float,default=0.7)
    p.add_argument('--workers',type=int,default=3)
    a=p.parse_args()
    if a.workers<1 or not 0<=a.temperature<=2:p.error('Invalid workers or temperature')
    session=a.session or dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:6]
    if Path(session).name!=session:p.error('Session must be a directory name, not a path')
    folder=ROOT/'results'/session
    if a.report_only:
        report(folder if folder.exists() else None);return
    if not os.getenv('OPENAI_API_KEY'):raise SystemExit('OPENAI_API_KEY missing. Configure .env locally; never put the key in a notebook or GitHub.')
    from openai import OpenAI
    client=OpenAI(timeout=60,max_retries=0)
    config={'model':a.model,'temperature':a.temperature,'workers':a.workers,'system':'You are a helpful assistant.','max_completion_tokens':700}
    folder.mkdir(parents=True,exist_ok=True)
    config_path=folder/'config.json'
    if config_path.exists() and json.loads(config_path.read_text())!=config:raise SystemExit('Session parameters differ; create a new session.')
    config_path.write_text(json.dumps(config,indent=2),encoding='utf-8')
    print('Session:',session)
    print('OpenAI client initialized. Connection success is confirmed only by actual responses.')
    existing=groups(all_rows(folder))
    execution_plan=PLAN[:-1]+[('variations','v3',5)]+PLAN[-1:]
    for phase,v,n in execution_plan:
        if a.stage not in ('all',phase):continue
        if any(k[0]==phase and k[2]==v and k[4]==n for k in existing):raise SystemExit('Batch already started. Use a fresh session to avoid mixing duplicate or incomplete runs.')
        run_batch(phase,v,n,client=client,folder=folder,model=a.model,temperature=a.temperature,workers=a.workers,variations=phase=='variations')
        report(folder)
    report(folder)

if __name__=='__main__':main()
