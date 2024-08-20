def recursiveApproach(arr, index, subsets) :
    if index >= len(arr):
        return []
    temp = list()
    for i in subsets :
        newSet = i*1
        newSet.append(arr[index])
        temp.append(newSet)
    subsets += temp
    recursiveApproach(arr, index+1, subsets)


def findAllSubSets(arr) :
    ans = [[]]
    for i in range(len(arr)):
        subsets = list()
        for subset in ans:
            tempSubset = subset*1
            tempSubset.append(arr[i])
            subsets.append(tempSubset)
        ans += subsets
    print(ans)
            
def findAllSubSetsRecursive(arr) :
    subsets = [[]]
    recursiveApproach(arr, 0, subsets)
    return subsets


def findAllSubSetsBitMask(arr) :
    masks = list()
    for i in range(2**len(arr)):
        binary = bin(i).lstrip("0b")
        if len(binary) != len(arr) :
            binary = "0"*(len(arr)-len(binary)) + binary
        masks.append(binary)
        
    print(masks)
    subsets = list()
    for mask in masks:
        set = []
        for index in range(len(mask)):
            if mask[index] == "1":
                set.append(arr[index])

        subsets.append(set)
            
    return subsets


if __name__ == "__main__" :
    inputArr = list(map(int, input().split()))
    findAllSubSets(inputArr)
    outputArrUsingRecursion = findAllSubSetsRecursive(inputArr)
    outputArrUsingBitMask = findAllSubSetsBitMask(inputArr)
    print(outputArrUsingRecursion, len(outputArrUsingRecursion))
    print(outputArrUsingBitMask)
