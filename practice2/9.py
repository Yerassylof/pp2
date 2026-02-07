n = int(input())
arr = list(map(int, input().split()))

mn = min(arr)
mx = max(arr)

for i in range(n):
    if arr[i] == mx:
        arr[i] = mn

print(*arr)       
     


