def cses():
    n = int(input())
    if n == 1:
        print(1)
    if n == 2:
        print("NO SOLUTION")
    if n == 3:
        print("NO SOLUTION")
    if n > 3 :
        for i in range(1, n+1):
            if i%2 == 0:
                print(i, end = " ")
        for i in range(1, n+1):
            if i%2 != 0:
                print(i, end = " ")

        
    

if __name__ == "__main__":
    cses()
