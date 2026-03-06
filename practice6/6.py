n = int(input())
numbers = list(map(int, input().split()))

print("Yes" if all(x >= 0 for x in numbers) else "No")