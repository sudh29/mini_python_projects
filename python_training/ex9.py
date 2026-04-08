# Write python function to find the powers of numbers.
# Each item in the Array must take the next element in 
# the array as it pow and return. If any number is 
# left-behind without next number, then it shall take the
# min number in the array as its pow. The max pow that can
# be taken is 5. If there is any item in the Array whose
# next number in the array is > 5, then pow will not apply
# and its value remains the same.


# function takes array as input and find the pow
def ex9(arr):
    # array for values
    val=[arr[i] for i in range(0,len(arr),2)]
    # array for power and remove greater the 5
    power=[arr[i] if arr[i]<=5 else 1 for i in range(1,len(arr),2) ]
    # left without power added min power 
    if len(power)<len(val):
        power.append(min(power))
    # value to the power array
    temp=[val[i]**power[i] for i in range(len(val))]
    return temp




# Run the function for given input
print(ex9([2,3,7,1,5,3,16,2]))

print(ex9([10,3,50,2,20,3,8,2,100]))

print(ex9([10,6,50,2,20,3,8,2,100]))