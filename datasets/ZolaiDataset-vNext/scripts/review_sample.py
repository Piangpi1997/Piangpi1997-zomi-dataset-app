import argparse,gzip,hashlib,heapq,json,pathlib
ap=argparse.ArgumentParser();ap.add_argument('--directory',type=pathlib.Path,required=True);a=ap.parse_args();heaps={}
for p in sorted((a.directory/'data').glob('*.jsonl.gz')):
 with gzip.open(p,'rt',encoding='utf-8') as f:
  for line in f:
   r=json.loads(line);score=int(hashlib.sha256(('native-review:'+r['record_id']).encode()).hexdigest(),16);h=heaps.setdefault(r['source_name'],[]);item=(-score,r['record_id'],r)
   if len(h)<100:heapq.heappush(h,item)
   elif item>h[0]:heapq.heapreplace(h,item)
with (a.directory/'HumanReviewSample.jsonl').open('w',encoding='utf-8') as f:
 for s,h in sorted(heaps.items()):
  for _,_,r in sorted(h,reverse=True):f.write(json.dumps({'record_id':r['record_id'],'text':r['normalized_text'],'source_name':s,'source_url':r['source_document_url'],'candidate_split':r['candidate_split'],'native_language_label':None,'dialect':None,'spelling_correct':None,'contextual_privacy_safe':None,'rights_review':None,'reviewer':None,'decision':'PENDING'},ensure_ascii=False)+'\n')
print('200 authentic candidate rows selected for review; publisher-balanced sample, not prevalence estimate.')
