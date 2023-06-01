def insertionSortAsc(l1: list) :
##    l1 is the input list(array)
    n = len(l1)
    for i in range(1, n):
        for j in range(i):
            if l1[j] > l1[i]:
                x = l1[i]
                del l1[i]
                l1.insert(j, x)
                break
    print(l1)

def insertionSortDesc(l1: list) :
    n = len(l1)
    for i in range(1, n):
        for j in range(i) :
            if l1[j] < l1[i]:
                x = l1[i]
                del l1[i]
                l1.insert(j, x)
                break
    print(l1)
if __name__ == "__main__":
    l1 = list(map(int, input().split(" ")))
    insertionSortAsc(l1)
    insertionSortDesc(l1)
