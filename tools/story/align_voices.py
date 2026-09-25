#!/usr/bin/env python3
"""Split selected-voice batches into exact in-game lines using measured ASR timestamps.
Reject ambiguous coverage rather than silently shipping misassigned dialogue.
Requires faster-whisper==1.2.1 and soundfile==0.13.1; models cached, not vendored.
"""
import json,re,difflib,subprocess,hashlib,shutil,argparse
from urllib.request import urlopen
from pathlib import Path
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
from huggingface_hub import snapshot_download
parser=argparse.ArgumentParser();parser.add_argument('--corpus',choices=['voices','filmvoices'],default='voices');args=parser.parse_args()
root=Path(__file__).resolve().parents[2];out=root/'BuildData'/args.corpus;plan=json.loads((out/'voice-plan.json').read_text());cache=root/'.cache'/('batches-'+args.corpus);cache.mkdir(parents=True,exist_ok=True);model=None;reports=[];issues=[]
def source(entry):
 path=root/entry.get('source_file',entry.get('file',''))
 if not path.exists():
  assert entry.get('url') and entry.get('sha256'), 'Missing reproducible source metadata'
  path.parent.mkdir(parents=True,exist_ok=True)
  with urlopen(entry['url'],timeout=90) as response:data=response.read()
  assert hashlib.sha256(data).hexdigest()==entry['sha256'];path.write_bytes(data)
 if entry.get('sha256'):assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
 return path
def tokens(s):
 words=re.findall(r'[а-яёa-z0-9]+',s.lower().replace('ё','е'))
 return [{'наргиз':'наргис','илья':'ильяс'}.get(w,w) for w in words]
for i,batch in enumerate(plan['batches']):
 pcm=cache/f'pcm{i}.wav'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(source(batch)),'-ac','1','-ar','24000','-c:a','pcm_s16le',str(pcm)],check=True)
 audio,rate=sf.read(pcm);assert rate==24000
 transcript=cache/('small-'+hashlib.sha256(pcm.read_bytes()).hexdigest()[:16]+'.json')
 if transcript.exists():words=json.loads(transcript.read_text())
 else:
  if model is None:
   pin=json.loads((root/'BuildData/voices/asr-model.lock.json').read_text())
   folder=snapshot_download(pin['repository'],revision=pin['revision'],allow_patterns=['config.json','model.bin','tokenizer.json','vocabulary.json'],cache_dir=str(root/'.cache/whisper'))
   model=WhisperModel(folder,device='cpu',compute_type='int8',cpu_threads=2)
  segments,info=model.transcribe(str(pcm),language='ru',word_timestamps=True,beam_size=5,condition_on_previous_text=False,initial_prompt=('Дэниел Рид, Мара Эллис, Оуэн Харт, Рут. Беллуэзер, шлюз, водомерный пост.' if args.corpus=='filmvoices' else 'Арсен, Лейла, Наргис, Тимур, Ильяс. Лазарет, насосная, шлюз.'))
  words=[{'text':w.word,'start':w.start,'end':w.end} for seg in segments for w in (seg.words or [])];transcript.write_text(json.dumps(words,ensure_ascii=False,indent=2))
 expected=[];ranges=[]
 for line in batch['lines']:
  start=len(expected);expected+=tokens(line['text']);ranges.append((start,len(expected)))
 heard=[];timings=[]
 for word in words:
  for token in tokens(word['text']):heard.append(token);timings.append((word['start'],word['end']))
 matcher=difflib.SequenceMatcher(None,expected,heard,autojunk=False);matches={}
 for block in matcher.get_matching_blocks():
  for j in range(block.size):matches[block.a+j]=block.b+j
 # Keep unmatched/misrecognised words inside their own utterance. Exact-word
 # coverage remains the QA metric; timing may span a full replacement block.
 timed=dict(matches)
 for tag,a0,a1,b0,b1 in matcher.get_opcodes():
  if tag=='replace' and b1>b0:
   for j in range(a0,a1):timed[j]=min(b1-1,b0+int((j-a0)*(b1-b0)/max(1,a1-a0)))
 bounds=[];valid=True
 for line,(start,end) in zip(batch['lines'],ranges):
  mapped=[(j,matches[j]) for j in range(start,end) if j in matches]
  if not mapped:issues.append({'id':line['id'],'error':'no aligned words'});valid=False;bounds.append(None);continue
  coverage=len(mapped)/(end-start);first,last=mapped[0],mapped[-1]
  if coverage<.65 or first[0]-start>2 or end-1-last[0]>2:
   issues.append({'id':line['id'],'error':'low lexical coverage','coverage':round(coverage,3),'expected':line['text'],'heard':' '.join(heard[first[1]:last[1]+1])})
  mapped_times=[timed[j] for j in range(start,end) if j in timed]
  bounds.append((timings[min(mapped_times)][0],timings[max(mapped_times)][1],coverage))
 if not valid:print('BATCH_ALIGNMENT_REJECTED',i,flush=True);continue
 cuts=[0.0]
 for j in range(len(bounds)-1):
  left=bounds[j][1];right=bounds[j+1][0]
  assert right>=left-.08,(batch['lines'][j]['id'],left,right)
  cuts.append((left+right)/2)
 cuts.append(len(audio)/rate)
 for j,(line,bound) in enumerate(zip(batch['lines'],bounds)):
  start,end=cuts[j:j+2];clip=audio[int(start*rate):int(end*rate)].copy();assert len(clip)>2400,line
  # Only soften segment edges; never remove recognised word interiors.
  fade=min(72,len(clip)//4);clip[:fade]*=np.linspace(0,1,fade);clip[-fade:]*=np.linspace(1,0,fade)
  sf.write(out/(line['id']+'.wav'),clip,rate,subtype='PCM_16')
  reports.append({'id':line['id'],'speaker':batch['speaker'],'voice_id':batch['voice_id'],'batch':i,'start_seconds':round(start,3),'end_seconds':round(end,3),'lexical_coverage':round(bound[2],3)})
 print('VOICE_BATCH_ALIGNED',i,len(batch['lines']),'lines',round(len(audio)/rate,1),'seconds',flush=True)
for alias,source in plan.get('aliases',{}).items():
 path=out/(source+'.wav')
 if path.exists():
  shutil.copyfile(path,out/(alias+'.wav'));original=next(r for r in reports if r['id']==source);reports.append(dict(original,id=alias,reuses_line=source))
 else:issues.append({'id':alias,'error':'missing source for shared line'})
for id,override in plan.get('direct_overrides',{}).items():
 dest=out/(id+'.wav');subprocess.run(['ffmpeg','-v','error','-y','-i',str(source(override)),'-ar','24000','-ac','1','-c:a','pcm_s16le',str(dest)],check=True)
 report_clip=next(r for r in reports if r['id']==id);report_clip['replacement']='fresh exact-line synthesis; not a batch cut';report_clip['original_alignment_flag']=[q for q in issues if q['id']==id]
 issues=[q for q in issues if q['id']!=id]
report={'lines_expected'  :plan['full_corpus_lines'],'lines_written':len(reports),'voice_count':len(plan['voices']),'issues':issues,'clips':reports,'in_game_audio_verified':False}
(out/'voice-alignment.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('VOICE_ALIGNMENT_COMPLETE',len(reports),'lines',len(issues),'review flags',flush=True)
if len(reports)!=plan['full_corpus_lines'] or issues:raise SystemExit(2)
