import re

with open('/Users/krm/Desktop/gits/chap2/thesis/einleitung.tex', 'r') as f:
    content = f.read()

# Add citation for Rice theorem
content = content.replace(
    "what can and cannot be correctly verified as a consequence of the Rice theorem.",
    "what can and cannot be correctly verified as a consequence of Rice's theorem \\cite{rice1953classes}."
)
content = content.replace(
    "what can and cannot be correctly verified as a consequence of the Rice theorem",
    "what can and cannot be correctly verified as a consequence of Rice's theorem \\cite{rice1953classes}"
)

# Remove unnecessary spacing (collapse 3 or more newlines into exactly 2 newlines)
content = re.sub(r'\n{3,}', '\n\n', content)

with open('/Users/krm/Desktop/gits/chap2/thesis/einleitung.tex', 'w') as f:
    f.write(content)

