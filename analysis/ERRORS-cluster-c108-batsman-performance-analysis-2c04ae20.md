# Error Patterns: Cluster C108 (`Batsman Performance Analysis`)

## Cluster Summary

- Cluster ID: `C108`
- Cluster title: `Batsman Performance Analysis`
- Cluster file (this file): `analysis/ERRORS-cluster-c108-batsman-performance-analysis-2c04ae20.md`
- Variants in cluster: `1`
- Total final submitters across variants: `362`
- Total non-full final submissions across variants: `339`
- Canonical variant (by submissions): `ns_25t2_py13_1/12`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py13_1/12` (canonical) | 362 | 339 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py13_1/12.json`

## Cluster-Level Outcome Summary

- Final submitters: `362`
- Full pass: `23`
- Non-full final submissions: `339`
- Parseable non-full (logic/runtime focus): `276`
- Non-parseable non-full: `63`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py13_1/12` | 362 | 23 | 339 | 276 | 63 |

## Private Case Structure

- Private case 1: `overall_run_stats(...)` on a larger hidden dataset (flatten-all-years min/max/total/rounded average)
- Private case 2: `century_rate(...)` hidden year lists including exact-100 boundary cases (`>= 100` required)
- Private case 3: `average_yearly_century_rate(...)` must average per-year century rates (not global century percentage)
- Private case 4: `years_with_more_than_average_yearly_century_rate(...)` strict `>` comparison and set return type
- Private case 5: `year_with_most_average_runs(...)` tie handling via earliest year on equal average runs

Private-case vectors in this report are 5-character pass/fail strings over the private case groups (e.g., `10001` marks pass/fail outcomes by private group order).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py13_1/12` |
| --- | ---: | ---: | ---: |
| Leaves template placeholders (`...`) in multiple required helper functions (partial multi-function implementation) | 105 | 31.0% | 105 |
| Syntax / non-parseable final submission | 63 | 18.6% | 63 |
| No return / implicit `None` | 47 | 13.9% | 47 |
| In `average_yearly_century_rate(...)`, uses the sample variable `data` instead of the parameter `batsman_data` | 21 | 6.2% | 21 |
| Leaves the template placeholder `...` in `year_with_most_average_runs(...)` (partial multi-function implementation) | 9 | 2.7% | 9 |
| Uses the sample global variable `data` inside helper functions instead of the provided parameters | 9 | 2.7% | 9 |
| Hard-codes the public sample overall stats dictionary (`112/157/66/2456`) instead of computing from `batsman_data` | 9 | 2.7% | 9 |
| In `century_rate(...)`, truncates the percentage with `int(...)` instead of rounding | 8 | 2.4% | 8 |
| Runtime TypeError from mixing years/lists/scalars while aggregating runs or rates | 8 | 2.4% | 8 |
| In `years_with_more_than_average_yearly_century_rate(...)`, uses the sample variable `data` instead of `batsman_data` | 8 | 2.4% | 8 |
| Uses the sample global variable `data` inside helper functions instead of the function parameter | 7 | 2.1% | 7 |
| In `overall_run_stats(...)`, treats `batsman_data` as flat values/list-of-lists instead of flattening all runs across years | 6 | 1.8% | 6 |
| Runtime NameError from undefined accumulators/temporaries in one or more helper functions | 6 | 1.8% | 6 |
| In `average_yearly_century_rate(...)`, computes a global century percentage over all matches instead of averaging per-year century rates | 4 | 1.2% | 4 |
| Batsman-analysis helper logic is broadly incorrect across the five required functions | 4 | 1.2% | 4 |
| Leaves the template placeholder `...` in `years_with_more_than_average_yearly_century_rate(...)` (partial multi-function implementation) | 4 | 1.2% | 4 |
| Treats `batsman_data` as a flat list (or list of scalars) instead of flattening the per-year run lists | 3 | 0.9% | 3 |
| Treats helper inputs as the wrong shape (e.g., `runs.values()` / `batsman_data.value()`), causing dict/list API AttributeErrors | 2 | 0.6% | 2 |
| Copies evaluator/sample dataset and `is_equal(...)` checks into the submission instead of implementing the five helpers | 2 | 0.6% | 2 |
| Branch initialization bug in helper output variables (`result`/`year`/`max`) before returning | 2 | 0.6% | 2 |
| Leaves the template placeholder `...` in `overall_run_stats(...)` (partial multi-function implementation) | 2 | 0.6% | 2 |
| Leaves the template placeholder `...` in `century_rate(...)` (partial multi-function implementation) | 2 | 0.6% | 2 |
| In `years_with_more_than_average_yearly_century_rate(...)`, uses `>=` instead of strict `>` | 1 | 0.3% | 1 |
| Later helpers mostly work, but one early helper (`overall_run_stats` or `century_rate`) still has hidden edge-case semantics wrong | 1 | 0.3% | 1 |
| Implements only a subset of the required helper functions (one or more named functions are missing) | 1 | 0.3% | 1 |
| Uses fixed year keys / nested-dict assumptions that do not match the hidden batsman data shape | 1 | 0.3% | 1 |
| Runtime error (parseable final submission) | 1 | 0.3% | 1 |
| Leaves the template placeholder `...` in `average_yearly_century_rate(...)` (partial multi-function implementation) | 1 | 0.3% | 1 |
| Partial multi-helper implementation: some helper functions are correct, but one or more required helpers still have logic/edge-case bugs | 1 | 0.3% | 1 |
| Runtime AttributeError from dict/list API misuse across the batsman-analysis helper functions | 1 | 0.3% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/339` (`0.0%`)

### Leaves template placeholders (`...`) in multiple required helper functions (partial multi-function implementation)

- Cluster frequency: `105/339` (`31.0%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `105/339` (`31.0%`)
- Dominant private-case vectors: `00000` x54, `00010` x30, `00100` x7, `00110` x7
- Score distribution (top): `0.0` x54, `20.0` x37, `40.0` x7, `80.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `2974bd42228e4d9098ee5bd15978b906`, summary `Wrong Answer`, score `20`, vector `00010`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    sum=0
    max=0
    min=1000
    num=0
    for k in batsman_data.keys():
        for i in batsman_data[k]:

            sum+=i
            if(i>max):
                max=i
            if(i<min):
                min=i
            num+=1
    dic={'average':(int(sum/num)+1),'max':max,'min':min,'total':sum}
    return(dic)
    ...
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `63/339` (`18.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `63/339` (`18.6%`)
- Dominant private-case vectors: `00000` x63
- Score distribution (top): `0.0` x63
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `893505d5e44746be87b9a83d00ff6476`, summary `Runtime Error`, score `0`, vector `00000`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    ...


def century_rate(runs:list) -> int:
    """Returns the century rate from the given runs

    century_rate = n_centuries / n_matches * 100

    Century is assumed when the runs scored is greater than or equal to 100.

    Args:
        runs (list): Runs scored in different matches.

    Returns:
        int: Century Rate rounded to nearest integer.
    """
# ...
```

### No return / implicit `None`

- Cluster frequency: `47/339` (`13.9%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `47/339` (`13.9%`)
- Dominant private-case vectors: `00000` x47
- Score distribution (top): `0.0` x47
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `9465c06ed96c4f0191b52e7e734cf349`, summary `Wrong Answer`, score `0`, vector `00000`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    ...
    n=len(batsman_data)
    min_run=min(batsman_data)
    max_run=max(batsman_data)
    total_run=sum(batsman_data)
    average_run=sum(batsman_data)/n
    dict={"min":min_run , "max":max_run, "total":total_run, "average":average_run}


def century_rate(runs:list) -> int:
    """Returns the century rate from the given runs.

    century_rate = n_centuries / n_matches * 100

    Century is assumed when the runs scored is greater than or equal to 100.

# ...
```

### In `average_yearly_century_rate(...)`, uses the sample variable `data` instead of the parameter `batsman_data`

- Cluster frequency: `21/339` (`6.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `21/339` (`6.2%`)
- Dominant private-case vectors: `00111` x16, `00110` x4, `00011` x1
- Score distribution (top): `80.0` x16, `40.0` x3, `60.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `4dabe7945d8544888c811c9682aca10e`, summary `Wrong Answer`, score `80`, vector `00111`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    min = 1000
    max = 0
    total = 0
    no_of_games = 0
    for year, runs_in_year in batsman_data.items():
        for run in runs_in_year:
            if run > max:
                max = run
            if run < min:
                min = run
        total += sum(runs_in_year)
        no_of_games += len(runs_in_year)
    average = int(round(total/no_of_games))
    new_dict = {"min": min, "max": max, "total": total, "average": average}
    return new_dict

# ...
```

### Leaves the template placeholder `...` in `year_with_most_average_runs(...)` (partial multi-function implementation)

- Cluster frequency: `9/339` (`2.7%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `9/339` (`2.7%`)
- Dominant private-case vectors: `00110` x3, `00111` x2, `00000` x2, `00010` x2
- Score distribution (top): `40.0` x3, `60.0` x2, `0.0` x2, `20.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `b1c578cd041647b18534186703a1ad86`, summary `Wrong Answer`, score `60`, vector `00111`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""

    years = batsman_data.keys()
    scores=[]
    for i in years:
        for j in batsman_data[i]:
            scores.append(j)

    minim = min(scores)
    maxim = max(scores)
    total = sum(scores)
    average1 = total/len(scores)

    out={}
    out['average'] = round(average1)
    out['max'] = maxim
    out['min'] = minim
# ...
```

### Uses the sample global variable `data` inside helper functions instead of the provided parameters

- Cluster frequency: `9/339` (`2.7%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `9/339` (`2.7%`)
- Dominant private-case vectors: `00111` x3, `00010` x2, `00110` x2, `00000` x1
- Score distribution (top): `80.0` x3, `40.0` x3, `20.0` x2, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `80b27ddd1b704599a0e41b0f513b3a6c`, summary `Wrong Answer`, score `40`, vector `00110`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    overall_stats = {}
    total = 0
    minimum = 1000
    maximum = 0
    matches_played = 0

    for year in data:
        for each_score in data[year]:
            total = total+ each_score
            if(each_score < minimum):
                minimum = each_score
            if(each_score > maximum):
                maximum = each_score
            matches_played = matches_played +1
    average = total/matches_played
    overall_stats['average'] = round(average)
# ...
```

### Hard-codes the public sample overall stats dictionary (`112/157/66/2456`) instead of computing from `batsman_data`

- Cluster frequency: `9/339` (`2.7%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `9/339` (`2.7%`)
- Dominant private-case vectors: `00000` x9
- Score distribution (top): `0.0` x9
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `7f2b62c2d81146caa1f1e61c2f5cedd2`, summary `Wrong Answer`, score `0`, vector `00000`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""

    return{
        'average':112,
        'max':157,
        'min':66,
        'total':2456
    }


def century_rate(runs:list) -> int:
    """Returns the century rate from the given runs.

    century_rate = n_centuries / n_matches * 100

    Century is assumed when the runs scored is greater than or equal to 100.

# ...
```

### In `century_rate(...)`, truncates the percentage with `int(...)` instead of rounding

- Cluster frequency: `8/339` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `8/339` (`2.4%`)
- Dominant private-case vectors: `00000` x2, `00111` x2, `00010` x2, `00100` x1
- Score distribution (top): `20.0` x3, `0.0` x2, `80.0` x2, `40.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `2f8e9a47942c4e8da3b9b7a6c4611df7`, summary `Wrong Answer`, score `20`, vector `00010`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    su=0
    c=0
    ma=0
    mi=100000
    for i in batsman_data.values():
        for j in i:
            su=su+j
            c=c+1
        if(ma<max(i)):
            ma=max(i)
        if(mi>min(i)):
            mi=min(i)
    if(su%c==0):
        avg=int(su/c)
    elif(su%c>=5):
        avg=int(su//c)+1
# ...
```

### Runtime TypeError from mixing years/lists/scalars while aggregating runs or rates

- Cluster frequency: `8/339` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `8/339` (`2.4%`)
- Dominant private-case vectors: `00000` x3, `00110` x2, `00100` x1, `00111` x1
- Score distribution (top): `40.0` x3, `0.0` x3, `80.0` x1, `20.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `bc54b6f07b1f4022bc95a5e79809f83b`, summary `Runtime Error`, score `80`, vector `00111`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    d ={}
    max = 0
    min = 10000
    total = 0
    num = 0
    for runs in batsman_data.values():
        for run in runs:
            if run > max:
                max = run
            if run < min:
                min = run
            total += run
            num +=1
    average = total/num
    d["max"]=max
    d["min"]= min
# ...
```

### In `years_with_more_than_average_yearly_century_rate(...)`, uses the sample variable `data` instead of `batsman_data`

- Cluster frequency: `8/339` (`2.4%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `8/339` (`2.4%`)
- Dominant private-case vectors: `00111` x6, `00000` x1, `00010` x1
- Score distribution (top): `80.0` x6, `0.0` x1, `20.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `9dc665c9215d442898e5017077e5f4b5`, summary `Wrong Answer`, score `80`, vector `00111`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    d={}
    maximum=0
    minimum=1000
    for _ in batsman_data.keys():
        for value in batsman_data[_]:
            if value<minimum:
                minimum=value
    d['min']=minimum
    for _ in batsman_data.keys():
        for value in batsman_data[_]:
            if value>maximum:
                maximum=value
    d['max']=maximum
    summation=0
    for _ in batsman_data.keys():
        for value in batsman_data[_]:
# ...
```

### Uses the sample global variable `data` inside helper functions instead of the function parameter

- Cluster frequency: `7/339` (`2.1%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `7/339` (`2.1%`)
- Dominant private-case vectors: `00111` x2, `00000` x2, `00100` x1, `00110` x1
- Score distribution (top): `60.0` x3, `20.0` x3, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `e630f84ed8e64c4899e1bbede6647941`, summary `Runtime Error`, score `20`, vector `00010`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    a={}
    maxi = batsman_data[2016]
    mini = batsman_data[2016]
    total = 0
    len = 0
    for i in batsman_data:
        """for j in i:
            total = total + j
            if maxi>j:
                maxi = j
            if mini< j:
                mini = j
    len = len + len(batsman_data[i])
    avg = total/len"""
    #a.append("max")=maxi
    #a.append("min")= mini
# ...
```

### In `overall_run_stats(...)`, treats `batsman_data` as flat values/list-of-lists instead of flattening all runs across years

- Cluster frequency: `6/339` (`1.8%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `6/339` (`1.8%`)
- Dominant private-case vectors: `00111` x3, `00110` x2, `00010` x1
- Score distribution (top): `80.0` x3, `40.0` x2, `20.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `223f0d3b90a04c1e91cee7df1c83aff0`, summary `Wrong Answer`, score `80`, vector `00111`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    d={}
    total=0
    avg=0
    maxRun=0
    minRun=10000
    num=0
    for i in batsman_data:
        for j in batsman_data[i]:
            if (j>maxRun):
                maxRun=j
            if (j<minRun):
                minRun=j
            num+=1
            total+=j
    avg=round(total/num)
    d['min']=minRun
# ...
```

### Runtime NameError from undefined accumulators/temporaries in one or more helper functions

- Cluster frequency: `6/339` (`1.8%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `6/339` (`1.8%`)
- Dominant private-case vectors: `00000` x6
- Score distribution (top): `0.0` x6
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `f14645d55837451d94a7afc5615ca1b7`, summary `Runtime Error`, score `0`, vector `00000`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    ...
    return video.get("likes", 0) + video.get("comments", 0)

def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    ...
    views = video.get("views", 0)
    if views == 0:
        return 0.0
    rate = (video.get("likes", 0) + video.get("comments", 0)) / views * 100
    return round(rate, 2)

def most_engaging_video(videos: list) -> str:
    """Returns the title of the video with the highest engagement rate. Returns the first in case of tie."""
    ...
    max_rate = -1
# ...
```

### In `average_yearly_century_rate(...)`, computes a global century percentage over all matches instead of averaging per-year century rates

- Cluster frequency: `4/339` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `4/339` (`1.2%`)
- Dominant private-case vectors: `00110` x2, `00111` x2
- Score distribution (top): `80.0` x2, `60.0` x1, `40.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `7dfae24614ba44e7866e78325cd4c1de`, summary `Wrong Answer`, score `40`, vector `00110`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    d={'average':0,'max':0,'min':1000,'total':0}
    tot=0
    n=0
    for i in batsman_data:
        d['total']+= sum(batsman_data[i])
        n+= len(batsman_data[i])
        for j in batsman_data[i]:
            if j < d['min']:
                d['min']=j
            if j>d['max']:
                d['max']=j
            tot+=j
    d['average']=int(round(tot/n,0))
    return d

def century_rate(runs:list) -> int:
# ...
```

### Batsman-analysis helper logic is broadly incorrect across the five required functions

- Cluster frequency: `4/339` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `4/339` (`1.2%`)
- Dominant private-case vectors: `00000` x4
- Score distribution (top): `0.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `fe04254019c34dfbad02c01cfc5f1da2`, summary `Wrong Answer`, score `0`, vector `00000`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    for i in batsman_data:
        a = (" 'average' = 122")
        b = (" 'max': 157")
        c = (" 'min': 66")
        d = (" 'total': 2456")
        e = {a, b, c, d}
        return(e)


def century_rate(runs:list) -> int:
    """Returns the century rate from the given runs.

    century_rate = n_centuries / n_matches * 100

    Century is assumed when the runs scored is greater than or equal to 100.

# ...
```

### Leaves the template placeholder `...` in `years_with_more_than_average_yearly_century_rate(...)` (partial multi-function implementation)

- Cluster frequency: `4/339` (`1.2%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `4/339` (`1.2%`)
- Dominant private-case vectors: `00010` x2, `00111` x1, `00000` x1
- Score distribution (top): `20.0` x2, `60.0` x1, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `5ca88b8e4d1f485791cace7f65d62179`, summary `Wrong Answer`, score `60`, vector `00111`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""

    result1={}
    min_run=1000
    max_run=0
    total_all=0
    len_list=0
    for each in batsman_data:
        year_run=batsman_data[each]

        total_all+=sum(year_run)
        len_list+=len(year_run)

        if max(year_run)>max_run:
            max_run= max(year_run)

        if min(year_run)<min_run:
# ...
```

### Treats `batsman_data` as a flat list (or list of scalars) instead of flattening the per-year run lists

- Cluster frequency: `3/339` (`0.9%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `3/339` (`0.9%`)
- Dominant private-case vectors: `00010` x2, `00000` x1
- Score distribution (top): `20.0` x2, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `a4d925cccc6a44de8995b7353f419418`, summary `Runtime Error`, score `20`, vector `00010`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    total=0
    count=0
    l=batsman_data.values()
    for i in batsman_data:
        total+=sum(batsman_data[i])
        count+=len(batsman_data[i])
    average=round(total/count)
    maximum=max(l)
    minimum=min(l)
    data={}
    data["average"]=average
    data["max"]=max(maximum)
    data["min"]=min(minimum)
    data["total"]=total
    return data

# ...
```

### Treats helper inputs as the wrong shape (e.g., `runs.values()` / `batsman_data.value()`), causing dict/list API AttributeErrors

- Cluster frequency: `2/339` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `2/339` (`0.6%`)
- Dominant private-case vectors: `00010` x1, `00100` x1
- Score distribution (top): `20.0` x1, `40.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `329774028f8043d293ecaed8ed3f094f`, summary `Runtime Error`, score `40`, vector `00100`

```python
def overall_run_stats(batsman_data:list) -> dict:
    all_runs = [run for year_runs in batsman_data.values() for run in year_runs]
    return{
        'min': min(all_runs),
        'max': max(all_runs),
        'total': sum(all_runs),
        'average': round(sum(all_runs)/len(all_runs))
    }
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    ...


def century_rate(runs:list) -> int:
    total_matches = 0
    total_centuries = 0
    for runs in runs.values():
        total_matches += len(runs)
        total_centuries += sum(1 for run in runs if run >= 100)
# ...
```

### Copies evaluator/sample dataset and `is_equal(...)` checks into the submission instead of implementing the five helpers

- Cluster frequency: `2/339` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `2/339` (`0.6%`)
- Dominant private-case vectors: `00000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `1fbe65fefadd49df8475878f6c963861`, summary `Wrong Answer`, score `0`, vector `00000`

```python
def overall_run_stats(batsman_data:list) -> dict:
    data={
        2016:[88,66,130,122,117,95,86],
        2017:[149,66,110],
        2018:[157,84],
        2019:[148,127,71,117],
        2020:[91,156,80,135,152,109]
    }
    batsman_data= data[2016]+data[2017]+data[2018]+data[2019]+data[2020]
    bats= sorted(batsman_data)
    mi=bats[0]
    ma=bats[-1]
    tot=0
    for x in bats:
        tot+=x
    avg=round(tot/len(bats))
    key=['average','max','min','total']
    val=[avg,ma,mi,tot]
# ...
```

### Branch initialization bug in helper output variables (`result`/`year`/`max`) before returning

- Cluster frequency: `2/339` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `2/339` (`0.6%`)
- Dominant private-case vectors: `00111` x1, `00110` x1
- Score distribution (top): `80.0` x1, `40.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `adc7bb30cdf846f28fd213a4e0f56fec`, summary `Runtime Error`, score `40`, vector `00110`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    d={}
    min=99999999999
    max=0
    sum=0
    total=0
    for year in batsman_data:
        for i in range(len(batsman_data[year])):
            if batsman_data[year][i]<min:
                min=batsman_data[year][i]
            if batsman_data[year][i]>max:
                max=batsman_data[year][i]
            sum+=batsman_data[year][i]
            total+=1
    d['min']=min
    d['max']=max
    d['total']=sum
# ...
```

### Leaves the template placeholder `...` in `overall_run_stats(...)` (partial multi-function implementation)

- Cluster frequency: `2/339` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `2/339` (`0.6%`)
- Dominant private-case vectors: `00000` x1, `00111` x1
- Score distribution (top): `0.0` x1, `80.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `e2e8cb6e716743ef8ffa785a3117aa12`, summary `Wrong Answer`, score `80`, vector `00111`

```python
import math
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    ...
    commarr=[]
    sum1=0
    c=0
    for x in batsman_data:
        for y in batsman_data[x]:
            commarr.append(y)
            sum1+=y
            c+=1

    d={"min":min(commarr),"max":max(commarr),"total":sum1,"average":round(sum1/c) }
    return d

def century_rate(runs:list) -> int:
    """Returns the century rate from the given runs.
# ...
```

### Leaves the template placeholder `...` in `century_rate(...)` (partial multi-function implementation)

- Cluster frequency: `2/339` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `2/339` (`0.6%`)
- Dominant private-case vectors: `00111` x2
- Score distribution (top): `80.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `d80dde059a7144898f33426cbdeb16aa`, summary `Wrong Answer`, score `80`, vector `00111`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    dict={}
    L=["average","max","min","total"]
    total=0
    max=0
    min=1000000
    games=0
    for k,v in batsman_data.items():

        for i in v:
            games+=1
            total+=i
            if i>max:
                max=i
            if i<min:
                min=i
    for i in range(len(L)):
# ...
```

### In `years_with_more_than_average_yearly_century_rate(...)`, uses `>=` instead of strict `>`

- Cluster frequency: `1/339` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `1/339` (`0.3%`)
- Dominant private-case vectors: `00010` x1
- Score distribution (top): `40.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `32afae39432b41a89a132bc741b8f40a`, summary `Wrong Answer`, score `40`, vector `00010`

```python
import math as ma
import statistics as st
def overall_run_stats(batsman_data:list) -> dict:
    c,su,max,avg,min,total=0,0,0,0,10000,0
    d=dict()
    for i in batsman_data.values():

        for j in i:
            c+=1
            su+=j
            if j>max:
                max=j
            if j<min:
                min=j
        avg=ma.ceil(su/c)
    d['average']=avg
    d['max']=max
    d['min']=min
# ...
```

### Later helpers mostly work, but one early helper (`overall_run_stats` or `century_rate`) still has hidden edge-case semantics wrong

- Cluster frequency: `1/339` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `1/339` (`0.3%`)
- Dominant private-case vectors: `00111` x1
- Score distribution (top): `80.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `59f0d3c201514384a586094ff6d074b2`, summary `Wrong Answer`, score `80`, vector `00111`

```python
import math
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    d = batsman_data
    x = {}
    min_ = 10000
    max_ = -10000
    sum_ = 0
    count = 0
    for i in d.values():
        if min(i)<min_:
            min_ = min(i)
        count+=len(i)
    x["min"] = min_
    for i in d.values():
        if max(i)>max_:
            max_ = max(i)
    x["max"] = max_
# ...
```

### Implements only a subset of the required helper functions (one or more named functions are missing)

- Cluster frequency: `1/339` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `1/339` (`0.3%`)
- Dominant private-case vectors: `00111` x1
- Score distribution (top): `60.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `b2a23b87af2a4fadb48fd74805b6a5d7`, summary `Wrong Answer`, score `60`, vector `00111`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    ...
    # print(batsman_data[2016])
    mini,maxi,total,average=100000,0,0,0
    count=0

    for key in batsman_data:
        l=batsman_data[key]
        x=min(l)
        y=max(l)
        mini=min(x,mini)
        maxi=max(y,maxi)
        for i in l:
            total+=i
            count+=1
    average=round(total/count)
    # print(total,round(total/count),mini,maxi)
# ...
```

### Uses fixed year keys / nested-dict assumptions that do not match the hidden batsman data shape

- Cluster frequency: `1/339` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `1/339` (`0.3%`)
- Dominant private-case vectors: `00010` x1
- Score distribution (top): `20.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `b40432590f9a4aac83d1706195930428`, summary `Runtime Error`, score `20`, vector `00010`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    mini=100000000000000000000000000000000000
    maxi=0
    total=0
    count=0
    for x in batsman_data:
        for y in range(len(batsman_data[x])):
            if batsman_data[x][y] > maxi:
                maxi=batsman_data[x][y]
            if batsman_data[x][y]<mini:
                mini=batsman_data[x][y]
            total+=batsman_data[x][y]
            count+=1
    average=total/count
    if average>(((int(average)+1)-int(average))/2):
        average=int(average)+1
    else:
# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `1/339` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `1/339` (`0.3%`)
- Dominant private-case vectors: `00000` x1
- Score distribution (top): `0.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `bc8dee2dabe5479f9c22e3a72a4b24d9`, summary `Runtime Error`, score `0`, vector `00000`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""

for k,v in batsman_data:
   return {"min" : min(v(batsman_data)),"max" : max(v(batsman_data)),"total" : sum(v(batsman_data)),"average" : int(average(v(batsman_datan_data)))}

def century_rate(runs:list) -> int:
    """Returns the century rate from the given runs."""

century_rate = n_centuries / n_matches * 100
n_centuries = count(v >= 100)
"""Century is assumed when the runs scored is greater than or equal to 100.

    Args:
        runs (list): Runs scored in different matches.

    Returns:
        int: Century Rate rounded to nearest integer.
# ...
```

### Leaves the template placeholder `...` in `average_yearly_century_rate(...)` (partial multi-function implementation)

- Cluster frequency: `1/339` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `1/339` (`0.3%`)
- Dominant private-case vectors: `00000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `cf88ea22e93a44618b1eddc69e8c9f2a`, summary `Wrong Answer`, score `0`, vector `00000`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    max=0
    min=250
    total=0
    a=0
    for i in range (len(data)):
        D={'average':a,'max':max,'min':min,'total': total}
        if data.value[i]>max:
            max=i
        if i<min:
            min=i
        total+=i
        a=total/len(data)
    return(D)



# ...
```

### Partial multi-helper implementation: some helper functions are correct, but one or more required helpers still have logic/edge-case bugs

- Cluster frequency: `1/339` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `1/339` (`0.3%`)
- Dominant private-case vectors: `00110` x1
- Score distribution (top): `40.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `e6380eedf9c94c2899c843e5265d1e74`, summary `Wrong Answer`, score `40`, vector `00110`

```python
def overall_run_stats(batsman_data:list) -> dict:
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""
    l = 0
    total = 0
    min = 1000
    max = 0
    avg = 0
    for i in batsman_data.values():
        for j in i:
            total += j
            if j<min:
                min = j
            if j>max:
                max = j
            l += 1
    avg = round(total/l)
    dict = {}
    dict['average'] = avg
# ...
```

### Runtime AttributeError from dict/list API misuse across the batsman-analysis helper functions

- Cluster frequency: `1/339` (`0.3%`)
- Variant frequencies:
  - `ns_25t2_py13_1/12`: `1/339` (`0.3%`)
- Dominant private-case vectors: `00000` x1
- Score distribution (top): `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_1/12`, Student ID `f65250d0ba134eeaac83cfe3f2e4a5a0`, summary `Runtime Error`, score `0`, vector `00000`

```python
def overall_run_stats(batsman_data:list) -> dict:
    d={}

    mini=min(batsman_data.values())
    maxi=max(batsman_data.values())
    tot=0
    for i in batsman_data:
        for j in i.values():
            tot+=batsman_data[j]

    avgi=tot/(len(batsman_data))
    d={"min":mini,"max":maxi,"total":tot,"avg":avgi}
    print(batsman_data.values())
    return d
    """Returns a dict with overall run statistics with keys 'min', 'max', 'total' and 'average'."""


def century_rate(runs:list) -> int:
# ...
```
