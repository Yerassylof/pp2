import re

text = input()

result = re.search(r"\S+@\S+\.\S+", text)

if result:
    print(result.group())
else:
    print("No email")