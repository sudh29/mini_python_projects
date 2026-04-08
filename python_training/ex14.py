# Write a Program to update dictionary Values using dict comprehensions. 
#     Your function will take 3 inputs, A dict, an Integet X and Interget Y.
#     Find keys whose values are >er than Integer X and multiply them by Integer Y.


def ex14(dict_arr, x,y):
    # v greater than x and multiple by y
    new_dic={k:v*y  for k,v in dict_arr.items() if v>x}
    return new_dic

# Run the function for given input
print(ex14({1:3,2:20,3:4,5:60,10:90},x=50,y=10))