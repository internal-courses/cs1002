# Error Patterns: Cluster C097 (`YouTube Video Engagement Analysis`)

## Cluster Summary

- Cluster ID: `C097`
- Cluster title: `YouTube Video Engagement Analysis`
- Cluster file (this file): `analysis/ERRORS-cluster-c097-youtube-video-engagement-analysis-e795b34c.md`
- Variants in cluster: `1`
- Total final submitters across variants: `542`
- Total non-full final submissions across variants: `514`
- Canonical variant (by submissions): `ns_25t2_py13_2/12`

Cluster membership (zero-submitter variants omitted):

| Variant | final_submitters | non_full | Relationship |
| --- | ---: | ---: | --- |
| `ns_25t2_py13_2/12` (canonical) | 542 | 514 | Exact duplicate problem JSON |

## Canonical Question Spec (Full Source Artifact)

- Canonical full question JSON: `problems/ns_25t2_py13_2/12.json`

## Cluster-Level Outcome Summary

- Final submitters: `542`
- Full pass: `28`
- Non-full final submissions: `514`
- Parseable non-full (logic/runtime focus): `450`
- Non-parseable non-full: `64`

Variant-level comparison:

| Variant | Final submitters | Full pass | Non-full | Parseable non-full | Non-parseable non-full |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ns_25t2_py13_2/12` | 542 | 28 | 514 | 450 | 64 |

## Private Case Structure

- Private case 1: `total_engagement(video)` on varied records incl zero-view videos
- Private case 2: `engagement_rate(video)` zero-view guard + rounding to 2 decimals
- Private case 3: `most_engaging_video(videos)` with first-on-tie behavior
- Private case 4: `videos_with_engagement_rate_above_threshold(...)` using strict `>`
- Private case 5: `average_engagement_rate(videos)` over non-zero-view videos only, rounded to 2 decimals
- Private case 6: comprehensive mixed suite combining all helpers (zero-view, tie, and threshold-edge cases)

Private-case vectors in this report are 6-character pass/fail strings over the private case groups (e.g., `100001` marks pass/fail outcomes by private group order).

## Exhaustive Pattern Inventory (Cluster-Level)

| Pattern | Cluster count | % of cluster non-full | `ns_25t2_py13_2/12` |
| --- | ---: | ---: | ---: |
| Does not round `engagement_rate` to 2 decimals | 103 | 20.0% | 103 |
| Zero-view handling is missing in one of the list-processing helpers (`most_engaging`, threshold, or average) | 95 | 18.5% | 95 |
| Runtime NameError from misspelled helper variables across the multi-function solution | 59 | 11.5% | 59 |
| Treats video dicts/lists as callable objects (e.g., `video('title')`) in helper composition | 52 | 10.1% | 52 |
| Syntax / non-parseable final submission | 51 | 9.9% | 51 |
| No return / implicit `None` | 43 | 8.4% | 43 |
| Does not round `average_engagement_rate` to 2 decimals | 19 | 3.7% | 19 |
| Uses `>= threshold` instead of strict `> threshold` in `videos_with_engagement_rate_above_threshold` | 13 | 2.5% | 13 |
| Runtime error (parseable final submission) | 11 | 2.1% | 11 |
| Runtime AttributeError | 10 | 1.9% | 10 |
| Hard-codes public sample video titles/results instead of computing engagement metrics | 10 | 1.9% | 10 |
| Most helper functions are present, but hidden edge-case handling (especially zero-view/average behavior) remains wrong | 10 | 1.9% | 10 |
| Leaves one or more required functions undefined or incomplete in the multi-function template | 7 | 1.4% | 7 |
| Returns a video record/index instead of the video title in `most_engaging_video` | 4 | 0.8% | 4 |
| Runtime IndexError | 4 | 0.8% | 4 |
| Runtime KeyError | 4 | 0.8% | 4 |
| Uses undefined placeholder/typo variables in engagement helper functions | 3 | 0.6% | 3 |
| List-processing helpers are partially correct but fail hidden tie/order/zero-view edge cases | 3 | 0.6% | 3 |
| Runtime ValueError | 3 | 0.6% | 3 |
| Copies test cases / `is_equal(...)` checks into the submission instead of implementing helper functions | 3 | 0.6% | 3 |
| Averages over all videos (`len(videos)`) instead of only non-zero-view videos | 2 | 0.4% | 2 |
| Partially correct helper set: hidden threshold/tie/average semantics are still incorrect | 2 | 0.4% | 2 |
| Reads `input()` in function definitions (interactive script approach causes EOF under evaluator) | 2 | 0.4% | 2 |
| Runtime RecursionError | 1 | 0.2% | 1 |

## Re-clustered Pattern Details

Residual `Other` after second-pass re-clustering: `0/514` (`0.0%`)

### Does not round `engagement_rate` to 2 decimals

- Cluster frequency: `103/514` (`20.0%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `103/514` (`20.0%`)
- Dominant private-case vectors: `000100` x55, `000101` x37, `000000` x4, `000111` x4
- Score distribution (top): `17.0` x47, `50.0` x36, `33.0` x11, `67.0` x5
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `6bf85f060cbd46cc98921a7a9c6cfd10`, summary `Wrong Answer`, score `50`, vector `000101`

```python
def total_engagement(video: dict) -> int:
    title=[]
    for i in videos:
        for j in i:
            if j=='title':
                title.append(i[j])


    views=[]
    for i in videos:
        for j in i:
            if j=='views':
                views.append(str(i[j]))
    likes=[]
    for i in videos:
        for j in i:
            if j=='likes':
                likes.append(str(i[j]))
# ...
```

### Zero-view handling is missing in one of the list-processing helpers (`most_engaging`, threshold, or average)

- Cluster frequency: `95/514` (`18.5%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `95/514` (`18.5%`)
- Dominant private-case vectors: `000111` x66, `000100` x25, `000110` x2, `000101` x2
- Score distribution (top): `83.0` x64, `17.0` x20, `33.0` x5, `50.0` x4
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `8bff5a4510114b0a834a824c910fddd0`, summary `Runtime Error`, score `50`, vector `000101`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    video[total_engagement]=video['likes']+video['comments']
    return video[total_engagement]



def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    if(video['views']==0):
        return 0.0
    video[engagement_rate]=((float(video['likes'])+float(video['comments']))/float(video['views']))*100
    return video[engagement_rate]

def most_engaging_video(videos: list) -> str:
   for i in range(len(videos)):
       if(videos[i]['views']==0):
           videos[i][engagement_rate]=0
# ...
```

### Runtime NameError from misspelled helper variables across the multi-function solution

- Cluster frequency: `59/514` (`11.5%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `59/514` (`11.5%`)
- Dominant private-case vectors: `000000` x33, `000100` x21, `000111` x3, `000110` x2
- Score distribution (top): `0.0` x33, `17.0` x21, `50.0` x3, `33.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `a6a306619e45426c9a8a055a24f37564`, summary `Runtime Error`, score `17`, vector `000100`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    return video.get('likes',0) + video.get('comments',0)


def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    views = video.get('views', 0)
    if views == 0:
        return 0.0
    total_engagement_rate= get_total_engagement(video)
    return round(total_engagement / views, 2)


def most_engaging_video(videos: list) -> str:
    """Returns the title of the video with the highest engagement rate. Returns the first in case of tie."""
    if not videos:
        return""
# ...
```

### Treats video dicts/lists as callable objects (e.g., `video('title')`) in helper composition

- Cluster frequency: `52/514` (`10.1%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `52/514` (`10.1%`)
- Dominant private-case vectors: `000100` x29, `000000` x20, `000101` x2, `000110` x1
- Score distribution (top): `17.0` x27, `0.0` x20, `33.0` x3, `50.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `36aa1fc37efa4293927cf46497ce9cd5`, summary `Runtime Error`, score `50`, vector `000101`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    return video['comments']+video['likes']


def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    if video['views']!=0:
        engagement=((video['comments']+video['likes'])/video['views'])*100
    else:
        engagement=0.0
    w=''
    for i in range(len(str(engagement))):
        if len(str(engagement))>5:
            if i==4:
                if engagement[i+1]>=5:
                    w+=str(int(engagement[i])+1)
                else:
# ...
```

### Syntax / non-parseable final submission

- Cluster frequency: `51/514` (`9.9%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `51/514` (`9.9%`)
- Dominant private-case vectors: `000000` x51
- Score distribution (top): `0.0` x51
- Interpretation: Final code is syntactically invalid or structurally broken, so logic is not meaningfully evaluated.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `67c43c2e0185468a98880534df61948b`, summary `Runtime Error`, score `0`, vector `000000`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""

t=str(input(title))
v=int(input(views))
l=int(input(likes))
c=int(input(comments))
TE= l+c
print("The total engagement is",TE) # this is the totla views of a given video



def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""

t=str(input(title))
v=int(input(views))
l=int(input(likes))
# ...
```

### No return / implicit `None`

- Cluster frequency: `43/514` (`8.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `43/514` (`8.4%`)
- Dominant private-case vectors: `000000` x43
- Score distribution (top): `0.0` x43
- Interpretation: The function computes something but fails to return the required result value.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `823086acd16047cd98a01723463a4bb4`, summary `Wrong Answer`, score `0`, vector `000000`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""

    for i in video:
        print([i])
    ...


def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    ...


def most_engaging_video(videos: list) -> str:
    """Returns the title of the video with the highest engagement rate. Returns the first in case of tie."""
    ...


# ...
```

### Does not round `average_engagement_rate` to 2 decimals

- Cluster frequency: `19/514` (`3.7%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `19/514` (`3.7%`)
- Dominant private-case vectors: `000110` x11, `000100` x5, `000111` x2, `000101` x1
- Score distribution (top): `33.0` x12, `17.0` x5, `50.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `9c8e221b797c43db9cd9c48467e919b4`, summary `Wrong Answer`, score `17`, vector `000100`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    engagement = 0
    for key in video:
        if key == "likes":
            engagement += video["likes"]
        if key == "comments":
            engagement += video["comments"]
    return engagement


def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    engagement = 0
    for key in video:
        if key == "likes":
            engagement += video["likes"]
        elif key == "comments":
# ...
```

### Uses `>= threshold` instead of strict `> threshold` in `videos_with_engagement_rate_above_threshold`

- Cluster frequency: `13/514` (`2.5%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `13/514` (`2.5%`)
- Dominant private-case vectors: `000101` x7, `000100` x3, `000111` x2, `000110` x1
- Score distribution (top): `50.0` x8, `33.0` x3, `17.0` x1, `67.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `81d683f976b04754a4b54aa1180cd443`, summary `Wrong Answer`, score `33`, vector `000101`

```python
def total_engagement(video: dict) -> int:
    total_engagement = 0
    for values,keys in video.items():
        if values == "likes":
            total_engagement = total_engagement + keys
        elif values == "comments":
            total_engagement = total_engagement + keys

    return total_engagement


def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    engagement = total_engagement(video)
    for values,keys in video.items():
        if values == "views":
            if keys == 0:
                return 0.0
# ...
```

### Runtime error (parseable final submission)

- Cluster frequency: `11/514` (`2.1%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `11/514` (`2.1%`)
- Dominant private-case vectors: `000100` x5, `000000` x3, `000111` x1, `000110` x1
- Score distribution (top): `17.0` x5, `0.0` x3, `33.0` x2, `83.0` x1
- Interpretation: Parseable code reaches a runtime failure not captured by a more specific recurring runtime family.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `469c87d9f45241fab2a8aee079b8bead`, summary `Runtime Error`, score `33`, vector `000110`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    for keys in video:
        sum =video['likes'] + video['comments']
        return sum

def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    for keys in video:
        if video['views']==0:
            return 0.0
        else:
            engagement_rate = ((video['likes']+video['comments'])/video['views'])*100
            return round(engagement_rate,2)

def most_engaging_video(videos: list) -> str:
    """Returns the title of the video with the highest engagement rate. Returns the first in case of tie."""
    max =0
# ...
```

### Runtime AttributeError

- Cluster frequency: `10/514` (`1.9%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `10/514` (`1.9%`)
- Dominant private-case vectors: `000000` x6, `000110` x2, `000100` x2
- Score distribution (top): `0.0` x6, `33.0` x2, `17.0` x2
- Interpretation: Calling a method/attribute on the wrong object type (e.g., wrong string/list API).
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `1b20f43bd2bb42bcacdf43c97c3e9cfc`, summary `Runtime Error`, score `33`, vector `000110`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    ...
    return video["likes"]+video["comments"]

def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    ...
    if video["views"]==0:
        return 0.0
    average=((video["likes"]+video["comments"])/video["views"])*100
    rounded_average=round(average,2)
    return rounded_average



def most_engaging_video(videos: list) -> str:
    """Returns the title of the video with the highest engagement rate. Returns the first in case of tie."""
# ...
```

### Hard-codes public sample video titles/results instead of computing engagement metrics

- Cluster frequency: `10/514` (`1.9%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `10/514` (`1.9%`)
- Dominant private-case vectors: `000000` x7, `000100` x3
- Score distribution (top): `0.0` x7, `17.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `cc2bb801ebb649adac748d8567e55c8a`, summary `Wrong Answer`, score `17`, vector `000100`

```python
def total_engagement(video: dict) -> int:
    return video["likes"]+video["comments"]
    """Returns the total engagement (likes + comments) of a given video."""
    ...


def engagement_rate(video: dict) -> float:
    if video["views"]==0:
        return(0.0)
    else:
        rate=((video["likes"]+video["comments"])/video["views"])*100
        return rate
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    ...


def most_engaging_video(videos: list) -> str:
    if videos == [
# ...
```

### Most helper functions are present, but hidden edge-case handling (especially zero-view/average behavior) remains wrong

- Cluster frequency: `10/514` (`1.9%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `10/514` (`1.9%`)
- Dominant private-case vectors: `000111` x10
- Score distribution (top): `67.0` x6, `83.0` x3, `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `dbe06b55f62c459a867a55712a1f197f`, summary `Wrong Answer`, score `67`, vector `000111`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    likes=video['likes']
    comments=video['comments']
    return likes+comments


def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    engagement=video['likes']+video['comments']
    views=video['views']
    if(views>0):
        engagement_rate=(engagement/views)*100
    if(views==0):
        engagement_rate=0.0
    return round(engagement_rate,2)


# ...
```

### Leaves one or more required functions undefined or incomplete in the multi-function template

- Cluster frequency: `7/514` (`1.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `7/514` (`1.4%`)
- Dominant private-case vectors: `000000` x7
- Score distribution (top): `0.0` x7
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `a141deafd59845f0a41b51299d6c93a9`, summary `Runtime Error`, score `0`, vector `000000`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""

    total_engagement = likes + comments
    return(total_engagement)


def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    engagement_rate(likes + comments) / views * 100
    return(engagement_rate)

    list) -> str:
    """Returns the title of the video with the highest engagement rate. Returns the first in case of tie."""



def videos_with_engagement_rate_above_threshold(videos: list, threshold: float) -> list:
# ...
```

### Returns a video record/index instead of the video title in `most_engaging_video`

- Cluster frequency: `4/514` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `4/514` (`0.8%`)
- Dominant private-case vectors: `000100` x2, `000101` x2
- Score distribution (top): `50.0` x2, `17.0` x1, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `a0b2e818c14c431abb8f8b4ae6af95f1`, summary `Wrong Answer`, score `50`, vector `000101`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    engagement = video["likes"] + video["comments"]
    return engagement


def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    if video["views"] != 0:
        engagement = (video["likes"]+video["comments"])/video["views"]*100
        return engagement
    return 0.0


def most_engaging_video(videos: list) -> str:
    """Returns the title of the video with the highest engagement rate. Returns the first in case of tie."""
    highest_engagement = 0
    for video in videos:
# ...
```

### Runtime IndexError

- Cluster frequency: `4/514` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `4/514` (`0.8%`)
- Dominant private-case vectors: `000100` x2, `000101` x1, `000110` x1
- Score distribution (top): `33.0` x2, `17.0` x1, `50.0` x1
- Interpretation: Out-of-range indexing during iteration/comparison logic.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `dc29a6ab709345c183e7dc066c409336`, summary `Runtime Error`, score `33`, vector `000100`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    return video["likes"]+video["comments"]


def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    if video["views"]==0:
        return 0.0
    else:return ((video["likes"]+video["comments"])/video["views"]*100)

def most_engaging_video(videos: list) -> str:
    e=0
    L=[]
    for x in range(len(videos)):
        if videos[x]["views"]==0:
            continue
        elif (videos[x]["likes"]+videos[x]["comments"]/videos[x]["views"]*100)>e:
# ...
```

### Runtime KeyError

- Cluster frequency: `4/514` (`0.8%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `4/514` (`0.8%`)
- Dominant private-case vectors: `000000` x3, `000111` x1
- Score distribution (top): `0.0` x3, `67.0` x1
- Interpretation: Dictionary lookup on uninitialized/unexpected key.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `52d374f36df74420a265fd3f384c3cdd`, summary `Runtime Error`, score `67`, vector `000111`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    s=video["likes"]+video["comments"]
    return s


def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    if video["views"]==0:
        return 0.0
    else:
        c=video["likes"]+video["comments"]
        a=video["views"]
        er=(c/a)*100
        e=round(er,2)
        return e


# ...
```

### Uses undefined placeholder/typo variables in engagement helper functions

- Cluster frequency: `3/514` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `3/514` (`0.6%`)
- Dominant private-case vectors: `000000` x2, `000100` x1
- Score distribution (top): `0.0` x2, `17.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `8a900784aa984246a9448c0569f07c87`, summary `Runtime Error`, score `17`, vector `000100`

```python
def total_engagement(video: dict) -> int:
    return video.get('likes',0)+video.get('comments',0)
    """Returns the total engagement (likes + comments) of a given video."""
    ...


def engagement_rate(video: dict) -> float:
    views = video.get('views', 0)
    if views==0:
        return 0.0
    engagement = total_engagement(video)
    return round(engagement/views,2)


    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    ...


# ...
```

### List-processing helpers are partially correct but fail hidden tie/order/zero-view edge cases

- Cluster frequency: `3/514` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `3/514` (`0.6%`)
- Dominant private-case vectors: `000110` x3
- Score distribution (top): `50.0` x2, `33.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `2f20a38a1dae495bb86b4637ee3cf5db`, summary `Wrong Answer`, score `50`, vector `000110`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    total_engagement_video = video["likes"] + video["comments"]
    return total_engagement_video

def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    total_engagement_video = video["likes"] + video["comments"]
    video_views = video["views"]
    if video_views == 0:
        engagement_rate_video = 0.0
    else:
        engagement_rate_video = round(((total_engagement_video / video_views) * 100), 2)
    return engagement_rate_video


def most_engaging_video(videos: list) -> str:
    """Returns the title of the video with the highest engagement rate. Returns the first in case of tie."""
# ...
```

### Runtime ValueError

- Cluster frequency: `3/514` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `3/514` (`0.6%`)
- Dominant private-case vectors: `000100` x2, `000000` x1
- Score distribution (top): `17.0` x2, `0.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `39ce79d932624e51a7bea7d19e9c04cb`, summary `Runtime Error`, score `17`, vector `000100`

```python
def total_engagement(video: dict) -> int:
    return (video['likes']+video['comments'])
    """Returns the total engagement (likes + comments) of a given video."""



def engagement_rate(video: dict) -> float:
    if video['views']==0:
        return 0.0
    else:
        rate=((video['likes']+video['comments'])/video['views'])*100
        return rate


    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""



# ...
```

### Copies test cases / `is_equal(...)` checks into the submission instead of implementing helper functions

- Cluster frequency: `3/514` (`0.6%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `3/514` (`0.6%`)
- Dominant private-case vectors: `000000` x3
- Score distribution (top): `0.0` x3
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `3d6127e9d7ba41ce9c385f920760654f`, summary `Runtime Error`, score `0`, vector `000000`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    input:

    videos = [
    {'title': 'Intro to Python', 'views': 1000, 'likes': 100, 'comments': 50},
    {'title': 'Advanced Python', 'views': 2000, 'likes': 300, 'comments': 100},
    {'title': 'Python Tips', 'views': 0, 'likes': 20, 'comments': 10},
]

is_equal(total_engagement(videos[0]), 150)
is_equal(total_engagement(videos[1]), 400)

def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    videos = [
    {'title': 'Intro to Python', 'views': 1000, 'likes': 100, 'comments': 50},
    {'title': 'Advanced Python', 'views': 2000, 'likes': 300, 'comments': 100},
# ...
```

### Averages over all videos (`len(videos)`) instead of only non-zero-view videos

- Cluster frequency: `2/514` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `2/514` (`0.4%`)
- Dominant private-case vectors: `000111` x2
- Score distribution (top): `67.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `a6885569e50c488ab296c012bfeae270`, summary `Wrong Answer`, score `67`, vector `000111`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    ...
    return video['likes'] + video['comments']

def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    ...
    if video['views']== 0:
        return 0.0
    rate = (video['likes'] + video['comments'])/ video['views']*100
    return round(rate,2)

def most_engaging_video(videos: list) -> str:
    """Returns the title of the video with the highest engagement rate. Returns the first in case of tie."""
    ...
    if not videos :
        return ""
# ...
```

### Partially correct helper set: hidden threshold/tie/average semantics are still incorrect

- Cluster frequency: `2/514` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `2/514` (`0.4%`)
- Dominant private-case vectors: `000101` x2
- Score distribution (top): `33.0` x1, `50.0` x1
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `d8ec39c73f4f409aa2630ee2aec24a5c`, summary `Wrong Answer`, score `50`, vector `000101`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""

    return(video['likes']+video['comments'])

def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""

    engagementRate = video['likes']+video['comments']
    if video['views']>0.0:
        engagementRate/=video['views']
    else:
        engagementRate = 0.0
    engagementRate*=100
    round(engagementRate,2)
    return(engagementRate)

def most_engaging_video(videos: list) -> str:
# ...
```

### Reads `input()` in function definitions (interactive script approach causes EOF under evaluator)

- Cluster frequency: `2/514` (`0.4%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `2/514` (`0.4%`)
- Dominant private-case vectors: `000000` x2
- Score distribution (top): `0.0` x2
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `eec5197bc88a4f659e413cc6e8c58864`, summary `Runtime Error`, score `0`, vector `000000`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    total_engagement = int(input())
    x = int(input(likes))
    y = int(input(comments))
    total_engagement = x + y
    print(total_engagement)


def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    engagement_rate = input()
    x = int(input(likes))
    y = int(input(comments))
    z = int(input(views))
    engagement_rate = ((x+ y) / z) * 100
    print(engagement_rate)

# ...
```

### Runtime RecursionError

- Cluster frequency: `1/514` (`0.2%`)
- Variant frequencies:
  - `ns_25t2_py13_2/12`: `1/514` (`0.2%`)
- Dominant private-case vectors: `000100` x1
- Score distribution (top): `17.0` x1
- Interpretation: Infinite/self recursion without a valid terminating condition.
- Representative examples (actual student submissions):
  - Variant `ns_25t2_py13_2/12`, Student ID `fa5c7b0620ca4275b6a6af0b23045689`, summary `Runtime Error`, score `17`, vector `000100`

```python
def total_engagement(video: dict) -> int:
    """Returns the total engagement (likes + comments) of a given video."""
    return video.get("likes",0)+video.get("comments",0)


def engagement_rate(video: dict) -> float:
    """Returns the engagement rate ((likes + comments) / views) * 100 rounded to 2 decimals. Returns 0.0 if views == 0."""
    max_rate=-1
    result_title=''
    for video in videos:
        rate=engagement_rate(video)
        if rate>max_rate:
            max_rate=rate
            result_title=video.get('title','')
    return result_title


def most_engaging_video(videos: list) -> str:
# ...
```
