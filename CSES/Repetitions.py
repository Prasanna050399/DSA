def cses() :
    s = input()
    count = 1
    prev = s[0]
    maxi = 1
    for i in s[1:]:
        if i == prev:
            count += 1
            if count > maxi :
                maxi = count
        else :
            count = 1
            prev = i

    print(maxi)


if __name__ == "__main__":
    cses()
