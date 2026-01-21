import re

# Read the file
with open('utils/viz_helpers.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace curly quotes with straight quotes
content = content.replace(''', "'")
content = content.replace(''', "'")
content = content.replace('"', '"')
content = content.replace('"', '"')

# Write back
with open('utils/viz_helpers.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed curly quotes in viz_helpers.py")
