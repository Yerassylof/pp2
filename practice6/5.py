s = input()
vowels = "aeiouAEIOU"

print("Yes" if any(c in vowels for c in s) else "No")