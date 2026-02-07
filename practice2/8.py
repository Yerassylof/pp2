n = int(input())
degree = 2
a = []

for i in range(0, n):
    if n >= pow(degree, i):
        a.append(pow(degree, i))
    else : break

print(*a)