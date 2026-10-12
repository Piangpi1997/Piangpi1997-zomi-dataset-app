"""Reproducible candidate audit. No model training, runtime deployment or user-memory writes."""
import argparse,collections,csv,gzip,hashlib,json,pathlib,re,unicodedata,urllib.parse
from baseline_inventory import normalize,folded,digest
REV='9c6bde579fcd0dc8f4e3b52a44d0632d8ac1cff8'
EXPECTED='7c84b835e45fdb26aef8822367dbc698988c5a28bdfd7d992cc50bed011353fd'
EMAIL=re.compile(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b')
PHONE=re.compile(r'(?<!\w)(?:\+\d[\d ()-]{7,}\d|0[1-9]\d[\d -]{5,}\d)(?!\w)')
LONGNUM=re.compile(r'(?<!\d)\d{9,19}(?!\d)')
HTML=re.compile(r'</?[A-Za-z][^>]*>')
URL=re.compile(r'https?://\S+|www\.\S+',re.I)
SPAM=re.compile(r'click here|subscribe now|cookie policy|join.{0,10}telegram|buy now|free money',re.I)
class Groups:
 def __init__(self):self.p={}
 def find(self,x):
  self.p.setdefault(x,x)
  if self.p[x]!=x:self.p[x]=self.find(self.p[x])
  return self.p[x]
 def union(self,a,b):
  a,b=self.find(a),self.find(b)
  if a!=b:self.p[max(a,b)]=min(a,b)
def source_group(row):
 m=re.search(r'Source:\s*(https?://[^;\s]+)',row.get('notes',''))
 if not m:return None,None
 u=urllib.parse.urlsplit(m.group(1));uri=urllib.parse.urlunsplit((u.scheme.lower(),u.netloc.lower(),u.path.rstrip('/')+'/', '', ''))
 return uri,digest(uri)
def checks(row,text):
 reasons=[];flags=[]
 if row.get('permission_status','').lower()!='approved':reasons.append('permission_not_approved')
 if row.get('review_status','').lower()!='approved':flags.append('upstream_review_not_approved')
 if not row.get('sentence_id'):reasons.append('missing_id')
 if '\ufffd' in text or any(unicodedata.category(c) in ('Cs','Co','Cc') and c not in '\n\r\t' for c in text):reasons.append('corrupt_or_control_text')
 if not 20<=len(text)<=5000 or len(text.split())<4:reasons.append('fragment_or_abnormal_length')
 if HTML.search(text):reasons.append('html_markup')
 if EMAIL.search(text) or PHONE.search(text) or LONGNUM.search(text):reasons.append('possible_contact_or_sensitive_identifier')
 if URL.search(text):reasons.append('embedded_link_review')
 if SPAM.search(text):reasons.append('spam_or_boilerplate_review')
 toks=folded(text).split();counts=collections.Counter(toks)
 if counts and max(counts.values())>=8 and max(counts.values())/len(toks)>.35:reasons.append('repetitive_spam_review')
 letters=[c for c in text if c.isalpha()];latin=sum('LATIN' in unicodedata.name(c,'') for c in letters)
 if not letters or latin/len(letters)<.8:reasons.append('mixed_script_or_language_review')
 en={'the','and','of','to','is','are','that','with','this','you','your','from','for','have','was','were','will','their','they'}
 if toks and sum(t in en for t in toks)/len(toks)>.35:reasons.append('possible_english_review')
 if any('\u1000'<=c<='\u109f' for c in text):flags.append('myanmar_script_present')
 if row.get('spelling_standard','').lower() in ['unknown','']:flags.append('spelling_standard_unknown')
 flags.extend(['independent_native_review_unknown','upstream_review_asserted_not_independently_repeated'])
 return sorted(set(reasons)),sorted(set(flags))
def split_for(group):
 n=int(digest('ZolaiDataset-vNext-20261007:'+group)[:8],16)%10000
 return 'train' if n<8000 else ('validation' if n<9000 else 'test')
def write_gzip(path,rows):
 with path.open('wb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as f:
  for row in rows:f.write((json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--csv',type=pathlib.Path,required=True);ap.add_argument('--output',type=pathlib.Path,required=True);ap.add_argument('--baseline',type=pathlib.Path);a=ap.parse_args();o=a.output;o.mkdir(parents=True,exist_ok=True);(o/'data').mkdir(exist_ok=True);(o/'quarantine').mkdir(exist_ok=True)
 h=hashlib.sha256(a.csv.read_bytes()).hexdigest()
 if h!=EXPECTED:raise SystemExit('Input checksum differs from pinned licensed release; ingestion blocked.')
 baseline=set();baseline_fold=set();baseline_report={'status':'UNVERIFIED','limitations':'No verified baseline supplied; novelty remains UNKNOWN.'}
 if a.baseline:
  baseline_report=json.load((a.baseline/'BaselineReport.json').open())
  for name,target in [('exact',baseline),('folded',baseline_fold)]:
   with gzip.open(a.baseline/(name+'-hashes.txt.gz'),'rt',encoding='ascii') as f:target.update(x.strip() for x in f if x.strip())
 groups=Groups();seen={};seen_fold={};ids=set();kept=[];excluded=[];reasons_count=collections.Counter();flag_count=collections.Counter();source_count=collections.Counter();topic_count=collections.Counter();stats=collections.Counter();buckets=collections.defaultdict(list)
 with a.csv.open(encoding='utf-8-sig',newline='') as f:
  reader=csv.DictReader(f)
  for idx,row in enumerate(reader,1):
   stats['input_rows']+=1;text=normalize(row.get('zomi_text',''));key=digest(text);fold=folded(text);fk=digest(fold);uri,group=source_group(row);bad,flags=checks(row,text)
   if row.get('sentence_id') in ids:bad.append('duplicate_id')
   ids.add(row.get('sentence_id'))
   if not group:bad.append('missing_document_provenance')
   else:groups.find(group)
   if key in seen:
    bad.append('exact_duplicate');groups.union(group or key,seen[key])
   elif fk in seen_fold:
    bad.append('punctuation_case_duplicate_review');groups.union(group or key,seen_fold[fk])
   if key in baseline or fk in baseline_fold:bad.append('existing_committed_corpus_overlap')
   if bad:
    for reason in set(bad):reasons_count[reason]+=1
    excluded.append({'sentence_id':row.get('sentence_id'),'source_row':idx,'content_sha256':key,'reasons':sorted(set(bad))})
    continue
   seen[key]=group;seen_fold[fk]=group
   toks=fold.split();sig=tuple(toks[:4]+toks[-4:])
   if len(toks)>=16:
    sh=set(tuple(toks[i:i+3]) for i in range(len(toks)-2))
    for old_sh,old_group in buckets[sig]:
     stats['near_pairs_checked']+=1
     if len(sh & old_sh)/max(1,len(sh | old_sh))>=.9:
      stats['near_pairs_detected']+=1;groups.union(group,old_group);flags.append('near_duplicate_review');break
    if len(buckets[sig])<16:buckets[sig].append((sh,group))
    else:stats['near_bucket_cap_skipped']+=1
   # Weighted conservative proxy: language .5 (source assertion), human .5
   # (upstream reviewer metadata); the independent correctness checks remain UNKNOWN.
   components={'language_correctness_proxy':.5,'human_review_proxy':.5,'source_provenance':1.,'completeness':1.,'format_cleanliness':1.,'license_notice':1.,'domain_balance_proxy':.5,'duplicate_status':.5 if 'near_duplicate_review' in flags else 1.}
   weights={'language_correctness_proxy':.30,'human_review_proxy':.20,'source_provenance':.15,'completeness':.10,'format_cleanliness':.05,'license_notice':.10,'domain_balance_proxy':.05,'duplicate_status':.05}
   score=round(sum(components[k]*weights[k] for k in weights),3)
   record={'record_id':row['sentence_id'],'original_text':row['zomi_text'],'normalized_text':text,'content_sha256':key,'folded_sha256':fk,'source_dataset':'LianHong/zomi-monolingual-corpus','source_revision':REV,'source_row':idx,'source_document_url':uri,'document_group':group,'source_name':row.get('source_name'),'source_type':row.get('source_type'),'topic':row.get('topic'),'region_source_label':row.get('region'),'language_source_label':'Zomi','iso639_3_source_label':'ctd','dialect_label':'Tedim Chin (SOURCE_DECLARED)','dialect_independent_verification':'UNKNOWN','spelling_standard':row.get('spelling_standard'),'license':'CC-BY-4.0','permission_status':'UPSTREAM_APPROVED_CLAIM; PUBLISHER_NOTICE_VERIFIED','upstream_reviewer':row.get('reviewer_1'),'upstream_review_status':row.get('review_status'),'quality_score_heuristic':score,'quality_components':components,'quality_flags':sorted(set(flags)),'training_eligible':False,'novelty':'NOT_IN_COMMITTED_ALLOWLIST; DEPLOYED_CORPUS_UNKNOWN' if a.baseline else 'UNKNOWN'}
   kept.append(record);source_count[record['source_name']]+=1;topic_count[record['topic']]+=1;flag_count.update(record['quality_flags'])
 splits=collections.Counter();group_splits={};source_splits=collections.defaultdict(collections.Counter);split_rows={k:[] for k in ['train','validation','test']};scores=collections.Counter()
 for r in kept:
  component=groups.find(r['document_group']);sp=split_for(component);r['split_group']=component;r['candidate_split']=sp;splits[sp]+=1;split_rows[sp].append(r);scores[r['quality_score_heuristic']]+=1;source_splits[sp][r['source_name']]+=1
  if component in group_splits and group_splits[component]!=sp:raise RuntimeError('Split leakage')
  group_splits[component]=sp
 for sp,rs in split_rows.items():write_gzip(o/'data'/(sp+'.jsonl.gz'),rs)
 write_gzip(o/'quarantine'/'record_decisions.jsonl.gz',excluded)
 group_sets={sp:{r['split_group'] for r in rs} for sp,rs in split_rows.items()};hash_sets={sp:{r['content_sha256'] for r in rs} for sp,rs in split_rows.items()};fold_sets={sp:{r['folded_sha256'] for r in rs} for sp,rs in split_rows.items()}
 for mapping in [group_sets,hash_sets,fold_sets]:
  assert not (mapping['train']&mapping['test'] or mapping['train']&mapping['validation'] or mapping['validation']&mapping['test'])
 assert len(kept)+len(excluded)==stats['input_rows'];assert len({r['record_id'] for r in kept})==len(kept);assert all(not r['training_eligible'] for r in kept)
 result={'version':'ZolaiDataset-vNext-20261007-candidate.1','status':'HUMAN_REVIEW_REQUIRED; TRAINING_DISABLED','source_sha256':h,'measured_csv_bytes':a.csv.stat().st_size,'counts':dict(stats),'retained_candidate_rows':len(kept),'excluded_rows':len(excluded),'exclusion_reasons_multilabel':dict(reasons_count),'quality_flags_multilabel':dict(flag_count),'quality_score_distribution':dict(scores),'source_distribution':dict(source_count),'topic_distribution':dict(topic_count),'split_rows':dict(splits),'split_groups':{sp:len(ss) for sp,ss in group_sets.items()},'source_split_distribution':{sp:dict(c) for sp,c in source_splits.items()},'split_policy':'80/10/10 hash buckets by source document plus connected duplicate groups; row ratios are measured, not forced.','split_leakage_tests':{'exact_hash_overlap':0,'folded_hash_overlap':0,'document_component_overlap':0},'baseline':baseline_report,'baseline_overlap_rows':reasons_count['existing_committed_corpus_overlap'],'language_identity':'Preserve source Zomi and ctd/Tedim labels, no independent native adjudication; no Zo/Zopau/Zolai relabeling.','limitations':['Quality scores are conservative heuristics, not independently validated language/spelling scores.','No native review was performed by this pipeline.','Upstream written permission is publicly asserted; private correspondence was not examined.','PII/spam/language regexes may miss sensitive information and may flag benign numbers. Named individuals and contextual privacy require human review.','Near duplicate search checks trigram Jaccard >= .9 only in shared first/last four-token buckets, capped 16 candidates. Unchecked near duplicates and paraphrases may remain.','No semantic or task-evaluation leakage verification; frozen test is provisional until native review.','Novelty is against committed allowlist only, not deployed/local runtime databases.','Monolingual corpus is not aligned translation supervision.']}
 (o/'QualityReport.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));(o/'SplitManifest.json').write_text(json.dumps({'version':result['version'],'seed':'ZolaiDataset-vNext-20261007','policy':result['split_policy'],'counts':dict(splits),'groups':{sp:len(ss) for sp,ss in group_sets.items()},'test_status':'PROVISIONAL_FROZEN_FILE_HASH; NOT_CERTIFIED_EVALUATION_SET','training_enabled':False},indent=2));print(json.dumps({k:result[k] for k in ['counts','retained_candidate_rows','excluded_rows','split_rows','baseline_overlap_rows','quality_score_distribution']},indent=2))
if __name__=='__main__':main()
