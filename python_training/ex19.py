# Write a function that takes **kwargs as an input and finds out the final values. 
#   - Use decorators to execute the code (Optional)
#   - Handle all Exceptions

# function for maximum of two number
def max_fn(arr):
    temp=float('-inf')
    for i in arr:
        if i>temp:
            temp=i
    return temp

# function for minimum of two number
def min_fn(arr):
    temp=float('inf')
    for i in arr:
        if i<temp:
            temp=i
    return temp

# function for calculating sum
def sum_fn(arr):
    total=0
    for i in arr:
        total+=i
    return total

# function for length of array
def len_fn(arr):
    c=0
    for i in arr:
        c+=1
    return c

# function for calculating avg
def avg_fn(arr):
    total=sum_fn(arr)
    count=len_fn(arr)
    return str(total)+'/'+str(count)

# decorator for showing action to be performed
def decorator_fn(fn):
    def inner( **kwargs):
        print("Output:",kwargs['action'])
        return fn(**kwargs)
    return inner

@decorator_fn
def ex19(**kwargs):
    temp=[value for key, value in kwargs.items() ]
    action=temp.pop()
    if action=='sum':
        return sum_fn(temp)
    elif action =='avg':
        return avg_fn(temp)
    elif action =='max':
        return max_fn(temp)
    elif action =='min':
        return min_fn(temp)
    
    
# Run the function for given input

print(ex19(x=100,y=200,z=150,a=300,b=180,e=90,f=25,g=80,h=120,action="avg"))

print(ex19(x=100,y=200,z=150,a=300,b=180,e=90,f=25,g=80,h=120,action="sum"))

print(ex19(x=100,y=200,z=150,a=300,b=180,e=90,f=25,g=80,h=120,action="max"))

print(ex19(x=100,y=200,z=150,a=300,b=180,e=90,f=25,g=80,h=120,action="min"))