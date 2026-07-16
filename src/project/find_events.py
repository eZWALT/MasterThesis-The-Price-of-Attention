import re, glob, sys

base = sys.argv[1]
events = set()
for f in glob.glob(base + '/**/*.py', recursive=True):
    for line in open(f):
        m = re.search(r"\.log\(['\"]([\w_]+)['\"]", line)
        if m:
            events.add(m.group(1))
for e in sorted(events):
    print(e)
