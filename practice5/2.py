import re

text = input()
text2 = input()  

if re.search(text2, text):
    print("Yes")
else:
    print("No")