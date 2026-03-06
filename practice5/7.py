import re

text = input()
pattern = input()
replacement = input()

result = re.sub(pattern, replacement, text)

print(result)