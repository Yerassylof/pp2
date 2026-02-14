def isUsual(num):
    for i in (2, 3, 5):
        while num % i == 0:
            num //= i

    return num == 1


n = int(input())

if isUsual(n):
    print("Yes")
else:
    print("No")
