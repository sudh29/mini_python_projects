# 🐍 Python Training Exercises

A set of 19 Python exercises designed to sharpen your problem-solving skills.  
Work through them in order — each one builds on core Python concepts.

> **Guidelines**
> - Write clean, readable code with clear function and variable names.
> - Add comments to explain your logic.
> - Do **not** use built-in shortcuts unless the question explicitly permits them.
> - Test your solution with the provided sample inputs before submitting.

---

## Exercise 1 — Remainders (Max & Min)

Your function will take an **array** as input and an **integer X**.  
Find the number in the array that leaves the **greatest** remainder and the number that leaves the **least** remainder when divided by X.  
Remainders must be **> 0**.

**Sample Input:**
```python
X = 10
array = [10, 20, 30, 40, 50, 44, 55, 60]
```

---

## Exercise 2 — Filter, Deduplicate & Sum

Your function will take an **integer X** and **multiple arrays** as inputs.  
- Filter the elements from each array that are **greater than X**.  
- Store all the filtered elements in a new array.  
- **Remove duplicates.**  
- Return the **sum** of all elements in the new array.

**Sample Input:**
```python
exp2(
    50,
    [10, 12, 34, 46, 55, 79, 80],
    [12, 22, 33, 44, 45, 60, 70, 80],
    [9, 10, 120, 130, 140, 55, 199],
    [20, 23, 4, 40, 50, 12, 23, 44, 55],
)
```

---

## Exercise 3 — Element Frequency per Array

Your function will take **multiple arrays** as inputs.  
For each element in each array, find out how many times that element occurs **in that array** and store it in a dictionary.  
**Sort the final dictionary by keys** and return it.

**Sample Input:**
```python
exp3([12, 12, 55, 79, 79, 12], [12, 33, 60, 60, 79], [199, 55, 199])
```

---

## Exercise 4 — Most Divisible List

Your function takes **any number of lists** as arguments (`*args`) and an **integer X**.  
Find the list that has the **most numbers divisible by X** and return it.  
If multiple lists tie, return the divisible elements from all tied lists combined.

**Sample Input:**
```python
ex4(3, [1, 2, 3, 4, 5], [1, 3, 4, 6, 9], [10, 12, 9, 7, 8], [12, 7, 9, 8, 14])
ex4(
    3,
    [1, 2, 3, 4, 5],
    [1, 3, 4, 6, 9],
    [3, 9, 10, 11, 18],
    [10, 12, 9, 7, 8],
    [12, 7, 9, 8, 14],
)
```

---

## Exercise 5 — Divisible Elements Frequency

Your function takes **any number of lists** as arguments (`*args`) and an **integer X**.  
Find all elements across all lists that are **divisible by X**.  
Create and return a **dictionary** containing the **count of occurrences** of each such element.

**Sample Input:**
```python
ex5(
    5,
    [10, 12, 14, 40, 60, 65, 80, 90],
    [3, 4, 65, 40, 40, 30, 20],
    [120, 400, 80, 90, 20, 60],
)
```

---

## Exercise 6 — Greater Than the Rest

Your function takes an **array** as an argument.  
Find out if there is **any number in the array which is greater than the sum of all other elements**.  
Return that number if found, otherwise return nothing.

**Sample Input:**
```python
ex6([10, 20, 30, 45, 90, 200, 2000, 10001])
ex6([10, 20, 30, 40, 90, 200, 20])
```

---

## Exercise 7 — Paired Divisibility (Max Pair)

Your function takes **2 arrays** and an **integer X** as arguments.  
Find pairs of numbers from both lists that are **both divisible by X**, where pairing is based on matching **index position** (`arr1[n]` and `arr2[n]`).  
Return only the pair that contains the **maximum value**.

**Sample Input:**
```python
ex7(10, [10, 20, 30, 40, 50], [12, 24, 40, 90, 200])
```

---

## Exercise 8 — Pattern Filter (Case-Insensitive, No Duplicates)

Your function takes **multiple arrays** (of strings) and a **pattern** string as arguments.  
Return a list of all elements across all arrays that **do not contain the pattern**.  
- Avoid duplicates.  
- The comparison must be **case-insensitive**.

**Sample Input:**
```python
ex8(
    "code",
    ["hello", "world", "code", "python"],
    ["code", "coding", "coder", "code lead"],
    ["Python", "Data", "AI", "C"],
)
ex8(
    "Arun",
    ["hello", "world", "code", "python"],
    ["code", "coding", "coder", "code lead"],
    ["Python", "Data", "AI", "C"],
)
```

---

## Exercise 9 — Powers with Rules

Write a Python function to find the **powers of numbers** given an array where:
- Each item at an **even index (0, 2, 4…)** is the **base**.
- Each item at an **odd index (1, 3, 5…)** is the **exponent** for the previous base.
- The **maximum exponent** allowed is **5**. If the exponent is > 5, the value remains unchanged (power = 1).
- If a base is left without a paired exponent, use the **minimum exponent** from the other pairs.

**Sample Input:**
```python
ex9([2, 3, 7, 1, 5, 3, 16, 2])
ex9([10, 3, 50, 2, 20, 3, 8, 2, 100])
ex9([10, 6, 50, 2, 20, 3, 8, 2, 100])
```

---

## Exercise 10 — Deep Positive Integer Extractor

From a given array that can contain any number of **sub-lists**, **dicts**, and **nested dicts**:
- Find all **positive integers** and store them in a flat array.
- For dicts, consider **both keys and values** (positive integers only).
- From the final array, create an **occurrence dictionary** to count each number.
- **Do not use any built-ins.**
- The input can have **any levels of nesting**.

**Sample Input:**
```python
input = [
    1,
    2,
    3,
    4,
    5,
    [True, False, -110.100, -200, 500, [1, 2, 3, 4, 5]],
    {0: 1, 1: 2, 3: 4, 5: [10, True, -1100, 200, 300]},
]
ex10(input)
```

---

## Exercise 11 — Ways to Form String A from String B

Your function takes **2 strings** as inputs.  
Find all possible ways by which you can form **String A** from **String B**.

**Rules:**
- Both strings must be **alphanumeric only** (letters and numbers, no other characters).
- The length of **String B must be greater than** String A.
- A character once used from String B **must not be reused**.
- Return the output as a **list of dictionaries**, where keys are indexes in String B and values are the characters from String A.

**Sample Input:**
```python
ex11("abc", "agcb xyzbc amnopq copnotab cosxab")
ex11("ab", "agcb xyzbc amnopq copnotab coscabbb")
```

---

## Exercise 12 — Flatten & Filter by Divisibility

Using **list comprehension**, pick elements from **ListA** that are **divisible by at least 2 elements in ListB**.  
- If ListB contains **fewer than 2 elements**, do not process — return an empty result.
- Return the final filtered list.

**Sample Input:**
```python
ex12([10, 30, 35, 40, 45, 28, 39, 50, 61, 78], [2, 5, 7, 10, 20, 50])
```

---

## Exercise 13 — Divisible Count per Array (Dict Comprehension)

Using **dict comprehension**, find the occurrence of numbers divisible by X.  
Your function takes an **integer X** followed by **any number of arrays**.  
Parse each array, find elements divisible by X, and return a dictionary where:
- **Key** = array position (index)
- **Value** = count of elements in that array divisible by X

**Sample Input:**
```python
ex13(
    5,
    [1, 20, 35, 45, 90],
    [100, 20, 30, 45, 60, 75, 90],
    [2, 3, 30, 19, 90, 25, 80],
    [5, 6, 9, 10, 15, 25, 30],
)
```

---

## Exercise 14 — Update Dictionary Values (Dict Comprehension)

Write a program to **update dictionary values** using dict comprehension.  
Your function takes **3 inputs**: a dict, an integer X, and an integer Y.  
Find keys whose values are **greater than X** and **multiply those values by Y**.  
Return the updated dictionary.

**Sample Input:**
```python
ex14({1: 3, 2: 20, 3: 4, 5: 60, 10: 90}, x=50, y=10)
```

---

## Exercise 15 — Flatten a List Using Recursion

Write a program to **flatten a list using recursion**.  
The input list can contain **any levels of sub-lists**.

**Sample Input:**
```python
ip = [1, 2, 3, 4, 5, [10, 20, 30, 4, 50, 60, 100], 90, 200, [300, 10]]
ex15(ip)
```

---

## Exercise 16 — Sort Array by Occurrence

Sort the array according to the **occurrence (frequency) of numbers** — most frequent first.  
Return an array of the unique numbers ordered by their frequency (descending).

**Sample Input:**
```python
array = [
    1,
    1,
    1,
    2,
    3,
    4,
    9,
    0,
    2,
    2,
    3,
    4,
    3,
    2,
    1,
    5,
    5,
    9,
    0,
    0,
    1,
    1,
    1,
    1,
    2,
    5,
    6,
    7,
    7,
    8,
    9,
    0,
    0,
    4,
    4,
    4,
    6,
    6,
    6,
    6,
    6,
    7,
    7,
    7,
    8,
    8,
    8,
    8,
    8,
    8,
]
ex16(array)
```

---

## Exercise 17 — Jumble Two Strings

Write Python code to **jumble 2 strings** without using any built-ins.  
Take characters from **alternate indexes** of both strings and interleave them.  
Before running, ensure **both strings are of the same length** — print a message and return if not.

**Sample Input:**
```python
ex17("hello", "world")
ex17("Python", "JavaCP")
ex17("sam", "tom")
```

---

## Exercise 18 — Count Vowel Occurrences

Write Python code to find the **count of each vowel** in a given string.  
Return a dictionary with each vowel and its count.

**Sample Input:**
```python
ex18("hello world")
ex18("lets get started with python")
```

---

## Exercise 19 — Keyword Arguments with Decorators

Write a function that takes `**kwargs` as input and performs an operation based on an `action` key.

**Supported actions:** `sum`, `avg`, `max`, `min`

**Rules:**
- Use a **decorator** to print the action being performed (optional but encouraged).
- **Handle all exceptions.**
- All non-`action` keyword arguments are treated as the numeric values to operate on.

**Sample Input:**
```python
ex19(x=100, y=200, z=150, a=300, b=180, e=90, f=25, g=80, h=120, action="avg")
ex19(x=100, y=200, z=150, a=300, b=180, e=90, f=25, g=80, h=120, action="sum")
ex19(x=100, y=200, z=150, a=300, b=180, e=90, f=25, g=80, h=120, action="max")
ex19(x=100, y=200, z=150, a=300, b=180, e=90, f=25, g=80, h=120, action="min")
```

---

