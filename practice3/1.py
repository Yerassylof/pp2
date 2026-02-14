n = str(input())
a, b = 0, 0

for i in n:
    if int(i) % 2 == 0:
        a+=1
    else :
        b+=1
if a != 0 and b == 0:
    print("Valid")
else :
    print("Not valid")
