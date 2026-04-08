# Function takes 2 Arrays, an integer X as Arguments.
# Find out pairs of numbers from both lists divisible by X.
# When Collecting Pairs the element in the first list index(n)
# and the element in the second list index(n) must both be 
# divisible by X, Only then it forms a pair.

# Function to return only the pair that has max value
def max_fn(arr):
    maxval=float('-inf')
    for i in range(len(arr)):
        if arr[i][0]>maxval:
            maxval=arr[i][0]
            index=i
        if arr[i][1]>maxval:
            maxval=arr[i][1]
            index=i
    return arr[index]

# Function takes 2 Arrays, an integer X as Arguments.
def ex7(x,arr1,arr2):
    # pairs of numbers from both lists divisible by X at index n.
    res=[(arr1[i],arr2[i])  for i in range(len(arr1)) if arr1[i]%x==0 and arr2[i]%x==0]
    # print(res)
    return max_fn(res)


# Run the function for given input
print(ex7(10,[10,20,30,40,50],[12,24,40,90,200]))