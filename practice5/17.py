import re

text = input()

dates = re.findall(r"\b\d{2}/\d{2}/\d{4}\b", text)

print(len(dates))