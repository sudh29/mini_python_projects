"""Comprehensive unit tests covering all 19 python_training algorithmic exercises."""

import pytest

from python_training import (
    ex1,
    ex2,
    ex3,
    ex4,
    ex5,
    ex6,
    ex7,
    ex8,
    ex9,
    ex10,
    ex11,
    ex12,
    ex13,
    ex14,
    ex15,
    ex16,
    ex17,
    ex18,
    ex19,
)


def test_ex1_remainders():
    """Exercise 1: max and min remainders > 0."""
    max_rem, min_rem = ex1(10, [10, 20, 30, 40, 50, 44, 55, 60])
    assert max_rem == 5  # 55 % 10 = 5
    assert min_rem == 4  # 44 % 10 = 4

    # All multiples of X (no remainder > 0)
    assert ex1(5, [10, 15, 20]) == (None, None)


def test_ex2_filter_dedup_sum():
    """Exercise 2: filter > x, deduplicate, and sum."""
    result = ex2(
        50,
        [10, 12, 34, 46, 55, 79, 80],
        [12, 22, 33, 44, 45, 60, 70, 80],
    )
    # Filtered > 50: [55, 79, 80, 60, 70] (80 deduplicated)
    assert result == 55 + 79 + 80 + 60 + 70


def test_ex3_element_frequency():
    """Exercise 3: frequency per array with sorted keys."""
    res = ex3([12, 12, 55, 79], [12, 33, 60, 60])
    assert res[0] == {12: 2, 55: 1, 79: 1}
    assert res[1] == {12: 1, 33: 1, 60: 2}


def test_ex4_most_divisible_list():
    """Exercise 4: list with most numbers divisible by X."""
    res = ex4(3, [1, 2, 3, 4, 5], [1, 3, 4, 6, 9], [10, 12, 9, 7, 8])
    assert res == [1, 3, 4, 6, 9]


def test_ex5_divisible_frequency():
    """Exercise 5: frequency of elements divisible by X across all lists."""
    res = ex5(5, [10, 15, 12], [15, 20, 7])
    assert res[10] == 1
    assert res[15] == 2
    assert res[20] == 1
    assert 12 not in res
    assert 7 not in res


def test_ex6_greater_than_sum_of_rest():
    """Exercise 6: element strictly greater than sum of all other elements."""
    assert ex6([10, 20, 30, 45, 90, 200, 2000, 10001]) == 10001
    assert ex6([10, 20, 30]) is None


def test_ex7_paired_divisibility_max():
    """Exercise 7: index-matching pairs both divisible by X, returning max pair."""
    pair = ex7(10, [10, 20, 30, 40, 50], [12, 24, 40, 90, 200])
    # Index 2: (30, 40), Index 3: (40, 90), Index 4: (50, 200) -> max is 200 in (50, 200)
    assert pair == (50, 200)


def test_ex8_pattern_filter_case_insensitive():
    """Exercise 8: elements not containing pattern, case-insensitive, deduplicated."""
    res = ex8(
        "code",
        ["hello", "world", "code", "python"],
        ["code", "coding", "coder"],
        ["Python", "AI"],
    )
    assert "code" not in res
    assert "coder" not in res
    assert "coding" in res
    assert "hello" in res
    assert "AI" in res

    # Case-insensitive pattern check
    res_upper = ex8("CODE", ["Code", "hello"])
    assert "Code" not in res_upper
    assert "hello" in res_upper


def test_ex9_powers():
    """Exercise 9: base-exponent pairing with max exponent 5."""
    res = ex9([2, 3, 7, 1, 5, 3, 16, 2])
    assert res == [2**3, 7**1, 5**3, 16**2]

    # Exponent > 5 stays power of 1
    res2 = ex9([10, 6])
    assert res2 == [10**1]


def test_ex10_deep_positive_integers():
    """Exercise 10: extract positive integers from deeply nested structures."""
    data = [1, 2, [3, -4, 5], {1: 2, 0: -5, 3: [1, 2]}]
    res = ex10(data)
    assert res[1] >= 2
    assert res[2] >= 2
    assert res[3] >= 1
    assert -4 not in res
    assert 0 not in res


def test_ex11_string_reconstruction():
    """Exercise 11: character index mappings from String B to form String A."""
    res = ex11("ab", "agcb xyzbc")
    assert isinstance(res, list)
    assert len(res) > 0
    assert "a" in res[0].values()
    assert "b" in res[0].values()


def test_ex12_divisibility_by_at_least_two():
    """Exercise 12: elements in ListA divisible by at least 2 in ListB."""
    res = ex12([10, 30, 35, 40, 45, 28, 39, 50, 61, 78], [2, 5, 7, 10, 20, 50])
    assert 10 in res  # divisible by 2, 5, 10
    assert 30 in res  # divisible by 2, 5, 10
    assert 61 not in res


def test_ex13_divisible_count_per_array():
    """Exercise 13: dict comprehension with array index as key and divisible count as value."""
    res = ex13(5, [1, 20, 35, 45, 90], [100, 20, 30, 45, 60, 75, 90])
    assert res[0] == 4  # 20, 35, 45, 90
    assert res[1] == 7


def test_ex14_dict_comprehension_multiplier():
    """Exercise 14: update dict values > x multiplied by y."""
    data = {1: 3, 2: 20, 3: 4, 5: 60, 10: 90}
    res = ex14(data, x=50, y=10)
    assert res == {5: 600, 10: 900}


def test_ex15_recursive_flatten():
    """Exercise 15: recursive list flattening."""
    nested = [1, 2, [3, [4, 5], 6], [7, 8]]
    assert ex15(nested) == [1, 2, 3, 4, 5, 6, 7, 8]


def test_ex16_sort_by_frequency():
    """Exercise 16: sort unique numbers by frequency descending."""
    data = [1, 1, 1, 2, 2, 3]
    assert ex16(data) == [1, 2, 3]


def test_ex17_jumble_strings():
    """Exercise 17: interleave alternating characters of equal-length strings."""
    assert ex17("hello", "world") == "hweolrllod"
    assert ex17("sam", "tom") == "staomm"
    assert ex17("short", "longerstring") is None


def test_ex18_vowel_occurrences():
    """Exercise 18: count occurrences of vowels."""
    res = ex18("hello world")
    assert res["e"] == 1
    assert res["o"] == 2
    assert "a" not in res


def test_ex19_kwargs_actions():
    """Exercise 19: kwargs evaluation for sum, avg, max, min."""
    assert ex19(x=10, y=20, z=30, action="sum") == 60
    assert ex19(x=10, y=20, z=30, action="max") == 30
    assert ex19(x=10, y=20, z=30, action="min") == 10
    assert ex19(x=10, y=20, z=30, action="avg") == "60/3"

    # Action position independence
    assert ex19(action="sum", a=100, b=200) == 300

    # Missing action raises ValueError
    with pytest.raises(ValueError, match="Missing 'action'"):
        ex19(x=10, y=20)
