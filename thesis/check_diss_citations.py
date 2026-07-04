import re
import os

def resolve_includes(file_path, base_dir='.'):
    # Recursively find all included/input files
    full_path = os.path.join(base_dir, file_path)
    if not os.path.exists(full_path) and not file_path.endswith('.tex'):
        full_path += '.tex'
    
    if not os.path.exists(full_path):
        return []
        
    with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        
    # Remove comments to avoid parsing commented out inputs/citations
    content = re.sub(r'%.*?\n', '\n', content)
    
    included_files = [file_path]
    # Find \input{...} and \include{...}
    inputs = re.findall(r'\\(?:input|include)\s*\{([^}]+)\}', content)
    for inp in inputs:
        # resolve recursively
        included_files.extend(resolve_includes(inp, base_dir))
        
    return included_files

# Resolve all files starting from thesis.tex
all_dissertation_files = set(resolve_includes('thesis.tex'))
print("Files included in the dissertation:")
for f in sorted(all_dissertation_files):
    print(f"  - {f}")

# Extract all keys cited in these files
diss_keys = set()
for f in all_dissertation_files:
    full_path = f if f.endswith('.tex') else f + '.tex'
    if not os.path.exists(full_path):
        continue
    with open(full_path, 'r', encoding='utf-8', errors='replace') as file_obj:
        content = file_obj.read()
    # Remove comments
    content = re.sub(r'%.*?\n', '\n', content)
    citations = re.findall(r'\\cite(?:[a-zA-Z]*)\s*\{([^}]+)\}', content)
    for cit in citations:
        for k in cit.split(','):
            diss_keys.add(k.strip())

print(f"\nTotal unique keys cited in dissertation: {len(diss_keys)}")

# Read keys from thesisz.bib
with open('thesisz.bib', 'r', encoding='utf-8') as f:
    bib_content = f.read()

bib_keys = set()
matches = re.finditer(r'@(\w+)\s*\{\s*([^,\s]+)', bib_content)
for m in matches:
    bib_keys.add(m.group(2).strip())

missing = []
case_mismatches = []
for k in sorted(diss_keys):
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

print(f"Total keys in thesisz.bib: {len(bib_keys)}")
print(f"Case mismatches in dissertation: {len(case_mismatches)}")
for cited, in_bib in case_mismatches:
    print(f"  - Cited as: '{cited}', in Bib: '{in_bib}'")
print(f"Keys cited in dissertation but missing in thesisz.bib: {len(missing)}")
print(missing)
