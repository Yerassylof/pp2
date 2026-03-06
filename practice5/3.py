import re

text = input()
text2 = input()  
num =  re.findall(text2, text)
sum = len(num)
print(sum)

