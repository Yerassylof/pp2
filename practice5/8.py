import re

text = input()
pattern = input()

parts = re.split(pattern, text)

print(",".join(parts))