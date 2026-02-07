a = int(input())
s = 0

for i in range(0, 20):
    if a == pow(2, i):
        print("YES")
        s = 1
        break

if s == 0:
    print("NO")
