n = int(input())
num = list(map(int, input().split()))
sq = map(lambda x : x**2, num)
print(sum(sq))