
# From the given array that has any number of sub-lists, dict,
# nested dicts find out all the positive integers and store 
# them in an array. In case of dicts take both keys & values 
# positive integers. From the final array create an occurrence dictionary to 
# figure out the occurrence of each number. Dont use any built-ins.
# Please remember the input array can have any levels of nested lists,
# sub-lists and nested dictionaries

from collections import defaultdict

# function to count frquency of elements in arr 
def countfreq(arr):
    temp=defaultdict(int)
    for i in arr:
        temp[i]+=1
    return temp

# for nested dictionary 
def dic_list(arr):
    for k,v in arr.items():
        # check key
        if type(k) is int and k>0:
            yield k
        # check value for int list and dict
        if type(v) is int and v>0:
            yield v
        elif type(v) is list:
            for j in list(list_list(v)):
                yield j
        elif type(v) is dict:
            for k in list(dic_list(v)):
                yield k

# for int and list
def list_list(arr):
    for i in arr:
        # int
        if type(i) is int and i>0:
            yield i
        # list
        elif type(i) is list:
            for j in list(list_list(i)):
                yield j
        # dict
        elif type(i) is dict:
            for k in list(dic_list(i)):
                yield k 

def ex10(arr):
    # count the freq of elements
    res=countfreq(list(list_list(arr)))
    return res


# Run the function for given input
input=[1,2,3,4,5, [True,False,-110.100,-200,500, [1,2,3,4,5]], {0:1,1:2,3:4,5:[10,True,-1100,200,300]}]
print(ex10(input))
