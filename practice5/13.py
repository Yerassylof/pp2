import re

text = input()

words = re.findall(r"\w+", text)

print(len(words))