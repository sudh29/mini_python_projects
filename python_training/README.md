# Python Algorithmic Training Suite (`python_training/`)

A curated collection of 19 core Python programming exercises designed to develop problem-solving intuition, data structure manipulation, recursion, comprehension syntax, and custom decorators.

---

## Exercise Catalog

| Exercise | Function | Concepts & Operations | Time Complexity | Space Complexity |
|:---|:---|:---|:---:|:---:|
| **Ex 1** | `ex1(x, arr)` | Remainders (Max & Min > 0) with zero-handling | $O(N)$ | $O(1)$ |
| **Ex 2** | `ex2(x, *args)` | Filtering elements $> x$, deduplication, and summation across variable lists | $O(\sum N_i)$ | $O(U)$ |
| **Ex 3** | `ex3(*args)` | Element frequency per array with lexicographically sorted keys | $O(K \log K)$ | $O(K)$ |
| **Ex 4** | `ex4(x, *args)` | Finding the list with maximum elements divisible by $x$, with tie union | $O(\sum N_i)$ | $O(N)$ |
| **Ex 5** | `ex5(x, *args)` | Frequency map of elements divisible by $x$ across multiple lists | $O(\sum N_i)$ | $O(U)$ |
| **Ex 6** | `ex6(arr)` | Identifying an element strictly greater than the sum of all other elements | $O(N)$ | $O(1)$ |
| **Ex 7** | `ex7(x, arr1, arr2)` | Paired index divisibility by $x$, returning the maximum pair | $O(N)$ | $O(P)$ |
| **Ex 8** | `ex8(pat, *args)` | Case-insensitive pattern exclusion with order-preserving deduplication | $O(\sum N_i \cdot L)$ | $O(U)$ |
| **Ex 9** | `ex9(arr)` | Alternating base-exponent pairing with upper bound threshold ($\le 5$) | $O(N)$ | $O(N)$ |
| **Ex 10** | `ex10(arr)` | Deep recursion through arbitrary nested lists and dictionaries for positive integers | $O(T)$ | $O(D)$ |
| **Ex 11** | `ex11(str1, str2)` | Reconstructing String A from non-reusable characters of String B with index mappings | $O(L_1 \cdot L_2)$ | $O(W)$ |
| **Ex 12** | `ex12(listA, listB)` | List comprehension filtering elements in A divisible by $\ge 2$ elements in B | $O(|A| \cdot |B|)$ | $O(|A|)$ |
| **Ex 13** | `ex13(x, *args)` | Dict comprehension mapping list index to divisible count | $O(\sum N_i)$ | $O(M)$ |
| **Ex 14** | `ex14(d, x, y)` | Dict comprehension transforming values $> x$ by factor $y$ | $O(|D|)$ | $O(|D|)$ |
| **Ex 15** | `ex15(arr)` | Deeply nested list flattening using pure recursion | $O(N)$ | $O(Depth)$ |
| **Ex 16** | `ex16(arr)` | Frequency-based descending unique element sorting | $O(U \log U)$ | $O(U)$ |
| **Ex 17** | `ex17(s1, s2)` | Alternating index string interleaving with strict length equality validation | $O(L)$ | $O(L)$ |
| **Ex 18** | `ex18(s)` | Frequency extraction of vowels (`a, e, i, o, u`) | $O(L)$ | $O(1)$ |
| **Ex 19** | `ex19(**kwargs)` | Decorator-wrapped kwargs dispatcher supporting `sum`, `avg`, `max`, and `min` | $O(K)$ | $O(K)$ |

---

## Python API Usage

All exercises are exposed via the package interface:

```python
from python_training import ex1, ex8, ex15, ex19

# Ex 1: Max & Min remainders
max_r, min_r = ex1(10, [10, 20, 30, 44, 55])
print(f"Max: {max_r}, Min: {min_r}")

# Ex 8: Pattern filter
filtered = ex8("code", ["hello", "code", "python"], ["coding", "rust"])
print(filtered)  # ['hello', 'python', 'rust']

# Ex 15: Recursive list flattening
flat = ex15([1, [2, [3, 4]], 5])
print(flat)  # [1, 2, 3, 4, 5]

# Ex 19: Decorator kwargs dispatcher
total = ex19(x=10, y=20, z=30, action="sum")
print(total)  # 60
```

---

## Testing

Run the comprehensive unit test suite covering all 19 exercises:

```bash
uv run pytest tests/test_python_training.py
```
