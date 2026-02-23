# Error Patterns: Cluster C010 (`Compute Electricity Bill`)

## Cluster Summary

- Cluster ID: `C010`
- Cluster title: `Compute Electricity Bill`
- Cluster file (this file): `analysis/ERRORS-cluster-c010-compute-electricity-bill-ef6eeec2.md`
- Variants in cluster: `2`
- Total final submitters across variants: `1498`
- Total non-full final submissions across variants: `226`
- Canonical variant (by submissions): `ns_25t2_py21_2/14`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py21_1/14` | 738 | 110 | Exact duplicate problem JSON |
| `ns_25t2_py21_2/14` (canonical) | 760 | 116 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py21_2/14.json`
- Other variants in cluster:
  - `problems/ns_25t2_py21_1/14.json`

## Cluster-Level Outcome Summary

- Final submitters: `1498`
- Full pass: `1272`
- Non-full final submissions: `226`
- Parseable non-full (logic/runtime focus): `154`
- Non-parseable non-full: `72`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py21_1/14` | 738 | 628 | 110 | 77 | 33 |
| `ns_25t2_py21_2/14` | 760 | 644 | 116 | 77 | 39 |

## Private Case Structure

- Private case 1: low slab only (0 and small units)
- Private case 2: middle slab incl 400 boundary
- Private case 3: high slab (>400)

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py21_1/14` | `ns_25t2_py21_2/14` |
| --- | ---: | ---: | ---: | ---: |
| Syntax / non-parseable final submission | 72 | 31.9% | 33 | 39 |
| Runtime NameError | 33 | 14.6% | 18 | 15 |
| Uses separate `if` slabs (branch overwrite / wrong slab precedence) | 26 | 11.5% | 8 | 18 |
| Runtime TypeError | 22 | 9.7% | 11 | 11 |
| Low-slab-only mistake (lower slab cases fail; upper slabs often pass) | 19 | 8.4% | 10 | 9 |
| Runtime error (parseable final submission) | 18 | 8.0% | 6 | 12 |
| Middle slab formula missing fixed `+150` charge | 7 | 3.1% | 5 | 2 |
| Ignores input parameter / uses hard-coded units | 7 | 3.1% | 5 | 2 |
| Implements progressive-slab billing instead of flat slab + fixed charge | 5 | 2.2% | 2 | 3 |
| Other wrong-answer logic pattern (residual) | 4 | 1.8% | 3 | 1 |
| High-slab mistake (>400 formula/branch error) | 3 | 1.3% | 2 | 1 |
| Runtime RecursionError | 2 | 0.9% | 1 | 1 |
| Excludes the `400` boundary from middle slab (`< 400` vs `<= 400`) | 2 | 0.9% | 1 | 1 |
| Middle-slab mistake (boundary/charge error in 200-400 range) | 2 | 0.9% | 2 | 0 |
| Only high-slab case passes (low/mid branch logic broken) | 1 | 0.4% | 0 | 1 |
| Returns tariff/rate expression instead of total bill | 1 | 0.4% | 1 | 0 |
| Computes slab conditions but overwrites bill unconditionally | 1 | 0.4% | 1 | 0 |
| High slab formula missing fixed `+300` charge | 1 | 0.4% | 1 | 0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `4/226` (`1.8%`)

### Syntax / non-parseable final submission

- Cluster frequency: `72/226` (`31.9%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `33/110` (`30.0%`)
  - `ns_25t2_py21_2/14`: `39/116` (`33.6%`)
- Dominant private-case vectors: `000` x72
- Score distribution (top): `0.0` x72
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `33bd05f9bc114554bdfbc0a574602654`, summary `Runtime Error`, score `0`, vector `000`

```python
def compute_electricity_bill(units:cost):
        if units<=200:
            cost=units*0.5
            Return(cost)
        if units<=400:
            cost=(units*0.75) + 150
            return(cost)
        if units>400:
            cost=(units*0.90)+300
            return(cost)
Return the bill amount to be
paid:
    - less than or equal 200 units: 0.5 per unit
- less than or equal to 400 units: 0.75 per unit + 150 extra
- greater 400 units: 0.90 per unit + 300 extra
Examples:
    compute_electricity_bill(200) -> `100.00`
compute_electricity_bill(210) -> `236.50`
# ...
```
  - Variant `ns_25t2_py21_2/14`, Student ID `305ae25f40b54d55bf08169efd6df7e9`, summary `Runtime Error`, score `0`, vector `000`

```python
def compute_electricity_bill(units)
    if units <= 200:
        total = units*0.5
        elif units <=400:
        total = units*0.75 + 150
        else:
            total = units*0.90 + 300

    """
    Calculate the electricity bill.

     <=200 units : 0.5 per unit
    - <= 400 units : 0.75 per unit + 150 extra
    - > 400 units : 0.90 per unit + 300 extra

    Args:
        units (int): Number of units consumed.

# ...
```

### Runtime NameError

- Cluster frequency: `33/226` (`14.6%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `18/110` (`16.4%`)
  - `ns_25t2_py21_2/14`: `15/116` (`12.9%`)
- Dominant private-case vectors: `000` x29, `101` x2, `110` x1, `011` x1
- Score distribution (top): `0.0` x29, `67.0` x4
- Interpretation: Undefined variable/helper usage, often caused by partial edits or renamed variables.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `c6fb9eef5b7f4729b6b4e09ba83dd194`, summary `Runtime Error`, score `0`, vector `000`

```python
def compute_electricity_bill(units: int) -> float:
    '''
    Return the bill amount to be paid:
    - less than or equal 200 units: 0.5 per unit
    - less than or equal to 400 units: 0.75 per unit + 150 extra
    - greater 400 units: 0.90 per unit + 300 extra

    Examples:
    compute_electricity_bill(200) -> `100.00`
    compute_electricity_bill(210) -> `236.50`
    compute_electricity_bill(412) -> `670.80`

    Args:
        units (int): The units consumed.

    Returns:
        float : The amount to be paid.
    '''
```
  - Variant `ns_25t2_py21_2/14`, Student ID `0901623cd89e47da95fd58df3f93d6fe`, summary `Runtime Error`, score `0`, vector `000`

```python
def is_reverse_combined_palindrome(s1: str, s2: str) -> str:
    '''
    Given two strings,
    - Reverses the first string
    - Concatenates it with the second string
    - Checks if the result is a palindrome or not

    Examples:
    >>> is_reverse_combined_palindrome("mad", "am")
    False
    >>> is_reverse_combined_palindrome("dam", "am")
    True

    Args:
        s1 (string): The first string
        s2 (string): The second string

    Returns:
# ...
```

### Uses separate `if` slabs (branch overwrite / wrong slab precedence)

- Cluster frequency: `26/226` (`11.5%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `8/110` (`7.3%`)
  - `ns_25t2_py21_2/14`: `18/116` (`15.5%`)
- Dominant private-case vectors: `011` x19, `010` x3, `001` x2, `000` x1
- Score distribution (top): `67.0` x20, `33.0` x5, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `d111cb992dd34062a304bc984b7e44b5`, summary `Wrong Answer`, score `33`, vector `010`

```python
cost = 0
extra_charge = 150
extra_charges = 300
if units <= 200:
        cost = units * 0.50
if units <=400:
        cost = units *0.75 + extra_charge
if units > 400:
        cost = 400 * 0.30 + extra_charges
return cost
```
  - Variant `ns_25t2_py21_2/14`, Student ID `f117944261a74c7ba1b3689f96a4f104`, summary `Wrong Answer`, score `67`, vector `011`

```python
total = 0
total= float(total)
if units <= 200:
        total += units * 0.5
if units <= 400:
        total += 0.75 * units + 150
if units > 400:
        total += 0.90*units + 300
return total
"""
    Calculate the electricity bill.

    - <=200 units : 0.5 per unit
    - <= 400 units : 0.75 per unit + 150 extra
    - > 400 units : 0.90 per unit + 300 extra

    Args:
        units (int): Number of units consumed.
# ...
```

### Runtime TypeError

- Cluster frequency: `22/226` (`9.7%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `11/110` (`10.0%`)
  - `ns_25t2_py21_2/14`: `11/116` (`9.5%`)
- Dominant private-case vectors: `000` x18, `011` x2, `101` x1, `100` x1
- Score distribution (top): `0.0` x18, `67.0` x3, `33.0` x1
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `13f418a981fe4e709fc9efa1564a9574`, summary `Runtime Error`, score `0`, vector `000`

```python
def compute_electricity_bill(units: int) -> float:
    '''
    Return the bill amount to be paid:
    - less than or equal 200 units: 0.5 per unit
    - less than or equal to 400 units: 0.75 per unit + 150 extra
    - greater 400 units: 0.90 per unit + 300 extra

    Examples:
    compute_electricity_bill(200) -> `100.00`
    compute_electricity_bill(210) -> `236.50`
    compute_electricity_bill(412) -> `670.80`

    Args:
        units (int): The units consumed.

    Returns:
        float : The amount to be paid.
    '''
```
  - Variant `ns_25t2_py21_2/14`, Student ID `a55af24eab08422d978328565d9d170b`, summary `Runtime Error`, score `0`, vector `000`

```python
def compute_electricity_bill(units: int) -> float:
    """
    Calculate the electricity bill.

    - <=200 units : 0.5 per unit
    - <= 400 units : 0.75 per unit + 150 extra
    - > 400 units : 0.90 per unit + 300 extra

    Args:
        units (int): Number of units consumed.

    Returns:
        float: Total amount to be paid.
    """
```

### Low-slab-only mistake (lower slab cases fail; upper slabs often pass)

- Cluster frequency: `19/226` (`8.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `10/110` (`9.1%`)
  - `ns_25t2_py21_2/14`: `9/116` (`7.8%`)
- Dominant private-case vectors: `011` x19
- Score distribution (top): `67.0` x19
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `137cce72a0874b34adf9cad72d3377d5`, summary `Wrong Answer`, score `67`, vector `011`

```python
if units<=0:
        cost=0
    else:
        if 0<units<=200:
            cost=round(units*(0.5),2)
        elif 200<units<=400:
            cost=round((units*0.75)+150,2)
        else :
            cost=round((units*0.90+300),2)
return cost
```
  - Variant `ns_25t2_py21_2/14`, Student ID `6edf98bfea0d4ea199bf70b8d947ec90`, summary `Wrong Answer`, score `67`, vector `011`

```python
cost = 0
if (units > 400) :
        cost = units*0.9 + 300
    elif (units <= 400) and (units > 200):
        cost = 0.75*units + 150
    elif (units <= 200) and (units > 0):
        cost = (0.5)*units
    else:
        print("Invalid input.")
return cost
```

### Runtime error (parseable final submission)

- Cluster frequency: `18/226` (`8.0%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `6/110` (`5.5%`)
  - `ns_25t2_py21_2/14`: `12/116` (`10.3%`)
- Dominant private-case vectors: `000` x8, `011` x4, `101` x3, `100` x2
- Score distribution (top): `0.0` x8, `67.0` x8, `33.0` x2
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `bed97911eb304dbcaa618a55d613930b`, summary `Runtime Error`, score `67`, vector `101`

```python
if units <200:
        cost= units*0.50

    elif 200<=units<400:
        cost = (units*0.75) + 150

    elif units >400:
        cost = (units*0.90) + 300
'''
    Return the bill amount to be paid:
    - less than or equal 200 units: 0.5 per unit
    - less than or equal to 400 units: 0.75 per unit + 150 extra
    - greater 400 units: 0.90 per unit + 300 extra

    Examples:
    compute_electricity_bill(200) -> `100.00`
    compute_electricity_bill(210) -> `236.50`
    compute_electricity_bill(412) -> `670.80`
# ...
```
  - Variant `ns_25t2_py21_2/14`, Student ID `90cefd7c86b14ff5b44a77a3f84b8f6b`, summary `Runtime Error`, score `33`, vector `100`

```python
if units <=200:
        cost=units*0.5
    elif cost <=400:
        cost=(0.75*units)+150
    elif cost > 400:
        cost=(0.90*units)+300
"""
    Calculate the electricity bill.

    - <=200 units : 0.5 per unit
    - <= 400 units : 0.75 per unit + 150 extra
    - > 400 units : 0.90 per unit + 300 extra

    Args:
        units (int): Number of units consumed.

    Returns:
        float: Total amount to be paid.
# ...
```

### Middle slab formula missing fixed `+150` charge

- Cluster frequency: `7/226` (`3.1%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `5/110` (`4.5%`)
  - `ns_25t2_py21_2/14`: `2/116` (`1.7%`)
- Dominant private-case vectors: `101` x4, `010` x1, `000` x1, `110` x1
- Score distribution (top): `67.0` x5, `33.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `b8bf67f3d02445d0bee2685e942414ed`, summary `Wrong Answer`, score `0`, vector `000`

```python
if units <= 200:
        return units * 0.5 and units - 100.0
    elif units <= 400:
        return units * 0.75 and  units + 98 - 0.5
    elif units > 400:
        return units * 0.90 and units + 300 - 41.2
    else:
        return cost
```
  - Variant `ns_25t2_py21_2/14`, Student ID `19c09847848a4aa9a1f2353bf08bb73f`, summary `Wrong Answer`, score `33`, vector `010`

```python
if units <= 200:
        cost = units*0,5

    elif units <= 400:
        cost = (200*0.5) + (units - 200)*0.75 + 200

    else:
        cost = (200*0.5) + (200*0.75) + (units - 400)*0.90 + 300
return cost
```

### Ignores input parameter / uses hard-coded units

- Cluster frequency: `7/226` (`3.1%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `5/110` (`4.5%`)
  - `ns_25t2_py21_2/14`: `2/116` (`1.7%`)
- Dominant private-case vectors: `011` x3, `000` x2, `110` x1, `101` x1
- Score distribution (top): `67.0` x5, `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `d52c58c7ddf148879f61fa79354d9896`, summary `Wrong Answer`, score `67`, vector `011`

```python
if units_consumed<=200:
        cost=round(0.5*units_consumed,2)
if units_consumed<=400:
        cost=round((0.75*units_consumed)+150,2)
if units_consumed>400:
        cost=round((0.90*units_consumed)+300,2)
return cost
'''
    Return the bill amount to be paid:
    - less than or equal 200 units: 0.5 per unit
    - less than or equal to 400 units: 0.75 per unit + 150 extra
    - greater 400 units: 0.90 per unit + 300 extra

    Examples:
    compute_electricity_bill(200) -> `100.00`
    compute_electricity_bill(210) -> `236.50`
    compute_electricity_bill(412) -> `670.80`

# ...
```
  - Variant `ns_25t2_py21_2/14`, Student ID `519db619d18b48208779763dfee33f0c`, summary `Wrong Answer`, score `67`, vector `110`

```python
unit = float(units)
if unit <= 200:
        cost = float(unit * 0.5)
    elif unit > 200 or unit <= 400:
        cost = float((unit * 0.75) + 150)
    elif unit > 400:
        cost = float((unit * 0.90) + 300)
return cost
compute_electricity_bill(100.00)
```

### Implements progressive-slab billing instead of flat slab + fixed charge

- Cluster frequency: `5/226` (`2.2%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `2/110` (`1.8%`)
  - `ns_25t2_py21_2/14`: `3/116` (`2.6%`)
- Dominant private-case vectors: `100` x3, `110` x2
- Score distribution (top): `33.0` x3, `67.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `db4ea38769344d1c8b7e1435d54dfbff`, summary `Wrong Answer`, score `33`, vector `100`

```python
if units <=200:
            amount= units*0.5
    elif units<=400:
            amount=200*0.5 + (units- 200)*0.75 +150
    else:
            amount=200*0.5 + 200*0.75 + (units - 400)*0.90+300
return round(amount,2)
return cost
```
  - Variant `ns_25t2_py21_2/14`, Student ID `a79de7cd3c6b48c986ddd587499cd87e`, summary `Wrong Answer`, score `67`, vector `110`

```python
if units <= 200 :
        cost = units*0.5
    elif units <= 400 :
        cost = (200*0.5 + (units-200) *0.75 + 200)
    else:
        cost = (200*0.5) + (200*0.75) + (units-400) *0.90 +300
"""
    Calculate the electricity bill.

    - <=200 units : 0.5 per unit
    - <= 400 units : 0.75 per unit + 150 extra
    - > 400 units : 0.90 per unit + 300 extra

    Args:
        units (int): Number of units consumed.

    Returns:
        float: Total amount to be paid.
# ...
```

### Other wrong-answer logic pattern (residual)

- Cluster frequency: `4/226` (`1.8%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `3/110` (`2.7%`)
  - `ns_25t2_py21_2/14`: `1/116` (`0.9%`)
- Dominant private-case vectors: `000` x2, `010` x1, `100` x1
- Score distribution (top): `33.0` x2, `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `7e420061c0da4494b3318f954707e4de`, summary `Wrong Answer`, score `0`, vector `000`

```python
units = int()
cost = []
if units <= 200:
        cost = units*0.5
        return cost

    elif units <= 400:
        cost = units*0.75 + 150
        return cost

    elif units > 400:
        cost = units*0.90 + 300
        return cost
return cost
```
  - Variant `ns_25t2_py21_2/14`, Student ID `f6c85110cf974cfabdb1b871a47da140`, summary `Wrong Answer`, score `33`, vector `010`

```python
cost = units * 0.75 + 150
return cost
```

### High-slab mistake (>400 formula/branch error)

- Cluster frequency: `3/226` (`1.3%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `2/110` (`1.8%`)
  - `ns_25t2_py21_2/14`: `1/116` (`0.9%`)
- Dominant private-case vectors: `110` x3
- Score distribution (top): `67.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `6e2121db37584312b8ad88456b1e4b4f`, summary `Wrong Answer`, score `67`, vector `110`

```python
if units<=200:
        cost=units*0.5
    elif units>200 & units<=400:
        cost=units*0.75+150
    elif units>400:
        cost=(units*0.90)+300.00
return cost
```
  - Variant `ns_25t2_py21_2/14`, Student ID `c99463e453ce42b2a2daec75fef52771`, summary `Wrong Answer`, score `67`, vector `110`

```python
if units <=200:
        cost = units*0.5
    elif units<= 400:
        cost = units*0.75 + 150
    elif units <= 600:
        cost = units*0.90 + 300
    else:
        cost = units*1.0+500
return cost
return cost
```

### Runtime RecursionError

- Cluster frequency: `2/226` (`0.9%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `1/110` (`0.9%`)
  - `ns_25t2_py21_2/14`: `1/116` (`0.9%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `26fe476cddef4fd0b6596a79a0206cf0`, summary `Runtime Error`, score `0`, vector `000`

```python
...
```
  - Variant `ns_25t2_py21_2/14`, Student ID `20f59052c1f746198f11a2bc78ad7c0c`, summary `Runtime Error`, score `0`, vector `000`

```python
units(
       round(compute_electricity_bill(units), 2),
    )
units(
        round(compute_electricity_bill(units), 2),
    )
return units
```

### Excludes the `400` boundary from middle slab (`< 400` vs `<= 400`)

- Cluster frequency: `2/226` (`0.9%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `1/110` (`0.9%`)
  - `ns_25t2_py21_2/14`: `1/116` (`0.9%`)
- Dominant private-case vectors: `101` x2
- Score distribution (top): `67.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `0dba5a732266429b98fcd161c5fec703`, summary `Wrong Answer`, score `67`, vector `101`

```python
if units<=200:
       cost=units*0.50
    elif units <400 and units>200:
       cost=units*0.75 +150
    else:
        cost=units*0.90+ 300
return cost
```
  - Variant `ns_25t2_py21_2/14`, Student ID `ba875cb74de94f8689df2e733c78760e`, summary `Wrong Answer`, score `67`, vector `101`

```python
if units <= 200:
        return units * 0.5
    elif units < 400:
        return units * 0.75 + 150
    else:
        return units * 0.90 + 300
```

### Middle-slab mistake (boundary/charge error in 200-400 range)

- Cluster frequency: `2/226` (`0.9%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `2/110` (`1.8%`)
  - `ns_25t2_py21_2/14`: `0/116` (`0.0%`)
- Dominant private-case vectors: `101` x2
- Score distribution (top): `67.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `e62f562074f74186973aad10eeb5d492`, summary `Wrong Answer`, score `67`, vector `101`

```python
cost=0
if units<=200.0:
        cost=(units*0.5)
    elif 200<cost and cost<=400:
        cost=(units*0.75)+150.0
    elif units>400.0:
        cost=(units*0.90)+300.0
return float(cost)
```

### Only high-slab case passes (low/mid branch logic broken)

- Cluster frequency: `1/226` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `0/110` (`0.0%`)
  - `ns_25t2_py21_2/14`: `1/116` (`0.9%`)
- Dominant private-case vectors: `001` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_2/14`, Student ID `9f8feef320ed41999a06ec569a457209`, summary `Wrong Answer`, score `33`, vector `001`

```python
units <= 200
cost = units*(0.5)
return cost
```

### Returns tariff/rate expression instead of total bill

- Cluster frequency: `1/226` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `1/110` (`0.9%`)
  - `ns_25t2_py21_2/14`: `0/116` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `1177b847db484aab8d3999afca12874c`, summary `Wrong Answer`, score `0`, vector `000`

```python
if units <= 200:
        return float(0.5)
    elif units <= 400:
        return float(0.75 + 150)
    elif units > 400:
        return float(0.90 + 300)
return float(amount)
return cost
```

### Computes slab conditions but overwrites bill unconditionally

- Cluster frequency: `1/226` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `1/110` (`0.9%`)
  - `ns_25t2_py21_2/14`: `0/116` (`0.0%`)
- Dominant private-case vectors: `001` x1
- Score distribution (top): `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `1af8b8766aa7419eb29e044f215eceff`, summary `Wrong Answer`, score `33`, vector `001`

```python
bill_cost = 0
num_of_units = units
is_num_of_units = (units <= 200)
bill_cost = (0.5*units + 0)
is_num_of_units = (200 < units <= 400)
bill_cost = (0.75*units + 150)
is_num_of_units = (400 < units )
bill_cost = (0.90*units + 300)
return bill_cost
```

### High slab formula missing fixed `+300` charge

- Cluster frequency: `1/226` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py21_1/14`: `1/110` (`0.9%`)
  - `ns_25t2_py21_2/14`: `0/116` (`0.0%`)
- Dominant private-case vectors: `110` x1
- Score distribution (top): `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py21_1/14`, Student ID `4884903468b0487b887613c3e71464e1`, summary `Wrong Answer`, score `67`, vector `110`

```python
if units <= 200:
        cost = units * 0.50
    elif units <= 400:
        cost = (units * 0.75) + 150
    else:
        cost = (units * 0.90) + 400
return cost
```
