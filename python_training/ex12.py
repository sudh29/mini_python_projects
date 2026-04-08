# Using List comprehension flatten a List. Your Function will take
# 2 Lists namely ListA and List B. You need to pick elements from
# ListA which are divisible by any element in ListB. Note ListB must
# contain atleast 2 elements else dont process. Return the final list.


# take two lists as input
def ex12(listA, listB):
    res=[]
    for i in listA:
        temp=0
        for j in listB:
            if i%j==0:  
                temp+=1
        if temp>=2:
            res.append(i)
    return res

# Run the function for given input
print(ex12([10,30,35,40,45,28,39,50,61,78],[2,5,7,10,20,50]))