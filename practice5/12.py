import re

text = input()

numbers = re.findall(r"\d{2,}", text)

print(" ".join(numbers))