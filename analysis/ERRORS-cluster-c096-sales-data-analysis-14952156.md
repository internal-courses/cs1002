# Error Patterns: Cluster C096 (`Sales Data Analysis`)

## Cluster Summary

- Cluster ID: `C096`
- Cluster title: `Sales Data Analysis`
- Cluster file (this file): `analysis/ERRORS-cluster-c096-sales-data-analysis-14952156.md`
- Variants in cluster: `1`
- Total final submitters across variants: `546`
- Total non-full final submissions across variants: `426`
- Canonical variant (by submissions): `ns_25t2_py22_1/19`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py22_1/19` (canonical) | 546 | 426 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py22_1/19.json`

## Cluster-Level Outcome Summary

- Final submitters: `546`
- Full pass: `120`
- Non-full final submissions: `426`
- Parseable non-full (logic/runtime focus): `362`
- Non-parseable non-full: `64`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py22_1/19` | 546 | 120 | 426 | 362 | 64 |

## Private Case Structure

- Private case 1: `total_revenue` over full and sliced transaction lists
- Private case 2: `product_wise_total_units_and_revenue` aggregation over repeated product IDs
- Private case 3: `top_selling_product` with unit-count tie broken by total revenue
- Private case 4: `average_product_price` as `total_revenue / total_units_sold` per product, rounded to 2 decimals

Private-case vectors in this report are 4-character pass/fail strings over the private case groups (e.g., `1001` marks pass/fail outcomes by private group order).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py22_1/19` |
| --- | ---: | ---: | ---: |
| Implements only the `total_revenue` task branch; other required task branches are missing | 71 | 16.7% | 71 |
| Syntax / non-parseable final submission | 64 | 15.0% | 64 |
| Computes average product price but does not round to 2 decimals | 45 | 10.6% | 45 |
| Implements only `total_revenue` + `product_wise_total_units_and_revenue` (top/average tasks missing) | 41 | 9.6% | 41 |
| Omits the `average_product_price` branch after implementing other sales-analysis tasks | 34 | 8.0% | 34 |
| No return / implicit `None` | 33 | 7.7% | 33 |
| Only one task branch is reliable; other sales-analysis branches are incomplete or hidden-case specific | 28 | 6.6% | 28 |
| Runtime NameError from misspelled helper/accumulator variables in task branches | 19 | 4.5% | 19 |
| Task dispatch and sales aggregation logic are broadly incorrect across all required tasks | 12 | 2.8% | 12 |
| Runtime TypeError | 11 | 2.6% | 11 |
| Runtime error (parseable final submission) | 10 | 2.3% | 10 |
| Task-dispatch string mismatch (branch names do not exactly match evaluator `task` values) | 9 | 2.1% | 9 |
| A branch-name mismatch leaves one required task unreachable while others are implemented | 7 | 1.6% | 7 |
| Runtime KeyError from wrong sales-record keys or malformed per-product summaries | 6 | 1.4% | 6 |
| Runtime TypeError from inconsistent summary container types (tuple/list/set mixups) | 6 | 1.4% | 6 |
| Aggregation helpers exist, but one advanced task (top-selling tie-break or average-price) is still wrong | 5 | 1.2% | 5 |
| Hard-codes public-sample product IDs (`P101/P102/P103`) so hidden product IDs fail | 5 | 1.2% | 5 |
| Average-price branch divides by zero because units are aggregated incorrectly for some products | 4 | 0.9% | 4 |
| Hard-codes the public sample size/positions (`sales_data[0]..[3]`) instead of aggregating arbitrary input length | 3 | 0.7% | 3 |
| Runtime ValueError | 3 | 0.7% | 3 |
| First three tasks mostly work, but `average_product_price` is incorrect on hidden cases | 3 | 0.7% | 3 |
| Runtime AttributeError | 2 | 0.5% | 2 |
| Runtime IndexError | 2 | 0.5% | 2 |
| Uses `set(product_id)` / fixed buckets for aggregation, leading to missing or unstable product summaries | 2 | 0.5% | 2 |
| Other wrong-answer logic pattern (residual) | 1 | 0.2% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `1/426` (`0.2%`)

### Implements only the `total_revenue` task branch; other required task branches are missing

- Cluster frequency: `71/426` (`16.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `71/426` (`16.7%`)
- Dominant private-case vectors: `0100` x57, `0000` x14
- Score distribution (top): `25.0` x57, `0.0` x14
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `afea0a243a5642679780d8b464c84eed`, summary `Wrong Answer`, score `25`, vector `0100`

```python
    if task=="total_revenue":
        total_revenue= sum(item['revenue']for item in sales_data)
        return total_revenue

    elif task=='product_wise':
        product_stats={}
        for item in sales_data:
            product_id=item['product_id']
            units=item['units_sold']
            revenue=item['revenue']
            if product_id not in product_stats:
                product_stats[product_id]={'total_units':0,'total_revenue':0}

            product_stats[product_id]['total_units'] += units
            product_stats[product_id]['total_revenue'] += revenue

        return product_stats
    ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `64/426` (`15.0%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `64/426` (`15.0%`)
- Dominant private-case vectors: `0000` x64
- Score distribution (top): `0.0` x64
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `37ed2d8f955c4f58baf8cefc3241dc20`, summary `Runtime Error`, score `0`, vector `0000`

```python
def analyse_sales_data(sales_data, task):
    if task == " total_revenue":
    total_revenue =sum(transactions['revenue']for transactions in sales_data)
    return total_revenue
    elif task =="product vise total units and revenue ":
        product_totals=={}
        for transactions in sales_data:
            product_id = transactions['product_id']
            units = transactions['units sold']
            revenue = transactions['revenue']
            if product_id not in product_totals:
                product_totals[product_id]=[0,0]
                product_totals[product_id][0] += units
                product_totals[product_id][1] += revenue
                return {pid:(totals[0],totals[1])for pid,totals in product_totals.items()}
                elif task == "top selling product":
                    product_totals={}
                    for transactionsin sales_data:
# ...
```

### Computes average product price but does not round to 2 decimals

- Cluster frequency: `45/426` (`10.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `45/426` (`10.6%`)
- Dominant private-case vectors: `0100` x18, `0111` x15, `0110` x8, `0000` x4
- Score distribution (top): `25.0` x18, `75.0` x15, `50.0` x8, `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `c21151481fe3489393293e8be2181c6c`, summary `Wrong Answer`, score `75`, vector `0111`

```python
    if(task=='total_revenue'):
        m=0
        for key in sales_data:
            m=m+key['revenue']
        return m
    if(task=='product_wise_total_units_and_revenue'):
        d={}
        s={}
        for key in sales_data:
            if(key['product_id'] in d ):
                continue
            else:
                d[key['product_id']]=0
        for key in sales_data:
            d[key['product_id']]+=key['units_sold']
        for key in sales_data:
            if(key['product_id'] in s ):
                continue
# ...
```

### Implements only `total_revenue` + `product_wise_total_units_and_revenue` (top/average tasks missing)

- Cluster frequency: `41/426` (`9.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `41/426` (`9.6%`)
- Dominant private-case vectors: `0100` x34, `0110` x4, `0000` x2, `0010` x1
- Score distribution (top): `25.0` x35, `50.0` x4, `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `a45b17ba134a4d9996248e04e78d4ef5`, summary `Wrong Answer`, score `25`, vector `0100`

```python
    if task == "total_revenue":
        all_sum = 0
        for product in sales_data:
            all_sum += product["revenue"]
        return all_sum
    if task == "product_wise_total_units_and_revenue":
        product_list = []
        for product in sales_data:
            product_list += product["product_id"]
        new_product_list = set(product_list)
        final_pro_list = list(product_list)
        units_sold = 0
        revenue = 0
        new_dict = {}
        new_list = []
        for product in final_pro_list :
            units_sold += int(product["units_sold"])
            revenue += int(product["revenue"])
# ...
```

### Omits the `average_product_price` branch after implementing other sales-analysis tasks

- Cluster frequency: `34/426` (`8.0%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `34/426` (`8.0%`)
- Dominant private-case vectors: `0100` x23, `0110` x7, `0000` x4
- Score distribution (top): `25.0` x23, `50.0` x7, `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `03312256bbf34432abd4a9b40d08ee9e`, summary `Wrong Answer`, score `25`, vector `0100`

```python
    def total_revenue():
        revenue=0
        for i in sales_data:
            revenue+=i["revenue"]
        return revenue
    def product_wise_total_units_and_revenue():
        d={}
        total_units1=0
        total_units2=0
        total_units3=0
        revenue1=0
        revenue2=0
        revenue3=0
        for i in sales_data:
            if i["product_id"]=="P101":
                total_units1+=i["units_sold"]
                revenue1+=i["revenue"]
            elif i["product_id"]=="P102":
# ...
```

### No return / implicit `None`

- Cluster frequency: `33/426` (`7.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `33/426` (`7.7%`)
- Dominant private-case vectors: `0000` x32, `0100` x1
- Score distribution (top): `0.0` x32, `25.0` x1
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `4ab72740a7ab4c419f81e8fadd963510`, summary `Wrong Answer`, score `0`, vector `0000`

```python
    sales_data = [
        {"product_id": "P101", "units_sold":120, "revenue":1000},
        {"product_id": "P102", "units_sold":30, "revenue":900},
{"product_id":"P103", "units_sold":120, "revenue":600},
]
```

### Only one task branch is reliable; other sales-analysis branches are incomplete or hidden-case specific

- Cluster frequency: `28/426` (`6.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `28/426` (`6.6%`)
- Dominant private-case vectors: `0100` x28
- Score distribution (top): `25.0` x27, `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `d642cd21b86c4a7d8883897772b4f036`, summary `Wrong Answer`, score `25`, vector `0100`

```python
    max_id = ''
    max_r = 0
    sum = maxi = 0
    items = []
    un_rev = []
    units = revenue = 0
    s = []
    for x in sales_data:
        for y in s:
            if x['product_id'] != y[0]:
                s.append([x['product_id'], x['units_sold'], x['revenue']])
            else:
                y[1] += x['units_sold']
                y[2] += x['revenue']
    if task == 'total_revenue':
        for i in sales_data:
            sum += i['revenue']
        return sum
# ...
```

### Runtime NameError from misspelled helper/accumulator variables in task branches

- Cluster frequency: `19/426` (`4.5%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `19/426` (`4.5%`)
- Dominant private-case vectors: `0000` x13, `0100` x5, `0110` x1
- Score distribution (top): `0.0` x13, `25.0` x5, `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `8f40b8aa682a433abe56ace1c3589c10`, summary `Runtime Error`, score `50`, vector `0110`

```python
    if task=="total_revenue":
        total=0
        for d in sales_data:
            amount=d["revenue"]
            total=total+amount
        return total
    if task=="product_wise_total_units_and_revenue":
        d={}
        for dictionary in sales_data:
            if dictionary["product_id"] in d:
                l=list(d[dictionary["product_id"]])
                l[0]+=dictionary["units_sold"]
                l[1]+=dictionary["revenue"]
                d[dictionary["product_id"]]=tuple(l)
            else:
                d[dictionary["product_id"]]=(dictionary["units_sold"],dictionary["revenue"])
        return d
    if task=="top_selling_product":
# ...
```

### Task dispatch and sales aggregation logic are broadly incorrect across all required tasks

- Cluster frequency: `12/426` (`2.8%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `12/426` (`2.8%`)
- Dominant private-case vectors: `0000` x12
- Score distribution (top): `0.0` x12
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `9a797f15134346dbb83a9d8e60392772`, summary `Wrong Answer`, score `0`, vector `0000`

```python
    product_totals={}
    for entry in sales_data:
        pid=entry['product_id']
        units=entry["units_sold"]
        rev=entry["revenue"]

        if pid not in product_totals:
            product_totals[pid] ={'units':0 ,"revenue":0}
        product_totals[pid]["units"]+=units
        product_totals[pid]["revenue"]+=rev


        if task == "total_revenue":
            return sum(e["revenue"] for e in product_totals.items())
        elif task== "product_wise_total_units_and_revenue" :
           return {pid:(vals["units"], vals["revenue"]) for pid, vals in product_totals.items()}

        elif task=="top_selling_product":
# ...
```

### Runtime TypeError

- Cluster frequency: `11/426` (`2.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `11/426` (`2.6%`)
- Dominant private-case vectors: `0000` x6, `0100` x4, `0110` x1
- Score distribution (top): `0.0` x6, `25.0` x4, `50.0` x1
- Interpretation: Type mismatch or invalid operation in the final code path.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `f5d7d933a08641be96d7710f93e7e5e7`, summary `Runtime Error`, score `25`, vector `0100`

```python
    if task == "total_revenue":
        return sum(item["revenue"] for item in sales_data)
    elif task =="product_wise_total_units_and_revenue":
        result = {}
        for item in sales_data:
            pid = item["product_id"]
            units = item["units_sold"]
            rev = item["revenue"]
            if pid not in result :
                result[pid] = (0, 0)
            total_units, total_rev = result[pid]
            result [pid] [0] += units
            result [pid] [1] += rev

    elif task == "top_selling_product":
        totals = {}
        for item in sales_data:
            pid = item["product_id"]
# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `10/426` (`2.3%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `10/426` (`2.3%`)
- Dominant private-case vectors: `0100` x7, `0000` x3
- Score distribution (top): `25.0` x7, `0.0` x3
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `52f1b2d7dc6b434d8b8d482ddfa400e4`, summary `Runtime Error`, score `25`, vector `0100`

```python
    if task == 'total_revenue':
        total=[]
        for item in sales_data:
            total.append(item['revenue'])
    return sum(total)
    if task=='top_selling_product':
        assumed= sales_data[0]
        for item in sales_data:
            if item['units_sold']>assumed['units_sold']:
                assumed=item
        if len(assumed['product_id'])>4:
            more_rev=assumed[0]
            for item in assumed:
                if item['revenue']>more_rev['revenue']:
                    more_rev=item
    return more_rev['product_id']
```

### Task-dispatch string mismatch (branch names do not exactly match evaluator `task` values)

- Cluster frequency: `9/426` (`2.1%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `9/426` (`2.1%`)
- Dominant private-case vectors: `0101` x4, `0100` x3, `0110` x1, `0111` x1
- Score distribution (top): `25.0` x3, `75.0` x3, `50.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `4e6a35863fae4fa5bb6ea38cd3e46133`, summary `Wrong Answer`, score `50`, vector `0110`

```python
    if task == "total_revenue":
        return sum(transaction['revenue'] for transaction in sales_data)

    elif task == "product_wise_total_units_and_revenue":
        product_totals = {}
        for transaction in sales_data:
            product_id = transaction['product_id']
            units = transaction['units_sold']
            revenue = transaction['revenue']

            if product_id in product_totals:
                product_totals[product_id] = (
                    product_totals[product_id][0]+ units,
                    product_totals[product_id][1]+ revenue
                )
            else:
                product_totals[product_id]= (units, revenue)

# ...
```

### A branch-name mismatch leaves one required task unreachable while others are implemented

- Cluster frequency: `7/426` (`1.6%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `7/426` (`1.6%`)
- Dominant private-case vectors: `0101` x7
- Score distribution (top): `50.0` x6, `75.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `267dce1af21846aa94896d1ab16a3429`, summary `Wrong Answer`, score `50`, vector `0101`

```python
    if (task == "total_revenue"):
        sum = 0
        for i in range (len(sales_data)):
            sum += sales_data[i]["revenue"]
        return (sum)
    if (task == "top_selling_product"):
        i_units = 0
        units = 0
        max = 0
        index = 0
        id = sales_data[0]["product_id"]
        for i in range (len(sales_data)):
            if (sales_data[i]["product_id"] != id):
                units = units + sales_data[i]["units_sold"]
                if (max < units):
                    max = units
                    index = i
                units = 0
# ...
```

### Runtime KeyError from wrong sales-record keys or malformed per-product summaries

- Cluster frequency: `6/426` (`1.4%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `6/426` (`1.4%`)
- Dominant private-case vectors: `0100` x3, `0000` x2, `0110` x1
- Score distribution (top): `25.0` x3, `0.0` x2, `75.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `23e5c711741740579db3c68b4a68631e`, summary `Runtime Error`, score `25`, vector `0100`

```python
    if task == "total_revenue":
        total = 0
        for K in sales_data:
            total+=K["revenue"]
        return total
    elif task=="product_wise_total_units_and_revenue":

        for i in range(len(sales_data)):
            for j in range(len(sales_data)):
                if (sales_data[i]["product_id"] == sales_data[j]["product_id"]):
                    if (sales_data[i]["units_sold"] != sales_data[j]["units_sold"]):
                        sales_data[i]["units_sold"] += sales_data[j]["units_sold"]
                        sales_data[i]["revenue"] += sales_data[j]["revenue"]
                        del(sales_data[j])
                        Final = { j["product_id"]: (j["units_sold"],j["revenue"]) for j in sales_data}
                        return Final


# ...
```

### Runtime TypeError from inconsistent summary container types (tuple/list/set mixups)

- Cluster frequency: `6/426` (`1.4%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `6/426` (`1.4%`)
- Dominant private-case vectors: `0100` x3, `0110` x2, `0111` x1
- Score distribution (top): `75.0` x2, `50.0` x2, `25.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `7582d2a7e8494eeaae2d8e1acac7b687`, summary `Runtime Error`, score `50`, vector `0100`

```python
    if task =="total_revenue":
        total_revenue= 0
        for dictionary in sales_data :
            total_revenue+=dictionary["revenue"]
        return total_revenue
    if task =="product_wise_total_units_and_revenue":
        dictionarytoreturn =dict({})
        for dictionary in sales_data:
            if dictionary["product_id"] not in dictionarytoreturn:
                dictionarytoreturn[dictionary["product_id"]]=list([dictionary["units_sold"],dictionary["revenue"]])
            else:
                dictionarytoreturn[dictionary["product_id"]][0]+=dictionary["units_sold"]
                dictionarytoreturn[dictionary["product_id"]][1]+=dictionary["revenue"]
                dictionarytoreturn[dictionary["product_id"]]=tuple(dictionarytoreturn[dictionary["product_id"]])
        for dictionary in sales_data:
            dictionarytoreturn[dictionary["product_id"]]=tuple(dictionarytoreturn[dictionary["product_id"]])
        return dictionarytoreturn
    if task == "top_selling_product":
# ...
```

### Aggregation helpers exist, but one advanced task (top-selling tie-break or average-price) is still wrong

- Cluster frequency: `5/426` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `5/426` (`1.2%`)
- Dominant private-case vectors: `0110` x5
- Score distribution (top): `50.0` x3, `75.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `09ede8614a374ef78ba5cdc9d17a03a8`, summary `Wrong Answer`, score `50`, vector `0110`

```python
    ...
    total_revenue = 0
    product_wise_total_units_and_revenue = {}
    top_selling_product = ""
    average_product_price = {}
    for d in sales_data:
        total_revenue += d["revenue"]
        avg = 0
        units = 0
        revenue = 0
        #product_wise_total_units_and_revenue.update({d["product_id"]:(d["units_sold"],d["revenue"])})
        #average_product_price.update({d["product_id"]:round((d["revenue"]/d["units_sold"]) * 100) // 100})
        for dd in sales_data:
            if dd["product_id"] == d["product_id"]:
                units += dd["units_sold"]
                revenue += dd["revenue"]
                avg += round((d["revenue"]/d["units_sold"]) * 100) / 100
        product_wise_total_units_and_revenue.update({d["product_id"]:(units, revenue)})
# ...
```

### Hard-codes public-sample product IDs (`P101/P102/P103`) so hidden product IDs fail

- Cluster frequency: `5/426` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `5/426` (`1.2%`)
- Dominant private-case vectors: `0100` x4, `0111` x1
- Score distribution (top): `25.0` x4, `75.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `4346aa027ba84b5892397166af5dff4c`, summary `Wrong Answer`, score `25`, vector `0100`

```python
    if task == "total_revenue":
        total = 0
        for i in range(len(sales_data)):
            total += sales_data[i]['revenue']
        return total
    if task == "product_wise_total_units_and_revenue":
        revt = 0
        ust = 0
        revt1 = 0
        revt2 = 0
        ust1 = 0
        ust2 = 0
        dic = {}
        for i in range(len(sales_data)):
            if sales_data[i]['product_id'] == "P101":
                revt += sales_data[i]['revenue']
                ust += sales_data[i]['units_sold']
                dic['P101'] = (ust,revt)
# ...
```

### Average-price branch divides by zero because units are aggregated incorrectly for some products

- Cluster frequency: `4/426` (`0.9%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `4/426` (`0.9%`)
- Dominant private-case vectors: `0100` x4
- Score distribution (top): `25.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `6cd611adba454e63a973bb0679f49e6c`, summary `Runtime Error`, score `25`, vector `0100`

```python
    if task=="total_revenue":
        sum=0
        for i in range(len(sales_data)):
            sum+=sales_data[i]["revenue"]
        return sum
        #return sales_data[0]["revenue"]+ sales_data[1]["revenue"] + sales_data[2]["revenue"] + sales_data[3]["revenue"]
    elif task=="product_wise_total_units_and_revenue":

        usp101=0; usp102=0; usp103=0; r101=0; r102=0; r103=0
        for i in range(len(sales_data)):
            if sales_data[i]["product_id"]=='P101':
                usp101+=sales_data[i]["units_sold"]
                r101+=sales_data[i]["revenue"]
            elif sales_data[i]["product_id"]=='P102':
                usp102+=sales_data[i]["units_sold"]
                r102+=sales_data[i]["revenue"]
            elif sales_data[i]["product_id"]=='P103':
                usp103+=sales_data[i]["units_sold"]
# ...
```

### Hard-codes the public sample size/positions (`sales_data[0]..[3]`) instead of aggregating arbitrary input length

- Cluster frequency: `3/426` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `3/426` (`0.7%`)
- Dominant private-case vectors: `0100` x2, `0000` x1
- Score distribution (top): `25.0` x2, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `df165db3f3ab4dce92507c9b37b36f00`, summary `Wrong Answer`, score `25`, vector `0100`

```python
    def total_revenue(sales_data):
        result=[]
        for d in sales_data:
            result.append(d['revenue'])
        s=sum(result)
        return s
    def product_wise_total_units_and_revenue(sales_data):
        result={}

        d1=sales_data[0]
        d2=sales_data[1]
        d3=sales_data[2]
        d4=sales_data[3]
        lst=[d1['product_id'],d2['product_id'],d3['product_id'],d4['product_id']]
        for i in lst:
            if lst.count(i)>1:
                if d1['product_id']==d2['product_id']:
                    result[d1['product_id']]=(d1['units_sold']+d2['units_sold'],d1['revenue']+d2['revenue'])
# ...
```

### Runtime ValueError

- Cluster frequency: `3/426` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `3/426` (`0.7%`)
- Dominant private-case vectors: `0000` x2, `0101` x1
- Score distribution (top): `0.0` x2, `75.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `ea36c4714a574666ba73b34c0f7caaf7`, summary `Runtime Error`, score `75`, vector `0101`

```python
    product_summary=defaultdict(lambda:[0,0])
    for transaction in sales_data:
        pid=transaction['product_id']
        units=transaction['units_sold']
        rev=transaction['revenue']
        product_summary[pid][0]+=units
        product_summary[pid][1]+=rev
    if task=="total_revenue":
        return sum(transaction['revenue'] for transaction in sales_data)
    elif task=="product_wise_total_units_and revenue":
        return {pid:(vals[0],vals[1]) for pid,vals in product_summary.items()}
    elif task=="top_selling_product":
        max_units= -1
        top_product=None
        for pid,(units,rev) in product_summary.items():
            if units > max_units or (units==max_units and rev>product_summary[top_product][1]):
                max_units=units
                top_product=pid
# ...
```

### First three tasks mostly work, but `average_product_price` is incorrect on hidden cases

- Cluster frequency: `3/426` (`0.7%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `3/426` (`0.7%`)
- Dominant private-case vectors: `0111` x3
- Score distribution (top): `75.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `c88f875d131a483e92af8f7448209644`, summary `Wrong Answer`, score `75`, vector `0111`

```python
    if task=="total_revenue":
        amount=0
        for i in sales_data:
            amount+=i['revenue']
        return amount

    elif task=="product_wise_total_units_and_revenue":
        tot={}
        for i in sales_data:
            product=i['product_id']
            if product in tot:
                unit,revenue=tot[product]
                unit+=i['units_sold']
                revenue+=i['revenue']
                tot[product]=(unit,revenue)
            else:
                tot[product]=(i['units_sold'],i['revenue'])
        return tot
# ...
```

### Runtime AttributeError

- Cluster frequency: `2/426` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `2/426` (`0.5%`)
- Dominant private-case vectors: `0110` x1, `0000` x1
- Score distribution (top): `50.0` x1, `0.0` x1
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `2d7d5df538e14ec8b1c26234b928e991`, summary `Runtime Error`, score `50`, vector `0110`

```python
    if task=='total_revenue':
        sum=0
        for data in sales_data:
            sum+=data["revenue"]
        return sum
    if task=='product_wise_total_units_and_revenue':
        d={}
        for data in sales_data:
            if data["product_id"] in d:
                new_unit=d[data["product_id"]][0]+data["units_sold"]
                new_revenue=d[data["product_id"]][1]+data["revenue"]
                d[data["product_id"]]=new_unit,new_revenue
            else:
                d[data["product_id"]]=data["units_sold"],data["revenue"]
        return d
    if task=='top_selling_product':
        d={}
        for data in sales_data:
# ...
```

### Runtime IndexError

- Cluster frequency: `2/426` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `2/426` (`0.5%`)
- Dominant private-case vectors: `0110` x1, `0000` x1
- Score distribution (top): `75.0` x1, `0.0` x1
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `a6bd465c79e0413cac4c75c62c9a7229`, summary `Runtime Error`, score `75`, vector `0110`

```python
    if(task=="total_revenue"):
        ans=0
        for i in sales_data:
            ans=ans+i["revenue"]
        return ans
    if(task=="product_wise_total_units_and_revenue"):
        d={}
        ans={}
        for i in sales_data:
            d[i["product_id"]]=[0,0]

        for i in sales_data:
            d[i["product_id"]][0]+=i["units_sold"]
            d[i["product_id"]][1]+=i["revenue"]
        for i  in d:
            ans[i]=tuple(d[i])
        return ans
    if(task=="average_product_price"):
# ...
```

### Uses `set(product_id)` / fixed buckets for aggregation, leading to missing or unstable product summaries

- Cluster frequency: `2/426` (`0.5%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `2/426` (`0.5%`)
- Dominant private-case vectors: `0110` x1, `0111` x1
- Score distribution (top): `75.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `bfda608629354f0db0f7fc139b13a5c0`, summary `Wrong Answer`, score `75`, vector `0110`

```python
    if task == "total_revenue":
        revenue = 0
        total_revenue = 0
        for i in sales_data:
            # revenue = i['units_sold']*i['revenue']
            total_revenue += i['revenue']
        return total_revenue
    if task == "product_wise_total_units_and_revenue":
        list1 = []
        for i in sales_data:
            a = i['product_id']
            list1.append(a)
        set1 = set(list1)
        list2 = list(set1)
        d = {}
        unit_sold1 = 0
        unit_sold2 = 0
        unit_sold3 = 0
# ...
```

### Other wrong-answer logic pattern (residual)

- Cluster frequency: `1/426` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py22_1/19`: `1/426` (`0.2%`)
- Dominant private-case vectors: `0001` x1
- Score distribution (top): `25.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py22_1/19`, Student ID `81a2b81634094ea999334177bd23c562`, summary `Wrong Answer`, score `25`, vector `0001`

```python
    ...
    if task=="product_total_units":
        total_units={}
        for sale in sales_data:
            piv=sale["product_id"]
            units=sale["units_sold"]
            total_units[piv]=total_units.get(pid,0)+units
        return total_units
    elif task=="product_total_revenue":
        total_rev={}
        for sale in sales_data:
            piv=sale["product_id"]
            revenue=sale["units_sold"]*sale["unit_price"]
            total_rev[piv]=total_rev.get(pid,0)+revenue
        return total_rev
    elif task=="total_revenue":
        return sum(sale["units_sold"]*sale["unit_price"] for sale in sales_data)
    elif task=="top_selling_product":
# ...
```
