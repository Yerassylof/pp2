a = int(input())

if a == 1:
    print(0)
else:
    for i in range(0, a + 1):
        if i % 2 == 0:
            if i != 0:
                print(",", end="")
            print(i, end="")