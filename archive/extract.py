import sys,re
lib=open("/home/"+__import__('os').environ.get('USER','')+"/x","r") if False else None
import os
p=os.path.expanduser("~/mnt/Cooking/MacArthur Recipes Sep 26 - library.md")
txt=open(p,encoding='utf-8').read()
# find heading lines
lines=txt.split("\n")
heads=[(i,l) for i,l in enumerate(lines) if l.startswith("#")]
names=sys.argv[1:]
for n in names:
    found=False
    for idx,(i,l) in enumerate(heads):
        if n.lower() in l.lower():
            end=heads[idx+1][0] if idx+1<len(heads) else len(lines)
            print("=====",l)
            print("\n".join(lines[i+1:min(end,i+60)]))
            found=True
            break
    if not found:
        print("===== NOT FOUND:",n)
