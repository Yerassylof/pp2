import re

text = input()

if re.match(r"Hello", text):
    print("Yes")
else:
    print("No")