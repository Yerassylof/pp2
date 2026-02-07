a = int(input())
n = input().split()

mx = int(n[0])

for i in n:
    if mx < int(i):
        mx = int(i)

print(mx)
