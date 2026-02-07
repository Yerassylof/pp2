n = int(input())
arr = list(map(int, input().split()))

mx_ct = 0
ans = arr[0]

for i in range(n):
    count = 0
    for j in range(n):
        if arr[j] == arr[i]:
            count += 1
    if count > mx_ct:
        mx_ct = count
        ans = arr[i]

print(ans)
