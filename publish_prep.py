#!/usr/bin/env python3
"""
Split the rebuilt library into the project's per-category documents and report
which ones differ from what is PUBLISHED, so only those need republishing.

    python3 build2.py && python3 publish_prep.py     # report only
    ...project_write each NEW/CHANGED doc, project_delete each GONE...
    python3 publish_prep.py --mark                   # record them as published

published.json is committed. It moves only on --mark, so it always describes the
project, never merely "what the last run saw" - the old manifest was rewritten on
every run and went stale whenever a run was not followed by a publish.
"""
import re,os,sys,json,hashlib,shutil
LIB="build/MacArthur Recipes Sep 26 - library.md"
ROS="build/MacArthur Recipes Sep 26 - roster.md"
OUT="build/docs"
MAN="published.json"
LIMIT=95000

def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def split(src):
    lines=src.split("\n"); idx=[i for i,l in enumerate(lines) if l.startswith("# ")]+[len(lines)]
    docs={}
    for a,b in zip(idx[:-1],idx[1:]):
        nm=lines[a][2:].strip(); body="\n".join(lines[a:b]).strip()
        if nm=="The MacArthur Family Recipes": docs["00-overview-and-whats-new.md"]=body; continue
        if len(body.encode())<=LIMIT: docs[f"{slug(nm)}.md"]=body; continue
        L=body.split("\n"); i=0
        while i<len(L) and not L[i].startswith('<a id='): i+=1
        st=[j for j in range(i,len(L)) if L[j].startswith('<a id=')]+[len(L)]
        ch=[];cur=[];sz=0
        for x,y in zip(st,st[1:]):
            blk="\n".join(L[x:y])
            if sz and sz+len(blk.encode())>LIMIT: ch.append(cur);cur=[];sz=0
            cur.append(blk); sz+=len(blk.encode())
        if cur: ch.append(cur)
        for q,c in enumerate(ch,1):
            docs[f"{slug(nm)}-{q}.md"]=f"# {nm} — part {q} of {len(ch)}\n\n"+"\n".join(c)
    return docs

shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT)
docs=split(open(LIB,encoding="utf-8").read())
docs["00-roster-complete.md"]=open(ROS,encoding="utf-8").read()
for k,v in docs.items(): open(os.path.join(OUT,k),"w",encoding="utf-8").write(v)
new={k:hashlib.md5(v.encode()).hexdigest() for k,v in docs.items()}
if "--mark" in sys.argv:
    json.dump(new,open(MAN,"w"),indent=1,sort_keys=True); open(MAN,"a").write("\n")
    print("published.json now records",len(new),"docs as published - commit it."); sys.exit()
old=json.load(open(MAN)) if os.path.exists(MAN) else {}
NEW=sorted(set(new)-set(old)); CH=sorted(k for k in set(new)&set(old) if new[k]!=old[k]); GONE=sorted(set(old)-set(new))
print("documents:",len(new))
print("NEW     :",NEW or "none")
print("CHANGED :",CH or "none")
print("GONE    :",GONE or "none")
print("\nfiles are in",OUT,"- project path is recipes/<name>")
print("project_write NEW+CHANGED (local_path), project_delete GONE, then: python3 publish_prep.py --mark")
print("then refresh the phone page: python3 page.py + Artifact publish (CLAUDE.md step 3)")
