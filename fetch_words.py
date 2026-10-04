"""Fetch recent public RSS headlines and extract matches from a locally maintained AWL subset.
No full articles are stored. Expand awl.txt only with words you are permitted to use.
"""
import collections, datetime, json, pathlib, re, urllib.request, xml.etree.ElementTree as ET
BASE=pathlib.Path(__file__).parent
WORDS={x.strip().lower() for x in (BASE/'awl.txt').read_text().splitlines() if x.strip() and not x.startswith('#')}
FEEDS={
 'BBC Science':'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
 'BBC Business':'https://feeds.bbci.co.uk/news/business/rss.xml',
}
counts=collections.Counter();sources=collections.defaultdict(set)
for label,url in FEEDS.items():
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'IELTS-Vocabulary-Study/1.0'})
  with urllib.request.urlopen(req,timeout=15) as res: root=ET.fromstring(res.read(1_000_000))
  for item in root.findall('.//item')[:35]:
   title=item.findtext('title','')
   for token in set(re.findall(r"[A-Za-z]+",title.lower())) & WORDS:
    counts[token]+=1;sources[token].add(label)
 except Exception as exc: print(f'{label}: {exc}')
out=BASE/'data'/'latest.json';out.parent.mkdir(exist_ok=True)
# Keep the previous cache if all feeds fail.
if counts or not out.exists():
 out.write_text(json.dumps({'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'note':'Recent RSS headlines filtered by a small academic vocabulary list; not an IELTS frequency ranking.', 'candidates':[{'word':w,'count':n,'sources':sorted(sources[w])} for w,n in counts.most_common(100)]},ensure_ascii=False,indent=2)+'\n')
print('candidate words:',len(counts))
