# Function to find the patterns across arrays. Your function will receive any no.
# arrays and another argument pattern. You must return a list of all elements in 
# all arrays that doesn't contain the pattern, avoid duplicates and its not case-sensitive.

# function to removeduplicate
def removeduplicate(arr):
    temp=[]
    for i in arr:
        if i.lower() not in temp and i.upper() not in temp:
            temp.append(i)
    return temp

# Function takes multiple Arrays, another argument pattern.
def ex8(x,*args):
    # filter all elements in all arrays that doesn't contain the pattern
    res =[i for arg in args for i in arg if x not in i]
    # removeduplicate 
    return removeduplicate(res)


# Run the function for given input
print(ex8("code", ["hello","world","code","python"] ,["code","coding","coder","code lead"],["Python","Data","AI","C"]))

print(ex8("Arun", ["hello","world","code","python"] ,["code","coding","coder","code lead"],["Python","Data","AI","C"]))