---
marp: true
theme: default
paginate: true
size: 16:9
style: |
  section {
    font-size: 28px;
  }
  section pre {
    font-size: 0.78em;
  }
  section.compact pre {
    font-size: 0.68em;
  }
---

<!--
namespace: ns_25t2_py11_1
problem_id: 6
student_id: e42a471813ae41a7b30d2f6927d92c32
event_no: 1
-->

# Q1 · Card to Value Tuple · Baseline

```python
rank = card[:-1]
suit = card[-1]
return (suit_map[suit], rank_map[rank])
```

Reads the contract as variable-width data, so `10D` never becomes a special case.

---

<!--
namespace: ns_25t2_py11_1
problem_id: 6
student_id: 56036b0cfd0a453da93c959861c50f96
event_no: 1
-->

# Q1 · Card to Value Tuple · Everything Except the Punctuation

```python
return tuple(a, b)
```

The concept is right; the first failure is Python punctuation before the tuple order fight even starts.

---

<!--
namespace: ns_25t2_py11_1
problem_id: 6
student_id: ad7a05553f034a4a9766e6061a80ed7f
event_no: 3
-->

# Q1 · Card to Value Tuple · The Hidden Boss

```python
value_1 = card[1]
value_2 = card[0]
try:
    value_1 = suit_values[value_1]
except:
    value_1 = int(value_1)
try:
    value_2 = rank_values[value_2]
except:
    value_2 = int(value_2)

result = (value_1, value_2)
return result
```

Public green hides a `card[0]` parser that `10D` breaks instantly.

---

<!--
namespace: ns_25t2_py22_1
problem_id: 15
student_id: 0fdf6645bdc54e7da88566e0422fbda1
event_no: 1
-->

# Q2 · Check for Greeting Prefix · Baseline

```python
return s.startswith("Hello ") or s.startswith("Hi ")
```

The whole English rule becomes one exact Python expression.

---

<!--
namespace: ns_25t2_py22_1
problem_id: 15
student_id: 60f6e5f27899406ea16a5470210db8d1
event_no: 1
-->

# Q2 · Check for Greeting Prefix · Python With a JavaScript Accent

```python
if s.startswith('Hello'|| 'Hi'):
    return True
return False
```

The intent is correct, but the operator came from JavaScript instead of Python.

---

<!--
namespace: ns_25t2_py22_1
problem_id: 15
student_id: aa68a2811ed74d968987be81d3d6fb31
event_no: 4
-->

# Q2 · Check for Greeting Prefix · One Missing Space

```python
return s.startswith("Hello ") or s.startswith("Hi ")
```

One hidden test points to one missing space, so the fix is a one-character contract repair.

---

<!--
namespace: ns_25t2_py22_1
problem_id: 15
student_id: 60f6e5f27899406ea16a5470210db8d1
event_no: 81
-->

# Q2 · Check for Greeting Prefix · Negotiating With the Grader

```python
if s == "Hithere":
    return False
if s.startswith("Hello" or "Hi" or "hello" or "hi"):
    return True
elif s.startswith("Hi"):
    return True
```

The code stops generalizing and starts bargaining with the visible test cases.

---

<!--
namespace: ns_25t2_py22_1
problem_id: 15
student_id: 590240758edf48fa81f701ae4295dc82
event_no: 131
-->
<!-- _class: compact -->

# Q2 · Check for Greeting Prefix · The Triple-Quoted Graveyard

```python
s = s.strip()
return s.startswith("Hello") or s.startswith("Hi")

"""cleaned_s=s.strip().lower()

is_hello=cleaned_s.startswith("hello") and (len(cleaned_s)==5 or not cleaned_s[5].isalpha())


is_hi=cleaned_s.startswith("hi") and (len(cleaned_s)==2 or not cleaned_s[2].isalpha())


return is_hello or is_hi"""
```

The better solution exists, but it has been buried inside triple quotes like ad-hoc version control.

---

<!--
namespace: ns_25t3_py13_1
problem_id: 7
student_id: ebd2cfa0ce7e4554850c3bc999fa10e2
event_no: 1
-->

# Q3 · Shuffle a Three Word Sentence · Baseline

```python
s = sentence.split(" ")
return " ".join([s[i] for i in order])
```

`order` is treated as data, not as six special cases.

---

<!--
namespace: ns_25t3_py13_1
problem_id: 7
student_id: 384851c6834647139983873aea99d419
event_no: 4
-->

# Q3 · Shuffle a Three Word Sentence · Fruit-Salad Overfit

```python
if order == (0, 2, 1):
    return "apple orange banana"
elif order == (2, 1, 0):
    return "mouse dog cat"
elif order == (1, 0, 2):
    return "yellow red green"
```

The function memorizes one fruit example instead of learning the reorder rule.

---

<!--
namespace: ns_25t3_py13_1
problem_id: 7
student_id: 107337b2583a4bfebe3e917b315d2684
event_no: 7
-->
<!-- _class: compact -->

# Q3 · Shuffle a Three Word Sentence · Enumerating the Universe

```python
if order == (0, 1, 2):
    return n0 + " " + n1 + " " + n2
elif order == (0, 2, 1):
    return n0 + " " + n2 + " " + n1
elif order == (1, 0, 2):
    return n1 + " " + n0 + " " + n2
elif order == (1, 2, 0):
    return n1 + " " + n2 + " " + n0
elif order == (2, 0, 1):
    return n2 + " " + n0 + " " + n1
else:
    return n2 + " " + n1 + " " + n0
```

Exhaustive case-listing passes here because the universe is tiny, not because the abstraction is sound.

---

<!--
namespace: ns_25t2_py21_2
problem_id: 18
student_id: 13bc0b2cf15145219dd6719b89dfc3cd
event_no: 1
-->

# Q4 · Pangram Check · Baseline

```python
alphabet = set("abcdefghijklmnopqrstuvwxyz")
return alphabet.issubset(set(text.lower()))
```

The invariant fits in one set expression, so the code stays shorter than the prompt.

---

<!--
namespace: ns_25t2_py21_2
problem_id: 18
student_id: a2316b024ae946b59ebe2f04090321d9
event_no: 2
-->

# Q4 · Pangram Check · The Checker Forgot C

```python
count = 0

for i in text.lower():
    if i in "absdefghijklmnopqrstuvwxyz":
        count += 1

if count == 26:
    return True

return False
```

Even the checker’s internal alphabet can be wrong when the student is reasoning under load.

---

<!--
namespace: ns_25t2_py21_2
problem_id: 18
student_id: 2ee6740d56614ebbb3e68f6fe2992f28
event_no: 61
-->

# Q4 · Pangram Check · The False Summit

```python
count = 0
for i in range(len(text1)):
    if text1[i] in alphabets:
        count += 1

if count >= 26:
    return True
return False
```

`count >= 26` is a plausible heuristic that collapses the moment repetition enters the room.

---

<!--
namespace: ns_25t2_py21_2
problem_id: 18
student_id: 2ee6740d56614ebbb3e68f6fe2992f28
event_no: 103
-->

# Q4 · Pangram Check · The Actual Invariant

```python
uniq = set()
for i in range(len(text1)):
    if text1[i] in alphabets:
        uniq.add(text1[i])

length = len(uniq)

if length >= 26:
    return True
return False
```

The recovery happens when counting characters becomes tracking unique letters.
