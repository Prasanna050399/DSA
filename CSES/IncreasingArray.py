def cses():
    n = int(input())
    nums = list(map(int, input().split()))

    total = 0
    prev = nums[0]
    for i in nums[1:]:
        if prev > i:
            total += (prev - i)
        else :
            prev = i
    print(total)
if __name__ == "__main__":
    cses()
