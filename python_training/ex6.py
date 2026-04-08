# Function takes an Array as an argument find out if there is
# any number in the Array which is greater than sum of other elements.

# function for length of array
def lenfn(arr):
    c=0
    for i in arr:
        c+=1
    return c

# function for calculating sum
def sumfn(arr):
    total=0
    for i in arr:
        total+=i
    return total

# take array arguments as input
def ex6(arr):
    for i in range(lenfn(arr)):
        if (arr[i]>sumfn(arr[0:i]+arr[i+1:])):
            return arr[i]
    return

# Run the function for given input
print(ex6([10,20,30,45,90,200,2000,10001]))

print(ex6([10,20,30,40,90,200,20]))