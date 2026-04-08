# Sort the array according to the occurrence of numbers

from collections import defaultdict

# function to count frquency of elements in arr 
def countfreq(arr):
    temp=defaultdict(int)
    for i in arr:
        temp[i]+=1
    return temp


def ex16(arr):
    # frequency count of elements
    freq=countfreq(arr)
    # sorting dict in reverse
    res= {k: v for k, v in sorted(freq.items(), key=lambda item: item[1], reverse=True)}
    # key array
    output=[i for i in res]
    return output

# Run the function for given input
array = [1, 1, 1, 2, 3, 4, 9, 0, 2, 2, 3, 4, 3, 2, 1, 5, 5, 9, 0, 0, 1, 1, 1, 1, 2,
        5, 6, 7, 7, 8, 9, 0, 0, 4, 4, 4, 6, 6, 6, 6, 6, 7, 7, 7,8,8,8,8,8,8]
print(ex16(array))