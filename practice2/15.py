n = int(input())
arr = []

for i in range(n):
    x = str(input())
    arr.append(x)

arr = list(set(arr))

print(len(arr))
