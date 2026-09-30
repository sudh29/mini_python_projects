"""Exercise 8: Pattern Filter across arrays (Case-insensitive, no duplicates)."""

# Function to find the patterns across arrays. Your function will receive any no.
# arrays and another argument pattern. You must return a list of all elements in
# all arrays that doesn't contain the pattern, avoid duplicates and its not case-sensitive.


# function to remove duplicates case-insensitively while preserving order
def removeduplicate(arr):
    temp = []
    seen = set()
    for i in arr:
        low = i.lower()
        if low not in seen:
            seen.add(low)
            temp.append(i)
    return temp


# Function takes multiple Arrays, another argument pattern.
def ex8(pattern, *args):
    # filter all elements in all arrays that doesn't contain the pattern (case-insensitive)
    pat_low = pattern.lower()
    res = [item for arg in args for item in arg if pat_low not in item.lower()]
    return removeduplicate(res)


# Run the function for given input
if __name__ == "__main__":
    print(
        ex8(
            "code",
            ["hello", "world", "code", "python"],
            ["code", "coding", "coder", "code lead"],
            ["Python", "Data", "AI", "C"],
        )
    )

    print(
        ex8(
            "Arun",
            ["hello", "world", "code", "python"],
            ["code", "coding", "coder", "code lead"],
            ["Python", "Data", "AI", "C"],
        )
    )
