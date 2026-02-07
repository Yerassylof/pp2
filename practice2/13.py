a = int(input())
s = 0

for i in range(1, a+1):
    if a % i == 0:
        s += 1
    else: continue

if s == 2:
    print("Yes")
else:
    print("No")