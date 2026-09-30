"""Exercise 1: Remainders (Max and Min > 0)."""

# Your function will take an array as input and an integer X,
# you need to find out and return the number that leaves the greatest
# and least reminders when divided by X. Reminders must be >0 .


# function for maximum of two numbers
def maxfn(a, b):
    return a if a > b else b


# function for minimum of two numbers
def minfn(a, b):
    return a if a < b else b


# take x and an array as input
def exp1(X, arr):
    if not arr or X == 0:
        return (None, None)

    min_rem = float("inf")
    max_rem = float("-inf")

    for i in arr:
        rem = i % X
        if rem > 0:
            max_rem = maxfn(max_rem, rem)
            min_rem = minfn(min_rem, rem)

    if max_rem == float("-inf"):
        return (None, None)

    return max_rem, min_rem


ex1 = exp1

# Run the function for given input
if __name__ == "__main__":
    x = 10
    array = [10, 20, 30, 40, 50, 44, 55, 60]
    print(exp1(x, array))
