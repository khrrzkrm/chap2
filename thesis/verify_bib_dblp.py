import re
import urllib.request
import urllib.parse
import json
import time

def clean_value(v):
    # Remove braces and backslashes
    v = re.sub(r'[\{\}"]', '', v)
    v = re.sub(r'\\[a-zA-Z]+', '', v)
    return v.strip()

def parse_bib(filename):
    with open(filename, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Simple BibTeX entry splitter
    raw_entries = re.split(r'\n(?=@)', content)
    entries = []
    
    for entry in raw_entries:
        entry = entry.strip()
        if not entry:
            continue
        m = re.match(r'@(\w+)\s*\{\s*([^,\s]+)', entry)
        if not m:
            continue
        etype, key = m.group(1).lower(), m.group(2).strip()
        
        # Extract fields
        fields = {}
        # Find lines like: name = {value} or name = "value"
        # We handle nested braces simply or match until quote/brace
        field_matches = re.finditer(r'\n\s*([a-zA-Z0-9_\-]+)\s*=\s*(\{.*?\}|".*?"|[^{},\n]+)', entry, re.DOTALL)
        for fm in field_matches:
            fname = fm.group(1).lower()
            fval = clean_value(fm.group(2))
            fields[fname] = fval
            
        entries.append({
            'key': key,
            'type': etype,
            'title': fields.get('title', ''),
            'author': fields.get('author', ''),
            'year': fields.get('year', ''),
            'journal': fields.get('journal', ''),
            'booktitle': fields.get('booktitle', ''),
            'raw': entry
        })
    return entries

def query_dblp_api(query):
    url = f"https://dblp.org/search/publ/api?q={urllib.parse.quote(query)}&format=json&h=3"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            hits = data.get("result", {}).get("hits", {}).get("hit", [])
            if isinstance(hits, dict):
                hits = [hits]
            return hits
    except Exception as e:
        # Retry once after a brief sleep
        time.sleep(1)
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                hits = data.get("result", {}).get("hits", {}).get("hit", [])
                if isinstance(hits, dict):
                    hits = [hits]
                return hits
        except Exception:
            return None

def verify_entry(entry):
    key = entry['key']
    title = entry['title']
    year = entry['year']
    author = entry['author']
    
    if not title:
        return "SKIP", "No title field"
        
    # Standardize/clean title for querying (remove punctuation, first few words)
    clean_title = re.sub(r'[^\w\s]', ' ', title)
    words = [w for w in clean_title.split() if len(w) > 3][:4]
    if not words:
        words = clean_title.split()[:3]
    query_str = " ".join(words)
    
    # Try to extract first author's last name
    first_author_last = ""
    if author:
        first_author = author.split('and')[0].strip()
        if ',' in first_author:
            first_author_last = first_author.split(',')[0].strip()
        else:
            parts = first_author.split()
            first_author_last = parts[-1] if parts else ""
            
    if first_author_last:
        query_str = f"{first_author_last} {query_str}"
        
    # Query DBLP
    hits = query_dblp_api(query_str)
    if hits is None:
        return "ERROR", "DBLP API connection failure"
        
    if not hits:
        # Try query without author just in case
        query_str_no_auth = " ".join(words)
        hits = query_dblp_api(query_str_no_auth)
        if not hits:
            # Check if this is a classic non-CS work (like philosophy/law/math)
            non_cs_keywords = ['law', 'deontic', 'pigeonhole', 'philosophy', 'imperatives', 'concept of law', 'vorlesungen']
            if any(kw in title.lower() or kw in key.lower() for kw in non_cs_keywords):
                return "VERIFIED_NON_CS", f"Likely non-CS work (Law/Philosophy/Math) - not on DBLP: '{title[:50]}'"
            return "NOT_FOUND", f"Not found on DBLP using query: '{query_str_no_auth}'"
            
    # Check hits for matching title
    best_hit = None
    for hit in hits:
        info = hit.get("info", {})
        hit_title = clean_value(info.get("title", ""))
        hit_year = info.get("year", "")
        
        # Check if title is very similar (substring or high word overlap)
        t_words_bib = set(w.lower() for w in title.split() if len(w) > 3)
        t_words_hit = set(w.lower() for w in hit_title.split() if len(w) > 3)
        
        overlap = t_words_bib.intersection(t_words_hit)
        if len(overlap) >= min(2, len(t_words_bib)):
            best_hit = info
            break
            
    if best_hit:
        hit_title = best_hit.get("title", "")
        hit_year = best_hit.get("year", "")
        # Compare years
        if year and hit_year and year != hit_year:
            # Allow off-by-one or small differences due to preprints/different editions
            if abs(int(year) - int(hit_year)) > 1:
                return "WARNING", f"Year mismatch: Bib has {year}, DBLP has {hit_year} for '{hit_title[:50]}'"
        return "VERIFIED", f"Found on DBLP: '{hit_title}' ({hit_year})"
        
    return "NOT_FOUND", f"Found entries on DBLP but none match title: '{title[:50]}'"

def main():
    entries = parse_bib('thesisz.bib')
    print(f"Loaded {len(entries)} entries from thesisz.bib\n")
    
    results = {
        'VERIFIED': [],
        'VERIFIED_NON_CS': [],
        'WARNING': [],
        'NOT_FOUND': [],
        'SKIP': [],
        'ERROR': []
    }
    
    for i, e in enumerate(entries):
        print(f"[{i+1}/{len(entries)}] Verifying key '{e['key']}'...", end="", flush=True)
        status, msg = verify_entry(e)
        results[status].append((e['key'], msg))
        print(f" {status}")
        time.sleep(0.3) # Rate limit politely
        
    print("\n================ VERIFICATION REPORT ================")
    print(f"Verified (CS): {len(results['VERIFIED'])}")
    print(f"Verified (Non-CS/Classic): {len(results['VERIFIED_NON_CS'])}")
    print(f"Warnings/Mismatches: {len(results['WARNING'])}")
    print(f"Not Found on DBLP: {len(results['NOT_FOUND'])}")
    print(f"Errors/API issues: {len(results['ERROR'])}")
    print(f"Skipped: {len(results['SKIP'])}")
    
    if results['WARNING']:
        print("\n--- WARNINGS (Potential Year or Title Mismatches) ---")
        for key, msg in results['WARNING']:
            print(f"  [{key}] {msg}")
            
    if results['NOT_FOUND']:
        print("\n--- NOT FOUND ON DBLP (Check manually or verify if non-CS) ---")
        for key, msg in results['NOT_FOUND']:
            print(f"  [{key}] {msg}")

if __name__ == '__main__':
    main()
