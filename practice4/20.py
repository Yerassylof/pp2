g = 0
def outer(commands):
     n = 0
     def inner():
         nonlocal n
         global g
         for cmd in commands:
             scope, vale = cmd
             val = int(vale)
             if scope == "global":
                 g += val
             elif scope == "nonlocal":
                 n += val
             elif scope == "local":
                 x = val
         return n
     n = inner()
     return n

n_final = outer([input().split() for _ in range(int(input()))])
print(g, n_final)
