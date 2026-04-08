from collections import defaultdict

# Function takes any n.o. lists as Arguments (*args), an integer X .
# Find all the elements in the lists that has numbers divisible by X.
# Create a final dictionary and return. The final dictionary must contain
# the count of occurrences of each element in the lists that are divisible by X.

# function to count frquency of elements in arr 
def countfreq(arr):
    temp=defaultdict(int)
    for i in arr:
        temp[i]+=1
    return temp

# take x and multiple arguments as input
def ex5(x,*args):
    # filter elements are divisible by X
    res=[i for arg in args for i in arg if i%x==0]
    # count the occurrences of each element 
    res_dic=countfreq(res)
    return res_dic


# Run the function for given input
print(ex5( 5,[10,12,14,40,60,65,80,90],[3,4,65,40,40,30,20],[120,400,80,90,20,60] ))

