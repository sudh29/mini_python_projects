# Function to find out ways to form a string from another string.
# Function will take 2 strings as inputs. You must find out all 
# possible ways by which you can form string A from String B. You 
# must validate to ensure that the strings are Alpha-numeric only, 
# it must contain only strings and numbers. No other types are 
# allowed. The length of String B must be >er than String A.
# Char once used from String B must not be used again.
# Return the final Output in dictionary format with indexes and values.
# Indexes represent the index value in String B that has occurrence of 
# a char from String A. Function to find out ways to form a string from 
# another string. Function will take 2 strings as inputs.


# function for length of array
def lenfn(arr):
    c=0
    for i in arr:
        c+=1
    return c

# find min char and slice others
def index_mins(index):
    mintemp=float('inf')
    for i in index:
        mintemp=min(mintemp,len(i))
    temp=[]
    for i in index:
        temp.append(i[0:mintemp])
    return temp


# dictionary sorting function based on keys
def sortdic(temp):
    temp2 = {}
    for j in sorted(temp):
        temp2[j] = temp[j]
    return temp2


# take two string as input
def ex11(list_str1,list_str2):
    index=[]
    for i in list_str1:
        temp=[idx for idx, val in enumerate(list_str2) if val==i]
        index.append(temp)
    sliced_idx=index_mins(index)
    op=[]
    res={}
    for i in range(lenfn(sliced_idx[0])):
        for j in range(lenfn(sliced_idx)):
            res[sliced_idx[j][i]]=list_str1[j]
        op.append(sortdic(res))
        res={}
    return op


# Run the function for given input
print(ex11("abc", "agcb xyzbc amnopq copnotab cosxab"))

print(ex11("ab", "agcb xyzbc amnopq copnotab coscabbb"))