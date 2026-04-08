# Write python code to find the count of occurrence of vowels.

from collections import defaultdict

# function to count frquency of vowels elements in arr 
def countfreq(arr):
    vowels=['a','e','i','o','u']
    temp=defaultdict(int)
    for i in arr:
        if i in vowels:
            temp[i]+=1
    return temp

def ex18(str1):
    res= countfreq(str1)
    return res

# Run the function for given input

print(ex18("hello world"))

print(ex18("lets get started with python"))