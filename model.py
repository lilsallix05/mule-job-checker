"""Small supervised multinomial Naive Bayes baseline; synthetic corpus only."""
from collections import Counter
import hashlib,json,math,re
from pathlib import Path
from checker import ROOT
CLASSES=['low','review','high']
TEST_FAMILIES={'secret_funds','lend_account','remote_device','task_escalation','promise','referral','design','sports'}

def tokens(text): return re.findall(r'[^\W\d_]{2,}',text.lower(),re.UNICODE)

def fit(rows):
    counts={k:Counter() for k in CLASSES}; n=Counter(); vocab=set()
    for r in rows:
        ts=tokens(r['text']);counts[r['label']].update(ts);n[r['label']]+=1;vocab.update(ts)
    return {'version':1,'kind':'Multinomial Naive Bayes, add-one smoothing','classes':CLASSES,'documents':dict(n),
            'counts':{k:dict(v) for k,v in counts.items()},'vocabulary':sorted(vocab),
            'training_ids':[r['id'] for r in rows],'training_families':sorted({r['family'] for r in rows})}

def predict(text,model=None):
    if model is None: model=json.loads((ROOT/'data/model.json').read_text())
    vocab=set(model['vocabulary']);ts=Counter(x for x in tokens(text) if x in vocab)
    scores={}
    for k in CLASSES:
        c=model['counts'][k];den=sum(c.values())+len(vocab)
        scores[k]=math.log(model['documents'][k]/sum(model['documents'].values()))+sum(n*math.log((c.get(t,0)+1)/den) for t,n in ts.items())
    best=max(scores,key=scores.get) if ts else 'insufficient'
    return {'label':best,'known_tokens':sum(ts.values()),'basis':'Experimental synthetic-trained text baseline; not calibrated and does not change rules.',
            'top_terms':sorted(ts,key=lambda t:model['counts'][best].get(t,0),reverse=True)[:8]}

def train_evaluate():
    raw=(ROOT/'data/offers.json').read_bytes();rows=json.loads(raw)
    train=[r for r in rows if r['family'] not in TEST_FAMILIES];test=[r for r in rows if r['family'] in TEST_FAMILIES]
    assert not ({r['family'] for r in train}&{r['family'] for r in test})
    assert not ({r['text'].casefold() for r in train}&{r['text'].casefold() for r in test})
    model=fit(train);matrix=[[0]*3 for _ in CLASSES];predictions=[]
    for row in test:
        pred=predict(row['text'],model)['label'];matrix[CLASSES.index(row['label'])][CLASSES.index(pred)]+=1
        predictions.append({'id':row['id'],'expected':row['label'],'predicted':pred})
    metrics={}
    for i,k in enumerate(CLASSES):
        tp=matrix[i][i];p=sum(row[i] for row in matrix);r=sum(matrix[i]);metrics[k]={'precision':tp/p if p else 0,'recall':tp/r if r else 0,'support':r}
    report={'model':model['kind'],'train_size':len(train),'test_size':len(test),'test_families':sorted(TEST_FAMILIES),'train_families':model['training_families'],
        'corpus_sha256':hashlib.sha256(raw).hexdigest(),'labels':CLASSES,'confusion_matrix':matrix,'per_class':metrics,'predictions':predictions,
        'limits':'Fixed family-held-out split of synthetic examples, translations grouped. No tuning on test labels. Tiny authored test set is not evidence of real-world detection quality.'}
    (ROOT/'data/model.json').write_text(json.dumps(model,indent=2));(ROOT/'evidence/model-evaluation.json').write_text(json.dumps(report,indent=2));return report
if __name__=='__main__':print(json.dumps(train_evaluate(),indent=2))
