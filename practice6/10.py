n = int(input())
numbers = list(map(int, input().split()))

count = sum(map(bool, numbers))

print(count)