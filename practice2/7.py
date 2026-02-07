a = int(input())
n = input().split()

mx = int(n[0])
index = 0
pos = 0

for i in n:
    if mx < int(i):
        mx = int(i)
        index = pos
    pos += 1

print(index + 1)
