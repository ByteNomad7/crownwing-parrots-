from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter,deque
import re,json,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]/'dist'
pages={('/' if p.parent==root else '/'+p.parent.relative_to(root).as_posix()+'/'):p for p in root.rglob('index.html')}
class Parse(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.ids=set();self.h1=0;self.text=[];self.canon=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='h1':self.h1+=1
  if d.get('id'):self.ids.add(d['id'])
  if t in ['a','link','img','script']:
   v=d.get('href',d.get('src'))
   if v:self.refs.append((t,v))
  if t=='link' and d.get('rel')=='canonical':self.canon.append(d['href'])
 def handle_data(self,d):self.text.append(d)
parsed={}
titles=[];descs=[];words=0
for path,p in pages.items():
 s=p.read_text();o=Parse();o.feed(s);parsed[path]=o
 assert o.h1==1,(path,'h1 count',o.h1)
 assert len(o.canon)==1 and o.canon[0].endswith(path),(path,'canonical')
 titles.append(re.search('<title>(.*?)</title>',s).group(1));descs.append(re.search('<meta name="description" content="([^"]*)"',s).group(1))
 for block in re.findall('<script type="application/ld\\+json">(.*?)</script>',s,re.S):json.loads(block)
 words+=len(' '.join(o.text).split())
assert len(set(titles))==len(pages),'Duplicate titles'
assert len(set(descs))==len(pages),'Duplicate descriptions'
graph={k:set() for k in pages};links=0
for path,o in parsed.items():
 for tag,v in o.refs:
  u=urlsplit(v)
  if u.scheme or u.netloc:continue
  local=unquote(u.path)
  target=(root/local.lstrip('/')) if local.startswith('/') else pages[path].parent/local
  if not local:target=pages[path]
  if target.is_dir():target=target/'index.html'
  assert target.exists(),(path,'missing target',v)
  if tag=='a' and target.name=='index.html':
   dest='/' if target.parent==root else '/'+target.parent.relative_to(root).as_posix()+'/'
   assert dest in pages,(path,dest)
   if u.fragment:assert u.fragment in parsed[dest].ids,(path,'missing fragment',v)
   graph[path].add(dest);links+=1
seen={'/'};q=deque(['/'])
while q:
 for dest in graph[q.popleft()]:
  if dest not in seen:seen.add(dest);q.append(dest)
assert seen==set(pages),('Unreachable pages',set(pages)-seen)
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'};urls=ET.parse(root/'sitemap.xml').findall('.//s:loc',ns)
indexable={path for path,p in pages.items() if 'content="noindex,follow"' not in p.read_text()}
assert {urlsplit(u.text).path for u in urls}==indexable,'Sitemap coverage'
assert all('href="/our-approach/"' in p.read_text() for p in pages.values()),'Approach navigation'
print(json.dumps({'pages':len(pages),'internal_links':links,'approximate_words_including_navigation':words,'unique_titles_and_descriptions':True,'all_pages_reachable':True,'sitemap_coverage':'all indexable pages','city_review_drafts':len(pages)-len(indexable),'local_assets_and_fragment_links':'passed','schema_json':'passed'},indent=2))
