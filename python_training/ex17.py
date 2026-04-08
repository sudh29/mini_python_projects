# Write python code to jumble 2 strings without using any built-ins.
#    Take chars from alternate indexes and shift.
#    Before running you must ensure both strings are of same length.

def  ex17(str1,str2):
    if len(str1)!=len(str2):
        print("Length not same")
        return
    else:
        res=""
        for i in range(len(str1)):
            res+=str1[i]
            res+=str2[i]
        return res

# Run the function for given input
print(ex17("hello","world"))

print(ex17("Python","JavaCP"))

print(ex17("sam","tom"))