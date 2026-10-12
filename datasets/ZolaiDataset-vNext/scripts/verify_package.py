"""Independent checks of serialized candidate records and provisional partitions."""
import argparse,collections,gzip,hashlib,json,pathlib,re,unicodedata
ap=argparse.ArgumentParser();ap.add_argument('--directory',type=pathlib.Path,required=True);a=ap.parse_args();p=a.directory;q=json.load((p/'QualityReport.json').open());gate=json.load((p/'TrainingGate.json').open());assert gate['training_enabled'] is False and gate['approved_training_rows']==0
ids=set();hashes=set();folds=set();groups={};counts=collections.Counter();flagged=0
for sp in ['train','validation','test']:
 with gzip.open(p/'data'/(sp+'.jsonl.gz'),'rt',encoding='utf-8') as f:
  for line in f:
   r=json.loads(line);counts[sp]+=1
   assert r['record_id'] not in ids;ids.add(r['record_id'])
   norm=' '.join(unicodedata.normalize('NFC',r['original_text']).split());assert norm==r['normalized_text']
   h=hashlib.sha256(norm.encode()).hexdigest();assert h==r['content_sha256'];assert h not in hashes;hashes.add(h)
   folded=' '.join(re.findall(r'[^\W_]+',norm.casefold(),re.UNICODE));fh=hashlib.sha256(folded.encode()).hexdigest();assert fh==r['folded_sha256'];assert fh not in folds;folds.add(fh)
   assert r['training_eligible'] is False and r['license']=='CC-BY-4.0';assert r['source_revision']=='9c6bde579fcd0dc8f4e3b52a44d0632d8ac1cff8'
   assert r['candidate_split']==sp;g=r['split_group'];assert g not in groups or groups[g]==sp;groups[g]=sp
   assert r['dialect_independent_verification']=='UNKNOWN'
   if 'near_duplicate_review' in r['quality_flags']:flagged+=1
with gzip.open(p/'quarantine/record_decisions.jsonl.gz','rt',encoding='utf-8') as f:
 excluded=[]
 for line in f:
  r=json.loads(line);assert set(r)=={'sentence_id','source_row','content_sha256','reasons'};assert r['reasons'];excluded.append(r)
assert dict(counts)==q['split_rows'];assert sum(counts.values())==q['retained_candidate_rows'];assert len(excluded)==q['excluded_rows'];assert len(excluded)+sum(counts.values())==q['counts']['input_rows']
result={'status':'PASS','serialized_rows_verified':sum(counts.values()),'quarantine_rows_verified':len(excluded),'split_counts':dict(counts),'unique_ids':len(ids),'unique_exact_hashes':len(hashes),'unique_folded_hashes':len(folds),'cross_split_document_components':0,'training_enabled':False,'near_flags':flagged}
(p/'PackageVerification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
