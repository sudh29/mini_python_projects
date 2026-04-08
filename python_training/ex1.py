# Your function will take an array as input and an integer X, 
# you need to find out and return the number that leaves the greatest
# and least reminders when divided by X. Reminders must be >0 .

# function for maximum of two number
def maxfn(a,b):
    if a>b:
        return a
    else:
        return b

# function for minimum of two number
def minfn(a,b):
    if a<b:
        return a
    else:
        return b

# take x and an array as input
def exp1(X,arr):
    # initial minimum remainder as maximum remainder
    min_rem=float('inf')
    # initial maximum remainder
    max_rem=arr[0]%X
    for i in arr:
        # check min & max rem. for each value
        max_rem=maxfn(max_rem,i%X)
        if i%X>0:
            min_rem=minfn(i%X,min_rem)
    # return max remainder and min remainder
    return max_rem,min_rem


# Run the function for given input
x=10
array=[10,20,30,40,50,44,55,60]

print(exp1(x,array))