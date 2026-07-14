import re
import sys

def parse_latex_log(log_path):
    with open(log_path, 'r', encoding='latin-1') as f:
        content = f.read()
    
    lines = content.splitlines()
    
    file_stack = []
    current_file = "Unknown"
    
    overfull_boxes = []
    
    # We will use a regex to find all tokens like `(path/to/file.tex` or `)` or `Overfull \hbox...`
    # However, parsing line by line is easier.
    for i, line in enumerate(lines):
        # Very naive file tracking
        # Look for ( followed by something ending in .tex
        starts = re.findall(r'\(([^)]*\.tex)', line)
        for s in starts:
            file_stack.append(s)
            
        ends = line.count(')')
        # This is too naive as ) could be part of text.
        
        # A more reliable way is to just find the Overfull line and then get the text of the line from the next line,
        # then search for that text in all .tex files.
        if "Overfull \\hbox" in line:
            match = re.search(r'lines? (\d+)', line)
            line_no = match.group(1) if match else "?"
            
            # Get the next line as context
            context = ""
            if i + 1 < len(lines):
                context = lines[i+1].strip()
                # Clean up latex font info like \T1/ptm/m/n/12
                context = re.sub(r'\\[a-zA-Z0-9/]+ ', '', context)
                context = re.sub(r'\[\]', '', context)
                context = context.strip()
                
            overfull_boxes.append((line, line_no, context))
            
    return overfull_boxes

boxes = parse_latex_log("thesis.log")
import subprocess

for box_line, line_no, context in boxes:
    # Print the warning
    print(f"Warning: {box_line}")
    # Search for context if we have it
    if context and len(context) > 10:
        # We need to escape for grep
        # Just use first 30 chars of context that are words
        words = [w for w in re.split(r'[^a-zA-Z0-9]+', context) if len(w) > 3]
        if len(words) >= 3:
            search_str = " ".join(words[:4])
            try:
                res = subprocess.check_output(['grep', '-rl', search_str, '.']).decode('utf-8').strip()
                files = [f for f in res.splitlines() if f.endswith('.tex') and 'parse_log' not in f]
                if files:
                    print(f"  -> Found in: {', '.join(files)} (approx line {line_no})")
                else:
                    print(f"  -> Context: {context}")
            except subprocess.CalledProcessError:
                print(f"  -> Context: {context}")
        else:
            print(f"  -> Context: {context}")
            
