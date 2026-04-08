# Program to flatten a list using recursions. Input list can contain any levels of sub-lists

def ex15(arr):
    # empty than return
    if not arr:
        return arr
    # check if list than call function again
    if type(arr[0]) is list:
        return ex15(*arr[:1]) + ex15(arr[1:])
    return arr[:1] + ex15(arr[1:])

# Run the function for given input
ip=[1,2,3,4,5, [10,20,30,4,50,60,100],90,200,[300,10]]
print(ex15(ip))