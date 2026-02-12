
import re

def strip_markdown(text):
    # Remove headers (e.g. # Header)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic (e.g. **bold**, *italic*)
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)
    # Remove images (e.g. ![alt](url)) - remove entirely or keep alt? Keeping alt is usually better for summaries.
    text = re.sub(r'!\[(.*?)\]\(.*?\)', r'\1', text)
    # Remove links (e.g. [text](url))
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Remove code blocks (e.g. ```code```)
    text = re.sub(r'`{3}.*?`{3}', '', text, flags=re.DOTALL)
    # Remove inline code (e.g. `code`)
    text = re.sub(r'`(.*?)`', r'\1', text)
    # Remove blockquotes (e.g. > quote)
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    return text.strip()

content = """
### Sick Leave...
Here is some **bold** text and a [link](http://google.com).

> A quote
"""

print(f"Original: {content!r}")
stripped = strip_markdown(content)
print(f"Stripped: {stripped!r}")
