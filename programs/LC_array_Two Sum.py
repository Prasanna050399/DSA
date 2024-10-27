'''
Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.

 

Example 1:

Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
Example 2:

Input: nums = [3,2,4], target = 6
Output: [1,2]
Example 3:

Input: nums = [3,3], target = 6
Output: [0,1]
'''

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        d1 = dict()
        for i in range(len(nums)):
            if nums[i] not in d1:
                d1[nums[i]] = list()
            d1[nums[i]].append(i)
        
        for i in nums:
            if target-i == i:
                if len(d1[i]) > 1:
                    return [d1[i][0], d1[i][1]]
            else :
                if target-i in d1:
                    return [d1[i][0], d1[target-i][0]]

'''
Solution :
    create a dictionary/hashmap for all the numbers
    the key will be the number and the value will be the list of indices at which the number is present in the array
    now iterate on the input array and check if the target-number is equal to the number itself, i.e the number is half the target number if yes
    check if the value in the dictionary for this number has more than one indices, i.e if the number occurs more than once if yes return the index of two occurances
    if the input is not equal to target-num
    then check if the target-num exist in dict if yes return the first index of num and target-num from the value arrays.
'''
