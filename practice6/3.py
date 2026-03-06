n = int(input())
words = input().split()

output = " ".join(f"{i}:{word}" for i, word in enumerate(words))
print(output)