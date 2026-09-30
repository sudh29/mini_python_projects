"""Exercise 3: Element frequency per array with sorted keys."""

from collections import defaultdict


# dictionary sorting function based on keys
def sortdic(temp):
    temp2 = {}
    for j in sorted(temp):
        temp2[j] = temp[j]
    return temp2


# function to count frequency of elements in arr
def countfreq(arr):
    temp = defaultdict(int)
    for i in arr:
        temp[i] += 1
    return temp


# take multiple arguments as input
def exp3(*args):
    # using enumerate to generate key,value pair
    marr = list(enumerate(args))
    # using dictionary comprehension
    res = {key: sortdic(countfreq(val)) for key, val in marr}
    return res


ex3 = exp3

# Run the function for given input
if __name__ == "__main__":
    print(exp3([12, 12, 55, 79, 79, 12], [12, 33, 60, 60, 79], [199, 55, 199]))
