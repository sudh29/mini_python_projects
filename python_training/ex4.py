# Function takes any n.o. lists as Arguments(*args), an integer X . 
# Find the list that has most numbers divisible by X.

# function for length of array
def lenfn(arr):
    c=0
    for i in arr:
        c+=1
    return c


# function for maximum in array
def maxfn(arr):
    res=float('-inf')
    for i in arr:
        if i >res:
            res=i
    return res

# function for divisible element count
def div_fn(n,arr):
    if n==0:
        print("Not Divisible by zero")
        return
    else:
        c=0
        for i in arr:
            if i%n==0:
                c+=1
        return c

# take x and multiple arguments as input
def ex4(x,*args):
    # enumerate the multiple arguments
    marr= list(enumerate(args))
    # count divisible by x and save in list
    temp=[div_fn(x,v) for k,v in marr]
    # find the index of max count
    index=[i for i in range(lenfn(temp)) if temp[i]>= maxfn(temp)]
    # if one array
    if lenfn(index)==1:
        return marr[index[0]][1]
    # if more than one array
    
    return [ v for i in index for v in marr[i][1] if v%x==0]


# Run the function for given input
print(ex4(3,[1,2,3,4,5],[1,3,4,6,9],[10,12,9,7,8],[12,7,9,8,14]))

print(ex4(3,[1,2,3,4,5],[1,3,4,6,9],[3,9,10,11,18],[10,12,9,7,8],[12,7,9,8,14]))