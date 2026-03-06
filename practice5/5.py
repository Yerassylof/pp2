import re

text = input()

if re.match(r"^[A-Za-z].*[0-9]$", text):
    print("Yes")
else:
    print("No")