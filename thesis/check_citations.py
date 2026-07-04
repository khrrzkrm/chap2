import re
import glob

# Extract all keys cited in all .tex files
tex_keys = set()
for tex_path in glob.glob('*.tex'):
    with open(tex_path, 'r', encoding='utf-8', errors='replace') as f:
        tex_content = f.read()
    # Find all occurrences of \cite{...} or \nocite{...} or similar
    citations = re.findall(r'\\cite(?:[a-zA-Z]*)\s*\{([^}]+)\}', tex_content)
    for cit in citations:
        for k in cit.split(','):
            tex_keys.add(k.strip())

# Read keys from thesisz.bib
with open('thesisz.bib', 'r', encoding='utf-8') as f:
    bib_content = f.read()

bib_keys = set()
matches = re.finditer(r'@(\w+)\s*\{\s*([^,\s]+)', bib_content)
for m in matches:
    bib_keys.add(m.group(2).strip())

missing = []
case_mismatches = []
for k in sorted(tex_keys):
    if not k:
        continue
    matched = False
    for bk in bib_keys:
        if bk.lower() == k.lower():
            matched = True
            if bk != k:
                case_mismatches.append((k, bk))
            break
    if not matched:
        missing.append(k)

print('Total unique keys cited in .tex files:', len(tex_keys))
print('Total keys in thesisz.bib:', len(bib_keys))
print('Case mismatches found:', len(case_mismatches))
for cited, in_bib in case_mismatches:
    print(f"  - Cited as: '{cited}', in Bib: '{in_bib}'")
print('Keys cited in .tex but missing in thesisz.bib:', len(missing))
print(missing)
