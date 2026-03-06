import re

text = input()

uppercase_letters = re.findall(r"[A-Z]", text)

print(len(uppercase_letters))