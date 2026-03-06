import re

text = input()
pattern = input()

count = len(re.findall(re.escape(pattern), text))

print(count)