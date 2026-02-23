# Error Patterns: Cluster C026 (`Sales Records Analysis`)

## Cluster Summary

- Cluster ID: `C026`
- Cluster title: `Sales Records Analysis`
- Cluster file (this file): `analysis/ERRORS-cluster-c026-sales-records-analysis-21cf7171.md`
- Variants in cluster: `2`
- Total final submitters across variants: `347`
- Total non-full final submissions across variants: `308`
- Canonical variant (by submissions): `ns_25t3_py14_1/11`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t3_py14_1/11` (canonical) | 347 | 308 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t3_py14_1/11.json`
- Other variants in cluster:
  - `problems/ns_25t3_py14_2/12.json`

## Cluster-Level Outcome Summary

- Final submitters: `347`
- Full pass: `39`
- Non-full final submissions: `308`
- Parseable non-full (logic/runtime focus): `252`
- Non-parseable non-full: `56`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t3_py14_1/11` | 347 | 39 | 308 | 252 | 56 |
| `ns_25t3_py14_2/12` | 0 | 0 | 0 | 0 | 0 |

## Private Case Structure

- Private case 1: `total_revenue_in_region(...)` correctness (region matching and no premature `return 0`)
- Private case 2: `revenue_range_for_product(...)` correctness (max-min range, including 0 for missing/single-record product)
- Private case 3: `region_with_max_sales(...)` + `steady_revenue_products(...)` (aggregation + tie-break + exact set semantics)

Private-case vectors in this report are 3-character pass/fail strings over the private case groups (e.g., `101` = passes cases 1 and 3, fails case 2).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t3_py14_1/11` | `ns_25t3_py14_2/12` |
| --- | ---: | ---: | ---: | ---: |
| Leaves template placeholders (`...`) in multiple required sales-analysis helper functions | 82 | 26.6% | 82 | 0 |
| Syntax / non-parseable final submission | 56 | 18.2% | 56 | 0 |
| Early helpers are mostly correct, but `region_with_max_sales(...)` / `steady_revenue_products(...)` logic fails hidden cases | 38 | 12.3% | 38 | 0 |
| Runtime NameError from undefined variables/accumulators in sales-analysis helpers | 30 | 9.7% | 30 | 0 |
| Runtime TypeError from treating sales records/list containers as the wrong shape | 24 | 7.8% | 24 | 0 |
| Leaves the template placeholder `...` in `steady_revenue_products(...)` (partial multi-function implementation) | 13 | 4.2% | 13 | 0 |
| Runtime KeyError from wrong sales-record keys or fragile dictionary indexing | 12 | 3.9% | 12 | 0 |
| Uses the sample variable `sales` inside helper functions instead of `sales_data` | 9 | 2.9% | 9 | 0 |
| Hard-codes public sample outputs (`17000`, `5000`, `'R1'`, sample product set) instead of computing from `sales_data` | 6 | 1.9% | 6 | 0 |
| Uses the sample variable `sales` inside helpers instead of the parameter `sales_data` | 5 | 1.6% | 5 | 0 |
| Runtime AttributeError from list/dict API misuse in sales-analysis helpers | 4 | 1.3% | 4 | 0 |
| Leaves the template placeholder `...` in `region_with_max_sales(...)` (partial multi-function implementation) | 4 | 1.3% | 4 | 0 |
| Runtime ValueError from malformed aggregation / conversion logic in sales-analysis helpers | 4 | 1.3% | 4 | 0 |
| Branch initialization bug in helper output variables before return | 4 | 1.3% | 4 | 0 |
| Most sales-analysis helpers work, but one hidden edge-case remains (commonly region tie-break aggregation or exact set semantics) | 3 | 1.0% | 3 | 0 |
| In `region_with_max_sales(...)`, compares individual records (or `revenue*quantity`) instead of aggregated totals per region | 3 | 1.0% | 3 | 0 |
| In `steady_revenue_products(...)`, filters by per-record revenue `< 5000` instead of product revenue range `< 5000` | 2 | 0.6% | 2 | 0 |
| Leaves the template placeholder `...` in `revenue_range_for_product(...)` (partial multi-function implementation) | 2 | 0.6% | 2 | 0 |
| Sales-analysis helper logic is broadly incorrect across the required functions | 2 | 0.6% | 2 | 0 |
| Only `total_revenue_in_region(...)` is mostly correct; later sales-analysis helpers are incorrect/incomplete | 2 | 0.6% | 2 | 0 |
| In `revenue_range_for_product(...)`, sums product revenues instead of returning `max(revenue) - min(revenue)` | 1 | 0.3% | 1 | 0 |
| In `total_revenue_in_region(...)`, compares the whole record to `region` instead of the record's `'region'` field | 1 | 0.3% | 1 | 0 |
| Reads input interactively inside helper functions instead of using the provided `sales_data` parameters | 1 | 0.3% | 1 | 0 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/308` (`0.0%`)

### Leaves template placeholders (`...`) in multiple required sales-analysis helper functions

- Cluster frequency: `82/308` (`26.6%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `82/308` (`26.6%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x41, `100` x22, `110` x16, `111` x3
- Score distribution (top): `0.0` x41, `20.0` x20, `40.0` x14, `60.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `16b60c17a91046a9a655943e3a2fb4a4`, summary `Wrong Answer`, score `60`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    total_revenue = 0
    for i in sales:
        # print(i['region'])
        if i['region'] == region:
            total_revenue += i['revenue']
    return(total_revenue)


    """Sum of revenue for the specified region."""
    ...


def revenue_range_for_product(sales_data: list, product: str) -> int:
    revenue_range = 0
    max_sale = 0
    min_sale = 10000000
    for i in sales:
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `56/308` (`18.2%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `56/308` (`18.2%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x56
- Score distribution (top): `0.0` x56
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `d99acc195dce484f81d339b96cdc5d83`, summary `Runtime Error`, score `0`, vector `000`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    sales = [
    {'product': 'Laptop', 'region': 'North', 'revenue': 12000, 'quantity_sold': 3},
    {'product': 'Phone',  'region': 'South', 'revenue': 8000,  'quantity_sold': 5},
    {'product': 'Tablet', 'region': 'North', 'revenue': 5000,  'quantity_sold': 2},
    {'product': 'Laptop', 'region': 'South', 'revenue': 15000, 'quantity_sold': 4},
]

is_equal(total_revenue_in_region(sales, 'North'), 17000)
is_equal(total_revenue_in_region(sales, 'East'), 0)



def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    sales = [
    {'product': 'Camera', 'region': 'West',  'revenue': 4000, 'quantity_sold': 1},
# ...
```

### Early helpers are mostly correct, but `region_with_max_sales(...)` / `steady_revenue_products(...)` logic fails hidden cases

- Cluster frequency: `38/308` (`12.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `38/308` (`12.3%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `110` x38
- Score distribution (top): `80.0` x14, `40.0` x14, `60.0` x10
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `3ba40a5f7a9a41e6bc88b39798e6d898`, summary `Wrong Answer`, score `80`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    tot_revenue = 0
    for product in sales_data:
        if product["region"]==region:
            tot_revenue+=product["revenue"]
    return tot_revenue


def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    revenue_range = 0
    max_revenue = -1
    min_revenue = -1
    for prod in sales_data:
        if prod["product"]==product:
            if max_revenue==-1:
                max_revenue = prod["revenue"]
# ...
```

### Runtime NameError from undefined variables/accumulators in sales-analysis helpers

- Cluster frequency: `30/308` (`9.7%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `30/308` (`9.7%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x21, `110` x5, `100` x3, `011` x1
- Score distribution (top): `0.0` x21, `40.0` x4, `20.0` x3, `80.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `8ab4e6c9915c4631b81ad0bbfae53261`, summary `Runtime Error`, score `40`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    total=0
    for record in sales_data:
         if record ["region"]==region:
             total +=record["revenue"]
    return total

def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    revenues = []
    for record in sales_data:
        if record["product"]==product:
            revenues.append(record["revenue"])
    if not revenues:
        return 0
    return max(revenues) - min(revenues)

# ...
```

### Runtime TypeError from treating sales records/list containers as the wrong shape

- Cluster frequency: `24/308` (`7.8%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `24/308` (`7.8%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x14, `110` x7, `100` x3
- Score distribution (top): `0.0` x14, `40.0` x7, `20.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `78441dbe20104e1087706d0ec25b55b8`, summary `Runtime Error`, score `40`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    c = 0
    q = int()
    for i in range (len(sales_data)):
        if sales_data[i]['region'] == region:
            q = 1
            r = int(sales_data[i]['revenue']) * q
            c = c + r
    return c


    """Sum of revenue for the specified region."""
    ...


def revenue_range_for_product(sales_data: list, product: str) -> int:
    m = 0
    ma = 0
# ...
```

### Leaves the template placeholder `...` in `steady_revenue_products(...)` (partial multi-function implementation)

- Cluster frequency: `13/308` (`4.2%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `13/308` (`4.2%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `110` x9, `100` x3, `111` x1
- Score distribution (top): `40.0` x9, `20.0` x3, `60.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `aa7ca1581b9c409e845be6cdf15e965e`, summary `Wrong Answer`, score `40`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    total_revenue_in_region = 0
    for i in range(0, len(sales_data)):
        if(sales_data[i]['region'] == region):
            total_revenue_in_region += sales_data[i]['revenue']
    return total_revenue_in_region


def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    max = 0
    min = 1000000
    flag = False
    for i in range(0, len(sales_data)):
        if(sales_data[i]['product'] == product):
            flag = True
            if(sales_data[i]['revenue'] <= min):
# ...
```

### Runtime KeyError from wrong sales-record keys or fragile dictionary indexing

- Cluster frequency: `12/308` (`3.9%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `12/308` (`3.9%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x8, `100` x3, `110` x1
- Score distribution (top): `0.0` x8, `20.0` x3, `40.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `9ec364e0363442eea6b2dbd34e36c17e`, summary `Runtime Error`, score `40`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    ...
    sum=0
    for element in sales_data:
        if(element["region"]==region):
            sum=sum+element["revenue"]
    return sum


def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    ...
    myrevenuerecords=[]
    for element in sales_data:
        if(element["product"]==product):
            myrevenuerecords.append(element["revenue"])
    if(len(myrevenuerecords)!=0):
# ...
```

### Uses the sample variable `sales` inside helper functions instead of `sales_data`

- Cluster frequency: `9/308` (`2.9%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `9/308` (`2.9%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `110` x8, `000` x1
- Score distribution (top): `80.0` x3, `40.0` x3, `60.0` x2, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `4e0a089065724ea599315b28adb59c99`, summary `Wrong Answer`, score `40`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    sum = 0
    for i in range(len(sales)):
        if (sales[i]['region']== region):
            sum += sales[i]['revenue']
        else:
            continue
    return sum



def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    maxx = 0
    mini =10000
    for i in range(len(sales_data)):
        if(sales_data[i]['product'] == product):
# ...
```

### Hard-codes public sample outputs (`17000`, `5000`, `'R1'`, sample product set) instead of computing from `sales_data`

- Cluster frequency: `6/308` (`1.9%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `6/308` (`1.9%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `110` x3, `000` x2, `100` x1
- Score distribution (top): `40.0` x2, `0.0` x2, `20.0` x1, `60.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `1b80651d8d264cbebe9d23883927a949`, summary `Wrong Answer`, score `40`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    r_sum=0
    for s in sales_data:
        if (s['region']==region):
            r_sum+=s['revenue']
    return r_sum

def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    # r_max=sales_data[0]['revenue']
    # r_min=sales_data[0]['revenue']
    flag=0
    r_max=0
    r_min=0
    for s in sales_data:
        if (s['product']==product):
            if flag==0:
# ...
```

### Uses the sample variable `sales` inside helpers instead of the parameter `sales_data`

- Cluster frequency: `5/308` (`1.6%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `5/308` (`1.6%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3, `110` x2
- Score distribution (top): `0.0` x3, `40.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `efea6141930d4ad9aa07f5b75f7fb525`, summary `Runtime Error`, score `40`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    ...
    s=0
    for i in range(len(sales)):
        if(sales[i]['region']==region):
            s+=sales[i]['revenue']
    return s

def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    ...

    m1=0
    m2=9999
    for i in range(len(sales)):
        if(sales[i]['product']==product):
            if sales[i]['revenue']>m1:
# ...
```

### Runtime AttributeError from list/dict API misuse in sales-analysis helpers

- Cluster frequency: `4/308` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `4/308` (`1.3%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x3, `110` x1
- Score distribution (top): `0.0` x3, `40.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `0383630b32414ae08b957f2f06d1d69c`, summary `Runtime Error`, score `40`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:

    sum=0
    for x in sales_data:
        if x['region']==region:
            sum+=x['revenue']
    return sum

def revenue_range_for_product(sales_data: list, product: str) -> int:
    dict={}
    for x in sales_data:
        if x['product']==product:
           dict[x['region']]=x['revenue']
    min=10000000
    max=0
    if dict=={}:
        return 0
    for i in dict.keys():
# ...
```

### Leaves the template placeholder `...` in `region_with_max_sales(...)` (partial multi-function implementation)

- Cluster frequency: `4/308` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `4/308` (`1.3%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `110` x2, `100` x1, `000` x1
- Score distribution (top): `40.0` x1, `20.0` x1, `0.0` x1, `60.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `8c38e8593bb24a7e84c34ebd67156c14`, summary `Wrong Answer`, score `60`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    n = len(sales_data)
    total = 0
    for i in range(n):
        if (sales_data[i])["region"] == region:
            total += (sales_data[i])["revenue"]
    return total


def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    n = len(sales_data)
    revenue=[]
    for i in range(n):
        if (sales_data[i])["product"] ==product:
            revenue.append((sales_data[i])["revenue"])
    if len(revenue)==1 or len(revenue) ==0:
# ...
```

### Runtime ValueError from malformed aggregation / conversion logic in sales-analysis helpers

- Cluster frequency: `4/308` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `4/308` (`1.3%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `010` x1, `110` x1, `000` x1, `100` x1
- Score distribution (top): `20.0` x2, `40.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `7872bff71c114c2097aa55aecb250c31`, summary `Runtime Error`, score `40`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    sum=0
    for dict in sales_data:
        if region== dict["region"]:
            sum+= int(dict["revenue"])

    return sum


def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    max_list=[]
    min_list=[]

    for dict in sales_data:
        if product==dict["product"]:
            if int(dict["revenue"]):
# ...
```

### Branch initialization bug in helper output variables before return

- Cluster frequency: `4/308` (`1.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `4/308` (`1.3%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2, `110` x2
- Score distribution (top): `0.0` x2, `40.0` x1, `60.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `cc24416bf34d4264847e28b91fd515b2`, summary `Runtime Error`, score `40`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    sum =0
    for i in range(len(sales_data)):
        if sales_data[i]['region']==region:
            sum+=sales_data[i]['revenue']
    return sum


def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    max=-99999
    min=99999
    for i in range(len(sales_data)):
        if(sales_data[i]['product']==product):
            if(sales_data[i]['revenue']>max):
                max=sales_data[i]['revenue']
            if(sales_data[i]['revenue']<min):
# ...
```

### Most sales-analysis helpers work, but one hidden edge-case remains (commonly region tie-break aggregation or exact set semantics)

- Cluster frequency: `3/308` (`1.0%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `3/308` (`1.0%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `111` x3
- Score distribution (top): `60.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `27850d1872c3425eb35e69116b9160d0`, summary `Wrong Answer`, score `60`, vector `111`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    return sum(record["revenue"] for record in sales_data if record["region"] == region)


def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    revenues = [record["revenue"] for record in sales_data if record["product"] == product]
    if not revenues:
        return 0
    if len(revenues) == 1:
        return 0
    return max(revenues) - min(revenues)


def region_with_max_sales(sales_data: list) -> str:
    """Region with highest total revenue; ties broken by total quantity_sold."""
    region_data = {}
# ...
```

### In `region_with_max_sales(...)`, compares individual records (or `revenue*quantity`) instead of aggregated totals per region

- Cluster frequency: `3/308` (`1.0%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `3/308` (`1.0%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `110` x1, `100` x1, `111` x1
- Score distribution (top): `80.0` x1, `20.0` x1, `60.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `2dc1c42bff304ca9b47eaf66fa96f585`, summary `Wrong Answer`, score `80`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    sum =0
    for data in sales_data:
        if data['region']== region:
            sum+=data['revenue']

    return sum



def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    revenue_list = []
    for data in sales_data:
        if data['product'] == product:
            revenue_list.append(data['revenue'])
    if revenue_list != []:
# ...
```

### In `steady_revenue_products(...)`, filters by per-record revenue `< 5000` instead of product revenue range `< 5000`

- Cluster frequency: `2/308` (`0.6%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `2/308` (`0.6%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `100` x1, `110` x1
- Score distribution (top): `20.0` x1, `60.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `a24d5f64d6274005a8e59a784b964c29`, summary `Wrong Answer`, score `60`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    total = 0
    for i in sales_data:
        if i['region']==region:
            total = total + i['revenue']
    return total

def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    sale = []
    max = 0
    min = 9999999999999999
    for i in sales_data:
        if i['product']==product:
            sale = sale + [i['revenue']]
    if len(sale) == 0 or len(sale) == 1:
        return 0
# ...
```

### Leaves the template placeholder `...` in `revenue_range_for_product(...)` (partial multi-function implementation)

- Cluster frequency: `2/308` (`0.6%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `2/308` (`0.6%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `110` x1, `000` x1
- Score distribution (top): `40.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `3883e1b6371c424184a7deb94947fdd8`, summary `Wrong Answer`, score `40`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    a =0
    for i in sales_data:
        if i['region'] == region:
            a = a+i['revenue']
    return a
    """Sum of revenue for the specified region."""

def revenue_range_for_product(sales_data: list, product: str) -> int:
    a=0
    max=0
    min = 0
    for i in sales_data:
        if i['product'] == product:
            if i['revenue']>max:
                max = i['revenue']
    min = max
    for i in sales_data:
# ...
```

### Sales-analysis helper logic is broadly incorrect across the required functions

- Cluster frequency: `2/308` (`0.6%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `2/308` (`0.6%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `99f5f03a58d74d6b92ad794559d1e312`, summary `Wrong Answer`, score `0`, vector `000`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""
    return(17000)
    return(0)
def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    return(5000)


def region_with_max_sales(sales_data: list) -> str:
    """Region with highest total revenue; ties broken by total quantity_sold."""
    return('R1')


def steady_revenue_products(sales_data: list) -> list:
    """Products whose revenue range is < 5000, sorted alphabetically."""
    dict={'Camera','Laptop','Phone','Tablet'}
    return(dict)
```

### Only `total_revenue_in_region(...)` is mostly correct; later sales-analysis helpers are incorrect/incomplete

- Cluster frequency: `2/308` (`0.6%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `2/308` (`0.6%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `100` x2
- Score distribution (top): `20.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `db89883f02994a7c9c49d6bf8b2a48e9`, summary `Wrong Answer`, score `20`, vector `100`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    total_revenue = 0
    for i in sales_data:
        if i["region"] == region:
            total_revenue += i["revenue"]
    return total_revenue


def revenue_range_for_product(sales_data: list, product: str) -> int:
    total_revenue = []
    n = 0
    max_revenue = 0
    min_revenue = 1000

    for i in sales_data:
        r = i["revenue"]
        if i["product"] == product:
            total_revenue.append(r)
# ...
```

### In `revenue_range_for_product(...)`, sums product revenues instead of returning `max(revenue) - min(revenue)`

- Cluster frequency: `1/308` (`0.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `1/308` (`0.3%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `100` x1
- Score distribution (top): `20.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `51cd897128174433a37f5a177d1e0cb3`, summary `Wrong Answer`, score `20`, vector `100`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    return sum(record['revenue'] for record in sales_data if record['region']==region)

def revenue_range_for_product(sales_data: list, product: str) -> int:
    return sum(record['revenue'] for record in sales_data if record['product']==product)
    if not revenue:
        return 0
    if len(revenue)==1:
        return 0
    return max(revenue)-min(revenue)
def region_with_max_sales(sales_data: list) -> str:
    """Region with highest total revenue; ties broken by total quantity_sold."""



def steady_revenue_products(sales_data: list) -> list:
    """Products whose revenue range is < 5000, sorted alphabetically."""
```

### In `total_revenue_in_region(...)`, compares the whole record to `region` instead of the record's `'region'` field

- Cluster frequency: `1/308` (`0.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `1/308` (`0.3%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `110` x1
- Score distribution (top): `60.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `8524e259e13f4339b6abcabe8867ff72`, summary `Wrong Answer`, score `60`, vector `110`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    """Sum of revenue for the specified region."""

    total = 0
    for item in sales_data:
        for key, value in item.items():
            if value ==region:
                total+=item['revenue']
    return total


def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    range = 0
    maxi = -1
    mini = 10000000
    for item in sales_data:
        for key, value in item.items():
# ...
```

### Reads input interactively inside helper functions instead of using the provided `sales_data` parameters

- Cluster frequency: `1/308` (`0.3%`)
- Variant frequencies:
  - `ns_25t3_py14_1/11`: `1/308` (`0.3%`)
  - `ns_25t3_py14_2/12`: `0/0` (`0.0%`)
- Dominant private-case vectors: `000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t3_py14_1/11`, Student ID `e5ef857e735a40d494591ed659add5e8`, summary `Runtime Error`, score `0`, vector `000`

```python
def total_revenue_in_region(sales_data: list, region: str) -> int:
    sales_data = []
    region = input()
    total_revenue_in_region = sales_data + region


def revenue_range_for_product(sales_data: list, product: str) -> int:
    """Maximum revenue minus minimum revenue for the given product."""
    ...


def region_with_max_sales(sales_data: list) -> str:
    """Region with highest total revenue; ties broken by total quantity_sold."""
    ...


def steady_revenue_products(sales_data: list) -> list:
    """Products whose revenue range is < 5000, sorted alphabetically."""
# ...
```
