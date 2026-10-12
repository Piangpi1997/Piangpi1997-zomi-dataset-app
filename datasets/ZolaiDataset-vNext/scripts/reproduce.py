"""Download a pinned public licensed source and rebuild the gated candidate."""
import argparse,pathlib,subprocess,sys,urllib.request,hashlib
from build_candidate import REV,EXPECTED
ap=argparse.ArgumentParser()
inputs=ap.add_mutually_exclusive_group(required=True)
inputs.add_argument('--project',type=pathlib.Path)
inputs.add_argument('--baseline',type=pathlib.Path)
ap.add_argument('--output',type=pathlib.Path,required=True)
a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True);raw=a.output/'raw';raw.mkdir(exist_ok=True);csv=raw/'corpus.csv';scripts=pathlib.Path(__file__).parent
if a.baseline:
 baseline=a.baseline
 for name in ['BaselineReport.json','exact-hashes.txt.gz','folded-hashes.txt.gz']:
  if not (baseline/name).is_file():raise SystemExit('Missing frozen baseline file: '+name)
else:
 baseline=a.output/'baseline'
 subprocess.run([sys.executable,str(scripts/'baseline_inventory.py'),'--root',str(a.project),'--output',str(baseline)],check=True)
url='https://huggingface.co/datasets/LianHong/zomi-monolingual-corpus/resolve/'+REV+'/data/zomi_monolingual_corpus_v1.0.csv'
if not csv.exists() or hashlib.sha256(csv.read_bytes()).hexdigest()!=EXPECTED:
 with urllib.request.urlopen(url,timeout=90) as r,csv.open('wb') as f:
  while True:
   chunk=r.read(1024*1024)
   if not chunk:break
   f.write(chunk)
if hashlib.sha256(csv.read_bytes()).hexdigest()!=EXPECTED:raise SystemExit('Checksum mismatch: blocked')
subprocess.run([sys.executable,str(scripts/'build_candidate.py'),'--csv',str(csv),'--output',str(a.output/'candidate'),'--baseline',str(baseline)],check=True)
print('Candidate built. Training remains disabled. Native review and rights/novelty gates must be resolved.')
