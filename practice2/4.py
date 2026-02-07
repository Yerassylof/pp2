a = int(input())
n = input().split()

sum = 0

for i in n:
    if int(i) > 0:
        sum += 1
print(sum)