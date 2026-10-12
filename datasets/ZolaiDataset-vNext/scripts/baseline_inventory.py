"""Read ONLY committed corpus files; never read SaaS operational data or secrets."""
import argparse,collections,gzip,hashlib,json,pathlib,re,sqlite3,unicodedata,subprocess

def normalize(text):return ' '.join(unicodedata.normalize('NFC',text).split())
def folded(text):return ' '.join(re.findall(r'[^\W_]+',normalize(text).casefold(),re.UNICODE))
def digest(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def strings(obj):
 if isinstance(obj,dict):
  for k,v in obj.items():
   if k in ('text','zomi','target_text','verse_text') and isinstance(v,str):yield v
   elif isinstance(v,(dict,list)):yield from strings(v)
 elif isinstance(obj,list):
  for x in obj:yield from strings(x)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=pathlib.Path,default=pathlib.Path('.'));ap.add_argument('--output',type=pathlib.Path,required=True);a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 hashes=set();fh=set();files=[];blobs=set()
 paths=sorted(a.root.glob('backend/datasets/raw/bibles/*_corpus.json'))
 for p in paths:
  b=p.read_bytes();sha=digest(b.decode('utf-8-sig'));n=0
  for t in strings(json.loads(b)):
   hashes.add(digest(normalize(t)));fh.add(digest(folded(t)));n+=1
  files.append({'path':str(p.relative_to(a.root)),'sha256_utf8':sha,'bytes':len(b),'text_records_examined':n})
 for rel in ['backend/corpus/ZomiCorpusRepository.js','backend/corpus/TranslationCorpusRepository.js','backend/corpus/SyllableRepository.js']:
  p=a.root/rel
  if not p.exists():continue
  b=p.read_bytes();s=b.decode('utf-8');ts=re.findall(r'\b(?:text|target_text|word):\s*"([^"\n]*)"',s)
  for t in ts:hashes.add(digest(normalize(t)));fh.add(digest(folded(t)))
  files.append({'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'text_records_examined':len(ts)})
 p=a.root/'app/src/main/assets/databases/tedim_bible_77.db'
 if p.exists():
  con=sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True);n=0
  for (table,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
   q='"'+table.replace('"','""')+'"';cols=[x[1] for x in con.execute('PRAGMA table_info('+q+')') if x[1].lower() in ['text','verse_text','content','zomi']]
   for col in cols:
    c='"'+col.replace('"','""')+'"'
    for (t,) in con.execute('SELECT '+c+' FROM '+q):
     if isinstance(t,str):hashes.add(digest(normalize(t)));fh.add(digest(folded(t)));n+=1
  con.close();files.append({'path':str(p.relative_to(a.root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'text_records_examined':n})
 for name,ss in [('exact',hashes),('folded',fh)]:
  with gzip.open(a.output/(name+'-hashes.txt.gz'),'wt',encoding='ascii',newline='\n') as f:f.write('\n'.join(sorted(ss))+'\n')
 try:commit=subprocess.check_output(['git','-C',str(a.root),'rev-parse','HEAD'],text=True).strip()
 except Exception:commit='UNKNOWN'
 result={'status':'VERIFIED_COMMITTED_ALLOWLIST_ONLY','commit':commit,'files':files,'unique_exact_texts':len(hashes),'unique_folded_texts':len(fh),'excluded':'SaaS users/profiles/payments/usage, secrets, local uncommitted files, deployed runtime stores; not examined and never exported.','limitations':'Only text/target_text/zomi/word fields and recognized Bible SQLite columns. Full deployed/private corpus novelty remains UNKNOWN.'}
 (a.output/'BaselineReport.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
