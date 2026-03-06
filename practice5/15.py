import re

text = input()

def double_digit(match):
    return match.group() * 2

result = re.sub(r"\d", double_digit, text)

print(result)