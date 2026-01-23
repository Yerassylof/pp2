a = str(input())
if len(a) == 1 :
    print(a + " " + a)
else :
    for i in range(len(a)):
        s = a[0]
        d = a[-1] 
        
        print(s + " " + d) 
        break  
