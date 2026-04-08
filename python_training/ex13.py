# Using Dict Comprehension find the Occurences of Numbers. 
# Your function will take an Integer X followed by any number of Arrays. 
# You need to parse each array and find out elements in the Array that
# is divisible by X and return the count of numbers thats divisible by X
# with its position.

# function to count frquency of elements divisible by X in arr 
def countfreq(arr,x):
    c=0
    for i in arr:
        if i%x==0:
            c+=1
    return c

def ex13(x, *args):
    # using enumerate to generate key,value pair
    marr=(list(enumerate(args)))
    res={i[0]:countfreq(i[1],x) for i in marr} 
    return res

# Run the function for given input
print(ex13(5, [1,20,35,45,90],[100,20,30,45,60,75,90],[2,3,30,19,90,25,80],[5,6,9,10,15,25,30]))