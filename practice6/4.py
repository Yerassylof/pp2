n = int(input())
a = list(map(int, input().split()))
b = list(map(int, input().split()))

dot_product = sum(x * y for x, y in zip(a, b))

print(dot_product)