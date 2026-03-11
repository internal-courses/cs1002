#!/usr/bin/env python3
"""
Generate analysis/replays-v3.html - a slideshow walkthrough of 7 student replays.
"""
import json, re, html, difflib

def parse_rec(fname):
    events = []
    with open(fname) as f:
        header = json.loads(f.readline())
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                ts, typ, text = json.loads(line)
                if typ != 'o': continue
                ev = {'time': ts}
                m = re.search(r'Event\s*:\s*(\d+)/(\d+)', text)
                if m: ev['event_idx'] = int(m.group(1))
                m = re.search(r'type=([\w_]+)', text)
                if m: ev['type'] = m.group(1)
                m = re.search(r'summary=(.*?)\s*\|.*?score=([\d.]+)\s*\|.*?tests=(\d+)/(\d+)', text)
                if m:
                    ev['summary'] = m.group(1).strip()
                    ev['score'] = float(m.group(2))
                    ev['tests_pass'] = int(m.group(3))
                    ev['tests_total'] = int(m.group(4))
                m = re.search(r'sha=([a-f0-9]+)', text)
                if m: ev['sha'] = m.group(1)
                if 'public' in text[200:600]: ev['visibility'] = 'public'
                elif 'private' in text[200:600]: ev['visibility'] = 'private'
                code_m = re.search(r'-{40,}\r?\n(.*?)\r?\n-{40,}', text, re.DOTALL)
                if code_m:
                    raw_code = code_m.group(1)
                    lines = []
                    for l in raw_code.split('\r\n'):
                        m2 = re.match(r'\s*\d+\s*\|\s?(.*)', l)
                        if m2: lines.append(m2.group(1))
                    ev['code'] = '\n'.join(lines)
                events.append(ev)
            except: pass
    return events

def event_with_code_near(events, t):
    candidates = [e for e in events if 'code' in e and e['code'].strip() and len(e['code'].strip().split('\n')) > 1]
    if not candidates:
        return None
    return min(candidates, key=lambda e: abs(e['time'] - t))

def compute_diff_highlights(code_a, code_b):
    """Returns (added_lines, changed_lines, removed_count) for code_b vs code_a. 1-indexed."""
    if not code_a:
        return list(range(1, len(code_b.split('\n'))+1)), [], 0
    a_lines = code_a.split('\n')
    b_lines = code_b.split('\n')
    matcher = difflib.SequenceMatcher(None, a_lines, b_lines)
    added, changed = [], []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'insert':
            added.extend(range(j1+1, j2+1))
        elif tag == 'replace':
            changed.extend(range(j1+1, j2+1))
    return added, changed

# ─── SLIDE DATA ───────────────────────────────────────────────────────────────

BASE = '/home/vscode/code/pyoppe/analysis'

def load_events(shortname):
    return parse_rec(f'{BASE}/replay-{shortname}.rec')

def snap(events, t):
    """Get code snapshot near time t."""
    e = event_with_code_near(events, t)
    return e

R1 = load_events('ns_25t2_py11_1-10-bad2c53a87bb459e9fcdb74f26283a20')
R2 = load_events('ns_25t2_py13_1-5-2662dd2b4ea744ad909a06569aecdc4b')
R3 = load_events('ns_25t2_py21_2-18-2ee6740d56614ebbb3e68f6fe2992f28')
R4 = load_events('ns_25t2_py22_1-15-60f6e5f27899406ea16a5470210db8d1')
R5 = load_events('ns_25t2_py22_1-17-a970a89d08064dccb13e8d51ae6a07b5')
R6 = load_events('ns_25t3_py13_1-10-ee012cee3fa5491d8db37141d2a954fe')
R7 = load_events('ns_25t3_py24_1-9-06f6fb4ea76144ef91df6ceec5f264a8')

def make_code_slide(ev, prev_ev=None, heading='', body='', manual_highlight=None, elapsed=None):
    code = ev.get('code', '') if ev else ''
    prev_code = prev_ev.get('code', '') if prev_ev else None
    added, changed = compute_diff_highlights(prev_code, code) if prev_code else ([], [])
    hi = manual_highlight or []
    return {
        'type': 'code',
        'code': code,
        'added': added,
        'changed': changed,
        'highlight': hi,
        'status': ev.get('summary', '?') if ev else '?',
        'tests_pass': ev.get('tests_pass', 0) if ev else 0,
        'tests_total': ev.get('tests_total', 0) if ev else 0,
        'visibility': ev.get('visibility', 'public') if ev else 'public',
        'time_label': f"{elapsed or (ev['time'] if ev else 0):.0f}s",
        'heading': heading,
        'body': body,
    }

# ─── Build replay 1: Replace Consonants ───────────────────────────────────────
r1_e0 = snap(R1, 0)
r1_e1 = snap(R1, 21.6)
r1_e2 = snap(R1, 54.5)
r1_e3 = snap(R1, 91.9)
r1_e4 = snap(R1, 95.4)
r1_e5 = snap(R1, 97.7)

REPLAY1 = {
    'id': 'r1',
    'title': 'Replace Consonants',
    'subtitle': 'Incremental Debugging to Full Score',
    'question': 'Replace Consonants with Hash',
    'namespace': 'ns_25t2_py11_1',
    'duration': '1:41',
    'outcome': 'Score 100 ✓',
    'outcome_class': 'pass',
    'insight': 'A patient debugger who cycled through many failures before landing a clean, generalised solution. The key? Each bug fix moved toward understanding, not just passing tests.',
    'tags': ['incremental debugger', 'runtime → logic', 'stable convergence'],
    'slides': [
        {
            'type': 'intro',
            'heading': 'The Problem',
            'question_desc': 'Given N strings, replace all consonants with <code>#</code> and print the result. Vowels (a, e, i, o, u — upper and lower) stay unchanged.',
            'why': 'This student took 83 attempts over 101 seconds and eventually scored 100 — but the path was anything but straight. Watch how they cycled through typos, wrong data structures, variable confusion, and then finally cracked it.',
            'what_to_look_for': [
                'Three distinct bugs in the very first submission',
                'The shift from RuntimeError → WrongAnswer (a healthy sign)',
                'A brief relapse into runtime errors mid-session',
                'How the final clean solution looked very different from the first attempt',
            ],
        },
        make_code_slide(r1_e0, None,
            heading='Three Bugs, One Shot',
            body='The very first submission is a goldmine for instructors. <strong>Line 4: <code>whille</code></strong> — a typo that causes a SyntaxError before anything runs. <strong>Line 10: <code>CH==\'U\'</code></strong> — capital CH is undefined (Python is case-sensitive). <strong>Line 13: <code>s[ch]=\'#\'</code></strong> — you can\'t assign to a string index; strings are immutable in Python.',
            manual_highlight=[4, 10, 13],
        ),
        make_code_slide(r1_e1, r1_e0,
            heading='Runtime → Logic: A Healthy Shift',
            body='By event #16 (~22s in), the student fixed the <code>while</code> typo. But now a subtler bug appears: <strong>Line 29: <code>i=\'#\'</code></strong> — they\'re trying to replace a character by mutating the loop variable <code>i</code>. That doesn\'t work; <code>i</code> is a local copy. The original string is untouched. This is the "wrong mental model of loops" error — extremely common in beginners.',
            manual_highlight=[25, 26, 29, 30],
        ),
        make_code_slide(r1_e2, r1_e1,
            heading='Complexity Spiral',
            body='Around 54 seconds in, the code has ballooned to 42 lines. The student is now building a separate string <code>ss</code>, using print statements inside loops, and commenting out old attempts. Notice <strong>Line 35: <code>ss[i]=\'#\'</code></strong> — the same string-immutability bug, just on a different variable. They haven\'t yet identified the root cause; they\'ve just added layers.',
            manual_highlight=[35, 29, 30, 31, 32, 33, 34],
        ),
        make_code_slide(r1_e3, r1_e2,
            heading='Almost There',
            body='At event #71 (~92s in), 1 out of 3 public tests pass. The core idea is emerging: build the output string one character at a time. <strong>The key fix is on lines 36–37</strong>: instead of modifying the loop variable or indexing a string, they now do <code>s[i]=\'#\'</code> where <code>s</code> is a list — so assignment actually works. Getting closer.',
            manual_highlight=[36, 37, 38],
        ),
        make_code_slide(r1_e4, r1_e3,
            heading='Public Tests: All Green 🟢',
            body='At 95 seconds, all 3 public tests pass. The logic is now: (1) convert string to list, (2) replace non-vowel, non-space characters with <code>\'#\'</code>, (3) rebuild and print each line. Notice the massive commented-out section — the student kept their old attempts around "just in case." The actual solution is lines 49–52.',
            manual_highlight=[49, 50, 51, 52],
        ),
        make_code_slide(r1_e5, r1_e4,
            heading='Private Tests Pass Too ✓',
            body='Just 2 seconds later, the student ran private tests and passed all 3. Notice how the final code (lines 1–35) is much cleaner — they removed the dead commented code. The private pass is the real signal: the logic <em>generalised</em>, not just overfit to the 3 public examples. This is a textbook model of "incremental debugging that eventually converges."',
            manual_highlight=[8, 9, 10, 11, 12, 13],
        ),
        {
            'type': 'summary',
            'heading': 'Key Takeaways',
            'bullets': [
                'Three concurrent bugs in the first submission — typo, case sensitivity, and string immutability. Each needed to be discovered separately.',
                'The shift from RuntimeError to WrongAnswer is <em>progress</em>: it means the code at least runs. Students shouldn\'t treat this as "still failing."',
                'Mutation via loop variable (<code>i = \'#\'</code>) is one of the most common Python misconceptions. It needs direct instruction.',
                'The final solution was algorithmically different from the first attempt — the student genuinely learned, not just patched.',
            ],
            'intervention': 'When you see a student with 15+ RuntimeErrors, ask: "What does Python say the error is?" Then ask: "What does that mean about your code?" — don\'t just tell them the fix. For the string-immutability bug specifically, a one-line demo (<code>s = list(s)</code>) changes everything.',
        }
    ]
}

# ─── Build replay 2: Decreasing 4-digit ───────────────────────────────────────
r2_e0 = snap(R2, 0)
r2_e1 = snap(R2, 10)
r2_e2 = snap(R2, 22.5)
r2_e3 = snap(R2, 30)
r2_e4 = snap(R2, 40)

REPLAY2 = {
    'id': 'r2',
    'title': 'Decreasing 4-Digit Number',
    'subtitle': 'Minimal-Change Solver',
    'question': 'Check If a Number is a Decreasing 4-Digit Number',
    'namespace': 'ns_25t2_py13_1',
    'duration': '0:44',
    'outcome': 'Score 100 ✓',
    'outcome_class': 'pass',
    'insight': 'A lean, focused session. Fix one thing, test, repeat. No over-engineering, no thrashing. This is what good debugging rhythm looks like — and it\'s rare.',
    'tags': ['minimal changes', 'stable convergence', 'short session'],
    'slides': [
        {
            'type': 'intro',
            'heading': 'The Problem',
            'question_desc': 'Given a 4-digit integer, check whether its digits are strictly decreasing from left to right. For example, 9876 → True, 4321 → True, 4312 → False.',
            'why': 'This 44-second session is a contrast to the others. The student makes exactly the right changes at exactly the right time. No thrashing, no spiralling complexity. Compare this to Replay 5 (Reversed Squares) — same difficulty level, completely different outcome.',
            'what_to_look_for': [
                'How quickly the runtime errors resolve (just 3 attempts)',
                'The brief regression at 30s — they "improved" and accidentally broke it',
                'The final solution is remarkably compact',
                'What separates an efficient session from a thrashing one',
            ],
        },
        make_code_slide(r2_e0, None,
            heading='Runtime Error: Two Bugs, Adjacent Lines',
            body='The first attempt has the right algorithm structure — convert to string, iterate, compare. But <strong>Line 26: <code>list(string)</code></strong> — the variable is <code>string1</code>, not <code>string</code>. NameError. And <strong>Line 28: <code>if list1[k] > list1[k+1]</code></strong> — <code>k</code> is the character itself (from <code>for k in list1</code>), not an index. So this would fail at runtime even if line 26 was fixed.',
            manual_highlight=[25, 26, 27, 28],
        ),
        make_code_slide(r2_e1, r2_e0,
            heading='Still Stuck: Iterating the Number Directly',
            body='After 10 seconds, they fixed the variable name but introduced a new bug: <strong>Line 26: <code>list(n)</code></strong> — you can\'t convert an integer directly to a list. The mental model here is "I want the digits as a list" but the path there is <code>list(str(n))</code>. The student is one function call away from success.',
            manual_highlight=[25, 26, 27, 28],
        ),
        make_code_slide(r2_e2, r2_e1,
            heading='All Tests Pass — But Wait...',
            body='At 22.5 seconds, all 3 tests pass! The fix was <code>list(string1)</code>. But look at <strong>Line 28</strong>: <code>if list1[0] > list1[1]</code> — this only checks the <em>first two digits</em>, not all four. It happened to pass the public tests (which probably don\'t have edge cases like 9811), but the logic is incomplete. The student doesn\'t know this yet.',
            manual_highlight=[27, 28, 29, 30, 31],
        ),
        make_code_slide(r2_e3, r2_e2,
            heading='Brief Regression: 2/3',
            body='30 seconds in, the student tries to "fix" the comparison and accidentally breaks it: <strong>Line 28: <code>if list1[2] > list1[1]</code></strong> — checking the wrong pair of digits now. This is a common pattern: student passes tests, decides to "improve" the solution, introduces a regression. The impulse to improve is good; the missing step is re-running tests immediately after each change.',
            manual_highlight=[27, 28, 29, 30, 31],
        ),
        make_code_slide(r2_e4, r2_e3,
            heading='Back to Passing — Final Submission ✓',
            body='40 seconds in, all tests pass again and the student submits. The final code still only checks one pair of adjacent digits (not all four strictly), but it happens to pass both public and private tests — suggesting the test cases don\'t stress this edge case. A useful discussion point: <em>can you write a test case that would break this?</em>',
            manual_highlight=[27, 28, 29, 30, 31],
        ),
        {
            'type': 'summary',
            'heading': 'Key Takeaways',
            'bullets': [
                'Minimal change strategy: this student changed one or two lines between attempts, making it easy to pinpoint what broke.',
                'The brief regression at 30s is instructive — improving code without testing after every change is risky.',
                'The final solution has a hidden bug (only checks two digits), but passes tests. This is worth discussing with the class: "how would you find this bug?"',
                'Short sessions aren\'t necessarily good sessions — but this one was. The student had a clear mental model and executed it efficiently.',
            ],
            'intervention': 'Use this replay as a "good debugging" model. Show it alongside Replay 5 (Reversed Squares) which has 213 attempts and no success. Ask students: "What is this student doing differently?"',
        }
    ]
}

# ─── Build replay 3: Pangram Check ───────────────────────────────────────────
r3_e0 = snap(R3, 0)
r3_e1 = snap(R3, 3.9)
r3_e2 = snap(R3, 24.6)
r3_e3 = snap(R3, 47)
r3_e4 = snap(R3, 52.5)
r3_e5 = snap(R3, 71.4)

REPLAY3 = {
    'id': 'r3',
    'title': 'Pangram Check',
    'subtitle': 'Public Pass, Private Miss, Then Fix',
    'question': 'Pangram Check',
    'namespace': 'ns_25t2_py21_2',
    'duration': '1:11',
    'outcome': 'Score 100 ✓',
    'outcome_class': 'pass',
    'insight': 'The classic "false summit." The student passed all public tests but failed private ones — then had to figure out why without seeing the hidden test cases.',
    'tags': ['false summit', 'hidden-case reasoning', 'public vs private'],
    'slides': [
        {
            'type': 'intro',
            'heading': 'The Problem',
            'question_desc': 'A <em>pangram</em> is a sentence that contains every letter of the alphabet at least once. "The quick brown fox jumps over the lazy dog" is the classic example. Return True if the input is a pangram, False otherwise.',
            'why': 'This replay demonstrates the "false summit" trap — the student passes all visible tests (3/3) but immediately fails private tests. Then they have to reason about what the hidden test cases might be testing, without being able to see them. This is a crucial skill: building code that\'s correct by construction, not just by example-matching.',
            'what_to_look_for': [
                'The first approach has the wrong logic direction (iterating text instead of checking alphabet)',
                'The "false summit" moment: all public tests pass at 47s',
                'The private failure exposes a counting bug: repeat characters inflate the count past 26',
                'The final fix uses a set — elegant and robust',
            ],
        },
        make_code_slide(r3_e0, None,
            heading='Wrong Logic Direction',
            body='The first attempt checks "for each character in the text, is it in the alphabet?" — but that\'s the <em>opposite</em> of pangram logic. A pangram requires every letter of the alphabet to appear in the text, not every character in the text to be a letter. Also, <strong>Line 25: return True inside the loop</strong> — this returns on the first character, ignoring the rest. Logic is fundamentally backwards.',
            manual_highlight=[21, 22, 23, 24, 25, 26],
        ),
        make_code_slide(r3_e1, r3_e0,
            heading='Making It Worse',
            body='4 seconds in, the student tries to patch: <strong>Line 24: <code>if i not in alphabets and int(i)=False</code></strong> — this is not valid Python (syntax error: <code>int(i)=False</code>). They\'re trying to exclude non-letter characters, but the approach is wrong and the syntax is broken. This is "patching symptoms without fixing the root cause."',
            manual_highlight=[24],
        ),
        make_code_slide(r3_e2, r3_e1,
            heading='New Approach: Counting Characters',
            body='Around 25 seconds in, the student strips spaces and counts how many characters are in the alphabet. The reasoning: "if 26 or more chars are in the alphabet, it\'s a pangram." This is better — but has a subtle bug. <strong>What if the text has repeated letters?</strong> "aaaaaaaaa...a" (26 a\'s) would count as 26 alphabet hits and return True.',
            manual_highlight=[12, 13, 14, 15, 16, 17, 18],
        ),
        make_code_slide(r3_e3, r3_e2,
            heading='False Summit: Public Tests All Green 🟢',
            body='At 47 seconds, all 3 public tests pass. The student might feel done. But the counting approach (<code>count >= 26</code>) will fail for inputs with repeated letters. The public test cases happened not to test this edge case. This is the "false summit" — visible success masking hidden failure.',
            manual_highlight=[11, 12, 13, 14, 15, 16, 17, 18],
        ),
        make_code_slide(r3_e4, r3_e3,
            heading='Private Tests Expose the Bug: 1/3',
            body='Immediately after the public pass, private tests reveal only 1/3. The hidden test cases likely include repeated-letter inputs like "aaabbbccc..." (26+ chars, all alphabet, but not a pangram). The student\'s counting logic inflates the count for repeated chars. The fix: count <em>unique</em> letters, not total letters.',
            manual_highlight=[6, 7, 8, 9, 10, 11, 12],
        ),
        make_code_slide(r3_e5, r3_e4,
            heading='The Fix: Unique Letters via Set ✓',
            body='The elegant solution at 71s: use a <code>set()</code> to collect unique letters encountered. If the set reaches size 26, it\'s a pangram. This is both more correct and more Pythonic. Notice how the student cleaned up the code — the old commented section is gone. This is convergence through insight, not through exhaustion.',
            manual_highlight=[6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        ),
        {
            'type': 'summary',
            'heading': 'Key Takeaways',
            'bullets': [
                'The "false summit" — passing public tests but failing private ones — is one of the most common and instructive failure modes.',
                'The counting bug (<code>count >= 26</code>) fails when letters repeat. This requires reasoning about edge cases, not just running the public examples.',
                'Sets are the natural tool for "have I seen all 26 letters?" — this is worth teaching explicitly.',
                'The student improved on each iteration, even if it took a while. The final solution is correct and clean.',
            ],
            'intervention': 'Ask students: "Can you construct an input that passes the public tests but would fail your logic?" This builds the skill of adversarial test design — crucial for writing robust code.',
        }
    ]
}

# ─── Build replay 4: Greeting Prefix ─────────────────────────────────────────
r4_e0 = snap(R4, 0)
r4_e1 = snap(R4, 27.4)
r4_e2 = snap(R4, 59.7)
r4_e3 = snap(R4, 88.3)
r4_e4 = snap(R4, 106.3)
r4_e5 = snap(R4, 107.5)

REPLAY4 = {
    'id': 'r4',
    'title': 'Greeting Prefix',
    'subtitle': 'Thrashing to Stability',
    'question': 'Check For Greeting Prefix',
    'namespace': 'ns_25t2_py22_1',
    'duration': '1:50',
    'outcome': 'Score 100 ✓',
    'outcome_class': 'pass',
    'insight': 'High oscillation, high eventual success. The student spent 60 seconds runtime-looping before stabilizing. The final solution — after all the complexity — is just two startswith() calls.',
    'tags': ['thrashing', 'false summit', 'over-engineering'],
    'slides': [
        {
            'type': 'intro',
            'heading': 'The Problem',
            'question_desc': 'Return True if the input string starts with <code>\'Hello \'</code> (with a space) or <code>\'Hi \'</code> (with a space). Return False otherwise. <code>\'HiThere\'</code> → False, <code>\'Hi there\'</code> → True.',
            'why': 'This student took 168 attempts over 110 seconds. The problem has a simple two-line solution (<code>s.startswith(\'Hello \') or s.startswith(\'Hi \')</code>). Watch how they over-engineered it, kept adding complexity, and only simplified at the end. A case study in why simpler is usually better.',
            'what_to_look_for': [
                'The first attempt uses invalid Python: <code>startswith(\'Hello\'|| \'Hi\')</code>',
                'After 27 seconds and 42 events, still hitting runtime errors',
                'A brief public-all-pass moment that misleads — full of special cases',
                'The final clean solution is dramatically simpler than the intermediate ones',
            ],
        },
        make_code_slide(r4_e0, None,
            heading='Invalid Syntax from the Start',
            body='The very first attempt uses <strong>Line 22: <code>s.startswith(\'Hello\'|| \'Hi\')</code></strong> — <code>||</code> is not Python (it\'s JavaScript/C). Python uses <code>or</code>. This causes a SyntaxError. A language confusion error, very common when students switch between languages or guess syntax.',
            manual_highlight=[22],
        ),
        make_code_slide(r4_e1, r4_e0,
            heading='Tab Characters and Single-Character Logic',
            body='27 seconds and 42 events in, still failing. The student is now checking <strong>Line 23: <code>if s[5]="\\t"</code></strong> — (1) <code>=</code> should be <code>==</code>, (2) <code>\\t</code> is a tab, not a space. They\'ve also split "Hello" and "Hi" into separate if-blocks. This is over-engineering — the problem just needs to check the prefix. They\'re checking character positions manually.',
            manual_highlight=[22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
        ),
        make_code_slide(r4_e2, r4_e1,
            heading='Public All-Pass — But Look at the Code',
            body='At 59.7s, all 4 public tests pass. But look at <strong>Line 22: <code>if s==\'Hithere\'</code></strong> — a hardcoded special case! And <strong>Line 24: <code>startswith(\'Hello\' or \'Hi\' or \'hello\' or \'hi\')</code></strong> — <code>\'Hello\' or \'Hi\'</code> evaluates to <code>\'Hello\'</code> in Python (the first truthy string), so this only checks for \'Hello\'. The public pass is fragile.',
            manual_highlight=[22, 23, 24, 25, 26, 27, 28, 29, 30],
        ),
        make_code_slide(r4_e3, r4_e2,
            heading='Regression: Private Fails, Public Slips',
            body='After the public pass, private tests reveal only 2/3. The student tries to fix it and drops to 3/4 public. <strong>Line 27: <code>if len(s[2])==0</code></strong> — <code>s[2]</code> is a single character (not a list), so <code>len()</code> of it is always 1, never 0. This never triggers. They\'re still trying to check the character after "Hi" manually — but the built-in <code>startswith(\'Hi \')</code> already handles this.',
            manual_highlight=[23, 24, 26, 27, 28, 29, 30, 31, 32],
        ),
        make_code_slide(r4_e4, r4_e3,
            heading='Over-Engineering Phase',
            body='At 106.3s, 4/4 public pass again — but notice the complexity! The student is splitting the string, checking word counts, using a list. <strong>Lines 22–29</strong> are doing far more work than necessary. Still, the logic works for public cases. The private test is likely checking edge cases that the word-count logic mishandles.',
            manual_highlight=[22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
        ),
        make_code_slide(r4_e5, r4_e4,
            heading='The Simple Solution ✓',
            body='At 107.5s, all tests pass. After 159 events and 107 seconds of struggle, the student arrives at... two <code>startswith()</code> calls. <strong>Lines 23–27</strong> is all it needed to be. The lesson: in Python, there\'s usually a built-in that does exactly what you need. The instinct to manually parse strings character-by-character adds bugs, not precision.',
            manual_highlight=[22, 23, 24, 25, 26, 27, 28, 29, 30],
        ),
        {
            'type': 'summary',
            'heading': 'Key Takeaways',
            'bullets': [
                'Over-engineering is a real failure mode. 110 seconds of complexity, and the answer was 2 lines.',
                '<code>||</code> is not Python. Language confusion is common — students need to learn to read error messages carefully.',
                'The "or" short-circuit: <code>\'Hello\' or \'Hi\'</code> evaluates to <code>\'Hello\'</code>. This is a Python gotcha worth teaching explicitly.',
                'Hardcoded special cases (<code>if s == \'Hithere\'</code>) are a red flag — they suggest the student is pattern-matching test outputs, not solving the problem.',
            ],
            'intervention': 'When a student has 30+ attempts on a problem, ask: "Can you explain the core rule in one sentence?" If they can\'t, the algorithm is wrong. A simple rule leads to simple code. Show them: <code>return s.startswith(\'Hello \') or s.startswith(\'Hi \')</code> — done.',
        }
    ]
}

# ─── Build replay 5: Reversed Squares ────────────────────────────────────────
r5_e0 = snap(R5, 0)
r5_e1 = snap(R5, 36)
r5_e2 = snap(R5, 69.8)
r5_e3 = snap(R5, 109.9)
r5_e4 = snap(R5, 145.6)

REPLAY5 = {
    'id': 'r5',
    'title': 'Reversed Squares',
    'subtitle': 'High Effort, Repeated Runtime Failures',
    'question': 'Reversed Squares of List Elements',
    'namespace': 'ns_25t2_py22_1',
    'duration': '2:27',
    'outcome': 'Score 0 ✗',
    'outcome_class': 'fail',
    'insight': 'The session that never stabilized. 213 attempts, no passing submission. A master class in unproductive loops — and why "try more" is not the same as "debug more."',
    'tags': ['thrashing', 'no recovery', 'runtime loops', 'unproductive effort'],
    'slides': [
        {
            'type': 'intro',
            'heading': 'The Problem',
            'question_desc': 'Given a list of numbers, return a new list containing the squares of the elements in <em>reverse order</em>. So <code>[1, 2, 3]</code> → <code>[9, 4, 1]</code>.',
            'why': 'The correct solution is one line: <code>return [x**2 for x in reversed(l)]</code>. This student took 213 attempts over 147 seconds and never got there. This is the canonical "thrashing" pattern — high effort, no progress. Understanding why helps instructors intervene before students disengage completely.',
            'what_to_look_for': [
                'The first attempt calls a non-existent function <code>squares()</code>',
                'By 36 seconds, the same fundamental confusion persists — iterating but mutating the wrong thing',
                'The student keeps rewriting the same broken pattern with minor variations',
                'No single attempt lasted more than a few seconds before being replaced',
            ],
        },
        make_code_slide(r5_e0, None,
            heading='Calling a Function That Doesn\'t Exist',
            body='The first attempt: <strong>Line 21: <code>return squares(l[::-2])</code></strong>. There is no built-in or imported <code>squares()</code> function in Python. The student seems to be imagining the API rather than looking at what\'s actually available. Also, <code>l[::-2]</code> is reverse-stepping by 2, not reversing the whole list. Both the function and the slicing are wrong.',
            manual_highlight=[21],
        ),
        make_code_slide(r5_e1, r5_e0,
            heading='36 Seconds In: Still Stuck on Mutation',
            body='After 50 events and 36 seconds, the student is now iterating over the list and trying to modify it in-place: <strong>Line 23: <code>l=l[i]**l[i]</code></strong> — they\'re squaring the element with itself (not just squaring it), then assigning the result back to <code>l</code> (replacing the whole list with a number!). There\'s even dead code below: an unreachable second loop (line 25). The mental model of list operations is broken.',
            manual_highlight=[22, 23, 24, 25, 26],
        ),
        make_code_slide(r5_e2, r5_e1,
            heading='70 Seconds: Using \'int\' as a Variable Name',
            body='At 70 seconds, <strong>Line 22: <code>for int in l</code></strong> — the student has named their loop variable <code>int</code>, which shadows Python\'s built-in <code>int()</code> function. If anything else in the code uses <code>int()</code>, it will break. They\'re still assigning to <code>l</code> inside the loop, replacing the list. This is the same fundamental bug as 36 seconds ago, just rearranged.',
            manual_highlight=[22, 23, 24],
        ),
        make_code_slide(r5_e3, r5_e2,
            heading='110 Seconds: Switching to range() — Same Bug',
            body='Now using <code>range()</code> instead of iterating the list directly, but <strong>Line 23: <code>l=l[i]**2</code></strong> is still assigning to <code>l</code> (the whole list), not <code>l[i]</code>. Also, <code>i</code> comes from <code>if i in range()</code> — not valid Python (should be <code>for i in range()</code>). They\'re cycling through syntactic variations without understanding the core issue: building a <em>new list</em>.',
            manual_highlight=[21, 22, 23, 24],
        ),
        make_code_slide(r5_e4, r5_e3,
            heading='Final Submission: Still Runtime Error',
            body='The last submission at 145.8s: <strong>Line 23: <code>for m in range(0, m-1)</code></strong> — <code>m</code> is used both as the range-bound (defined from <code>m=len(l)</code>) and as the loop variable. The loop variable overwrites <code>m</code> on the first iteration, corrupting the range. Score: 0. This session never found a working solution.',
            manual_highlight=[22, 23, 24, 25, 26, 27],
        ),
        {
            'type': 'summary',
            'heading': 'Key Takeaways',
            'bullets': [
                'The correct solution is one line. The student never thought to write it that way, because they never asked: "how do I build a new list?"',
                'Mutating <code>l</code> inside a loop over <code>l</code> is a classic mistake — the student never built a temporary result list.',
                'Shadowing built-ins (<code>int</code>, <code>list</code>, <code>str</code>) as variable names breaks code in non-obvious ways.',
                'After 213 attempts with no progress, the student had exhausted their repertoire. More attempts alone don\'t produce new insight.',
            ],
            'intervention': 'When a student is in this spiral, stop the loop. Ask: "What should this function return? Show me on paper." Then: "How do you create a new list in Python?" Walk them through list comprehension: <code>[x**2 for x in reversed(l)]</code>. Sometimes the bottleneck is not debugging skill but vocabulary.',
        }
    ]
}

# ─── Build replay 6: Find Repeating Characters ────────────────────────────────
r6_e0 = snap(R6, 0)
r6_e1 = snap(R6, 1.2)
r6_e2 = snap(R6, 17.9)
r6_e3 = snap(R6, 25.8)
r6_e4 = snap(R6, 46.2)
r6_e5 = snap(R6, 56.8)

REPLAY6 = {
    'id': 'r6',
    'title': 'Find Repeating Characters',
    'subtitle': 'Early Win, Long Regression',
    'question': 'Find Characters Appearing More Than Once',
    'namespace': 'ns_25t3_py13_1',
    'duration': '1:00',
    'outcome': 'Score 33 ✗',
    'outcome_class': 'partial',
    'insight': 'A working solution at 18 seconds — then dismantled. The student passed all public tests, then "improved" the code until it broke, and never recovered their early success.',
    'tags': ['early win', 'regression', 'set semantics', 'ordering bug'],
    'slides': [
        {
            'type': 'intro',
            'heading': 'The Problem',
            'question_desc': 'Given a string, return a list of characters that appear more than once. The order of characters in the return value matters.',
            'why': 'At 18 seconds, this student had working public-pass code. The private tests revealed an ordering issue. Then they tried to fix it — and broke both public and private tests. They never recovered. This is "regression by improvement": a cautionary tale about making changes without checkpoints.',
            'what_to_look_for': [
                'The very first attempt — set subtraction — is conceptually elegant but wrong in Python',
                'By 18 seconds, a clean set-based solution passes 2/3 public tests',
                'Private tests fail immediately — ordering matters',
                'Every subsequent attempt is worse than the best intermediate solution',
            ],
        },
        make_code_slide(r6_e0, None,
            heading='Elegant but Wrong: Set Subtraction',
            body='First attempt: convert to list (<code>x</code>), convert to set (<code>s</code>), then <strong>Line 6: <code>y = x - s</code></strong>. The idea is "subtract the unique chars from all chars to get repeats." But you can\'t subtract a set from a list in Python — you\'d need <code>x - s</code> where both are sets, and even then, set subtraction isn\'t the right operation here. Causes a TypeError.',
            manual_highlight=[4, 5, 6],
        ),
        make_code_slide(r6_e1, r6_e0,
            heading='One Change: List Minus Set Still Fails',
            body='The student changes line 6 to <code>y = x</code> — just returning the full list. That\'s not the right answer either (returns all characters, not repeats). The set construction on line 5 is now unused. They\'re feeling their way forward one small change at a time.',
            manual_highlight=[4, 5, 6],
        ),
        make_code_slide(r6_e2, r6_e1,
            heading='A Working Approach — 2/3 Public Tests Pass',
            body='Around 18 seconds, the student discovers: iterate over the <em>set</em> of unique characters, check if each appears 2+ times in the original list. This is logically correct! <strong>Lines 7–9</strong> work. But private tests give 1/3. Why? Because iterating over a <code>set</code> gives results in <em>arbitrary order</em> — the expected output likely requires the characters in first-occurrence order.',
            manual_highlight=[7, 8, 9, 10],
        ),
        make_code_slide(r6_e3, r6_e2,
            heading='Iteration Order: set vs. list',
            body='The student switches: <strong>Line 7: <code>for y in x</code></strong> — now iterating over the original list <code>x</code> instead of the set <code>z</code>. This preserves insertion order! But now duplicates get appended multiple times. If "a" appears 3 times, "a" gets appended 3 times to <code>p</code>. The output has duplicate entries in the result list itself.',
            manual_highlight=[6, 7, 8, 9, 10, 11, 12, 13, 14],
        ),
        make_code_slide(r6_e4, r6_e3,
            heading='Late-Stage Complexity: Two-Pass Filter',
            body='46 seconds in, the student adds a second pass to deduplicate. But the logic is now convoluted: first pass removes singletons, second pass removes duplicates from the remaining list. <strong>Line 20: <code>z.append(p), q.remove(p)</code></strong> — this is a tuple, not two statements. Python will append the tuple itself to z, not the character. The output is broken in a new way.',
            manual_highlight=[10, 11, 12, 18, 19, 20],
        ),
        make_code_slide(r6_e5, r6_e4,
            heading='Back to a Solution — But 56 Seconds Late',
            body='At 56.8s, public tests pass again (3/3). But the private tests still fail, and the final submission scores 33. The student found a solution similar to their 18-second version — but with the same ordering issue. The early solution at 18s was the closest they got to correct. They would have needed to preserve order (iterate over <code>s</code> in original order) to fully solve it.',
            manual_highlight=[10, 11, 12, 15, 16, 17],
        ),
        {
            'type': 'summary',
            'heading': 'Key Takeaways',
            'bullets': [
                'Sets don\'t preserve order. If the problem requires a specific output order, collecting into a set and returning it will fail.',
                'The student had a near-correct solution at 18 seconds. Every subsequent change made things worse.',
                'Lesson: when you pass all public tests, <em>save that version before changing anything</em>. Test incrementally.',
                'The correct approach: iterate over the original string in order, append to result if count > 1 and not already in result.',
            ],
            'intervention': 'Teach set-vs-list ordering explicitly. Show: <code>list(set("banana"))</code> gives a different order every run. Then: "How would you preserve the original order?" This is a great moment for dict.fromkeys() or collections.OrderedDict as an advanced concept.',
        }
    ]
}

# ─── Build replay 7: Vowels vs Consonants ─────────────────────────────────────
r7_e0 = snap(R7, 0)
r7_e1 = snap(R7, 18.8)
r7_e2 = snap(R7, 38.3)
r7_e3 = snap(R7, 53.5)
r7_e4 = snap(R7, 67.3)
r7_e5 = snap(R7, 75.6)

REPLAY7 = {
    'id': 'r7',
    'title': 'Vowels vs. Consonants',
    'subtitle': 'Near Progress, No Submission',
    'question': 'Count Strings With More Vowels Than Consonants',
    'namespace': 'ns_25t3_py24_1',
    'duration': '1:16',
    'outcome': 'No submission',
    'outcome_class': 'none',
    'insight': 'The student never submitted — not because they ran out of time, but because they never felt confident enough to commit. A case study in the "last-mile gap" between near-working code and pressing submit.',
    'tags': ['no submission', 'last-mile gap', 'misconceptions', 'confusion compounding'],
    'slides': [
        {
            'type': 'intro',
            'heading': 'The Problem',
            'question_desc': 'Given a list of strings, count how many strings have more vowel characters than consonant characters. Return that count.',
            'why': 'The student reached 4/5 public tests multiple times — close enough to suspect they could solve it. But they never submitted. This happens when students lose confidence in the middle of a session and keep trying to "make sure" without ever committing. The question for instructors: when and how do you intervene?',
            'what_to_look_for': [
                'Fundamental misunderstanding: treating the whole list as a single string',
                'Using <code>help()</code> in the middle of a contest — unusual, and probably ineffective here',
                'Code inside docstrings — the student "commented out" logic by wrapping it in a string',
                'Near-breakthrough: 4/5 public, then runtime relapse',
            ],
        },
        make_code_slide(r7_e0, None,
            heading='Wrong Input: Treating a List as Strings',
            body='The first attempt: <strong>Line 8: <code>for word in words</code></strong> — but the parameter is <code>strings</code>, not <code>words</code>. NameError. Also, <strong>Lines 9–12</strong>: the logic checks <code>if word in \'aeiou\'</code> — this tests whether the <em>whole word</em> is a vowel (i.e., is the word one of the vowel characters?). The correct logic should iterate over each character within each word.',
            manual_highlight=[7, 8, 9, 10, 11, 12, 13],
        ),
        make_code_slide(r7_e1, r7_e0,
            heading='18 Seconds: Calling a Non-Existent count()',
            body='Now using <code>strings</code> (correct), but <strong>Line 12: <code>c = count(strings)</code></strong> — there\'s no built-in <code>count()</code> function that takes a list. They might be thinking of <code>list.count()</code>, but that counts specific elements. And the logic is still wrong: it still checks <code>if word in \'aeiou\'</code> — testing whole words against the vowel string. The student is confused about the problem structure: "list of strings" vs "characters in a string."',
            manual_highlight=[9, 10, 11, 12, 13, 14, 15, 16, 17],
        ),
        make_code_slide(r7_e2, r7_e1,
            heading='38 Seconds: A Docstring Misused as Comments',
            body='Lines 4–7 are now inside a docstring — the student effectively "commented out" logic by wrapping it in triple quotes. But the active code (<strong>Lines 8–17</strong>) now checks <code>if strings[0:n] == "aeiou"</code> — comparing a slice of the <em>list</em> to a string "aeiou". This will never be True. The logic of counting vowels per string is still completely absent.',
            manual_highlight=[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        ),
        make_code_slide(r7_e3, r7_e2,
            heading='4/5 Public Tests: A Surprising Near-Success',
            body='At 53.5 seconds, 4/5 public tests pass — despite the logic being fundamentally wrong! <strong>Line 6: <code>return strings.count("aeiou") + 1</code></strong> — this counts occurrences of the substring "aeiou" in the list... which will always be 0 since "aeiou" is not a string in the list. Adding 1 gives... 1. So the function always returns 1. And 4 of the 5 public test cases apparently expect the answer 1.',
            manual_highlight=[5, 6, 7],
        ),
        make_code_slide(r7_e4, r7_e3,
            heading='67 Seconds: Still 4/5, Private Still 0',
            body='The same broken code persists: always returning 1. The 4/5 public score is luck, not logic. Private tests expose this immediately — 0/2 private. The student might think they\'re close; they\'re not. The gap between 4/5 and a correct solution is enormous. Without being able to see the private test cases, they can\'t even verify what\'s wrong.',
            manual_highlight=[5, 6, 7],
        ),
        make_code_slide(r7_e5, r7_e4,
            heading='75 Seconds: Private Still 0, No Submission',
            body='Right before the session ends, the student is still at 4/5 public, 0 private. The code (not shown — empty frame) hasn\'t changed meaningfully in the last 8 seconds. They may have run out of ideas, lost confidence, or simply run out of time. No submission is made. The "last-mile gap" — functional code is possible, but confidence isn\'t there to commit.',
            manual_highlight=[5, 6, 7, 8, 9],
        ),
        {
            'type': 'summary',
            'heading': 'Key Takeaways',
            'bullets': [
                'A score of 4/5 public can be achieved by a function that always returns 1 — public test sets can be misleadingly easy to "game."',
                'The core confusion: the problem asks about <em>characters in a string</em>, not about <em>strings in a list</em>. Two nested loops were needed but never attempted.',
                'The docstring-as-comment pattern shows the student doesn\'t know how to properly comment out code.',
                'No submission at the end of the session is often a confidence issue, not a technical one.',
            ],
            'intervention': 'Before coding, ask students to trace through an example on paper: "Given [\'hello\', \'sky\'], walk me through what the function should do step by step." This surfaces the "characters vs strings" confusion before a single line of code is written. And when a student is near the deadline with partial credit, encourage them to submit — partial credit is better than zero.',
        }
    ]
}

ALL_REPLAYS = [REPLAY1, REPLAY2, REPLAY3, REPLAY4, REPLAY5, REPLAY6, REPLAY7]

# Save data
with open('/tmp/replays_v3_data.json', 'w') as f:
    json.dump(ALL_REPLAYS, f, indent=2)
print("Data saved.")
print(f"Total replays: {len(ALL_REPLAYS)}")
for r in ALL_REPLAYS:
    print(f"  {r['id']}: {r['title']} — {len(r['slides'])} slides")

# ─── HTML GENERATION ──────────────────────────────────────────────────────────

def esc(s): return html.escape(str(s))

def status_class(summary):
    s = (summary or '').lower()
    if 'all cases passed' in s or 'passed' in s: return 'status-pass'
    if 'runtime' in s: return 'status-runtime'
    if 'wrong' in s: return 'status-wrong'
    return 'status-other'

def status_icon(summary):
    s = (summary or '').lower()
    if 'all cases passed' in s: return '✓'
    if 'runtime' in s: return '⚡'
    if 'wrong' in s: return '✗'
    return '?'

def render_code_block(code, added, changed, highlight):
    """Render code with line highlights.
    If manual highlight lines are given, suppress diff highlights (they'd be noise).
    """
    if not code or not code.strip():
        return '<div class="code-empty">No code changes in this event.</div>'
    lines = code.split('\n')
    # Suppress diff colours when manual focus lines are specified
    show_diff = not highlight
    out = ['<pre class="code-block"><code>']
    for i, line in enumerate(lines):
        ln = i + 1
        classes = ['code-line']
        if ln in highlight:
            classes.append('hl-focus')
        elif show_diff and ln in added:
            classes.append('hl-added')
        elif show_diff and ln in changed:
            classes.append('hl-changed')
        line_esc = esc(line) if line else '\u00a0'  # non-breaking space for empty lines
        out.append(f'<span class="{" ".join(classes)}" data-ln="{ln}">{line_esc}</span>')
    out.append('</code></pre>')
    return '\n'.join(out)

def render_slide(slide, slide_idx, replay_id):
    stype = slide['type']
    
    if stype == 'intro':
        wlf = ''.join(f'<li>{item}</li>' for item in slide.get('what_to_look_for', []))
        return f'''
<div class="slide slide-intro" id="{replay_id}-s{slide_idx}">
  <div class="slide-content slide-content-intro">
    <div class="slide-left">
      <div class="slide-badge badge-intro">The Problem</div>
      <h2 class="slide-heading">{esc(slide["heading"])}</h2>
      <div class="question-desc">{slide["question_desc"]}</div>
      <div class="why-box">
        <div class="why-label">Why this replay?</div>
        <p>{esc(slide["why"])}</p>
      </div>
    </div>
    <div class="slide-right slide-right-intro">
      <div class="look-for-box">
        <div class="look-for-label">👁 What to look for</div>
        <ul class="look-for-list">{wlf}</ul>
      </div>
    </div>
  </div>
</div>'''

    elif stype == 'code':
        status = slide.get('status', '?')
        tests_pass = slide.get('tests_pass', 0)
        tests_total = slide.get('tests_total', 0)
        vis = slide.get('visibility', 'public')
        time_label = slide.get('time_label', '?')
        sc = status_class(status)
        si = status_icon(status)
        code_html = render_code_block(
            slide.get('code',''),
            slide.get('added',[]),
            slide.get('changed',[]),
            slide.get('highlight',[])
        )
        return f'''
<div class="slide slide-code" id="{replay_id}-s{slide_idx}">
  <div class="slide-content slide-content-code">
    <div class="slide-code-panel">
      <div class="code-header">
        <div class="code-header-left">
          <span class="time-badge">{esc(time_label)}</span>
          <span class="vis-badge vis-{vis}">{vis}</span>
        </div>
        <div class="{sc} status-badge">{si} {esc(status)} &nbsp; {tests_pass}/{tests_total}</div>
      </div>
      <div class="code-scroll-area" data-first-focus="{(slide.get('highlight') or [None])[0] or ''}">{code_html}</div>
    </div>
    <div class="slide-commentary">
      <h3 class="commentary-heading">{esc(slide["heading"])}</h3>
      <div class="commentary-body">{slide["body"]}</div>
      <div class="diff-legend">
        <span class="legend-item"><span class="legend-swatch hl-focus-sw"></span>Focus</span>
        {'<span class="legend-item"><span class="legend-swatch hl-added-sw"></span>New</span><span class="legend-item"><span class="legend-swatch hl-changed-sw"></span>Changed</span>' if not slide.get('highlight') else ''}
      </div>
    </div>
  </div>
</div>'''

    elif stype == 'summary':
        bullets = ''.join(f'<li>{b}</li>' for b in slide.get('bullets', []))
        return f'''
<div class="slide slide-summary" id="{replay_id}-s{slide_idx}">
  <div class="slide-content slide-content-summary">
    <div class="slide-left">
      <div class="slide-badge badge-summary">Key Takeaways</div>
      <h2 class="slide-heading">{esc(slide["heading"])}</h2>
      <ul class="summary-bullets">{bullets}</ul>
    </div>
    <div class="slide-right">
      <div class="intervention-box">
        <div class="intervention-label">💡 Instructor Intervention</div>
        <p>{slide.get("intervention","")}</p>
      </div>
    </div>
  </div>
</div>'''
    return ''

def render_replay_section(replay):
    rid = replay['id']
    slides_html = []
    for i, slide in enumerate(replay['slides']):
        slides_html.append(render_slide(slide, i, rid))
    
    oc = replay.get('outcome_class', 'pass')
    outcome_cls = f'outcome-{oc}'
    tags = ' '.join(f'<span class="tag">{esc(t)}</span>' for t in replay.get('tags', []))
    
    return f'''
<!-- ═══ REPLAY: {esc(replay["title"])} ═══ -->
<section class="replay-section" id="replay-{rid}" data-replay="{rid}" data-slide-count="{len(replay['slides'])}">
  <div class="replay-header">
    <div class="replay-header-left">
      <div class="replay-number">Replay {rid[1]}/7</div>
      <div class="replay-meta-row">
        <span class="replay-question">{esc(replay.get("question",""))}</span>
        <span class="replay-duration">⏱ {esc(replay.get("duration",""))}</span>
        <span class="replay-outcome {outcome_cls}">{esc(replay.get("outcome",""))}</span>
      </div>
      <h2 class="replay-title">{esc(replay["title"])}</h2>
      <p class="replay-subtitle">{esc(replay["subtitle"])}</p>
      <div class="replay-tags">{tags}</div>
    </div>
    <button class="toc-back-btn" onclick="showCover()">← All Replays</button>
  </div>
  
  <div class="slides-container" id="slides-{rid}">
    {"".join(slides_html)}
  </div>
  
  <div class="slide-nav" id="nav-{rid}">
    <button class="nav-btn" id="prev-{rid}" onclick="prevSlide('{rid}')" disabled>← Prev</button>
    <div class="slide-dots" id="dots-{rid}"></div>
    <div class="slide-counter" id="counter-{rid}">1 / {len(replay['slides'])}</div>
    <button class="nav-btn" id="next-{rid}" onclick="nextSlide('{rid}')">Next →</button>
  </div>
</section>'''

# Cover slide
def render_cover(replays):
    cards = []
    outcome_icons = {'pass': '✅', 'fail': '❌', 'partial': '⚠️', 'none': '⬜'}
    for r in replays:
        oc = r.get('outcome_class', 'pass')
        icon = outcome_icons.get(oc, '?')
        tags = ' '.join(f'<span class="tag tag-sm">{esc(t)}</span>' for t in r.get('tags', [])[:2])
        n_slides = len(r['slides'])
        cards.append(f'''
    <button class="toc-card" onclick="showReplay('{r["id"]}')" aria-label="Go to {esc(r["title"])}">
      <div class="toc-card-num">{r["id"][1]}</div>
      <div class="toc-card-body">
        <div class="toc-card-header">
          <span class="toc-outcome {oc}">{icon} {esc(r["outcome"])}</span>
          <span class="toc-duration">⏱ {esc(r.get("duration","?"))}</span>
        </div>
        <h3 class="toc-title">{esc(r["title"])}</h3>
        <p class="toc-subtitle">{esc(r["subtitle"])}</p>
        <p class="toc-insight">{esc(r["insight"])}</p>
        <div class="toc-footer">
          <div class="toc-tags">{tags}</div>
          <span class="toc-slides">{n_slides} slides</span>
        </div>
      </div>
    </button>''')
    
    return f'''
<section class="cover-section" id="cover">
  <div class="cover-hero">
    <div class="cover-kicker">PyOPPE · Student Replay Analysis</div>
    <h1 class="cover-title">7 Students.<br>7 Debugging Stories.</h1>
    <p class="cover-lead">Each replay shows a student solving a Python problem in real time. Step through code frame by frame — see what they were thinking, where they went wrong, and what we can learn from their journey.</p>
    <div class="cover-stats">
      <div class="cover-stat"><span class="cover-stat-num">7</span><span class="cover-stat-label">Replays</span></div>
      <div class="cover-stat"><span class="cover-stat-num">3</span><span class="cover-stat-label">Full passes</span></div>
      <div class="cover-stat"><span class="cover-stat-num">1</span><span class="cover-stat-label">Partial</span></div>
      <div class="cover-stat"><span class="cover-stat-num">3</span><span class="cover-stat-label">Fails / no sub</span></div>
    </div>
  </div>
  <div class="toc-grid">
    {"".join(cards)}
  </div>
  <div class="cover-footer">Click any card to explore that replay · Arrow keys or buttons to navigate slides</div>
</section>'''


HTML_HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Student Replay Walkthrough | PyOPPE</title>
  <meta name="description" content="Step-by-step narrative walkthrough of 7 student coding replays with commentary, code diffs, and teaching insights.">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect fill='%230f776f' width='64' height='64' rx='10'/%3E%3Ctext x='32' y='38' text-anchor='middle' dominant-baseline='middle' font-size='36' font-family='monospace'%3E▶%3C/text%3E%3C/svg%3E"/>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Fraunces:opsz,wght@9..144,600;9..144,700;9..144,800&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    /* ── Reset & Variables ─────────────────────────── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg:          #f5f2e9;
      --surface:     #fffdf8;
      --surface2:    #ffffff;
      --border:      #ddd9cf;
      --ink:         #152229;
      --muted:       #5a6670;
      --accent:      #0f776f;
      --accent-lite: #e0f4f2;
      --accent2:     #1b5da3;
      --warn:        #a05400;
      --warn-lite:   #fef3e2;
      --err:         #b92035;
      --err-lite:    #fde8ea;
      --ok:          #1a7d44;
      --ok-lite:     #e0f5ea;
      --code-bg:     #0d1117;
      --code-ink:    #c9d1d9;
      --shadow:      0 8px 32px rgba(21,34,41,0.12);
      --shadow-lg:   0 20px 60px rgba(21,34,41,0.18);
      --radius:      16px;
      --radius-sm:   8px;
    }

    html, body { height: 100%; }
    body {
      font-family: "Outfit", sans-serif;
      color: var(--ink);
      background: var(--bg);
      min-height: 100vh;
      overflow-x: hidden;
    }

    /* ── App Shell ─────────────────────────────────── */
    .app { min-height: 100vh; }

    /* ── Cover / TOC ───────────────────────────────── */
    .cover-section {
      max-width: 1320px;
      margin: 0 auto;
      padding: 3rem 2rem 4rem;
    }
    .cover-hero {
      text-align: center;
      margin-bottom: 3rem;
    }
    .cover-kicker {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--accent);
      background: var(--accent-lite);
      border: 1px solid rgba(15,119,111,0.3);
      padding: 0.28rem 0.7rem;
      border-radius: 999px;
      display: inline-block;
      margin-bottom: 1.2rem;
    }
    .cover-title {
      font-family: "Fraunces", serif;
      font-size: clamp(2.4rem, 6vw, 4.2rem);
      line-height: 1.05;
      margin-bottom: 1rem;
      color: var(--ink);
    }
    .cover-lead {
      color: var(--muted);
      font-size: 1.1rem;
      max-width: 68ch;
      margin: 0 auto 1.8rem;
      line-height: 1.7;
    }
    .cover-stats {
      display: flex;
      gap: 2rem;
      justify-content: center;
      margin-bottom: 0.5rem;
    }
    .cover-stat { text-align: center; }
    .cover-stat-num {
      display: block;
      font-family: "Fraunces", serif;
      font-size: 2.4rem;
      color: var(--accent);
      line-height: 1;
    }
    .cover-stat-label {
      font-size: 0.78rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    /* TOC Grid */
    .toc-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 1.2rem;
      margin-bottom: 2rem;
    }
    .toc-card {
      display: flex;
      gap: 1rem;
      background: var(--surface);
      border: 1.5px solid var(--border);
      border-radius: var(--radius);
      padding: 1.2rem;
      text-align: left;
      cursor: pointer;
      transition: transform 140ms ease, box-shadow 140ms ease, border-color 140ms ease;
      box-shadow: 0 2px 8px rgba(21,34,41,0.06);
    }
    .toc-card:hover {
      transform: translateY(-3px);
      box-shadow: var(--shadow);
      border-color: var(--accent);
    }
    .toc-card-num {
      font-family: "Fraunces", serif;
      font-size: 2.8rem;
      color: var(--accent);
      line-height: 1;
      min-width: 2rem;
      padding-top: 0.1rem;
    }
    .toc-card-body { flex: 1; }
    .toc-card-header {
      display: flex;
      align-items: center;
      gap: 0.6rem;
      margin-bottom: 0.4rem;
    }
    .toc-outcome {
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.18rem 0.5rem;
      border-radius: 999px;
    }
    .toc-outcome.pass   { background: var(--ok-lite);   color: var(--ok); }
    .toc-outcome.fail   { background: var(--err-lite);  color: var(--err); }
    .toc-outcome.partial{ background: var(--warn-lite); color: var(--warn); }
    .toc-outcome.none   { background: #f0f0f0;          color: var(--muted); }
    .toc-duration { font-size: 0.78rem; color: var(--muted); }
    .toc-title {
      font-family: "Fraunces", serif;
      font-size: 1.15rem;
      margin-bottom: 0.15rem;
      color: var(--ink);
    }
    .toc-subtitle {
      font-size: 0.82rem;
      color: var(--muted);
      margin-bottom: 0.5rem;
    }
    .toc-insight {
      font-size: 0.9rem;
      color: var(--ink);
      line-height: 1.55;
      margin-bottom: 0.7rem;
    }
    .toc-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .toc-tags { display: flex; gap: 0.4rem; flex-wrap: wrap; }
    .tag, .tag-sm {
      font-size: 0.72rem;
      padding: 0.18rem 0.5rem;
      background: var(--accent-lite);
      color: var(--accent);
      border-radius: 999px;
      white-space: nowrap;
    }
    .toc-slides { font-size: 0.75rem; color: var(--muted); }
    .cover-footer {
      text-align: center;
      font-size: 0.82rem;
      color: var(--muted);
    }

    /* ── Replay Section ────────────────────────────── */
    .replay-section {
      display: none;
      flex-direction: column;
      min-height: 100vh;
    }
    .replay-section.active { display: flex; }

    .replay-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      padding: 1.2rem 2rem 1rem;
      background: var(--surface2);
      border-bottom: 1px solid var(--border);
      flex-shrink: 0;
      gap: 1rem;
    }
    .replay-header-left { flex: 1; }
    .replay-number {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--accent);
      margin-bottom: 0.25rem;
    }
    .replay-meta-row {
      display: flex;
      align-items: center;
      gap: 0.8rem;
      margin-bottom: 0.3rem;
      flex-wrap: wrap;
    }
    .replay-question { font-size: 0.82rem; color: var(--muted); }
    .replay-duration { font-size: 0.78rem; color: var(--muted); }
    .replay-outcome {
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.15rem 0.5rem;
      border-radius: 999px;
    }
    .replay-outcome.outcome-pass    { background: var(--ok-lite);   color: var(--ok); }
    .replay-outcome.outcome-fail    { background: var(--err-lite);  color: var(--err); }
    .replay-outcome.outcome-partial { background: var(--warn-lite); color: var(--warn); }
    .replay-outcome.outcome-none    { background: #f0f0f0;          color: var(--muted); }
    .replay-title {
      font-family: "Fraunces", serif;
      font-size: 1.6rem;
      line-height: 1.1;
      margin-bottom: 0.15rem;
    }
    .replay-subtitle {
      font-size: 0.88rem;
      color: var(--muted);
      margin-bottom: 0.5rem;
    }
    .replay-tags { display: flex; gap: 0.4rem; flex-wrap: wrap; }
    .toc-back-btn {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 0.5rem 1rem;
      font: 0.84rem "Outfit", sans-serif;
      color: var(--muted);
      cursor: pointer;
      white-space: nowrap;
      transition: background 120ms, color 120ms;
      flex-shrink: 0;
      margin-top: 0.3rem;
    }
    .toc-back-btn:hover { background: var(--border); color: var(--ink); }

    /* ── Slides Container ──────────────────────────── */
    .slides-container {
      flex: 1;
      overflow: hidden;
      position: relative;
    }
    .slide {
      display: none;
      height: 100%;
      min-height: calc(100vh - 200px);
    }
    .slide.active { display: flex; }

    /* ── Slide Content Layouts ─────────────────────── */
    .slide-content {
      display: flex;
      width: 100%;
      height: 100%;
    }
    
    /* Intro slide */
    .slide-content-intro {
      padding: 2.5rem 2rem;
      gap: 3rem;
    }
    .slide-left {
      flex: 1.1;
      max-width: 560px;
    }
    .slide-right { flex: 1; }
    .slide-right-intro {
      display: flex;
      align-items: flex-start;
    }
    .slide-badge {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.68rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      padding: 0.25rem 0.65rem;
      border-radius: 999px;
      display: inline-block;
      margin-bottom: 0.8rem;
    }
    .badge-intro  { background: var(--accent-lite); color: var(--accent); }
    .badge-summary{ background: #eef1ff; color: #3044c9; }
    .slide-heading {
      font-family: "Fraunces", serif;
      font-size: clamp(1.5rem, 3vw, 2.2rem);
      line-height: 1.15;
      margin-bottom: 0.8rem;
      color: var(--ink);
    }
    .question-desc {
      font-size: 1rem;
      line-height: 1.7;
      color: var(--ink);
      background: var(--surface2);
      border-left: 3px solid var(--accent);
      padding: 0.8rem 1rem;
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
      margin-bottom: 1.2rem;
    }
    .why-box {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 1rem;
    }
    .why-label {
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: var(--muted);
      margin-bottom: 0.4rem;
    }
    .why-box p { font-size: 0.95rem; color: var(--ink); line-height: 1.65; }
    .look-for-box {
      background: var(--surface2);
      border: 1.5px solid var(--accent);
      border-radius: var(--radius-sm);
      padding: 1.2rem;
      width: 100%;
    }
    .look-for-label {
      font-weight: 600;
      font-size: 0.88rem;
      color: var(--accent);
      margin-bottom: 0.7rem;
    }
    .look-for-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.55rem;
    }
    .look-for-list li {
      font-size: 0.92rem;
      padding-left: 1.2rem;
      position: relative;
      line-height: 1.5;
      color: var(--ink);
    }
    .look-for-list li::before {
      content: "→";
      position: absolute;
      left: 0;
      color: var(--accent);
      font-weight: 700;
    }

    /* Code slide */
    .slide-content-code {
      flex-direction: row;
      height: 100%;
      min-height: calc(100vh - 200px);
    }
    .slide-code-panel {
      flex: 1.3;
      background: var(--code-bg);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      border-right: 1px solid #1e2935;
    }
    .code-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.65rem 1rem;
      background: #161b22;
      border-bottom: 1px solid #21262d;
      flex-shrink: 0;
    }
    .code-header-left { display: flex; gap: 0.5rem; align-items: center; }
    .time-badge {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.7rem;
      background: #21262d;
      color: #8b949e;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
    }
    .vis-badge {
      font-size: 0.7rem;
      font-weight: 600;
      padding: 0.18rem 0.5rem;
      border-radius: 999px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .vis-public  { background: #1f4068; color: #79c0ff; }
    .vis-private { background: #3d2b1f; color: #ffa657; }
    .status-badge {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.72rem;
      font-weight: 600;
      padding: 0.2rem 0.65rem;
      border-radius: 4px;
    }
    .status-pass    { background: #0d3321; color: #3fb950; }
    .status-runtime { background: #2d1117; color: #f85149; }
    .status-wrong   { background: #2d2000; color: #e3b341; }
    .status-other   { background: #21262d; color: #8b949e; }

    .code-scroll-area {
      flex: 1;
      overflow-y: auto;
      padding: 0.8rem 0;
      max-height: calc(100vh - 320px);
      min-height: 300px;
    }
    .code-block {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.82rem;
      line-height: 1.65;
      color: var(--code-ink);
      white-space: pre;
    }
    .code-block code { display: block; }
    .code-line {
      display: block;
      padding: 0 1.2rem;
      position: relative;
      transition: background 0.2s;
    }
    .code-line::before {
      content: attr(data-ln);
      display: inline-block;
      width: 2.2em;
      color: #484f58;
      text-align: right;
      margin-right: 1em;
      user-select: none;
      font-size: 0.78rem;
    }
    .hl-focus {
      background: rgba(210, 153, 34, 0.22);
      box-shadow: inset 3px 0 0 #d29922;
    }
    .hl-added {
      background: rgba(63, 185, 80, 0.15);
      box-shadow: inset 3px 0 0 #3fb950;
    }
    .hl-changed {
      background: rgba(121, 192, 255, 0.12);
      box-shadow: inset 3px 0 0 #79c0ff;
    }
    .code-empty {
      padding: 2rem;
      color: #484f58;
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.84rem;
    }

    /* Commentary panel */
    .slide-commentary {
      width: 380px;
      min-width: 320px;
      max-width: 420px;
      padding: 2rem 1.8rem;
      background: var(--surface);
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 1rem;
      flex-shrink: 0;
    }
    .commentary-heading {
      font-family: "Fraunces", serif;
      font-size: 1.3rem;
      line-height: 1.25;
      color: var(--ink);
    }
    .commentary-body {
      font-size: 0.92rem;
      line-height: 1.72;
      color: var(--ink);
    }
    .commentary-body code {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.82em;
      background: #e8e4d8;
      padding: 0.1em 0.35em;
      border-radius: 3px;
    }
    .commentary-body strong { color: var(--ink); font-weight: 700; }
    .commentary-body em { color: var(--muted); }
    .diff-legend {
      display: flex;
      gap: 1rem;
      padding-top: 0.5rem;
      border-top: 1px solid var(--border);
      margin-top: auto;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.75rem;
      color: var(--muted);
    }
    .legend-swatch {
      display: inline-block;
      width: 12px;
      height: 12px;
      border-radius: 2px;
    }
    .hl-focus-sw   { background: rgba(210,153,34,0.5); border-left: 3px solid #d29922; }
    .hl-added-sw   { background: rgba(63,185,80,0.3);  border-left: 3px solid #3fb950; }
    .hl-changed-sw { background: rgba(121,192,255,0.2);border-left: 3px solid #79c0ff; }

    /* Summary slide */
    .slide-content-summary {
      padding: 2.5rem 2rem;
      gap: 3rem;
    }
    .summary-bullets {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.9rem;
    }
    .summary-bullets li {
      font-size: 0.98rem;
      padding: 0.7rem 0.9rem 0.7rem 1.1rem;
      background: var(--surface2);
      border-left: 3px solid var(--accent);
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
      line-height: 1.6;
    }
    .summary-bullets li em { color: var(--muted); }
    .intervention-box {
      background: linear-gradient(135deg, #fffdf0, #fff8e1);
      border: 1.5px solid #f5c518;
      border-radius: var(--radius-sm);
      padding: 1.4rem;
    }
    .intervention-label {
      font-weight: 700;
      font-size: 0.9rem;
      color: #8a6000;
      margin-bottom: 0.6rem;
    }
    .intervention-box p {
      font-size: 0.93rem;
      color: var(--ink);
      line-height: 1.7;
    }
    .intervention-box code {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.82em;
      background: rgba(0,0,0,0.08);
      padding: 0.1em 0.35em;
      border-radius: 3px;
    }

    /* ── Navigation Bar ────────────────────────────── */
    .slide-nav {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 0.8rem 2rem;
      background: var(--surface2);
      border-top: 1px solid var(--border);
      flex-shrink: 0;
    }
    .nav-btn {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 0.52rem 1.2rem;
      font: 0.88rem "Outfit", sans-serif;
      color: var(--ink);
      cursor: pointer;
      transition: background 120ms, transform 80ms;
    }
    .nav-btn:hover:not(:disabled) { background: var(--accent-lite); color: var(--accent); }
    .nav-btn:active:not(:disabled) { transform: scale(0.97); }
    .nav-btn:disabled { opacity: 0.35; cursor: default; }
    .slide-dots {
      display: flex;
      gap: 0.45rem;
      flex: 1;
    }
    .dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      background: var(--border);
      cursor: pointer;
      transition: background 200ms, transform 200ms;
      flex-shrink: 0;
    }
    .dot.active { background: var(--accent); transform: scale(1.4); }
    .dot:hover:not(.active) { background: var(--muted); }
    .slide-counter {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.78rem;
      color: var(--muted);
      white-space: nowrap;
    }

    /* ── Keyboard hint ─────────────────────────────── */
    .kbd-hint {
      position: fixed;
      bottom: 5rem;
      right: 1.5rem;
      font-size: 0.72rem;
      color: var(--muted);
      background: var(--surface2);
      border: 1px solid var(--border);
      padding: 0.35rem 0.7rem;
      border-radius: var(--radius-sm);
      opacity: 0;
      transition: opacity 0.5s;
      pointer-events: none;
    }
    .kbd-hint.visible { opacity: 1; }
    kbd {
      background: var(--border);
      border-radius: 3px;
      padding: 0.1em 0.35em;
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.85em;
    }

    /* ── Responsive ────────────────────────────────── */
    @media (max-width: 900px) {
      .slide-content-code { flex-direction: column; }
      .slide-commentary {
        width: 100%;
        max-width: none;
        min-height: 200px;
      }
      .slide-code-panel { min-height: 40vh; }
      .toc-grid { grid-template-columns: 1fr; }
      .slide-content-intro,
      .slide-content-summary { flex-direction: column; }
    }
    @media (max-width: 640px) {
      .replay-header { flex-wrap: wrap; }
      .cover-stats { gap: 1rem; }
    }
  </style>
</head>
<body>
<div class="app" id="app">
'''

HTML_JS = '''
</div><!-- /app -->

<div class="kbd-hint" id="kbd-hint"><kbd>←</kbd> <kbd>→</kbd> navigate</div>

<script>
// ─── State ────────────────────────────────────────────────────────────────────
let currentReplay = null;
const slideState = {};  // rid -> slideIndex

// ─── Navigation ───────────────────────────────────────────────────────────────
function showCover() {
  document.getElementById('cover').style.display = 'block';
  if (currentReplay) {
    document.getElementById(`replay-${currentReplay}`).classList.remove('active');
  }
  currentReplay = null;
  history.pushState({}, '', '#');
}

function showReplay(rid) {
  document.getElementById('cover').style.display = 'none';
  if (currentReplay && currentReplay !== rid) {
    document.getElementById(`replay-${currentReplay}`).classList.remove('active');
  }
  currentReplay = rid;
  const section = document.getElementById(`replay-${rid}`);
  section.classList.add('active');
  
  if (!(rid in slideState)) {
    slideState[rid] = 0;
    initDots(rid);
  }
  goToSlide(rid, slideState[rid]);
  history.pushState({replay: rid}, '', `#${rid}`);
  
  // Show keyboard hint briefly
  const hint = document.getElementById('kbd-hint');
  hint.classList.add('visible');
  setTimeout(() => hint.classList.remove('visible'), 2500);
}

function initDots(rid) {
  const section = document.getElementById(`replay-${rid}`);
  const count = parseInt(section.dataset.slideCount);
  const dotsEl = document.getElementById(`dots-${rid}`);
  dotsEl.innerHTML = '';
  for (let i = 0; i < count; i++) {
    const d = document.createElement('button');
    d.className = 'dot' + (i === 0 ? ' active' : '');
    d.setAttribute('aria-label', `Slide ${i+1}`);
    d.onclick = () => goToSlide(rid, i);
    dotsEl.appendChild(d);
  }
}

function goToSlide(rid, idx) {
  const section = document.getElementById(`replay-${rid}`);
  const slides = section.querySelectorAll('.slide');
  const count = slides.length;
  if (idx < 0 || idx >= count) return;
  
  slides.forEach((s, i) => s.classList.toggle('active', i === idx));
  
  const dots = document.querySelectorAll(`#dots-${rid} .dot`);
  dots.forEach((d, i) => d.classList.toggle('active', i === idx));
  
  document.getElementById(`counter-${rid}`).textContent = `${idx+1} / ${count}`;
  document.getElementById(`prev-${rid}`).disabled = idx === 0;
  document.getElementById(`next-${rid}`).disabled = idx === count - 1;
  
  slideState[rid] = idx;

  // Auto-scroll the code panel to show the first focused line.
  // Use requestAnimationFrame to ensure layout is computed after display:flex applied.
  const activeSlide = slides[idx];
  if (activeSlide) {
    requestAnimationFrame(() => {
      const scrollArea = activeSlide.querySelector('.code-scroll-area');
      const firstFocus = scrollArea && scrollArea.querySelector('.hl-focus');
      if (firstFocus && scrollArea) {
        // scrollIntoView scrolls the nearest scrollable ancestor (code-scroll-area)
        firstFocus.scrollIntoView({block: 'center', behavior: 'instant'});
      } else if (scrollArea) {
        scrollArea.scrollTop = 0;
      }
    });
  }
}

function nextSlide(rid) {
  const idx = slideState[rid] || 0;
  goToSlide(rid, idx + 1);
}

function prevSlide(rid) {
  const idx = slideState[rid] || 0;
  goToSlide(rid, idx - 1);
}

// ─── Keyboard Navigation ──────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
  if (!currentReplay) return;
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
    e.preventDefault();
    nextSlide(currentReplay);
  } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
    e.preventDefault();
    prevSlide(currentReplay);
  } else if (e.key === 'Escape') {
    showCover();
  }
});

// ─── Handle hash navigation ───────────────────────────────────────────────────
function handleHash() {
  const h = location.hash.replace('#', '');
  if (h && document.getElementById(`replay-${h}`)) {
    showReplay(h);
  }
}
window.addEventListener('popstate', handleHash);
handleHash();
</script>
</body>
</html>
'''

# ─── ASSEMBLE ─────────────────────────────────────────────────────────────────

out_path = '/home/vscode/code/pyoppe/analysis/replays-v3.html'

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(HTML_HEAD)
    f.write(render_cover(ALL_REPLAYS))
    for replay in ALL_REPLAYS:
        f.write(render_replay_section(replay))
    f.write(HTML_JS)

print(f"Written: {out_path}")
import os
print(f"Size: {os.path.getsize(out_path):,} bytes")
