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

# ─── UTILITIES ────────────────────────────────────────────────────────────────

def fmt_time(t):
    """Format seconds as mm:ss (for ≥60s) or Xs."""
    t = int(round(t))
    if t >= 60:
        return f"{t//60}:{t%60:02d}"
    return f"{t}s"

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

def make_code_slide(ev, prev_ev=None, heading='', body='', note='', manual_highlight=None, elapsed=None):
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
        'time_label': fmt_time(time_val),
        'heading': heading,
        'body': body,
        'note': note,
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
            'question_desc': 'Given N strings, replace all consonants with <code>#</code> and print each result. Vowels (a, e, i, o, u — upper and lower) stay unchanged.',
            'question_code': 'Input:    3\n          hello\n          Python\n          World\n\nOutput:   #e##o\n          #y##o#\n          #o###',
            'why': 'This student eventually got full marks — but took over 80 attempts to get there. Watch how three completely different bugs appear right from the start, and how the student layers on complexity until finally landing on a clean, correct solution.',
            'what_to_look_for': [
                'Three separate bugs in the very first submission — typo, wrong variable name, and an invalid operation',
                'The shift from "code crashes" to "code runs but gives wrong answer" — this is actually <em>progress</em>',
                'A brief relapse midway through, where old bugs reappear in new clothing',
                'The final solution is built completely differently from the first attempt',
            ],
        },
        make_code_slide(r1_e0, None,
            heading='Three Bugs, One Shot',
            body='<strong>Line 4:</strong> <code>whille</code> is a typo — Python crashes before the code even starts. <strong>Line 10:</strong> <code>CH</code> is a new variable name, but <code>ch</code> (lowercase) is what the loop gives us — Python treats these as different names. <strong>Line 13:</strong> You cannot change a single letter in a Python string by position — strings are locked once created.',
            note='Mental model: "I can modify a string the same way I\'d write to an array slot." This is the most common beginner Python misconception.',
            manual_highlight=[4, 10, 13],
        ),
        make_code_slide(r1_e1, r1_e0,
            heading='Runtime → Wrong Answer: Progress!',
            body='The typo is fixed — now the code at least <em>runs</em>. But it still gives the wrong output. <strong>Line 29:</strong> <code>i = \'#\'</code> — the student is updating the loop variable <code>i</code>, but that doesn\'t change the original string. <code>i</code> is a temporary copy for each step through the loop. The string itself is untouched.',
            note='Mental model: "If I change the loop variable, the original data changes too." This is a misunderstanding of how Python\'s for-loop works.',
            manual_highlight=[29],
        ),
        make_code_slide(r1_e2, r1_e1,
            heading='Adding Complexity Without Progress',
            body='The code has grown from 15 lines to 42. There are now print statements inside loops, commented-out old attempts, and a new variable <code>ss</code> — but <strong>Line 35:</strong> <code>ss[i] = \'#\'</code> hits the exact same wall as before: you still can\'t overwrite a character in a string by index.',
            note='Mental model: "My approach is right, I just need to do it on a different variable." The real issue (strings can\'t be changed in place) hasn\'t been understood yet.',
            manual_highlight=[35],
        ),
        make_code_slide(r1_e3, r1_e2,
            heading='One Test Passes — The Insight Arrives',
            body='1 out of 3 test cases passes. The key change: <strong>Lines 36–38</strong> — instead of trying to modify the string directly, the student now converts it to a list first. Lists <em>can</em> be changed by position. This is the breakthrough — the algorithm is now fundamentally correct.',
            note='Mental model shifting to: "Convert to list, change the item, convert back." This is the correct approach.',
            manual_highlight=[36, 37, 38],
        ),
        make_code_slide(r1_e4, r1_e3,
            heading='All Public Tests Pass 🟢',
            body='All 3 public tests pass. <strong>Lines 49–52</strong> contain the actual solution — everything above is commented-out old attempts the student kept "just in case." The logic: convert to list → replace non-vowels → join back and print.',
            note='Common behaviour: students keep old code around even after it\'s superseded, in case they need to "go back."',
            manual_highlight=[49, 50, 51, 52],
        ),
        make_code_slide(r1_e5, r1_e4,
            heading='Private Tests Pass Too ✓',
            body='The student cleaned up the code and submitted to the harder private tests. All passed. <strong>Lines 8–13</strong> show the final, lean version — the logic generalised correctly, not just matched the visible examples.',
            note='This is what real learning looks like: the student arrived at a solution they understand, not just one they copied.',
            manual_highlight=[8, 9, 10, 11, 12, 13],
        ),
        {
            'type': 'summary',
            'heading': 'Key Takeaways',
            'bullets': [
                '<strong>Strings are immutable.</strong> Students often assume they can change a character in a string the same way they\'d change a value in a list. This misconception shows up constantly and needs direct, explicit teaching.',
                '<strong>Crashes → wrong answers → correct answers</strong> is the healthy debugging arc. When students move from crashes to wrong output, celebrate — it means the code is actually running.',
                '<strong>Layering complexity hides the root cause.</strong> Adding more variables and print statements doesn\'t fix a wrong mental model. It just delays the moment of clarity.',
                '<strong>Simplicity is the destination.</strong> The final 5-line solution looks nothing like the 40-line intermediate versions. Clean code usually emerges from understanding, not from polish.',
            ],
            'intervention': 'When a student tries to modify a string by position, don\'t just correct them — <em>demonstrate</em> the error in a blank Python shell: <code>s = "hello"; s[0] = "H"</code>. Then show the fix: <code>s = list(s); s[0] = "H"; s = "".join(s)</code>. A 30-second live demo is worth ten explanations.',
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
            'question_desc': 'Given a 4-digit integer, check whether its digits are strictly decreasing from left to right.',
            'question_code': '9876  →  True   (9 > 8 > 7 > 6)\n4321  →  True\n4312  →  False  (3 > 1, but 1 < 2 at the end)\n1234  →  False',
            'why': 'This 44-second session is a masterclass in focused debugging. The student makes small, deliberate changes and tests after each one. Compare this to Replay 5 where 213 attempts achieve nothing — same problem difficulty, opposite behaviour.',
            'what_to_look_for': [
                'Two bugs in the first attempt — a wrong variable name and a wrong loop approach — fixed in just 3 tries',
                'A brief regression at 30 seconds: the student "improved" the code and accidentally broke it',
                'The final solution has a hidden flaw — but the tests don\'t catch it',
                'What makes this session efficient: one change at a time, test immediately',
            ],
        },
        make_code_slide(r2_e0, None,
            heading='Two Bugs, Adjacent Lines',
            body='The algorithm is on the right track — convert to string, compare digits. But <strong>Line 26:</strong> the variable is <code>string1</code>, but the code writes <code>list(string)</code> — wrong name, causing a crash. And <strong>Line 28:</strong> <code>k</code> comes from the for-loop and is a <em>character</em>, not an index, so <code>list1[k]</code> would fail even if line 26 were fixed.',
            note='Mental model: "I know what I want to do, I just need to figure out the right variable names." The student is close — understanding is there, execution is off.',
            manual_highlight=[26, 28],
        ),
        make_code_slide(r2_e1, r2_e0,
            heading='Still Stuck: Can\'t List an Integer',
            body='Variable name is fixed, but now <strong>Line 26:</strong> <code>list(n)</code> — you can\'t turn an integer directly into a list of its digits. The path to digits is: integer → string → list of character digits. The student is one step away.',
            note='Mental model: "I should be able to break the number into parts directly." They\'re not yet thinking of the integer→string→list conversion chain.',
            manual_highlight=[26],
        ),
        make_code_slide(r2_e2, r2_e1,
            heading='All Tests Pass — But Is It Right?',
            body='All 3 public tests pass. But <strong>Line 28</strong> only compares the first two digits: <code>list1[0] > list1[1]</code>. A truly "decreasing" number needs all four consecutive pairs checked. The student doesn\'t know this yet — the public tests happened to pass anyway.',
            note='This is the "lucky pass" — code that works on the visible examples but is incomplete. A teachable moment: passing tests doesn\'t prove correctness.',
            manual_highlight=[28],
        ),
        make_code_slide(r2_e3, r2_e2,
            heading='Regression: Fixing What Wasn\'t Broken',
            body='The student tries to improve the comparison and accidentally swaps the indices — <strong>Line 28:</strong> now reads <code>list1[2] > list1[1]</code> (checking the wrong pair). This is a classic trap: the impulse to "clean up" code that\'s working, without re-running tests after each change.',
            note='Mental model: "More changes = more correct." The safer habit: make one change, test, then continue.',
            manual_highlight=[28],
        ),
        make_code_slide(r2_e4, r2_e3,
            heading='Back to Passing — Final Submission ✓',
            body='All tests pass again. The code still only checks one pair of adjacent digits — and gets away with it because the test set doesn\'t expose the gap. A rich classroom discussion: <em>can you write a test case that would break this?</em>',
            note='The student\'s mental model is now "check if first digit > second digit = decreasing number." This works for the tests given, but isn\'t the full rule.',
            manual_highlight=[27, 28],
        ),
        {
            'type': 'summary',
            'heading': 'Key Takeaways',
            'bullets': [
                '<strong>One change at a time.</strong> This student\'s short session succeeded because each attempt changed only one or two things. When something broke, it was easy to see why.',
                '<strong>Tests can lie by omission.</strong> The final solution only checks two of the four digit comparisons — and passes both public and private tests anyway. This is a gap in the test design worth discussing.',
                '<strong>Regression by improvement.</strong> The 30-second dip shows how improving working code without testing can introduce new bugs. Teach: "test after every change."',
                '<strong>Efficiency comes from clarity.</strong> This student had a clear algorithm in mind from the start. The errors were mechanical (wrong names, wrong conversion), not conceptual.',
            ],
            'intervention': 'Use this replay alongside Replay 5 (which takes 213 attempts and fails). Ask students: "What is this student doing differently?" The answer — making small, testable changes — is the debugging skill worth teaching explicitly.',
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
            'question_desc': 'A <em>pangram</em> is a sentence that uses every letter of the alphabet at least once.',
            'question_code': '"The quick brown fox jumps over the lazy dog"  →  True\n"Hello world"                                  →  False\n"Pack my box with five dozen liquor jugs"      →  True',
            'why': 'This replay shows the "false summit" trap. At 47 seconds the student passes all visible tests — and feels done. But hidden tests fail immediately, and now they must figure out why without being able to see those hidden tests. This skill — reasoning about invisible cases — is rarely taught directly.',
            'what_to_look_for': [
                'The first approach has the logic <em>backwards</em>: checking if each character is in the alphabet, rather than if the alphabet is in the text',
                'The "false summit": all public tests pass at 47 seconds',
                'A counting bug that repeat characters can exploit',
                'The elegant final fix using a Python <code>set</code>',
            ],
        },
        make_code_slide(r3_e0, None,
            heading='Logic Backwards From the Start',
            body='The question is "does the text contain all 26 letters?" But the code asks "is each character a letter?" — the opposite direction. Also, <strong>Line 25:</strong> the <code>return True</code> is inside the loop, so the function stops and returns after checking just the first character.',
            note='Mental model: "I need to check the text against the alphabet" — but implementing it as "for each letter in text, check if it\'s in the alphabet" rather than "for each letter in the alphabet, check if it\'s in the text."',
            manual_highlight=[21, 22, 23, 24, 25],
        ),
        make_code_slide(r3_e1, r3_e0,
            heading='Patching a Broken Approach',
            body='The student tries to exclude non-letter characters: <strong>Line 24:</strong> <code>int(i)=False</code> — this isn\'t valid Python at all. You can\'t assign to a function call. They\'re trying to filter out numbers and punctuation, but the approach (checking each character instead of checking all 26 letters) is still fundamentally off.',
            note='Mental model: "My loop structure is correct, I just need to exclude the wrong kinds of characters." The loop structure itself is the problem.',
            manual_highlight=[24],
        ),
        make_code_slide(r3_e2, r3_e1,
            heading='Better Idea — With a Hidden Bug',
            body='A fresh approach: strip spaces, count how many characters are in the alphabet. If the count reaches 26, it\'s a pangram. This is much closer! But <strong>Lines 12–17</strong> count <em>every</em> character that appears in the alphabet, including repeats. A string like "aaa...a" (repeated 26 times) would wrongly count as a pangram.',
            note='Mental model: "If I\'ve seen 26 alphabet letters in the text, I\'ve seen all of them." True if each letter counted once — false if repeats inflate the count.',
            manual_highlight=[12, 13, 14, 15, 16, 17, 18],
        ),
        make_code_slide(r3_e3, r3_e2,
            heading='False Summit: All Public Tests Pass 🟢',
            body='All 3 public tests pass at 47 seconds. The counting logic works for the visible test cases — they don\'t include repeated-letter inputs. But the hidden tests do, and they will expose the bug. The student doesn\'t know this moment of confidence is about to break.',
            note='This is the "false summit" — visible success masking hidden failure. A crucial concept: passing tests proves the code works for those inputs, not for all inputs.',
            manual_highlight=[11, 12, 13, 14, 15],
        ),
        make_code_slide(r3_e4, r3_e3,
            heading='Hidden Tests Reveal the Bug: 1/3',
            body='Private tests: only 1/3 pass. The hidden cases almost certainly include inputs with repeated letters. <strong>Lines 6–12:</strong> the student is now reasoning — "why does 3/3 public become 1/3 private?" They need to think of an input that would fool their count logic. This is adversarial thinking — rare and valuable.',
            note='The gap between 3/3 public and 1/3 private is the signal. The question is whether the student can reason about it without seeing the hidden tests.',
            manual_highlight=[6, 7, 8, 9, 10, 11, 12],
        ),
        make_code_slide(r3_e5, r3_e4,
            heading='The Fix: Unique Letters via Set ✓',
            body='The solution: use a <code>set</code> to collect unique letters. Sets automatically discard duplicates. If the set contains all 26 letters, it\'s a pangram. <strong>Lines 6–15</strong> — cleaner, more correct, and more Pythonic than the counting approach.',
            note='The insight: "I don\'t want to count letters, I want to collect unique letters." This is what a set is made for.',
            manual_highlight=[6, 7, 8, 9, 10, 11, 12, 13, 14],
        ),
        {
            'type': 'summary',
            'heading': 'Key Takeaways',
            'bullets': [
                '<strong>The "false summit" is a real teaching moment.</strong> Passing all visible tests creates false confidence. Students need to learn: "passing tests means it works for these cases, not for all cases." Ask them to imagine a case that would break their logic.',
                '<strong>Logic direction matters.</strong> "For each character, is it a letter?" is not the same as "for each letter, is it in the text?" These are different loops over different things. Drawing the logic on paper first helps.',
                '<strong>Sets are the right tool for uniqueness.</strong> When the question involves "have I seen all X?" — whether it\'s letters, numbers, or anything else — a set is almost always the correct data structure.',
                '<strong>Reasoning about hidden tests is a learnable skill.</strong> Ask: "Can you think of an input that would pass the public tests but fail your logic?" This builds robustness, not just correctness on examples.',
            ],
            'intervention': 'Before students run tests, ask: "Can you describe an input that would trick your solution?" This builds the habit of adversarial thinking. For the set insight: show <code>len(set("the quick brown fox...")) == 26</code> — one line, correct, idiomatic Python.',
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
            'question_desc': 'Return <code>True</code> if the input string starts with <code>"Hello "</code> or <code>"Hi "</code> (with a space after each). Return <code>False</code> otherwise.',
            'question_code': '"Hello there"   →  True\n"Hi there"      →  True\n"HiThere"       →  False  (no space)\n"hello there"   →  False  (lowercase)\n"Hey there"     →  False',
            'why': 'The correct solution is two lines. This student took 168 attempts over 110 seconds, building complex code before arriving at the simple answer. A case study in why beginners over-engineer: they don\'t know what built-in tools exist, so they implement everything manually.',
            'what_to_look_for': [
                'The very first attempt uses <code>||</code> — the "or" from other programming languages, not Python',
                'By 27 seconds, still stuck — now manually checking character positions one by one',
                'A brief moment where all tests pass, built on hard-coded special cases',
                'The final solution is dramatically simpler than anything in between',
            ],
        },
        make_code_slide(r4_e0, None,
            heading='Wrong Language: <code>||</code> Is Not Python',
            body='<strong>Line 22:</strong> <code>s.startswith(\'Hello\'|| \'Hi\')</code> — <code>||</code> is the "or" operator in JavaScript and C, not Python. Python uses the word <code>or</code>. This causes a crash before anything runs. A common error when students switch between languages or guess syntax.',
            note='Mental model: "or" works like in other languages I\'ve used. Students who\'ve coded in JavaScript or C++ bring their syntax with them.',
            manual_highlight=[22],
        ),
        make_code_slide(r4_e1, r4_e0,
            heading='Manual Character Checking',
            body='27 seconds and 42 attempts in. The student has split the logic into separate blocks for "Hello" and "Hi". But <strong>Line 23:</strong> <code>if s[5]="\\t"</code> has two bugs: <code>=</code> should be <code>==</code>, and <code>\\t</code> is a tab character, not a space. They\'re trying to check whether there\'s a space after the greeting — but using the wrong character.',
            note='Mental model: "I\'ll check each character by position." Instead of using a built-in like <code>startswith()</code>, they\'re reimplementing what it already does.',
            manual_highlight=[22, 23, 24, 25],
        ),
        make_code_slide(r4_e2, r4_e1,
            heading='All Tests Pass — But Look at the Code',
            body='All 4 public tests pass. But the code works by accident. <strong>Line 22:</strong> <code>if s==\'Hithere\'</code> — a hard-coded special case for one specific string. <strong>Line 24:</strong> <code>startswith(\'Hello\' or \'Hi\')</code> — in Python, <code>\'Hello\' or \'Hi\'</code> evaluates to just <code>\'Hello\'</code> (Python returns the first "true" value). So this only checks for Hello, not Hi.',
            note='Mental model: "or inside the function means check both." But Python evaluates <code>\'Hello\' or \'Hi\'</code> as an expression <em>before</em> passing it to the function — and it simplifies to <code>\'Hello\'</code>.',
            manual_highlight=[22, 24],
        ),
        make_code_slide(r4_e3, r4_e2,
            heading='Private Tests Fail — Complexity Grows',
            body='After the public pass, private tests reveal only 2/3. The student adds more conditions, but now public tests also slip. <strong>Line 27:</strong> <code>if len(s[2])==0</code> — <code>s[2]</code> is always a single character (length 1, never 0). This condition never triggers. The code is getting longer but not more correct.',
            note='Mental model: "Adding more conditions will cover more cases." But the core logic is still wrong, so adding conditions just creates new failure modes.',
            manual_highlight=[27],
        ),
        make_code_slide(r4_e4, r4_e3,
            heading='Over-Engineering Peak',
            body='<strong>Lines 22–31:</strong> the student is now splitting the string, counting words, using lists. This is far more complex than needed. The code works for public tests but fails private ones. Notice how far the code has drifted from the original simple idea.',
            note='The student has lost sight of the problem. When code grows this complex for a simple rule, it\'s usually a sign the core approach needs to change, not expand.',
            manual_highlight=[22, 23, 24, 25, 26, 27, 28, 29],
        ),
        make_code_slide(r4_e5, r4_e4,
            heading='The Simple Solution ✓',
            body='After 159 attempts: two <code>startswith()</code> calls. <strong>Lines 23–24</strong>. That\'s it. The entire 107-second journey ends at the two-line solution that was available from the start.',
            note='This is what happens when a student discovers the right built-in at the end: everything they built manually becomes unnecessary. The lesson: look for built-in functions before implementing manually.',
            manual_highlight=[23, 24],
        ),
        {
            'type': 'summary',
            'heading': 'Key Takeaways',
            'bullets': [
                '<strong>Over-engineering is a symptom of not knowing the vocabulary.</strong> Students who don\'t know <code>startswith()</code> implement it manually — and get it wrong. Teaching built-in string methods directly prevents this whole class of errors.',
                '<strong>Language syntax carries over.</strong> <code>||</code> for "or" is valid in several other languages. When students switch to Python, they bring their syntax habits. Error messages that say "invalid syntax" don\'t explain <em>why</em> — students need to be told explicitly.',
                '<strong>"A or B" in Python is not what it looks like.</strong> <code>\'Hello\' or \'Hi\'</code> evaluates to <code>\'Hello\'</code> — the first truthy value. This surprises beginners who expect it to mean "either of these." Worth teaching as a distinct concept.',
                '<strong>Hard-coded special cases are a red flag.</strong> When a student writes <code>if s == \'Hithere\'</code>, they\'re matching test output, not solving the problem. This pattern deserves a gentle but direct conversation.',
            ],
            'intervention': 'Show students the Python documentation for string methods — or just demo <code>"Hello there".startswith("Hello ")</code> in a Python shell. Ask: "What does this return? What about <code>"Hi there".startswith("Hi ")</code>?" Then: "How would you combine these two checks?" The student often solves it in under a minute once they know the tool exists.',
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
    'insight': '213 attempts. Zero passing tests. This student worked harder than anyone else in this set — and got nowhere. A defining example of "thrashing": effort without traction. The session illuminates why teaching <em>how</em> to debug matters as much as teaching syntax.',
    'tags': ['thrashing', 'no recovery', 'mutation bug', 'missing vocabulary'],
    'slides': [
        {
            'type': 'intro',
            'heading': 'The Problem',
            'question_desc': 'Given a list of numbers, return a <em>new list</em> with each number squared, but in <em>reverse order</em>. The original list should not be changed.',
            'question_code': '[1, 2, 3]  →  [9, 4, 1]   (3²=9, 2²=4, 1²=1)\n[2, 4]     →  [16, 4]',
            'why': 'The complete solution is one short line. This student made 213 attempts over 147 seconds and never reached a passing score. This is the "thrashing" pattern — lots of activity, no progress. Watching this session reveals a specific knowledge gap: the student never understood how to build a new list from an old one.',
            'what_to_look_for': [
                'First attempt calls <code>squares()</code> — a function that does not exist in Python',
                'Every attempt after that tries to modify the <em>original</em> list instead of building a new one',
                'The student keeps cycling through slight variations of the same broken idea',
                'No attempt ever produces a correct result — 147 seconds of sincere, unproductive effort',
            ],
        },
        make_code_slide(r5_e0, None,
            heading='Imagining a Function That Doesn\'t Exist',
            body='<strong>Line 21:</strong> <code>return squares(l[::-2])</code>. Python has no built-in <code>squares()</code> function. The student is guessing at the API — inventing a function name that sounds right. Also, <code>l[::-2]</code> steps backwards by 2 (skipping every other element), not a full reversal. Both ideas are wrong from the start.',
            note='Mental model: "There must be a built-in that does this." When students don\'t know the right tools, they invent plausible-sounding names. This is a vocabulary gap, not a logic gap.',
            manual_highlight=[21],
        ),
        make_code_slide(r5_e1, r5_e0,
            heading='Overwriting the List Instead of Building a New One',
            body='36 seconds in. Now using a loop — but <strong>Line 23:</strong> <code>l = l[i] ** l[i]</code> replaces the entire list <code>l</code> with a single number (the element squared by itself, not even <code>x²</code>). After the first iteration, <code>l</code> is no longer a list at all. The loop then crashes trying to access a number like a list.',
            note='Mental model: "I can update the list as I go." Students who haven\'t yet learned to build a new, separate result list will try to modify the original — which destroys it during iteration.',
            manual_highlight=[23],
        ),
        make_code_slide(r5_e2, r5_e1,
            heading='Using a Built-in Word as a Variable Name',
            body='70 seconds in. <strong>Line 23:</strong> <code>int = l[i] ** 2</code> — the student named their variable <code>int</code>, which is Python\'s built-in for converting things to whole numbers. Using it as a variable name hides the built-in — if anything else needs <code>int()</code>, it will fail. The deeper bug is still there: assigning to <code>int</code> (or <code>l</code>) instead of collecting results into a new list.',
            note='Mental model: "<code>int</code> is just a word I can use for a number." Students don\'t always know which words are "reserved" or built-in in Python.',
            manual_highlight=[23],
        ),
        make_code_slide(r5_e3, r5_e2,
            heading='Same Bug, Different Syntax',
            body='110 seconds in, trying a different approach with <code>range()</code>. But <strong>Line 23:</strong> <code>l = l[i] ** 2</code> is the same overwrite-the-list bug as before. The structure has changed (using index <code>i</code> now) but the core mistake — assigning to <code>l</code> instead of building a new list — persists. The student is iterating through syntax changes without fixing the logic.',
            note='Mental model: "If I change how the loop works, maybe it\'ll produce the right answer." Thrashing often looks like this: surface-level variation without diagnosing the root cause.',
            manual_highlight=[23],
        ),
        make_code_slide(r5_e4, r5_e3,
            heading='Final Submission: Never Found the Pattern',
            body='Last attempt before time runs out. <strong>Line 22:</strong> <code>m = len(l)</code> sets the range size, but <strong>Line 23:</strong> <code>for m in range(0, m-1)</code> immediately overwrites <code>m</code> with the loop counter — so the range calculation is corrupted on the first step. Score: 0. After 213 attempts, the student never discovered that the answer needed a <em>new list</em>.',
            note='This is what "thrashing" looks like at the end: the code is now more complex than at the start, and still broken. The student needed a conceptual reset, not more attempts.',
            manual_highlight=[22, 23],
        ),
        {
            'type': 'summary',
            'heading': 'Key Takeaways',
            'bullets': [
                '<strong>"Try harder" is not a debugging strategy.</strong> 213 attempts with the same broken mental model produces 213 failures. Students need to learn how to <em>diagnose</em> errors, not just vary their code.',
                '<strong>The "build a new list" pattern is a key milestone.</strong> Students who don\'t know how to accumulate results into a new list will always try to modify the original — and run into the same crash. Teaching this pattern explicitly prevents whole families of bugs.',
                '<strong>Thrashing is a signal for instructor intervention.</strong> When a student makes many rapid attempts with no progress, it usually means a conceptual gap that more attempts won\'t fix. The student needs a conversation, not more time.',
                '<strong>Invented API names reveal missing vocabulary.</strong> When a student writes <code>squares()</code> or <code>reverse_list()</code>, they\'re showing you what they wish Python could do. That\'s a teaching opportunity: show them the tool that actually does it.',
            ],
            'intervention': 'Stop the loop early. Ask: "What should come back from this function — walk me through one example." Then: "How would you make a new list in Python?" Demonstrate: <code>result = []</code> followed by <code>result.append(x**2)</code> in a loop, or just <code>[x**2 for x in reversed(l)]</code>. One minute of explanation here is worth more than 100 more attempts.',
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
    'insight': 'At 18 seconds, this student had code that passed most tests. Then they tried to make it better — and broke it. They never recovered the early working version. A quiet cautionary tale about changing code without checkpoints.',
    'tags': ['early win', 'regression', 'set ordering', 'over-editing'],
    'slides': [
        {
            'type': 'intro',
            'heading': 'The Problem',
            'question_desc': 'Given a string, return a list of all characters that appear <em>more than once</em>. The characters must appear in the <em>same order</em> as they first appear in the string.',
            'question_code': '"banana"  →  ["a", "n"]   (a appears 3×, n appears 2×)\n"hello"   →  ["l"]        (l appears 2×)',
            'why': 'Eighteen seconds in, the student had code that passed 2 out of 3 public tests. They were close. Then they kept changing it, and each change made things worse. They ended with a score of 33 — below where they started. This is "regression by improvement": tinkering with code that\'s mostly working until it no longer works at all.',
            'what_to_look_for': [
                'The first attempt (set subtraction) is creative but uses Python incorrectly',
                'At 18 seconds, a clean working approach passes 2/3 tests — the student is nearly there',
                'The remaining issue is subtle: sets in Python don\'t preserve the order characters appear',
                'Every change after 18 seconds makes things worse rather than better',
            ],
        },
        make_code_slide(r6_e0, None,
            heading='Creative Idea, Wrong Syntax',
            body='<strong>Line 6:</strong> <code>y = x - s</code>. The student is thinking: "all characters minus unique characters = repeated characters." The idea is clever! But you can\'t subtract a set from a list in Python — they\'re different types. This crashes immediately. Still, the thinking is more sophisticated than most first attempts.',
            note='Mental model: "Subtracting sets gives me the duplicates." The idea is borrowed from math (set difference), but Python requires both sides to be the same type.',
            manual_highlight=[6],
        ),
        make_code_slide(r6_e1, r6_e0,
            heading='Trying Something, Anything',
            body='1 second later, the student changes <strong>Line 6</strong> to just <code>y = x</code> — returning the full list of characters, not the repeating ones. This isn\'t the answer either, but shows they\'re feeling around for what works. The set <code>s</code> is now built but never used.',
            note='Mental model: "Maybe if I simplify it, something will click." Students sometimes reduce code to make it run at all, even if incorrectly, before building back up.',
            manual_highlight=[5, 6],
        ),
        make_code_slide(r6_e2, r6_e1,
            heading='18 Seconds: A Real Working Approach',
            body='Now the logic is clear: <strong>Lines 7–9</strong> iterate over each unique character, check if it appears more than once in the original string, and collect it. This is correct! It passes 2/3 public tests. The remaining failure is an ordering issue: when you loop over a <em>set</em>, the characters come back in random order — not in the order they first appeared in the string.',
            note='Mental model: "I\'ll check each unique character." Sound logic! But sets in Python shuffle their contents — the output order is unpredictable, and the test expects a specific order.',
            manual_highlight=[7, 8, 9, 10],
        ),
        make_code_slide(r6_e3, r6_e2,
            heading='Fixing Order — But Creating Duplicates',
            body='The student switches to looping over the original list <code>x</code> instead of the set: <strong>Line 7: <code>for y in x</code></strong>. This preserves order! But now, if "a" appears 3 times, "a" gets appended 3 times to the result. Instead of <code>["a", "n"]</code>, you\'d get <code>["a", "a", "a", "n", "n"]</code>. Fixing one problem introduced another.',
            note='Mental model: "If I loop over the original, I\'ll get the right order." True — but without a check for "have I already added this?", duplicates pile up.',
            manual_highlight=[7, 8, 9, 10],
        ),
        make_code_slide(r6_e4, r6_e3,
            heading='Adding Complexity Instead of a Simple Check',
            body='46 seconds in: the student adds a second loop to de-duplicate the result. But <strong>Line 20:</strong> <code>z.append(p), q.remove(p)</code> — this is a Python <em>tuple expression</em>, not two separate statements. Python will run both, but the comma creates a tuple which is appended to <code>z</code> rather than the character itself. The output is now a list of tuples instead of characters.',
            note='Mental model: "I\'ll clean up the result in a second pass." The approach would work conceptually, but a comma between two function calls doesn\'t mean "do both" — it creates a tuple.',
            manual_highlight=[20],
        ),
        make_code_slide(r6_e5, r6_e4,
            heading='Public Tests Pass Again — But Private Still Fail',
            body='56 seconds in, 3/3 public tests pass again. But private tests still fail, and the final score is 33. The solution at this point is similar to the one at 18 seconds — close, but still with the ordering issue. The best version of the code existed 38 seconds ago. All the changes since then were net-negative.',
            note='The student never saved their best version. If they\'d submitted at 18 seconds with 2/3 public, they might have done better than 33 — or at least kept a working foundation to improve from.',
            manual_highlight=[10, 11, 12, 15, 16, 17],
        ),
        {
            'type': 'summary',
            'heading': 'Key Takeaways',
            'bullets': [
                '<strong>Sets don\'t preserve order — a lesson worth teaching explicitly.</strong> <code>set("banana")</code> might give <code>{\'b\', \'n\', \'a\'}</code> in any order. Students who rely on sets for ordered output will fail tests that check order. The fix: loop over the original string, not the set.',
                '<strong>The "regression by improvement" pattern is common and costly.</strong> Students who keep editing passing code often end up worse off. Teaching them to <em>save checkpoints</em> — or at least note down what was working — prevents hours of backtracking.',
                '<strong>Commas between expressions create tuples, not separate statements.</strong> <code>f(a), g(b)</code> runs both but produces a tuple. This is a subtle Python behavior that trips up students coming from other languages.',
                '<strong>Partial credit is often better than zero, but students don\'t always know to stop.</strong> A submission at 18 seconds with 2/3 public tests might have earned more than the final 33 score.',
            ],
            'intervention': 'Demo set ordering explicitly: run <code>for c in set("banana"): print(c)</code> several times and show that the order changes. Then ask: "How would you loop over the characters in the order they appear?" Lead them to: iterate over the string, check the count, and use an <code>if c not in result</code> guard to avoid duplicates.',
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
    'insight': 'This student reached 4 out of 5 public tests multiple times — and never submitted. Not because time ran out, but because they never felt certain enough to commit. A lesson in what the "last-mile gap" looks like from the inside.',
    'tags': ['no submission', 'confidence gap', 'nested loops', 'confusion compounding'],
    'slides': [
        {
            'type': 'intro',
            'heading': 'The Problem',
            'question_desc': 'Given a list of strings, count how many strings have <em>more vowels than consonants</em>. Return that count as a number.',
            'question_code': '["hello", "sky", "area"]  →  2\n  # "hello": 2 vowels (e,o), 3 consonants → no\n  # "sky":   0 vowels, 3 consonants → no\n  # "area":  3 vowels (a,e,a), 1 consonant → yes\n  # → count is 1... wait, "hello" is tricky!\n  # Result: 1 (only "area")',
            'why': 'The student gets 4/5 public tests passing — they\'re so close! But their "working" solution is actually returning a fixed value by accident, not solving the problem correctly. And they never submit. This replay explores two things: how students get fooled by lucky test results, and why confidence matters as much as correctness at submission time.',
            'what_to_look_for': [
                'First attempt: treating the whole list as if it were a single string',
                'Calling <code>help()</code> during a timed session — a sign of panic',
                'Code inside triple-quoted strings (the student "comments out" by accident)',
                'Getting 4/5 tests by always returning the number 1 — a coincidence, not a solution',
            ],
        },
        make_code_slide(r7_e0, None,
            heading='Wrong Level: Words vs. Characters',
            body='<strong>Lines 9–12:</strong> the student loops over each word, then checks <code>if word in "aeiou"</code>. This asks: "is this entire word the letter a, e, i, o, or u?" A word like "hello" is never in "aeiou" — only single vowel characters are. The student needs two loops: one over words, and one over <em>characters inside each word</em>.',
            note='Mental model: "I\'m checking if the word contains a vowel." But <code>in</code> checks for exact membership — "hello" is not in the string "aeiou". They need to loop over each letter in the word.',
            manual_highlight=[9, 10, 11, 12],
        ),
        make_code_slide(r7_e1, r7_e0,
            heading='Calling a Built-In That Doesn\'t Exist This Way',
            body='18 seconds in. <strong>Line 12:</strong> <code>c = count(strings)</code> — there is no free-standing <code>count()</code> function. Python has <code>list.count(value)</code> to count how many times a specific item appears in a list, but that\'s different. The student is imagining a shortcut. Also, the <code>if word in "aeiou"</code> bug persists on line 9.',
            note='Mental model: "There should be a <code>count()</code> function that counts things for me." When students don\'t know the right tool, they guess names that sound reasonable.',
            manual_highlight=[12],
        ),
        make_code_slide(r7_e2, r7_e1,
            heading='Triple Quotes as Accidental "Comments"',
            body='38 seconds in. <strong>Lines 4–7</strong> are now inside a triple-quoted string — the student\'s old logic has been "commented out" by wrapping it. But it\'s not really a comment: it\'s a string literal that Python creates and immediately throws away. The active code now does <strong>Line 8:</strong> <code>if strings[0:n] == "aeiou"</code> — comparing a slice of the <em>list</em> to the word "aeiou". This will always be False.',
            note='Mental model: "Triple quotes turns things into comments." In Python, triple-quoted strings are just string values. They don\'t comment out code unless assigned to nothing — and even then they\'re not quite comments.',
            manual_highlight=[4, 5, 6, 7],
        ),
        make_code_slide(r7_e3, r7_e2,
            heading='4/5 Public Tests — By Accident',
            body='53 seconds in. <strong>Line 6:</strong> <code>return strings.count("aeiou") + 1</code>. This counts how many times the string <code>"aeiou"</code> appears as an element in the list — which is always 0 (no list element is exactly "aeiou"). So the function always returns <code>0 + 1 = 1</code>. Four of the five public test cases expect the answer to be 1. So 4/5 tests "pass" — but not because the logic is right.',
            note='Mental model: "count() tells me how many vowels there are." But <code>list.count(x)</code> counts how many times <em>x</em> appears as a list element — not characters inside elements.',
            manual_highlight=[6],
        ),
        make_code_slide(r7_e4, r7_e3,
            heading='Still 4/5 Public, 0 Private',
            body='67 seconds in, nothing has changed in the logic. The function still returns 1 unconditionally. Private tests reveal the truth: 0/2. The student is stuck — they can see 4/5 working, but they don\'t understand why the 5th fails, and they can\'t see the private tests. Without visibility into what\'s failing, they can\'t fix it.',
            note='The 4/5 public score creates a false signal: "I\'m almost there." But the solution is fundamentally wrong. 4/5 here doesn\'t mean "one edge case away from correct."',
            manual_highlight=[5, 6, 7],
        ),
        make_code_slide(r7_e5, r7_e4,
            heading='Time Up — Nothing Submitted',
            body='75 seconds in. The session ends with no submission. The student had 4/5 public tests passing for the last 20 seconds but never committed. This is the "confidence gap": even partial credit (which a submission would earn) is better than zero, but the student doesn\'t feel ready to submit and keeps trying to improve a solution they don\'t fully understand.',
            note='No submission is often a signal of low confidence, not lack of effort. Students may feel that submitting "wrong" code is worse than not submitting — especially under test conditions.',
            manual_highlight=[5, 6, 7],
        ),
        {
            'type': 'summary',
            'heading': 'Key Takeaways',
            'bullets': [
                '<strong>Test scores can be misleading.</strong> 4/5 public tests passing doesn\'t mean the logic is 80% correct — it can mean a completely wrong solution happened to match 4 test cases. Students and instructors should look at the logic, not just the score.',
                '<strong>The "list vs. string" distinction trips up many beginners.</strong> The problem requires looping over words <em>and</em> over letters inside each word. Students who only do one level of looping will never solve it. Teaching "nested loops for nested data" explicitly helps.',
                '<strong>No submission often means low confidence, not no solution.</strong> Students who don\'t submit near a deadline usually need encouragement: "Submit what you have — partial credit is better than zero." This is a simple, high-impact nudge.',
                '<strong>Python\'s <code>in</code> operator checks exact membership.</strong> <code>"hello" in "aeiou"</code> is False because "hello" is not a single character in that string. Students need explicit examples of the difference between <code>"h" in "hello"</code> (True) and <code>"hello" in "aeiou"</code> (False).',
            ],
            'intervention': 'Draw it out: "Your function gets a <em>list</em> of <em>strings</em>. Each string has <em>letters</em>. How many loops do you need?" Then walk through: <code>for word in strings:</code> → <code>for letter in word:</code> → <code>if letter in "aeiou":</code>. Seeing the three levels labeled explicitly helps students map code to concept. Then remind them: always submit something near the deadline.',
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

def render_code_block(code, added, changed, highlight, annotation='', body='', note=''):
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
            body_part = f'<span class="ann-body">{body}</span>' if body else ''
            note_part = f'<span class="ann-note">💭 {note}</span>' if note else ''
            out.append(
                f'<span class="code-ann" role="note">'
                f'<span class="ann-heading">{annotation}</span>'
                f'{body_part}'
                f'{note_part}'
                f'</span>'
            )
    out.append('</code></pre>')
    return ''.join(out)

def render_slide(slide, slide_idx, replay_id):
    stype = slide['type']
    sid = f'{replay_id}-s{slide_idx}'

    if stype == 'intro':
        # Use raw HTML (trusted author content) — do NOT escape
        wlf = ''.join(f'<li>{item}</li>' for item in slide.get('what_to_look_for', []))
        q_code = slide.get('question_code', '')
        q_code_block = f'<pre class="intro-code">{html.escape(q_code)}</pre>' if q_code else ''
        return f'''
<div class="slide slide-intro" id="{sid}">
  <div class="intro-layout">
    <div class="intro-top">
      <h2 class="intro-heading">{slide["question_desc"]}</h2>
      {q_code_block}
    </div>
    <div class="intro-cols">
      <div class="intro-col intro-why">
        <div class="intro-col-label">Why this replay?</div>
        <p class="intro-col-text">{slide["why"]}</p>
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
            body=slide.get('body', ''),
            note=slide.get('note', ''),
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
  </div>
</div>'''

    elif stype == 'summary':
        # Use raw HTML (trusted author content)
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
      max-height: calc(100vh - 44px - 28px - 50px - 38px);
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
      display: block;
      margin: 0.4rem 1rem 0.4rem calc(1rem + 2.5em + 1em + 3px);
      background: rgba(26,22,10,0.7);
      border-left: 3px solid #d29922;
      padding: 0.6rem 0.9rem 0.65rem;
      white-space: normal;
    }
    .ann-heading {
      display: block;
      font-family: "Outfit", sans-serif;
      font-size: 14px; font-weight: 700; letter-spacing: 0.01em;
      color: #e8c888; margin-bottom: 0.3rem;
      text-transform: none;
    }
    .ann-heading code {
      font-family: "IBM Plex Mono", monospace; font-size: 0.85em;
      background: rgba(255,255,255,0.07); padding: 0.05em 0.32em;
      border-radius: 3px; color: #f0d080; display: inline;
    }
    .ann-body {
      display: block;
      font-family: "Outfit", sans-serif;
      font-size: 14px; line-height: 1.55; color: #b0bdcf;
    }
    .ann-body strong { color: var(--ink); }
    .ann-body code {
      font-family: "IBM Plex Mono", monospace; font-size: 0.85em;
      background: rgba(255,255,255,0.07); padding: 0.05em 0.32em;
      border-radius: 3px; color: #e8c888; display: inline;
    }
    .ann-body em { color: #89b4fa; font-style: normal; font-weight: 500; display: inline; }
    .ann-note {
      display: block;
      font-family: "Outfit", sans-serif;
      font-size: 13px; line-height: 1.45;
      color: #7a8499; margin-top: 0.35rem;
      border-top: 1px solid rgba(255,255,255,0.06);
      padding-top: 0.3rem;
    }
    .ann-note code {
      font-family: "IBM Plex Mono", monospace; font-size: 0.85em;
      background: rgba(255,255,255,0.06); padding: 0.05em 0.32em;
      border-radius: 3px; color: #8a9ab0; display: inline;
    }
    .ann-note em { font-style: italic; color: #6a7a8f; display: inline; }

    /* ── Commentary strip (bottom of code slide) — meta only ──── */
    .commentary-strip {
      flex-shrink: 0;
      background: var(--strip-bg); border-top: 1px solid var(--strip-border);
      padding: 0.35rem 1.2rem;
      min-height: 0; height: 38px;
      display: flex; align-items: center;
    }
    .strip-meta {
      display: flex; gap: 0.6rem; align-items: center;
      flex-wrap: wrap;
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

    /* ── Intro slide ───────────────────────────────────────────── */
    .slide-intro { display: flex; flex-direction: column; justify-content: center; }
    .intro-layout {
      max-width: 960px; width: 100%; margin: 0 auto;
      display: flex; flex-direction: column; padding: 1.6rem 2.5rem 1.4rem;
      gap: 1rem; overflow-y: auto;
    }
    .intro-top {}
    .intro-heading {
      font-family: "Fraunces", serif;
      font-size: clamp(1.4rem, 2.5vw, 1.9rem);
      line-height: 1.25; color: var(--ink); margin-bottom: 0.4rem;
    }
    .intro-heading code {
      font-family: "IBM Plex Mono", monospace; font-size: 0.85em;
      background: rgba(255,255,255,0.08); padding: 0.1em 0.4em;
      border-radius: 4px; color: #e8c888;
    }
    .intro-code {
      font-family: "IBM Plex Mono", monospace; font-size: 13px;
      line-height: 1.5; color: #b0bdcf;
      background: var(--code-bg); border: 1px solid var(--border);
      border-radius: var(--r); padding: 0.6rem 1rem;
      margin-top: 0.3rem; white-space: pre;
    }
    .intro-cols {
      display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem;
    }
    .intro-col {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--r); padding: 1rem 1.2rem;
    }
    .intro-col-label {
      font-family: "IBM Plex Mono", monospace; font-size: 0.72rem;
      text-transform: uppercase; letter-spacing: 0.08em;
      color: var(--accent); margin-bottom: 0.5rem;
    }
    .intro-col-text { font-size: 15px; line-height: 1.6; color: #b0bdcf; }
    .intro-col-text code {
      font-family: "IBM Plex Mono", monospace; font-size: 0.85em;
      background: rgba(255,255,255,0.07); padding: 0.05em 0.35em;
      border-radius: 3px; color: #e8c888;
    }
    .intro-look-list {
      font-size: 15px; line-height: 1.6; color: #b0bdcf;
      padding-left: 1.1em; display: flex; flex-direction: column; gap: 0.35rem;
    }
    .intro-look-list li::marker { color: var(--accent); }
    .intro-look-list code {
      font-family: "IBM Plex Mono", monospace; font-size: 0.85em;
      background: rgba(255,255,255,0.07); padding: 0.05em 0.35em;
      border-radius: 3px; color: #e8c888;
    }

    /* ── Summary slide ─────────────────────────────────────────── */
    .slide-summary { display: flex; flex-direction: column; justify-content: center; }
    .summary-layout {
      max-width: 1100px; width: 100%; margin: 0 auto;
      display: flex; flex-direction: column;
      padding: 1.6rem 2.5rem 1.4rem; gap: 1rem; overflow-y: auto;
    }
    .summary-heading {
      font-family: "Fraunces", serif;
      font-size: clamp(1.4rem, 2.5vw, 1.8rem);
      color: var(--accent); margin-bottom: 0;
    }
    .summary-cards {
      display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.8rem;
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
