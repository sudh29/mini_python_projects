from collections import defaultdict

# Your function will take multiple arrays as inputs
# For each element in each array:
# Find out how many times that element occurs in each array, store it in a dictionary.
# Sort the final dictionary based on keys and return.

# dictionary sorting function based on keys
def sortdic(temp):
    temp2 = {}
    for j in sorted(temp):
        temp2[j] = temp[j]
    return temp2

# function to count frquency of elements in arr 
def countfreq(arr):
    temp=defaultdict(int)
    for i in arr:
        temp[i]+=1
    return temp

# take multiple arguments as input
def exp3(*args):
    res={} # initailize empty dic
    # using enumerate to generate key,value pair
    marr=(list(enumerate(args))) 
    # using dictionary compression 
    res={key:sortdic(countfreq(val)) for key,val in marr}
    return res

# Run the function for given input

print(exp3([12,12,55,79,79,12],[12,33,60,60,79],[199,55,199]))