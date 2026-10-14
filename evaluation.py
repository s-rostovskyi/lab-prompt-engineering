"""Deterministic checks, not a substitute for human factual/style review."""
import json
from collections import Counter

def evaluate(task, case, text):
    problems = []
    if task == 'sentiment':
        if text not in {'positive','negative','neutral'}: problems.append('label_format')
        if text.strip().lower() != case['expected']: problems.append('wrong_sentiment')
    else:
        try:
            obj = json.loads(text)
        except (ValueError, TypeError):
            return ['invalid_json']
        if not isinstance(obj, dict): return ['not_object']
        if task == 'extraction':
            if set(obj) != set(case['expected']): problems.append('schema_fields')
            for key, expected in case['expected'].items():
                if obj.get(key) != expected: problems.append('wrong_'+key)
        else:
            if set(obj) != {'title','description','price'}: problems.append('schema_fields')
            if obj.get('title') != case['input']['name']: problems.append('wrong_title')
            if obj.get('price') != case['input']['price']: problems.append('wrong_price')
            desc = obj.get('description')
            if not isinstance(desc,str): problems.append('description_type')
            else:
                if not 30 <= len(desc.split()) <= 45: problems.append('word_count')
                if '\n' in desc or any(x in desc for x in ['•','- ', '* ']): problems.append('paragraph_format')
                if case['input']['name'].lower() not in desc.lower(): problems.append('missing_name')
                # A screen for common invented features; human review is still required.
                banned = ['bluetooth','ergonomic','battery','dpi','compatible','warranty','discount','waterproof','rechargeable','precision','durable','lightweight','portable']
                if any(x in desc.lower() and x not in case['input']['name'].lower() for x in banned): problems.append('unsupported_claim_screen')
    return problems

def summarize(rows):
    n=len(rows)
    success=[r for r in rows if r['status']=='ok']
    fmt={'label_format','invalid_json','not_object','schema_fields','word_count','paragraph_format','description_type'}
    return {
        'attempted':n,'api_success':len(success),
        'format_pct':100*sum(not fmt.intersection(r['failures']) for r in success)/n if n else None,
        'consistency_pct':100*sum(not r['failures'] for r in success)/n if n else None,
        'exact_match_pct':100*max(Counter(r['response'] for r in success).values(),default=0)/n if n else None,
        'unique_responses':len(set(r['response'] for r in success)),
        'failure_counts':dict(Counter(p for r in rows for p in r['failures']))
    }
