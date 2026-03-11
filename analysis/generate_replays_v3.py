#!/usr/bin/env python3
"""
Generate analysis/replays-v3.html - a slideshow walkthrough of 7 student replays.
"""
import json, re, html, difflib, tokenize, io
import token as _tk

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

# ─── PYTHON SYNTAX HIGHLIGHTER ────────────────────────────────────────────────

_PY_KEYWORDS = frozenset({
    'False','None','True','and','as','assert','async','await','break',
    'class','continue','def','del','elif','else','except','finally',
    'for','from','global','if','import','in','is','lambda','nonlocal',
    'not','or','pass','raise','return','try','while','with','yield',
})
_PY_BUILTINS = frozenset({
    'abs','all','any','bin','bool','callable','chr','dict','dir','divmod',
    'enumerate','eval','exec','filter','float','format','getattr','globals',
    'hasattr','hash','help','hex','id','input','int','isinstance','issubclass',
    'iter','len','list','locals','map','max','min','next','object','oct',
    'open','ord','pow','print','property','range','repr','reversed','round',
    'set','setattr','slice','sorted','staticmethod','str','sum','super',
    'tuple','type','vars','zip',
})

def _classify(tok_type, tok_string):
    if tok_type == _tk.COMMENT:   return 'tk-cmt'
    if tok_type == _tk.STRING:    return 'tk-str'
    if tok_type == _tk.NUMBER:    return 'tk-num'
    if tok_type == _tk.NAME:
        if tok_string in _PY_KEYWORDS: return 'tk-kw'
        if tok_string in _PY_BUILTINS: return 'tk-bi'
        return None
    if tok_type == _tk.OP:
        if tok_string in '()[]{}': return 'tk-brk'
        return 'tk-op'
    return None

def highlight_python(code):
    """Return list of per-line HTML strings with syntax highlighting spans."""
    raw_lines = code.split('\n')
    result = [html.escape(l) if l else '' for l in raw_lines]
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except tokenize.TokenError:
        return result

    # Map token positions back to lines
    skip = {_tk.NEWLINE, _tk.NL, _tk.ENDMARKER, _tk.ENCODING,
            _tk.INDENT, _tk.DEDENT, _tk.ERRORTOKEN}
    line_spans = [[] for _ in raw_lines]  # list of (scol, ecol, class) per line

    for tok in toks:
        ttype, tstring, (sr, sc), (er, ec), _ = tok
        if ttype in skip:
            continue
        cls = _classify(ttype, tstring)
        if not cls:
            continue
        # Handle tokens spanning multiple lines (e.g. triple-quoted strings)
        for row in range(sr, min(er + 1, len(raw_lines) + 1)):
            li = row - 1
            if li < 0 or li >= len(raw_lines):
                continue
            line = raw_lines[li]
            s = sc if row == sr else 0
            e = ec if row == er else len(line)
            line_spans[li].append((s, e, cls))

    for li, spans in enumerate(line_spans):
        if not spans:
            continue
        line = raw_lines[li]
        parts = []
        cur = 0
        for s, e, cls in sorted(spans):
            if s > cur:
                parts.append(html.escape(line[cur:s]))
            parts.append(f'<span class="{cls}">{html.escape(line[s:e])}</span>')
            cur = e
        if cur < len(line):
            parts.append(html.escape(line[cur:]))
        result[li] = ''.join(parts)

    return result

# ─── SLIDE DATA ────────────────────────────────────────────────────────────────

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
    time_val = elapsed if elapsed is not None else (ev['time'] if ev else 0)
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
        'time_val': time_val,
        'time_label': f"{time_val:.0f}s",
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
    'total_duration': 101,
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
    'total_duration': 44,
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
    'total_duration': 71,
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
    'total_duration': 110,
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
    'total_duration': 147,
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
    'total_duration': 60,
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
    'total_duration': 76,
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

def render_code_block(code, added, changed, highlight, annotation=''):
    """Render code with syntax highlighting, line highlights, and inline annotation callout."""
    if not code or not code.strip():
        return '<div class="code-empty">No code yet.</div>'
    lines = code.split('\n')
    show_diff = not highlight
    hi_set = set(highlight)
    add_set = set(added)
    chg_set = set(changed)
    last_hi = max(highlight) if highlight else None

    hl_lines = highlight_python(code)

    out = ['<pre class="code-block"><code>']
    for i, raw in enumerate(lines):
        ln = i + 1
        cls = ['code-line']
        if ln in hi_set:          cls.append('hl-focus')
        elif show_diff and ln in add_set: cls.append('hl-added')
        elif show_diff and ln in chg_set: cls.append('hl-changed')
        inner = hl_lines[i] if i < len(hl_lines) else html.escape(raw)
        if not inner: inner = '\u00a0'
        out.append(f'<span class="{" ".join(cls)}" data-ln="{ln}">{inner}</span>')
        # Inject inline annotation callout immediately after the last highlighted line
        if ln == last_hi and annotation:
            ann_html = html.escape(annotation)
            out.append(f'<span class="code-ann" role="note" aria-label="Annotation">'
                        f'<span class="code-ann-arrow">▲</span>'
                        f'<span class="code-ann-text">{ann_html}</span>'
                        f'</span>')
    out.append('</code></pre>')
    return ''.join(out)

def render_slide(slide, slide_idx, replay_id):
    stype = slide['type']
    sid = f'{replay_id}-s{slide_idx}'

    if stype == 'intro':
        wlf = ''.join(f'<li>{esc(item)}</li>' for item in slide.get('what_to_look_for', []))
        return f'''
<div class="slide slide-intro" id="{sid}">
  <div class="intro-layout">
    <div class="intro-top">
      <h2 class="intro-heading">{slide["question_desc"]}</h2>
    </div>
    <div class="intro-cols">
      <div class="intro-col intro-why">
        <div class="intro-col-label">Why this replay?</div>
        <p class="intro-col-text">{esc(slide["why"])}</p>
      </div>
      <div class="intro-col intro-look">
        <div class="intro-col-label">👁 What to watch for</div>
        <ul class="intro-look-list">{wlf}</ul>
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
            slide.get('code', ''),
            slide.get('added', []),
            slide.get('changed', []),
            slide.get('highlight', []),
            annotation=slide.get('heading', ''),
        )
        legend = ''
        if not slide.get('highlight'):
            legend = '<span class="leg"><span class="leg-sw hl-added"></span>New</span><span class="leg"><span class="leg-sw hl-changed"></span>Changed</span>'
        return f'''
<div class="slide slide-code" id="{sid}">
  <div class="code-scroll-area">{code_html}</div>
  <div class="commentary-strip">
    <div class="strip-meta">
      <span class="s-time">{esc(time_label)}</span>
      <span class="s-vis s-vis-{vis}">{vis}</span>
      <span class="s-status {sc}">{si} {esc(status)} &thinsp; <strong>{tests_pass}/{tests_total}</strong></span>
      {legend}
    </div>
    <div class="strip-body">{slide.get("body", "")}</div>
  </div>
</div>'''

    elif stype == 'summary':
        cards = ''.join(
            f'<div class="summary-card">{b}</div>'
            for b in slide.get('bullets', [])
        )
        intervention = slide.get('intervention', '')
        int_block = f'<div class="intervention-box"><span class="int-icon">💡</span><div class="int-text">{intervention}</div></div>' if intervention else ''
        return f'''
<div class="slide slide-summary" id="{sid}">
  <div class="summary-layout">
    <h2 class="summary-heading">{esc(slide["heading"])}</h2>
    <div class="summary-cards">{cards}</div>
    {int_block}
  </div>
</div>'''
    return ''

def render_replay_section(replay):
    rid = replay['id']
    rnum = rid[1]
    slides_html = []
    for i, slide in enumerate(replay['slides']):
        slides_html.append(render_slide(slide, i, rid))

    oc = replay.get('outcome_class', 'pass')
    total_dur = replay.get('total_duration', 60)

    # Build timeline dots from code slides (those with time_val)
    timeline_dots = []
    code_slide_times = []
    for i, slide in enumerate(replay['slides']):
        tv = slide.get('time_val')
        if tv is not None:
            pct = min(100, max(0, tv / total_dur * 100))
            code_slide_times.append({'idx': i, 'pct': pct, 'label': slide.get('time_label', '')})
    # Store as JSON attr for JS
    import json as _json
    tl_json = _json.dumps(code_slide_times)

    return f'''
<!-- ═══ REPLAY: {esc(replay["title"])} ═══ -->
<section class="replay-section" id="replay-{rid}"
  data-replay="{rid}" data-slide-count="{len(replay['slides'])}"
  data-rnum="{rnum}" data-timeline='{tl_json}' data-total-dur="{total_dur}">
  <div class="replay-header">
    <div class="rh-left">
      <button class="rh-back" onclick="showCover()" title="All replays">← Index</button>
      <span class="rh-num">Replay {rnum}/7</span>
      <span class="rh-sep">·</span>
      <span class="rh-title">{esc(replay["title"])}</span>
      <span class="rh-sep">·</span>
      <span class="rh-question">{esc(replay.get("question",""))}</span>
    </div>
    <div class="rh-right">
      <span class="rh-dur">⏱ {esc(replay.get("duration",""))}</span>
      <span class="rh-outcome outcome-{oc}">{esc(replay.get("outcome",""))}</span>
    </div>
  </div>
  <div class="timeline-bar" id="tl-{rid}">
    <div class="tl-track">
      <div class="tl-fill" id="tl-fill-{rid}"></div>
    </div>
    <div class="tl-dots" id="tl-dots-{rid}"></div>
    <div class="tl-label" id="tl-label-{rid}">0s</div>
  </div>
  <div class="slides-container" id="slides-{rid}">
    {"".join(slides_html)}
  </div>
  <div class="slide-nav" id="nav-{rid}">
    <button class="nav-btn" id="prev-{rid}" onclick="prevSlide('{rid}')" disabled>&#8592;</button>
    <div class="slide-dots" id="dots-{rid}"></div>
    <span class="slide-counter" id="counter-{rid}">1&thinsp;/&thinsp;{len(replay['slides'])}</span>
    <button class="nav-btn" id="next-{rid}" onclick="nextSlide('{rid}')">&#8594;</button>
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
    /* ── Reset & Vars ─────────────────────────────────────────── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg:       #1a1f2e;
      --ink:      #e8ecf0;
      --muted:    #8b9bb4;
      --border:   #2d3548;
      --surface:  #222736;
      --surface2: #2a3042;
      --accent:   #3dd6c8;
      --accent2:  #5b9cf6;
      --warn:     #f0a842;
      --err:      #f05869;
      --ok:       #3dd68c;
      --code-bg:  #0d1117;
      --code-ink: #c9d1d9;
      --ann-bg:   #1c2b3a;
      --ann-border: #3dd6c8;
      --ann-ink:  #e8ecf0;
      --strip-bg: #1e2535;
      --strip-border: #2d3548;
      --hdr-bg:   #141824;
      --hdr-ink:  #c8d0de;
      --tl-bg:    #111622;
      --r: 10px;
    }
    html, body { height: 100%; overflow: hidden; }
    body {
      font-family: "Outfit", sans-serif;
      font-size: 18px;
      color: var(--ink);
      background: var(--bg);
    }
    .app { height: 100vh; display: flex; flex-direction: column; overflow: hidden; }

    /* ── Cover / TOC ───────────────────────────────────────────── */
    #cover {
      flex: 1;
      overflow-y: auto;
      padding: 2.5rem 2rem 3rem;
      background: var(--bg);
    }
    .cover-hero { text-align: center; margin-bottom: 2rem; }
    .cover-kicker {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase;
      color: var(--accent); background: rgba(61,214,200,0.12);
      border: 1px solid rgba(61,214,200,0.3);
      padding: 0.25rem 0.8rem; border-radius: 999px;
      display: inline-block; margin-bottom: 1rem;
    }
    .cover-title {
      font-family: "Fraunces", serif;
      font-size: clamp(2.2rem, 5vw, 3.6rem);
      line-height: 1.1; color: var(--ink); margin-bottom: 0.8rem;
    }
    .cover-lead {
      font-size: clamp(1rem, 1.8vw, 1.15rem); color: var(--muted);
      max-width: 680px; margin: 0 auto 1.5rem; line-height: 1.6;
    }
    .cover-stats {
      display: flex; gap: 2rem; justify-content: center; margin-bottom: 2rem;
    }
    .cover-stat { display: flex; flex-direction: column; align-items: center; }
    .cover-stat-num {
      font-family: "Fraunces", serif; font-size: 2.2rem;
      color: var(--accent); line-height: 1;
    }
    .cover-stat-label { font-size: 0.78rem; color: var(--muted); margin-top: 0.2rem; }
    .toc-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 1rem; max-width: 1300px; margin: 0 auto;
    }
    .toc-card {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--r); padding: 0; cursor: pointer;
      text-align: left; display: flex; gap: 0;
      transition: border-color 160ms, transform 160ms, box-shadow 160ms;
    }
    .toc-card:hover {
      border-color: var(--accent); transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }
    .toc-card-num {
      font-family: "Fraunces", serif; font-size: 2rem; font-weight: 700;
      color: var(--accent); padding: 1rem 1rem;
      border-right: 1px solid var(--border);
      min-width: 56px; display: flex; align-items: flex-start;
      justify-content: center;
    }
    .toc-card-body { padding: 0.9rem 1rem; flex: 1; }
    .toc-card-header { display: flex; gap: 0.6rem; align-items: center; margin-bottom: 0.4rem; }
    .toc-title { font-size: 1rem; font-weight: 700; color: var(--ink); margin-bottom: 0.2rem; }
    .toc-subtitle { font-size: 0.8rem; color: var(--muted); margin-bottom: 0.4rem; }
    .toc-insight { font-size: 0.82rem; color: #9aa8c0; line-height: 1.5; margin-bottom: 0.5rem; }
    .toc-footer { display: flex; justify-content: space-between; align-items: center; }
    .toc-tags { display: flex; gap: 0.3rem; flex-wrap: wrap; }
    .toc-slides { font-size: 0.72rem; color: var(--muted); }
    .toc-duration { font-size: 0.75rem; color: var(--muted); }
    .toc-outcome { font-size: 0.72rem; font-weight: 600; padding: 0.15rem 0.45rem;
      border-radius: 999px; }
    .toc-outcome.pass  { background: rgba(61,214,140,0.15); color: #3dd68c; }
    .toc-outcome.fail  { background: rgba(240,88,105,0.15); color: #f05869; }
    .toc-outcome.partial { background: rgba(240,168,66,0.15); color: #f0a842; }
    .toc-outcome.none  { background: rgba(139,155,180,0.15); color: var(--muted); }
    .cover-footer { text-align: center; margin-top: 1.5rem; font-size: 0.8rem; color: var(--muted); }

    /* ── Tags ──────────────────────────────────────────────────── */
    .tag, .tag-sm {
      font-family: "IBM Plex Mono", monospace; font-size: 0.67rem;
      background: rgba(91,156,246,0.12); color: var(--accent2);
      border: 1px solid rgba(91,156,246,0.25);
      padding: 0.1rem 0.45rem; border-radius: 999px; white-space: nowrap;
    }

    /* ── Replay section (full-screen) ──────────────────────────── */
    .replay-section {
      display: none; flex-direction: column;
      height: 100vh; overflow: hidden;
    }
    .replay-section.active { display: flex; }

    /* ── Compact replay header ─────────────────────────────────── */
    .replay-header {
      flex-shrink: 0;
      background: var(--hdr-bg);
      border-bottom: 1px solid var(--border);
      display: flex; align-items: center; justify-content: space-between;
      padding: 0 1rem;
      height: 44px;
      gap: 0.6rem;
    }
    .rh-left { display: flex; align-items: center; gap: 0.55rem; min-width: 0; }
    .rh-right { display: flex; align-items: center; gap: 0.6rem; flex-shrink: 0; }
    .rh-back {
      background: none; border: 1px solid var(--border);
      color: var(--muted); font-size: 0.78rem; padding: 0.25rem 0.6rem;
      border-radius: 6px; cursor: pointer; white-space: nowrap; flex-shrink: 0;
      transition: color 120ms, border-color 120ms;
    }
    .rh-back:hover { color: var(--ink); border-color: var(--muted); }
    .rh-num {
      font-family: "IBM Plex Mono", monospace; font-size: 0.78rem;
      color: var(--accent); flex-shrink: 0;
    }
    .rh-sep { color: var(--border); flex-shrink: 0; }
    .rh-title {
      font-weight: 700; font-size: 0.95rem; color: var(--ink);
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
      flex-shrink: 1;
    }
    .rh-question {
      font-size: 0.8rem; color: var(--muted); white-space: nowrap;
      overflow: hidden; text-overflow: ellipsis; flex-shrink: 2;
    }
    .rh-dur { font-size: 0.78rem; color: var(--muted); }
    .rh-outcome {
      font-size: 0.75rem; font-weight: 600;
      padding: 0.15rem 0.55rem; border-radius: 999px;
    }
    .rh-outcome.outcome-pass    { background: rgba(61,214,140,0.15); color: #3dd68c; }
    .rh-outcome.outcome-fail    { background: rgba(240,88,105,0.15); color: #f05869; }
    .rh-outcome.outcome-partial { background: rgba(240,168,66,0.15); color: #f0a842; }
    .rh-outcome.outcome-none    { background: rgba(139,155,180,0.1); color: var(--muted); }

    /* ── Timeline bar ──────────────────────────────────────────── */
    .timeline-bar {
      flex-shrink: 0; height: 28px;
      background: var(--tl-bg);
      border-bottom: 1px solid var(--border);
      position: relative; padding: 0 12px;
      display: flex; align-items: center;
    }
    .tl-track {
      flex: 1; height: 3px; background: rgba(255,255,255,0.1);
      border-radius: 2px; position: relative;
    }
    .tl-fill {
      position: absolute; left: 0; top: 0; bottom: 0;
      background: var(--accent); border-radius: 2px;
      width: 0%; transition: width 0.4s ease;
    }
    .tl-dots { position: absolute; left: 12px; right: 60px; top: 0; bottom: 0; pointer-events: none; }
    .tl-dot {
      position: absolute; top: 50%; transform: translate(-50%, -50%);
      width: 8px; height: 8px; border-radius: 50%;
      background: rgba(255,255,255,0.25); border: 1px solid rgba(255,255,255,0.35);
      transition: background 0.3s, transform 0.3s;
      pointer-events: all; cursor: pointer;
    }
    .tl-dot.active {
      background: var(--accent); border-color: var(--accent);
      transform: translate(-50%, -50%) scale(1.5);
    }
    .tl-dot:hover { background: var(--accent2); }
    .tl-label {
      font-family: "IBM Plex Mono", monospace; font-size: 0.65rem;
      color: var(--accent); min-width: 48px; text-align: right;
      transition: all 0.3s;
    }

    /* ── Slides container ──────────────────────────────────────── */
    .slides-container {
      flex: 1; position: relative; overflow: hidden;
    }
    .slide {
      position: absolute; inset: 0;
      opacity: 0; pointer-events: none;
      transition: opacity 0.3s ease;
      display: flex; flex-direction: column;
    }
    .slide.active { opacity: 1; pointer-events: all; }

    /* ── Code slide ────────────────────────────────────────────── */
    .code-scroll-area {
      flex: 1; overflow-y: auto; background: var(--code-bg);
      max-height: calc(100vh - 44px - 28px - 50px - 120px);
    }
    .code-block {
      font-family: "IBM Plex Mono", monospace;
      font-size: 15px; line-height: 1.45;
      color: var(--code-ink); white-space: pre;
    }
    .code-block code { display: block; }
    .code-line {
      display: block; padding: 0 1rem;
      border-left: 3px solid transparent;
      transition: background 0.2s;
    }
    .code-line::before {
      content: attr(data-ln);
      display: inline-block; width: 2.5em;
      color: #3d4451; text-align: right; margin-right: 1em;
      font-size: 0.8em; user-select: none;
    }
    .hl-focus  { background: rgba(210,153,34,0.2);  border-left-color: #d29922; }
    .hl-added  { background: rgba(61,214,140,0.12); border-left-color: #3dd68c; }
    .hl-changed{ background: rgba(91,156,246,0.12); border-left-color: #5b9cf6; }

    /* ── Inline code annotation ────────────────────────────────── */
    .code-ann {
      display: block; margin: 0 1rem 0 calc(1rem + 2.5em + 1em + 3px);
      background: var(--ann-bg); border: 1px solid var(--ann-border);
      border-radius: 6px; padding: 0.55rem 0.9rem;
      border-left: 3px solid var(--ann-border);
      position: relative;
    }
    .code-ann-arrow {
      position: absolute; left: 1.2rem; top: -0.7rem;
      font-size: 0.9rem; color: var(--ann-border);
      line-height: 1;
    }
    .code-ann-text {
      font-family: "Outfit", sans-serif;
      font-size: 16px; font-weight: 600;
      color: var(--ann-ink); white-space: normal; display: block;
    }

    /* ── Commentary strip (bottom of code slide) ───────────────── */
    .commentary-strip {
      flex-shrink: 0;
      background: var(--strip-bg); border-top: 1px solid var(--strip-border);
      padding: 0.5rem 1.2rem 0.55rem;
      min-height: 100px; max-height: 140px;
      overflow-y: auto;
    }
    .strip-meta {
      display: flex; gap: 0.6rem; align-items: center;
      margin-bottom: 0.35rem; flex-wrap: wrap;
    }
    .s-time {
      font-family: "IBM Plex Mono", monospace; font-size: 0.75rem;
      color: var(--accent); background: rgba(61,214,200,0.1);
      padding: 0.15rem 0.5rem; border-radius: 4px;
    }
    .s-vis {
      font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 4px;
      text-transform: uppercase; letter-spacing: 0.04em;
    }
    .s-vis-public  { background: rgba(91,156,246,0.12); color: var(--accent2); }
    .s-vis-private { background: rgba(240,168,66,0.12); color: var(--warn); }
    .s-status { font-size: 0.82rem; padding: 0.1rem 0.55rem; border-radius: 4px; }
    .status-pass    { background: rgba(61,214,140,0.15); color: #3dd68c; }
    .status-wrong   { background: rgba(240,88,105,0.15); color: #f05869; }
    .status-runtime { background: rgba(240,168,66,0.15); color: #f0a842; }
    .status-other   { background: rgba(139,155,180,0.1); color: var(--muted); }
    .leg { font-size: 0.72rem; color: var(--muted); display: flex; align-items: center; gap: 0.25rem; }
    .leg-sw { display: inline-block; width: 10px; height: 10px; border-radius: 2px; }
    .strip-body {
      font-size: 15px; line-height: 1.55; color: #b0bdcf;
    }
    .strip-body strong { color: var(--ink); }
    .strip-body code {
      font-family: "IBM Plex Mono", monospace; font-size: 0.85em;
      background: rgba(255,255,255,0.07); padding: 0.05em 0.35em;
      border-radius: 3px; color: #e8c888;
    }
    .strip-body em { color: var(--accent2); font-style: normal; font-weight: 500; }

    /* ── Intro slide ───────────────────────────────────────────── */
    .slide-intro { display: flex; flex-direction: column; }
    .intro-layout {
      flex: 1; display: flex; flex-direction: column; padding: 1.8rem 2rem 1.2rem;
      gap: 1.2rem; overflow-y: auto;
    }
    .intro-top {}
    .intro-heading {
      font-family: "Fraunces", serif;
      font-size: clamp(1.4rem, 2.5vw, 1.9rem);
      line-height: 1.25; color: var(--ink); margin-bottom: 0;
    }
    .intro-cols {
      display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; flex: 1;
    }
    .intro-col {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--r); padding: 1.2rem 1.4rem;
    }
    .intro-col-label {
      font-family: "IBM Plex Mono", monospace; font-size: 0.72rem;
      text-transform: uppercase; letter-spacing: 0.08em;
      color: var(--accent); margin-bottom: 0.6rem;
    }
    .intro-col-text { font-size: 16px; line-height: 1.6; color: #b0bdcf; }
    .intro-look-list {
      font-size: 16px; line-height: 1.6; color: #b0bdcf;
      padding-left: 1.1em; display: flex; flex-direction: column; gap: 0.4rem;
    }
    .intro-look-list li::marker { color: var(--accent); }

    /* ── Summary slide ─────────────────────────────────────────── */
    .slide-summary { display: flex; flex-direction: column; }
    .summary-layout {
      flex: 1; display: flex; flex-direction: column;
      padding: 1.6rem 2rem 1.2rem; gap: 1rem; overflow-y: auto;
    }
    .summary-heading {
      font-family: "Fraunces", serif;
      font-size: clamp(1.4rem, 2.5vw, 1.8rem);
      color: var(--accent); margin-bottom: 0;
    }
    .summary-cards {
      display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.8rem; flex: 1;
    }
    .summary-card {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--r); padding: 1rem 1.2rem;
      font-size: 15px; line-height: 1.55; color: #b0bdcf;
    }
    .summary-card strong { color: var(--ink); }
    .summary-card code {
      font-family: "IBM Plex Mono", monospace; font-size: 0.85em;
      background: rgba(255,255,255,0.07); padding: 0.05em 0.35em;
      border-radius: 3px; color: #e8c888;
    }
    .summary-card em { color: var(--accent2); font-style: normal; }
    .intervention-box {
      background: rgba(61,214,200,0.07); border: 1px solid rgba(61,214,200,0.3);
      border-radius: var(--r); padding: 1rem 1.4rem;
      display: flex; gap: 0.8rem; align-items: flex-start; flex-shrink: 0;
    }
    .int-icon { font-size: 1.3rem; flex-shrink: 0; margin-top: 0.1rem; }
    .int-text { font-size: 15px; line-height: 1.55; color: #b0bdcf; }
    .int-text strong { color: var(--ink); }
    .int-text code {
      font-family: "IBM Plex Mono", monospace; font-size: 0.85em;
      background: rgba(255,255,255,0.07); padding: 0.05em 0.35em;
      border-radius: 3px; color: #e8c888;
    }

    /* ── Bottom nav ────────────────────────────────────────────── */
    .slide-nav {
      flex-shrink: 0; height: 50px;
      background: var(--hdr-bg); border-top: 1px solid var(--border);
      display: flex; align-items: center; justify-content: center; gap: 0.8rem;
      padding: 0 1rem;
    }
    .nav-btn {
      background: none; border: 1px solid var(--border); color: var(--muted);
      font-size: 1.3rem; width: 38px; height: 34px; border-radius: 6px;
      cursor: pointer; display: flex; align-items: center; justify-content: center;
      transition: background 120ms, color 120ms;
    }
    .nav-btn:hover:not(:disabled) { background: var(--surface2); color: var(--ink); }
    .nav-btn:disabled { opacity: 0.3; cursor: default; }
    .slide-dots { display: flex; gap: 6px; align-items: center; }
    .dot {
      width: 8px; height: 8px; border-radius: 50%;
      background: var(--border); border: none; cursor: pointer; padding: 0;
      transition: background 0.25s, transform 0.25s;
    }
    .dot.active { background: var(--accent); transform: scale(1.4); }
    .slide-counter {
      font-family: "IBM Plex Mono", monospace; font-size: 0.78rem;
      color: var(--muted); min-width: 44px; text-align: center;
    }

    /* ── Syntax highlighting ───────────────────────────────────── */
    .tk-kw  { color: #c792ea; font-weight: 500; }  /* purple — keywords */
    .tk-bi  { color: #82aaff; }                     /* blue — builtins */
    .tk-str { color: #c3e88d; }                     /* green — strings */
    .tk-num { color: #f78c6c; }                     /* orange — numbers */
    .tk-cmt { color: #546e7a; font-style: italic; } /* grey — comments */
    .tk-op  { color: #89ddff; }                     /* cyan — operators */
    .tk-brk { color: #89ddff; }                     /* cyan — brackets */

    /* ── Keyboard hint ─────────────────────────────────────────── */
    .kbd-hint {
      position: fixed; bottom: 60px; right: 1.5rem; z-index: 99;
      background: rgba(30,36,55,0.9); border: 1px solid var(--border);
      border-radius: 8px; padding: 0.4rem 0.8rem;
      font-size: 0.8rem; color: var(--muted); pointer-events: none;
      opacity: 0; transition: opacity 0.4s;
    }
    .kbd-hint.visible { opacity: 1; }
    .kbd-hint kbd {
      background: var(--surface2); border: 1px solid var(--border);
      border-radius: 4px; padding: 0.1rem 0.4rem; font-size: 0.78rem;
    }

    /* ── Responsive ────────────────────────────────────────────── */
    @media (max-width: 768px) {
      .intro-cols { grid-template-columns: 1fr; }
      .summary-cards { grid-template-columns: 1fr; }
      .rh-question { display: none; }
    }
  </style>
</head>
<body>
<div class="app" id="app">
'''


HTML_JS = '''
</div><!-- /app -->

<div class="kbd-hint" id="kbd-hint"><kbd>←</kbd> <kbd>→</kbd> navigate &nbsp; <kbd>Esc</kbd> index</div>

<script>
// ── State ────────────────────────────────────────────────────────────────────
let currentReplay = null;
const slideState = {};       // rid -> slideIndex
const REPLAY_ORDER = ['r1','r2','r3','r4','r5','r6','r7'];

// ── Cover ────────────────────────────────────────────────────────────────────
function showCover() {
  const cover = document.getElementById('cover');
  cover.style.display = 'block';
  if (currentReplay) {
    document.getElementById(`replay-${currentReplay}`).classList.remove('active');
  }
  currentReplay = null;
  history.pushState({}, '', '#');
}

// ── Show replay at slide idx ─────────────────────────────────────────────────
function showReplay(rid, idx) {
  idx = idx === undefined ? (slideState[rid] || 0) : idx;

  document.getElementById('cover').style.display = 'none';
  if (currentReplay && currentReplay !== rid) {
    document.getElementById(`replay-${currentReplay}`).classList.remove('active');
  }
  currentReplay = rid;
  const section = document.getElementById(`replay-${rid}`);
  section.classList.add('active');

  if (!(rid in slideState)) {
    initDots(rid);
    initTimeline(rid);
  }
  goToSlide(rid, idx, false);   // no push — handled below
  history.pushState({replay: rid, idx}, '', `#${rid}/${idx + 1}`);

  const hint = document.getElementById('kbd-hint');
  hint.classList.add('visible');
  setTimeout(() => hint.classList.remove('visible'), 2800);
}

// ── Init nav dots ────────────────────────────────────────────────────────────
function initDots(rid) {
  const section = document.getElementById(`replay-${rid}`);
  const count = parseInt(section.dataset.slideCount);
  const dotsEl = document.getElementById(`dots-${rid}`);
  dotsEl.innerHTML = '';
  for (let i = 0; i < count; i++) {
    const d = document.createElement('button');
    d.className = 'dot';
    d.setAttribute('aria-label', `Slide ${i + 1}`);
    d.onclick = () => { goToSlide(rid, i); pushHash(rid, i); };
    dotsEl.appendChild(d);
  }
}

// ── Init timeline ────────────────────────────────────────────────────────────
function initTimeline(rid) {
  const section = document.getElementById(`replay-${rid}`);
  const tl = JSON.parse(section.dataset.timeline || '[]');
  const dotsEl = document.getElementById(`tl-dots-${rid}`);
  dotsEl.innerHTML = '';
  tl.forEach(({idx, pct, label}) => {
    const d = document.createElement('button');
    d.className = 'tl-dot';
    d.style.left = pct + '%';
    d.title = label;
    d.onclick = () => { goToSlide(rid, idx); pushHash(rid, idx); };
    dotsEl.appendChild(d);
  });
}

// ── Update timeline state ────────────────────────────────────────────────────
function updateTimeline(rid, idx) {
  const section = document.getElementById(`replay-${rid}`);
  const tl = JSON.parse(section.dataset.timeline || '[]');
  const totalDur = parseFloat(section.dataset.totalDur || '60');

  // Find which code slide corresponds to this slide index
  const entry = tl.find(e => e.idx === idx);
  const fill = document.getElementById(`tl-fill-${rid}`);
  const label = document.getElementById(`tl-label-${rid}`);
  const dots = document.querySelectorAll(`#tl-dots-${rid} .tl-dot`);

  if (entry) {
    fill.style.width = entry.pct + '%';
    label.textContent = entry.label;
    dots.forEach((d, i) => d.classList.toggle('active', tl[i]?.idx === idx));
  } else {
    // Intro or summary: no timeline position; don't change fill
    dots.forEach(d => d.classList.remove('active'));
  }
}

// ── Go to a slide ────────────────────────────────────────────────────────────
function goToSlide(rid, idx, push) {
  const section = document.getElementById(`replay-${rid}`);
  const slides = section.querySelectorAll('.slide');
  const count = slides.length;
  if (idx < 0 || idx >= count) return;

  slides.forEach((s, i) => s.classList.toggle('active', i === idx));

  const dots = document.querySelectorAll(`#dots-${rid} .dot`);
  dots.forEach((d, i) => d.classList.toggle('active', i === idx));

  document.getElementById(`counter-${rid}`).innerHTML = `${idx + 1}&thinsp;/&thinsp;${count}`;
  document.getElementById(`prev-${rid}`).disabled = idx === 0;
  document.getElementById(`next-${rid}`).disabled = idx === count - 1;
  slideState[rid] = idx;

  updateTimeline(rid, idx);
  if (push !== false) pushHash(rid, idx);

  // Auto-scroll code panel to first highlighted line
  const activeSlide = slides[idx];
  if (activeSlide) {
    requestAnimationFrame(() => {
      const scrollArea = activeSlide.querySelector('.code-scroll-area');
      const firstFocus = scrollArea && scrollArea.querySelector('.hl-focus');
      if (firstFocus && scrollArea) {
        firstFocus.scrollIntoView({block: 'center', behavior: 'instant'});
      } else if (scrollArea) {
        scrollArea.scrollTop = 0;
      }
    });
  }
}

function pushHash(rid, idx) {
  history.pushState({replay: rid, idx}, '', `#${rid}/${idx + 1}`);
}

// ── Sequential replay navigation ─────────────────────────────────────────────
function nextSlide(rid) {
  const idx = slideState[rid] || 0;
  const section = document.getElementById(`replay-${rid}`);
  const count = parseInt(section.dataset.slideCount);
  if (idx < count - 1) {
    goToSlide(rid, idx + 1);
  } else {
    // End of this replay → go to next replay or cover
    const pos = REPLAY_ORDER.indexOf(rid);
    if (pos >= 0 && pos < REPLAY_ORDER.length - 1) {
      showReplay(REPLAY_ORDER[pos + 1], 0);
    } else {
      showCover();
    }
  }
}

function prevSlide(rid) {
  const idx = slideState[rid] || 0;
  if (idx > 0) goToSlide(rid, idx - 1);
}

// ── Keyboard ─────────────────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { showCover(); return; }
  if (!currentReplay) return;
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
    e.preventDefault(); nextSlide(currentReplay);
  } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
    e.preventDefault(); prevSlide(currentReplay);
  }
});

// ── Hash routing: #r2/3 → replay r2, slide 3 (1-indexed) ────────────────────
function handleHash() {
  const h = location.hash.replace('#', '');
  if (!h) return;
  const [rid, sidxStr] = h.split('/');
  const sidx = sidxStr ? Math.max(0, parseInt(sidxStr) - 1) : 0;
  if (rid && document.getElementById(`replay-${rid}`)) {
    showReplay(rid, sidx);
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
