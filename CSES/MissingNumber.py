def ans():
    n = int(input())
    l = map(int, input().split())
    lTotal = 0
    for i in l:
        lTotal += i
    print(n*(n+1)//2 - lTotal)

if __name__ == "__main__":
    ans()
