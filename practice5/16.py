import re

text = input()

match = re.search(r"Name: (.*), Age: (.*)", text)

if match:
    print(match.group(1), match.group(2))