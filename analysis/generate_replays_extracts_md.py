#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["duckdb>=1.4.0"]
# ///
"""Generate a stage-ready extracts sheet for the replay talk outline."""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
PROCESS_CSV = ANALYSIS_DIR / "process_analysis" / "attempt_archetypes.csv"
TIMELINE_PARQUET = ANALYSIS_DIR / "submission_timeline.parquet"
SNAPSHOTS_PARQUET = ANALYSIS_DIR / "code_snapshots.parquet"
OUT_PATH = ANALYSIS_DIR / "replays-extracts.md"


@dataclass(frozen=True)
class EventRef:
    event_no: int
    note: str
    replay_timestamp: str | None = None


@dataclass(frozen=True)
class BeatConfig:
    label: str
    student_id: str
    beat_kind: str
    why_in_talk: str
    response_summary: str
    snippet: str | None
    clip_focus: str
    outline_lines: list[str]
    stage_notes: list[str]
    event_refs: list[EventRef]


@dataclass(frozen=True)
class QuestionConfig:
    order: int
    namespace: str
    problem_id: int
    stage_title: str
    why_here: str
    transition_line: str
    contract_summary: str
    prompt_notes: list[str]
    hidden_test_notes: list[str]
    source_artifacts: list[tuple[str, str]]
    beats: list[BeatConfig]


@dataclass(frozen=True)
class SkeletonInfo:
    prefixed_code: str
    uneditable_code: str
    suffixed_invisible_code: str


QUESTIONS: list[QuestionConfig] = [
    QuestionConfig(
        order=1,
        namespace="ns_25t2_py11_1",
        problem_id=6,
        stage_title="Parsing by Shape, Not Contract",
        why_here=(
            "Shortest replays in the set. The full arc of clean solution, productive struggle, and public-pass/private-fail overfit fits into under ninety seconds of screen time."
        ),
        transition_line=(
            "That gap between public and private tests: let’s see it again on a harder question."
        ),
        contract_summary=(
            "Parse a card string of the form `{rank}{suit}` and return the tuple `(suit_value, rank_value)`. "
            "The key conceptual move is to parse by string shape (`card[:-1]`, `card[-1]`), not by assuming the rank is always one character."
        ),
        prompt_notes=[
            "The prompt examples already include `10D -> (3, 10)`, so the multi-character-rank case is visible in the statement even though it is absent from the public tests.",
            "The output contract is exact: tuple type and tuple order both matter.",
        ],
        hidden_test_notes=[
            "Public tests cover only one-character ranks: `AH`, `7D`, `QS`, `9C`.",
            "Private group 2 introduces `10H`, which instantly exposes `card[0]` / `card[1]` parsers.",
            "This is the cleanest repo example of 'prompt examples and public tests are not the whole task.'",
        ],
        source_artifacts=[
            ("problem JSON", "problems/ns_25t2_py11_1/6.json"),
            ("same-code public/private gap table", "analysis/classical_item_quality/public_private_gap_same_code_by_question.csv"),
        ],
        beats=[
            BeatConfig(
                label="Student 1 — The Baseline",
                student_id="e42a471813ae41a7b30d2f6927d92c32",
                beat_kind="baseline",
                why_in_talk=(
                    "Opens the talk with the cleanest possible contract-reading replay."
                ),
                response_summary=(
                    "Uses `card[:-1]` for rank and `card[-1]` for suit, then does direct dictionary/int conversion."
                ),
                snippet="rank = card[:-1]\nsuit = card[-1]",
                clip_focus="Show events 1-4 as a compact code sequence. First run passes. No edits. Submission.",
                outline_lines=[
                    "This student modelled the input as a variable-width string before touching the keyboard.",
                    "This is what it looks like when someone reads the contract before they read the examples.",
                ],
                stage_notes=[
                    "Ten-second warm opener.",
                    "Use this replay to establish the intended mental model before showing struggle and overfit.",
                ],
                event_refs=[
                    EventRef(1, "First public run already passes.", replay_timestamp="earlier cast timing: `0:00-0:10`"),
                    EventRef(2, "Private all-pass lands immediately."),
                    EventRef(4, "Submission follows with no substantive edits."),
                ],
            ),
            BeatConfig(
                label="Student 2 — The Funny/Productive Struggle",
                student_id="56036b0cfd0a453da93c959861c50f96",
                beat_kind="productive-struggle",
                why_in_talk=(
                    "First gentle laugh of the talk: the student understands the logic but loses a short fight with Python syntax and output order."
                ),
                response_summary=(
                    "Computes the right values early, but first writes `tuple(a,b)`, then `(a,b)`, then finally fixes the tuple order."
                ),
                snippet="return tuple(a,b)\n# then (a, b)\n# then (b, a)",
                clip_focus="Show the line `tuple(a,b)`, pause, then let the replay run through the tuple-order repair.",
                outline_lines=[
                    "Everything is right except the punctuation.",
                    "Everything is right except left and right.",
                ],
                stage_notes=[
                    "This is a universal Python laugh, not ridicule.",
                    "The repair is fast enough that the audience can hold the whole contract in working memory.",
                ],
                event_refs=[
                    EventRef(1, "Runtime error on the constructor call."),
                    EventRef(2, "Now runnable, but tuple order is still wrong."),
                    EventRef(3, "Public all-pass after swapping tuple order."),
                    EventRef(4, "Private all-pass arrives seconds later."),
                    EventRef(6, "Submission lands at full pass."),
                ],
            ),
            BeatConfig(
                label="Student 3 — The Hidden Boss",
                student_id="ad7a05553f034a4a9766e6061a80ed7f",
                beat_kind="public-private-gap",
                why_in_talk=(
                    "This is the conceptual anchor for the whole talk: green public checks do not mean the underlying abstraction is right."
                ),
                response_summary=(
                    "Ends on a neat-looking one-character parser with `card[0]` and `card[1]`, which passes public tests and then fails private tests on a two-character rank."
                ),
                snippet="rank = card[0]\nsuit = card[1]",
                clip_focus="Build suspense around the public `2/2`, then put `10D` on the slide when private drops to `50`.",
                outline_lines=[
                    "The only two-character card in the deck walks on stage like a hidden boss, and `10D` destroys the parser in one step.",
                    "The visible examples are not the task.",
                ],
                stage_notes=[
                    "Use `10D` as the first recurring refrain of the talk.",
                    "This replay is short enough to keep the contrast extremely sharp.",
                ],
                event_refs=[
                    EventRef(1, "Early indexing attempt crashes immediately."),
                    EventRef(2, "Public tests are now fully green.", replay_timestamp="`0:56-1:02`"),
                    EventRef(3, "Private tests drop to `50`; one hidden case breaks the parser."),
                    EventRef(5, "Submission freezes the overfit in place."),
                ],
            ),
        ],
    ),
    QuestionConfig(
        order=2,
        namespace="ns_25t2_py22_1",
        problem_id=15,
        stage_title="Negotiating With the Tests",
        why_here=(
            "Three different failure modes on the same tiny problem, plus the strongest laugh-per-line ratio in the set."
        ),
        transition_line=(
            "Same pattern again: examples memorized, rule ignored, but now the whole algorithm collapses to one sentence."
        ),
        contract_summary=(
            "Return `True` only when the string starts with `'Hello '` or `'Hi '`. "
            "The crucial contract details are the trailing space, case sensitivity, no leading whitespace, and empty-string safety."
        ),
        prompt_notes=[
            "The public prompt examples already contrast `'Hello World'` with `'HelloWorld'` to signal the trailing-space requirement.",
            "Because this is a function question, students who think in 'just patch the visible strings' mode are especially exposed.",
        ],
        hidden_test_notes=[
            "Public tests include `Hithere -> False`, which becomes the target of literal patching in the funniest replay.",
            "Private tests cover bare greetings without a space, lowercase `'hello world'`, leading whitespace, empty string, and exact `'Hi '` / `'Hello '` edge cases.",
            "One missing condition is enough to explain the public/private gap here; the question rewards small semantic repairs, not rewrites.",
        ],
        source_artifacts=[
            ("problem JSON", "problems/ns_25t2_py22_1/15.json"),
            ("error cluster analysis", "analysis/ERRORS-cluster-c078-check-for-greeting-prefix-969f783c.md"),
        ],
        beats=[
            BeatConfig(
                label="Student 1 — The Baseline",
                student_id="0fdf6645bdc54e7da88566e0422fbda1",
                beat_kind="baseline",
                why_in_talk=(
                    "Fastest possible semantic translation of an English sentence into exact Python."
                ),
                response_summary=(
                    "Writes the full solution immediately: `s.startswith('Hello ') or s.startswith('Hi ')`."
                ),
                snippet="return s.startswith('Hello ') or s.startswith('Hi ')",
                clip_focus="Show the whole one-second replay and move on.",
                outline_lines=[
                    "The student read the sentence 'starts with Hello or Hi followed by a space' and wrote exactly that in Python. Nothing more.",
                ],
                stage_notes=[
                    "This is the contrast case for all the spec-reading failures that follow.",
                ],
                event_refs=[
                    EventRef(1, "First checkpoint already passes private `3/3`."),
                    EventRef(2, "Public also passes `4/4`."),
                    EventRef(3, "Submission follows immediately."),
                ],
            ),
            BeatConfig(
                label="Funny Moment 1 — JavaScript Accent",
                student_id="60f6e5f27899406ea16a5470210db8d1",
                beat_kind="funny-syntax",
                why_in_talk=(
                    "Highest-immediacy syntax laugh in the repo."
                ),
                response_summary=(
                    "Starts with `s.startswith('Hello'|| 'Hi')`, then `s.startswith('Hello' or 'Hi')`, before eventually landing on a valid two-prefix check."
                ),
                snippet="s.startswith('Hello'|| 'Hi')\n# then\ns.startswith('Hello' or 'Hi')",
                clip_focus="Show the first two code states and read the opening line out loud before explaining it.",
                outline_lines=[
                    "Python, but spoken with a JavaScript accent.",
                    "The intent is perfect. The operator is from another universe.",
                    "Surface intent can be completely correct while language fluency is still catching up.",
                ],
                stage_notes=[
                    "Let the audience catch the bug before you explain it.",
                ],
                event_refs=[
                    EventRef(1, "Immediate runtime failure on the first attempt.", replay_timestamp="earlier cast timing: `0:00-0:03`"),
                    EventRef(2, "Second attempt is still semantically wrong, even though the syntax is now valid."),
                    EventRef(3, "The student is still only at public `3/4`, despite basically understanding the goal."),
                ],
            ),
            BeatConfig(
                label="Student 2 — The Trailing Space Repair",
                student_id="aa68a2811ed74d968987be81d3d6fb31",
                beat_kind="hidden-test-repair",
                why_in_talk=(
                    "Cleanest illustration that one hidden failure can point to one missing condition."
                ),
                response_summary=(
                    "Starts with `startswith('Hello')` / `startswith('Hi')`, then adds the trailing space after a single private miss."
                ),
                snippet="return s.startswith('Hello') or s.startswith('Hi')\n# then\nreturn s.startswith('Hello ') or s.startswith('Hi ')",
                clip_focus="Show the miss (`3/4`, then `67`) and the one-line repair to full pass.",
                outline_lines=[
                    "Ask the room: what exact contract did the public tests fail to make you notice?",
                    "This is the cleanest illustration of 'one hidden case, one missing condition, not a rewrite.'",
                ],
                stage_notes=[
                    "Very efficient clip for boundary-case reasoning.",
                ],
                event_refs=[
                    EventRef(1, "Public `3/4`; missing-space prefixes still look mostly right."),
                    EventRef(2, "Private `67`; hidden tests reveal the missing condition."),
                    EventRef(4, "Public reaches `4/4` after adding spaces."),
                    EventRef(5, "Private reaches `100`."),
                    EventRef(7, "Submission locks in the repair."),
                ],
            ),
            BeatConfig(
                label="Funny Moment 2 — Negotiating With the Grader",
                student_id="60f6e5f27899406ea16a5470210db8d1",
                beat_kind="funny-overfit",
                why_in_talk=(
                    "Pure sample patching, visible in one line."
                ),
                response_summary=(
                    "The first all-public-pass version contains `if s == 'Hithere': return False` before a still-brittle prefix rule."
                ),
                snippet="if s == 'Hithere':\n    return False",
                clip_focus="Jump to event `81`, then show private falling immediately after on event `82`.",
                outline_lines=[
                    "The student has entered treaty negotiations with the grader.",
                    "This is not debugging. This is diplomacy.",
                ],
                stage_notes=[
                    "A good moment to name sample-patching behavior kindly but precisely.",
                ],
                event_refs=[
                    EventRef(81, "First all-public pass appears.", replay_timestamp="earlier cast timing: `~59.7s`"),
                    EventRef(82, "Private immediately falls back to `67`."),
                    EventRef(157, "Private all-pass comes much later, after extensive thrashing."),
                    EventRef(166, "First successful submission finally lands."),
                ],
            ),
            BeatConfig(
                label="Funny Moment 3 — The Triple-Quoted Graveyard",
                student_id="590240758edf48fa81f701ae4295dc82",
                beat_kind="funny-regression",
                why_in_talk=(
                    "High-recognition debugging laugh that also teaches why students use comments as version control."
                ),
                response_summary=(
                    "The better boundary-aware solution exists in the file, but only inside triple quotes. The weaker rule remains live."
                ),
                snippet='""" better boundary-aware version lives here """',
                clip_focus="Do not play the whole session. Show the static before/after state: correct code buried, wrong code running.",
                outline_lines=[
                    "The fix exists. It's just not allowed to run.",
                    "I call this the triple-quoted graveyard: the correct solution was buried alive while the wrong one inherited the execution runtime.",
                ],
                stage_notes=[
                    "This gets both the laugh and the sympathetic nod.",
                    "Use it to discuss ad-hoc version control and regression risk.",
                ],
                event_refs=[
                    EventRef(7, "First private `67` arrives on the broad `strip()`-based rule."),
                    EventRef(16, "Public finally reaches `4/4` with a better boundary-aware approach."),
                    EventRef(17, "Private still catches a hidden edge case."),
                    EventRef(131, "Final submission is back at `67`; the better code is commented out."),
                ],
            ),
        ],
    ),
    QuestionConfig(
        order=3,
        namespace="ns_25t3_py13_1",
        problem_id=7,
        stage_title="Solving the Examples, Not the Problem",
        why_here=(
            "The purest overfitting exhibit in the dataset, plus two of the best comic student responses in the whole repo."
        ),
        transition_line=(
            "Let’s move from sentence structure to something even more fundamental: what is a pangram, really?"
        ),
        contract_summary=(
            "Split a three-word sentence, treat `order` as a tuple of indices, and return the reordered sentence. "
            "The question is tiny, so the difference between abstraction and memorization becomes visible immediately."
        ),
        prompt_notes=[
            "The public prompt examples all use visible words and visible permutations, which makes sample memorization tempting.",
            "The intended abstraction is short enough to fit in a single line of working memory.",
        ],
        hidden_test_notes=[
            "Private tests introduce unseen vocabularies and additional order tuples, including the identity order `(0, 1, 2)`.",
            "One hard-coded public sentence can pass all public tests and still fail every private test.",
            "Because the universe has only six permutations, brute-force case listing can also succeed, which makes for a valuable teaching contrast.",
        ],
        source_artifacts=[
            ("problem JSON", "problems/ns_25t3_py13_1/7.json"),
            ("error cluster analysis", "analysis/ERRORS-cluster-c002-shuffle-a-three-word-sentence-6b942fc6.md"),
        ],
        beats=[
            BeatConfig(
                label="Student 1 — The Baseline",
                student_id="ebd2cfa0ce7e4554850c3bc999fa10e2",
                beat_kind="baseline",
                why_in_talk=(
                    "Shows the intended abstraction in one line before the overfitting cases arrive."
                ),
                response_summary=(
                    "Splits the sentence, indexes the three positions from `order`, and joins them back into a string."
                ),
                snippet="words = sentence.split()\nreturn f\"{words[order[0]]} {words[order[1]]} {words[order[2]]}\"",
                clip_focus="Show the three code states in order; the whole arc is effectively instantaneous.",
                outline_lines=[
                    "The student treated `order` as data. One line. Full pass.",
                    "The intended abstraction, visible in working memory.",
                ],
                stage_notes=[
                    "This baseline makes the later hard-coded clips look obviously like different ways of thinking.",
                ],
                event_refs=[
                    EventRef(1, "Private all-pass is already there."),
                    EventRef(2, "Public also passes immediately."),
                    EventRef(3, "Submission follows unchanged."),
                ],
            ),
            BeatConfig(
                label="Funny Moment 4 — The Entire Function Learns One Fruit Sentence",
                student_id="384851c6834647139983873aea99d419",
                beat_kind="funny-overfit",
                why_in_talk=(
                    "Purest innocent overfit in the repo."
                ),
                response_summary=(
                    "Improves public results by hard-coding more sample cases, culminating in `if order == (0, 2, 1): return 'apple orange banana'`."
                ),
                snippet="if order == (0, 2, 1):\n    return 'apple orange banana'",
                clip_focus="Walk through public `1/3`, `2/3`, `3/3`, then the private `0/3` collapse.",
                outline_lines=[
                    "This function is convinced that all sentence shuffling in Python is secretly about one fruit salad.",
                    "The student didn't learn the transformation rule. They learned the example.",
                    "The visible tests are not the task.",
                ],
                stage_notes=[
                    "Pause after the fruit-salad line. The absurdity lands on its own.",
                ],
                event_refs=[
                    EventRef(1, "Public begins at `1/3` with a sample-specific idea."),
                    EventRef(2, "Public climbs to `2/3` by adding more case-specific logic."),
                    EventRef(3, "Public reaches `3/3` without becoming generic."),
                    EventRef(4, "Private immediately drops to `0/3`."),
                    EventRef(6, "Submission stays at zero."),
                ],
            ),
            BeatConfig(
                label="Funny Moment 5 — Why Use a Tuple When You Can List Every Universe",
                student_id="107337b2583a4bfebe3e917b315d2684",
                beat_kind="finite-state-bruteforce",
                why_in_talk=(
                    "Shows a correct but non-transferable strategy: exhaustive case listing over a tiny state space."
                ),
                response_summary=(
                    "Enumerates all six possible three-word permutations with explicit `if/elif` branches."
                ),
                snippet="if order == (0, 1, 2): ...\nelif order == (0, 2, 1): ...\n# ... all six permutations",
                clip_focus="Show a few branches, then reveal that all six permutations are listed and the code really does pass.",
                outline_lines=[
                    "Brute force wins a small, perfectly legal victory over elegance.",
                    "Some students reason by cases before they reason by data structure. That's not a bug. It's a stage.",
                ],
                stage_notes=[
                    "This is a subtler laugh than the fruit-salad clip, but a stronger learning-pattern conversation.",
                ],
                event_refs=[
                    EventRef(1, "Early public runs show the branch table is incomplete."),
                    EventRef(3, "Public reaches only `1/3` after some case enumeration."),
                    EventRef(6, "Public finally reaches `3/3`."),
                    EventRef(7, "Private also reaches `100`; the brute force really works."),
                    EventRef(9, "Submission locks in the exhaustive solution."),
                ],
            ),
        ],
    ),
    QuestionConfig(
        order=4,
        namespace="ns_25t2_py21_2",
        problem_id=18,
        stage_title="Heuristics vs. Invariants",
        why_here=(
            "Best closing arc: quick baseline, instant laughs, then a long emotionally resonant false summit / recovery story."
        ),
        transition_line="End on save points: the code lesson is real, but the process lesson is bigger.",
        contract_summary=(
            "Return `True` only if the input contains every letter of the alphabet at least once. "
            "The invariant is about distinct alphabetic letters after filtering and lowercasing, not about total character count."
        ),
        prompt_notes=[
            "The sample solution path is short: build an alphabet set and compare it with `set(text.lower())`.",
            "Because the prompt examples are all clean strings, students often miss that punctuation and digits must be filtered out or safely ignored.",
        ],
        hidden_test_notes=[
            "Public tests already mix case, but private tests add punctuation, digits, non-pangrams with many letters, and alternative pangrams.",
            "This is an ideal 'false summit' question because `count >= 26` can pass public tests while still failing private tests immediately.",
            "The long replay also shows the process lesson: recovery is possible, but repeated overwriting makes it slower and more fragile.",
        ],
        source_artifacts=[
            ("problem JSON", "problems/ns_25t2_py21_2/18.json"),
            ("error cluster analysis", "analysis/ERRORS-cluster-c013-pangram-check-f0d5ae7d.md"),
        ],
        beats=[
            BeatConfig(
                label="Student 1 — The Baseline",
                student_id="13bc0b2cf15145219dd6719b89dfc3cd",
                beat_kind="baseline",
                why_in_talk=(
                    "Shortest clean invariant in the whole set."
                ),
                response_summary=(
                    "Builds the alphabet as a set and checks whether it is a subset of `set(text.lower())`."
                ),
                snippet="alphabet = set(string.ascii_lowercase)\nreturn alphabet <= set(text.lower())",
                clip_focus="Show the single-expression invariant as a one-step code reveal.",
                outline_lines=[
                    "Build the alphabet as a set. Check if it's a subset of the lowercase input. That's it.",
                    "The entire invariant in one expression.",
                ],
                stage_notes=[
                    "Use this to anchor the audience before showing heuristic shortcuts.",
                ],
                event_refs=[
                    EventRef(1, "Private all-pass is already present."),
                    EventRef(2, "Public also passes immediately."),
                    EventRef(3, "Submission follows with no edits."),
                ],
            ),
            BeatConfig(
                label="Funny Moment 6 — The Pangram Checker That Forgot C",
                student_id="a2316b024ae946b59ebe2f04090321d9",
                beat_kind="funny-representation-bug",
                why_in_talk=(
                    "The representation used to check the invariant is itself broken."
                ),
                response_summary=(
                    "Builds an alphabet string that omits `c`: `letters = 'absdefghijklmnopqrstuvwxyz'`."
                ),
                snippet='letters = "absdefghijklmnopqrstuvwxyz"',
                clip_focus="Use the code as a static slide. Say nothing for a beat and let the audience spot the missing letter.",
                outline_lines=[
                    "The function whose entire job is to verify all 26 letters starts by forgetting one.",
                    "Under cognitive load, even the checking mechanism needs to be checked.",
                ],
                stage_notes=[
                    "This lands best with silence first.",
                    "It also broadens the talk beyond 'students don't get it' into 'representations themselves can fail under load.'",
                ],
                event_refs=[
                    EventRef(12, "Public first reaches `3/3` even though the internal alphabet model is still wrong."),
                    EventRef(13, "Private drops to `33`; hidden cases expose the missing-letter representation bug."),
                    EventRef(30, "Private all-pass eventually arrives after the representation is fixed."),
                    EventRef(35, "Submission lands at full pass."),
                ],
            ),
            BeatConfig(
                label="Funny Moment 7 + The Regression Arc — 'Lots of Letters'",
                student_id="2ee6740d56614ebbb3e68f6fe2992f28",
                beat_kind="false-summit-and-recovery",
                why_in_talk=(
                    "Combines the funniest heuristic bug with the strongest long-form recovery story."
                ),
                response_summary=(
                    "Starts with brittle filtering, reaches a false summit with `return count >= 26`, then eventually repairs the logic by switching to unique-letter set reasoning."
                ),
                snippet="return count >= 26",
                clip_focus="Show events `61-62` for the heuristic fail, then jump to the late `set()` repair and mention the 107-event session shape.",
                outline_lines=[
                    "Ask the room: is 'aaaaaaaaaaaaaaaaaaaaaaaaaa' great literature?",
                    "The false summit is the moment you think you've solved it.",
                    "The actual solution comes later, when you ask not 'does my code pass?' but 'what family of inputs would break it?'",
                    "This student found the right invariant near the end. But they had overwritten a working partial solution multiple times getting there. The lesson isn't about the code. It's about save points.",
                ],
                stage_notes=[
                    "This is both the heuristic-vs-invariant lesson and the save-points lesson.",
                    "Do not narrate every event; narrate the shape.",
                ],
                event_refs=[
                    EventRef(1, "Starts at public `2/3`; the student is close but not yet reasoning with the full invariant."),
                    EventRef(61, "Public reaches `3/3` on the `count >= 26` heuristic.", replay_timestamp="earlier cast timing: `46.9s-47.2s`"),
                    EventRef(62, "Private immediately fails at `33`; hidden cases reveal the heuristic shortcut."),
                    EventRef(81, "Another false-green cycle: public is back to `3/3`, private still only `33`."),
                    EventRef(103, "Private finally reaches `100` after switching to a real unique-letter invariant."),
                    EventRef(107, "Submission ends at full pass after `107` events and `1:51:23` of active time."),
                ],
            ),
        ],
    ),
]


def fmt_seconds(total_seconds: float | int | None) -> str:
    if total_seconds is None or math.isnan(float(total_seconds)):
        return "-"
    seconds = max(0, int(round(float(total_seconds))))
    hh = seconds // 3600
    mm = (seconds % 3600) // 60
    ss = seconds % 60
    if hh:
        return f"{hh}:{mm:02d}:{ss:02d}"
    return f"{mm}:{ss:02d}"


def fmt_score(score_text: str | float | int | None) -> str:
    if score_text in (None, "", "nan"):
        return "-"
    score = float(score_text)
    if abs(score - round(score)) < 1e-9:
        return str(int(round(score)))
    return f"{score:.1f}"


def rel_report_path(path: str) -> str:
    if path.startswith("analysis/"):
        return "./" + path.removeprefix("analysis/")
    if path.startswith("problems/"):
        return "../" + path
    return path


def normalize_newlines(text: str | None) -> str:
    if not text:
        return ""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def extract_skeleton(problem: dict[str, Any]) -> SkeletonInfo:
    allowed = problem.get("allowed_languages") or []
    lang_obj = next((item for item in allowed if (item or {}).get("language") == "py3"), None)
    if lang_obj is None and allowed:
        lang_obj = allowed[0]
    lang_obj = lang_obj or {}
    return SkeletonInfo(
        prefixed_code=str(lang_obj.get("prefixed_code") or ""),
        uneditable_code=str(lang_obj.get("uneditable_code") or ""),
        suffixed_invisible_code=str(lang_obj.get("suffixed_invisible_code") or ""),
    )


def extract_student_editable_code(full_code: str, sk: SkeletonInfo) -> tuple[str, str]:
    code = normalize_newlines(full_code)
    prefix = normalize_newlines(sk.prefixed_code)
    suffix = normalize_newlines(sk.suffixed_invisible_code)
    uneditable = normalize_newlines(sk.uneditable_code)

    prefix_stripped = False
    suffix_stripped = False

    if prefix:
        if code.startswith(prefix):
            code = code[len(prefix) :]
            prefix_stripped = True
        else:
            idx = code.find(prefix)
            if 0 <= idx <= 8:
                code = code[idx + len(prefix) :]
                prefix_stripped = True

    if suffix:
        if code.endswith(suffix):
            code = code[: -len(suffix)]
            suffix_stripped = True
        else:
            idx = code.rfind(suffix)
            if idx >= 0 and (len(code) - (idx + len(suffix))) <= 8:
                code = code[:idx]
                suffix_stripped = True

    if uneditable and code.startswith(uneditable):
        code = code[len(uneditable) :]

    if prefix or suffix:
        if prefix_stripped and suffix_stripped:
            status = "exact_prefix_suffix"
        elif prefix_stripped or suffix_stripped:
            status = "partial_prefix_suffix"
        else:
            status = "prefix_suffix_not_found"
    else:
        status = "no_scaffolding_config"

    return code.strip("\n"), status


def load_attempt_rows() -> dict[tuple[str, int, str], dict[str, str]]:
    rows: dict[tuple[str, int, str], dict[str, str]] = {}
    with PROCESS_CSV.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            key = (row["namespace"], int(row["problem_id"]), row["student_id"])
            rows[key] = row
    return rows


def load_question_stats(
    keys: list[tuple[str, int]],
) -> dict[tuple[str, int], dict[str, Any]]:
    key_sql = ", ".join(f"('{ns}', {pid})" for ns, pid in keys)
    conn = duckdb.connect()
    try:
        qstats = conn.execute(
            f"""
            WITH chosen(namespace, problem_id) AS (
              VALUES {key_sql}
            )
            SELECT
              a.namespace,
              a.problem_id,
              any_value(a.question_title) AS question_title,
              COUNT(*) AS attempts,
              ROUND(100.0 * AVG(CASE WHEN a.outcome_category = 'Full pass' THEN 1 ELSE 0 END), 1) AS full_pass_pct,
              ROUND(AVG(CAST(a.latest_submission_score AS DOUBLE)), 1) AS avg_score,
              ROUND(AVG(CAST(a.public_test_run_count AS DOUBLE)), 1) AS avg_public_runs
            FROM read_csv_auto(? ) a
            JOIN chosen USING (namespace, problem_id)
            WHERE a.track = 'Track A: submitters'
            GROUP BY 1, 2
            ORDER BY 1, 2
            """,
            [str(PROCESS_CSV)],
        ).fetchall()
        qarch = conn.execute(
            f"""
            WITH chosen(namespace, problem_id) AS (
              VALUES {key_sql}
            ),
            counts AS (
              SELECT
                a.namespace,
                a.problem_id,
                a.primary_archetype,
                COUNT(*) AS attempts
              FROM read_csv_auto(?) a
              JOIN chosen USING (namespace, problem_id)
              WHERE a.track = 'Track A: submitters'
              GROUP BY 1, 2, 3
            ),
            ranked AS (
              SELECT
                *,
                ROW_NUMBER() OVER (
                  PARTITION BY namespace, problem_id
                  ORDER BY attempts DESC, primary_archetype
                ) AS rn
              FROM counts
            )
            SELECT namespace, problem_id, primary_archetype, attempts
            FROM ranked
            WHERE rn <= 4
            ORDER BY namespace, problem_id, rn
            """,
            [str(PROCESS_CSV)],
        ).fetchall()
    finally:
        conn.close()

    out: dict[tuple[str, int], dict[str, Any]] = {}
    for namespace, problem_id, title, attempts, full_pass_pct, avg_score, avg_public_runs in qstats:
        out[(namespace, problem_id)] = {
            "question_title": str(title),
            "attempts": int(attempts),
            "full_pass_pct": float(full_pass_pct),
            "avg_score": float(avg_score),
            "avg_public_runs": float(avg_public_runs),
            "top_archetypes": [],
        }
    for namespace, problem_id, primary_archetype, attempts in qarch:
        out[(namespace, problem_id)]["top_archetypes"].append(
            f"{primary_archetype} ({int(attempts)})"
        )
    return out


def load_problem(namespace: str, problem_id: int) -> dict[str, Any]:
    path = ROOT / "problems" / namespace / f"{problem_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def extract_signature(problem: dict[str, Any]) -> str:
    template = str(problem["allowed_languages"][0]["code_template"])
    for line in template.splitlines():
        stripped = line.strip()
        if stripped.startswith("def "):
            return stripped
    return "-"


def load_events(
    namespace: str,
    problem_id: int,
    student_id: str,
    skeleton: SkeletonInfo,
) -> dict[int, dict[str, Any]]:
    conn = duckdb.connect()
    try:
        rows = conn.execute(
            """
            SELECT
              ROW_NUMBER() OVER (
                ORDER BY timestamp_utc,
                  CASE event_type
                    WHEN 'saved_code' THEN 1
                    WHEN 'test_run' THEN 2
                    WHEN 'submission' THEN 3
                    ELSE 9
                  END,
                  evaluation_type
              ) AS event_no,
              seconds_since_start,
              event_type,
              evaluation_type,
              summary,
              score,
              num_test_passed,
              test_case_count,
              t.code_sha256,
              t.code_length,
              t.is_parseable,
              c.code_snapshot
            FROM read_parquet(?) t
            LEFT JOIN read_parquet(?) c USING (code_sha256)
            WHERE namespace = ?
              AND problem_id = ?
              AND student_id = ?
            ORDER BY 1
            """,
            [str(TIMELINE_PARQUET), str(SNAPSHOTS_PARQUET), namespace, problem_id, student_id],
        ).fetchall()
    finally:
        conn.close()

    out: dict[int, dict[str, Any]] = {}
    for (
        event_no,
        seconds_since_start,
        event_type,
        evaluation_type,
        summary,
        score,
        num_test_passed,
        test_case_count,
        code_sha256,
        code_length,
        is_parseable,
        code_snapshot,
    ) in rows:
        raw_code = str(code_snapshot or "") if code_snapshot is not None else ""
        student_code = ""
        strip_status = "code_missing"
        if raw_code:
            student_code, strip_status = extract_student_editable_code(raw_code, skeleton)
        out[int(event_no)] = {
            "event_no": int(event_no),
            "seconds_since_start": float(seconds_since_start or 0.0),
            "event_type": str(event_type or ""),
            "evaluation_type": str(evaluation_type or ""),
            "summary": str(summary or ""),
            "score": float(score) if score is not None else None,
            "num_test_passed": int(num_test_passed) if num_test_passed is not None else None,
            "test_case_count": int(test_case_count) if test_case_count is not None else None,
            "code_sha256": str(code_sha256 or ""),
            "code_length": int(code_length) if code_length is not None else None,
            "is_parseable": bool(is_parseable) if is_parseable is not None else None,
            "student_code": student_code,
            "strip_status": strip_status,
        }
    return out


def render_testcases(label: str, cases: list[dict[str, Any]]) -> list[str]:
    lines = [f"#### {label}"]
    for idx, case in enumerate(cases, start=1):
        input_text = str(case["input"]).strip()
        output_text = str(case["output"]).strip()
        lines.extend(
            [
                "",
                f"- Group `{idx}`",
                "```py",
                input_text,
                "```",
                "- Expected outputs:",
                "```text",
                output_text,
                "```",
            ]
        )
    return lines


def render_event_table(
    cfg: QuestionConfig,
    beat: BeatConfig,
    events: dict[int, dict[str, Any]],
) -> list[str]:
    lines = [
        "Key evaluation checkpoints:",
        "",
        "| Event | Time | Kind | Summary | Tests | Score | Why it matters |",
        "|---|---:|---|---|---|---:|---|",
    ]
    for ref in beat.event_refs:
        event = events[ref.event_no]
        test_bits = "-"
        if event["num_test_passed"] is not None and event["test_case_count"] is not None:
            test_bits = f"{event['num_test_passed']}/{event['test_case_count']}"
        score_bits = "-"
        if event["evaluation_type"] == "private" or event["event_type"] == "submission":
            score_bits = fmt_score(event["score"])
        time_bits = fmt_seconds(event["seconds_since_start"])
        if ref.replay_timestamp:
            time_bits = f"{time_bits}<br>{ref.replay_timestamp}"
        kind = f"{event['event_type']} / {event['evaluation_type']}"
        lines.append(
            f"| `{ref.event_no}` | {time_bits} | `{kind}` | {event['summary']} | `{test_bits}` | `{score_bits}` | {ref.note} |"
        )
    return lines


def render_event_code_snapshots(
    beat: BeatConfig,
    events: dict[int, dict[str, Any]],
) -> list[str]:
    lines = [
        "Full Python code for the referenced events:",
        "",
        "These are the canonical student-editable code snapshots reconstructed from `analysis/code_snapshots.parquet` after stripping evaluator scaffolding.",
    ]
    for ref in beat.event_refs:
        event = events[ref.event_no]
        kind = f"{event['event_type']} / {event['evaluation_type']}"
        test_bits = "-"
        if event["num_test_passed"] is not None and event["test_case_count"] is not None:
            test_bits = f"{event['num_test_passed']}/{event['test_case_count']}"
        score_bits = "-"
        if event["evaluation_type"] == "private" or event["event_type"] == "submission":
            score_bits = fmt_score(event["score"])
        lines.extend(
            [
                "",
                f"#### Event `{ref.event_no}`",
                f"- Time: `{fmt_seconds(event['seconds_since_start'])}`",
                f"- Kind: `{kind}`",
                f"- Summary: `{event['summary']}`",
                f"- Tests: `{test_bits}`",
                f"- Score: `{score_bits}`",
                f"- Parseable: `{event['is_parseable']}`",
                f"- Code hash: `{event['code_sha256']}`",
                f"- Snapshot length: `{event['code_length']}`",
                f"- Scaffold strip status: `{event['strip_status']}`",
                f"- Why this event matters: {ref.note}",
            ]
        )
        if ref.replay_timestamp:
            lines.append(f"- Clip hint from earlier cast work: {ref.replay_timestamp}")
        code = event["student_code"] or "# [missing code snapshot]"
        lines.extend(["```python", code, "```"])
    return lines


def render_outline_lines(title: str, lines_in: list[str]) -> list[str]:
    lines = [title]
    for item in lines_in:
        lines.append(f"- {item}")
    return lines


def render_beat(
    qcfg: QuestionConfig,
    beat: BeatConfig,
    attempt_row: dict[str, str],
    events: dict[int, dict[str, Any]],
) -> list[str]:
    lines = [
        f"### {beat.label}",
        "",
        f"- Beat type: `{beat.beat_kind}`",
        f"- Student ID: `{beat.student_id}`",
        f"- Replay tuple: `{qcfg.namespace} / {qcfg.problem_id} / {beat.student_id}`",
        f"- Primary archetype: `{attempt_row['primary_archetype']}`",
        f"- Outcome: `{attempt_row['outcome_category']}`",
        f"- Final score: `{fmt_score(attempt_row['latest_submission_score'])}`",
        f"- Event count: `{attempt_row['event_count']}`",
        f"- Public test runs: `{attempt_row['public_test_run_count']}`",
        f"- Active time: `{fmt_seconds(attempt_row['total_active_time_seconds'])}`",
    ]
    lines.extend(
        [
            "",
            "Why this beat is in the talk:",
            f"- {beat.why_in_talk}",
            "",
            "Response to show:",
        ]
    )
    if beat.snippet:
        lines.extend(["```python", beat.snippet, "```"])
    else:
        lines.append(f"- {beat.response_summary}")
    lines.extend(
        [
            "",
            "Clip focus:",
            f"- {beat.clip_focus}",
            "",
            *render_outline_lines("Narrative lines from the outline:", beat.outline_lines),
            "",
            *render_outline_lines("Stage-use notes:", beat.stage_notes),
            "",
            *render_event_table(qcfg, beat, events),
            "",
            *render_event_code_snapshots(beat, events),
        ]
    )
    return lines


def render_question(
    qcfg: QuestionConfig,
    stats: dict[str, Any],
    problem: dict[str, Any],
    attempts: dict[tuple[str, int, str], dict[str, str]],
) -> list[str]:
    skeleton = extract_skeleton(problem)
    source_links = ", ".join(
        f"[{label}]({rel_report_path(path)})" for label, path in qcfg.source_artifacts
    )
    lines = [
        f"## Question {qcfg.order}: {stats['question_title']} — _\"{qcfg.stage_title}\"_",
        "",
        "### Talk framing",
        f"- Why here: {qcfg.why_here}",
        f"- Transition out: {qcfg.transition_line}",
        "",
        "### Canonical question metadata",
        f"- Namespace / problem: `{qcfg.namespace}/{qcfg.problem_id}`",
        f"- Difficulty: `{problem['difficulty']}`",
        f"- Function signature: `{extract_signature(problem)}`",
        f"- Tags: {', '.join(f'`{tag}`' for tag in problem['tags'])}",
        f"- Track A submitters: `{stats['attempts']}`",
        f"- Full-pass rate among submitters: `{stats['full_pass_pct']}%`",
        f"- Average public test runs: `{stats['avg_public_runs']}`",
        f"- Dominant archetypes: {', '.join(stats['top_archetypes'])}",
        f"- Source artifacts: {source_links}",
        "",
        "### Contract summary",
        f"- {qcfg.contract_summary}",
        "",
        *render_outline_lines("Prompt and example notes to remember:", qcfg.prompt_notes),
        "",
        *render_outline_lines("Public/private test tension to remember:", qcfg.hidden_test_notes),
        "",
        "### Canonical evaluator cases",
        "",
        *render_testcases("Public test groups", list(problem["public_testcase"])),
        "",
        *render_testcases("Private test groups", list(problem["private_testcase"])),
        "",
        "### Replay beats in stage order",
    ]

    for idx, beat in enumerate(qcfg.beats, start=1):
        lines.append(
            f"- `{idx}`. {beat.label} — student `{beat.student_id}`: {beat.response_summary}"
        )

    for beat in qcfg.beats:
        key = (qcfg.namespace, qcfg.problem_id, beat.student_id)
        attempt_row = attempts[key]
        events = load_events(qcfg.namespace, qcfg.problem_id, beat.student_id, skeleton)
        lines.extend(["", *render_beat(qcfg, beat, attempt_row, events)])

    return lines


def build_markdown() -> str:
    generated_at = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC")
    attempts = load_attempt_rows()
    keys = [(q.namespace, q.problem_id) for q in QUESTIONS]
    qstats = load_question_stats(keys)

    lines = [
        "# Replay Extracts For Talk Outline",
        "",
        f"_Generated by `analysis/generate_replays_extracts_md.py` on {generated_at}._",
        "",
        "This file is a production sheet for building the replays and the accompanying narrative commentary. "
        "It is organized around the exact four-question talk outline rather than the broader curation memo.",
        "",
        "How to use this sheet:",
        "- Start from the quick index to find the next question and student beat.",
        "- Use the canonical question metadata and test groups when writing slides or voiceover.",
        "- Use the replay tuple and the embedded event-level code snapshots when building code-based replays or slide sequences.",
        "- Treat the quoted narrative lines as outline-approved phrasing, and the event tables plus code blocks as the canonical backing data.",
        "",
        "## Quick Index",
    ]

    for question in QUESTIONS:
        title = qstats[(question.namespace, question.problem_id)]["question_title"]
        lines.extend(
            [
                f"- Question {question.order}: `{title}` — _{question.stage_title}_",
                f"  - Namespace / problem: `{question.namespace}/{question.problem_id}`",
                f"  - Stage reason: {question.why_here}",
            ]
        )
        for beat in question.beats:
            lines.append(
                f"  - {beat.label}: student `{beat.student_id}` ({beat.beat_kind})"
            )

    for question in QUESTIONS:
        problem = load_problem(question.namespace, question.problem_id)
        stats = qstats[(question.namespace, question.problem_id)]
        lines.extend(["", *render_question(question, stats, problem, attempts)])

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    markdown = build_markdown()
    OUT_PATH.write_text(markdown, encoding="utf-8")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
