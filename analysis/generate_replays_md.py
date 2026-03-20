#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["duckdb>=1.4.0"]
# ///
"""Generate a talk-prep markdown memo of exemplar student replays."""

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
OUT_PATH = ANALYSIS_DIR / "replays.md"


@dataclass(frozen=True)
class CaseConfig:
    student_id: str
    talk_role: str
    approach_summary: str
    why_interesting: str
    key_moments: list[str]
    teaching_implications: list[str]
    question_design_implications: list[str]


@dataclass(frozen=True)
class QuestionConfig:
    namespace: str
    problem_id: int
    cluster_file: str
    why_use: str
    question_takeaways: list[str]
    cases: list[CaseConfig]
    source_artifacts: list[tuple[str, str]] | None = None


@dataclass(frozen=True)
class FunnyMoment:
    namespace: str
    problem_id: int
    student_id: str
    title: str
    timestamp: str
    what_happens: str
    why_funny: str
    reveals: str
    stage_angle: str


@dataclass(frozen=True)
class FunnyQuestionChoice:
    student_id: str
    response_to_share: str
    reason: str


@dataclass(frozen=True)
class FunnyQuestionPlan:
    namespace: str
    problem_id: int
    question_summary: str
    choices: list[FunnyQuestionChoice]


CURATED: list[QuestionConfig] = [
    QuestionConfig(
        namespace="ns_25t2_py11_1",
        problem_id=6,
        cluster_file="analysis/classical_item_quality/public_private_gap_same_code_by_question.csv",
        why_use=(
            "A compact parsing-and-mapping question whose hidden edge case is unusually teachable: "
            "many students write a perfectly plausible two-character parser that passes public tests "
            "and then fails on multi-character ranks like `10D`."
        ),
        question_takeaways=[
            "This is the strongest same-code public-pass/private-fail question in the repo, so it is the cleanest exhibit for hidden-test overfitting.",
            "It reveals a precise novice assumption: `card[0]` is always the rank and `card[1]` is always the suit.",
            "The best replays are very short, which makes this a strong opener for a talk section on question design."
        ],
        cases=[
            CaseConfig(
                student_id="e42a471813ae41a7b30d2f6927d92c32",
                talk_role="Fast exact parser",
                approach_summary=(
                    "Uses `card[:-1]` for rank, `card[-1]` for suit, and dictionary lookups from the first snapshot."
                ),
                why_interesting=(
                    "A true baseline replay: the student models variable-width input correctly before touching the keyboard much."
                ),
                key_moments=[
                    "`0s`: first public run already passes `2/2`.",
                    "`9s`: the same code immediately passes private `2/2`.",
                    "`9s`: submission happens with no substantive edits after the first working version."
                ],
                teaching_implications=[
                    "Model parsing by input shape, not by the width of the visible examples.",
                    "This replay is a good reminder that strong students often solve format questions by decomposing the contract before coding."
                ],
                question_design_implications=[
                    "Questions with variable-width inputs reward students who separate rank and suit semantically instead of by hard-coded positions.",
                    "This is a strong contrast case for the much weaker one-character parsers below."
                ],
            ),
            CaseConfig(
                student_id="56036b0cfd0a453da93c959861c50f96",
                talk_role="Steady builder / contract repair",
                approach_summary=(
                    "Parses rank and suit correctly from the start with an explicit `if/elif` ladder, but first trips on tuple construction "
                    "and then on the required output order."
                ),
                why_interesting=(
                    "An excellent compact contract-debugging replay: the hard part is not card logic, it is returning the exact structure `(suit_value, rank_value)`."
                ),
                key_moments=[
                    "`0s`: runtime error from `return tuple(a,b)`.",
                    "`14s`: first runnable version returns `(a,b)` and still fails because the tuple order is reversed.",
                    "`32s`: swapping to `(b,a)` reaches public `2/2`.",
                    "`39s`: private `100`; submission follows on the same fixed code."
                ],
                teaching_implications=[
                    "Separate 'how do I compute the pieces?' from 'what exact structure must I return?' when teaching novice debugging.",
                    "Students often need explicit prompting to treat tuple order as part of the specification, not decoration."
                ],
                question_design_implications=[
                    "Public tests do useful work here because they catch tuple/type/order mistakes before the hidden edge case even appears.",
                    "This is a well-designed short question for teaching representation and contract checking without a large algorithmic load."
                ],
            ),
            CaseConfig(
                student_id="ad7a05553f034a4a9766e6061a80ed7f",
                talk_role="Public-pass / hidden-case overfitter",
                approach_summary=(
                    "Repairs early indexing mistakes, lands on a neat two-character parser with `card[1]` and `card[0]`, "
                    "and submits after public success even though multi-character ranks are still impossible."
                ),
                why_interesting=(
                    "This is the repo's clearest 'visible tests are green, the real spec is not' replay in miniature."
                ),
                key_moments=[
                    "`0s`: runtime error from indexing as if the string had nested characters (`card[0][1]`).",
                    "`56s`: public `2/2` with a one-character parser using `card[1]` and `card[0]`.",
                    "`61s`: private drops to `50`; the hidden case exposes that `'10D'` is not a two-character card.",
                    "`62s`: submission still happens at `50`, freezing the overfit in place."
                ],
                teaching_implications=[
                    "Teach students to ask 'what family of unseen inputs would break this parser?' before trusting green public tests.",
                    "This replay is ideal for showing how overfitting can look rational from the student's point of view."
                ],
                question_design_implications=[
                    "If public tests only show one-character ranks, hidden tests must include `10`; this question proves why.",
                    "For instruction, consider making `10D` a visible counterexample or explicitly asking students to propose one hidden case of their own."
                ],
            ),
        ],
        source_artifacts=[
            ("problem JSON", "problems/ns_25t2_py11_1/6.json"),
            ("same-code gap table", "analysis/classical_item_quality/public_private_gap_same_code_by_question.csv"),
        ],
    ),
    QuestionConfig(
        namespace="ns_25t2_py22_1",
        problem_id=15,
        cluster_file="analysis/ERRORS-cluster-c078-check-for-greeting-prefix-969f783c.md",
        why_use=(
            "A deceptively simple specification question that exposes whether students read semantics precisely: "
            "case sensitivity, required trailing space, leading-space negatives, and empty-string safety."
        ),
        question_takeaways=[
            "The problem looks trivial, which makes it excellent for showing how often failure is really spec-reading failure.",
            "It creates strong public-versus-private moments because many students solve a narrower rule than the real prompt.",
            "The replay contrast is especially good for teaching boundary-case reasoning."
        ],
        cases=[
            CaseConfig(
                student_id="0fdf6645bdc54e7da88566e0422fbda1",
                talk_role="Shortest semantics-first solver",
                approach_summary=(
                    "The first observed code is already the whole solution: "
                    "`s.startswith('Hello ') or s.startswith('Hi ')`."
                ),
                why_interesting=(
                    "A better opening exemplar than the previous longer baseline. "
                    "There is almost nothing to narrate except correct semantic translation of the prompt."
                ),
                key_moments=[
                    "Event 1: the first observed checkpoint already passes private `3/3`.",
                    "Event 2: the same code also passes public `4/4`.",
                    "Event 3: submission follows immediately with unchanged code."
                ],
                teaching_implications=[
                    "Use this replay to model translating a natural-language rule into a tiny set of exact string predicates.",
                    "It is the ideal opening contrast before showing spec-reading failures and public-test overfitting."
                ],
                question_design_implications=[
                    "The question is valuable because it discriminates between vague prefix intuition and exact contract reading.",
                    "Its hidden tests still matter even though this student did not need them; they keep weaker prefix heuristics from looking equivalent."
                ],
            ),
            CaseConfig(
                student_id="aa68a2811ed74d968987be81d3d6fb31",
                talk_role="Compact hidden-test repair",
                approach_summary=(
                    "Starts with the almost-right rule `startswith('Hello') or startswith('Hi')`, "
                    "then corrects it to require the trailing space after a single hidden-test miss."
                ),
                why_interesting=(
                    "A much tighter replay for the same boundary-semantics lesson. "
                    "You can see the exact missing condition appear on screen in one edit."
                ),
                key_moments=[
                    "Event 1: public `3/4`; missing-space prefixes look correct on the visible tests.",
                    "Event 2: private `67`; hidden tests reject `startswith('Hello')` / `startswith('Hi')` without the trailing space.",
                    "Event 4: public `4/4` after adding the spaces.",
                    "Event 5: private `100`; event 7: final submission."
                ],
                teaching_implications=[
                    "This is an ideal clip for asking, 'What exact contract did the public tests fail to force you to notice?'",
                    "It shows students that one hidden-case miss often means one missing condition, not a need for a wholesale rewrite."
                ],
                question_design_implications=[
                    "The question is well tuned when a one-condition repair can convert a nearly-right solution into a correct one.",
                    "Keeping the public tests slightly under-specified here is pedagogically useful because the hidden failure still points to a coherent missing boundary."
                ],
            ),
            CaseConfig(
                student_id="590240758edf48fa81f701ae4295dc82",
                talk_role="Regression on edge cases",
                approach_summary=(
                    "Begins with a broad `strip()` plus `startswith('Hello')/'Hi'` rule, briefly constructs a better boundary-aware version, "
                    "then reverts to the weaker logic and leaves the improved code commented out."
                ),
                why_interesting=(
                    "A near-solver who appears to understand the task but never fully locks down the edge cases. "
                    "This case helps the audience see how private-test misses often come from one semantic gap, not total confusion."
                ),
                key_moments=[
                    "`0s`, event 1: runtime error.",
                    "`684s`, event 7: first private `67` with `s.strip(); startswith('Hello'/'Hi')` logic.",
                    "`4772s`, event 16: public reaches `4/4` with a more careful boundary-aware approach.",
                    "`5809s`, event 131: final submission falls back to `67`; the better logic is left inside a triple-quoted comment block."
                ],
                teaching_implications=[
                    "Students need help naming the exact counterexamples they are trying to eliminate: empty string, no trailing space, leading whitespace.",
                    "This is a good replay for teaching checkpoint-based debugging after partial private success."
                ],
                question_design_implications=[
                    "The question's most valuable design feature is that its edge cases are conceptually coherent rather than arbitrary.",
                    "Keep the public tests sparse enough to create a private-test reveal, but not so sparse that students cannot orient themselves."
                ],
            ),
        ],
    ),
    QuestionConfig(
        namespace="ns_25t3_py13_1",
        problem_id=7,
        cluster_file="analysis/ERRORS-cluster-c002-shuffle-a-three-word-sentence-6b942fc6.md",
        why_use=(
            "A compact permutation problem that is unusually good for showing sample overfitting, "
            "finite-state brute forcing, and the difference between using `order` as data versus memorizing visible cases."
        ),
        question_takeaways=[
            "This is the clearest missing pattern from the earlier memo: students sometimes solve the public examples rather than the task.",
            "The question is especially strong for discussing public-test design because one hard-coded sentence can pass all visible checks.",
            "It also reveals that some students prefer exhaustive case enumeration over the intended tuple-driven abstraction."
        ],
        cases=[
            CaseConfig(
                student_id="ebd2cfa0ce7e4554850c3bc999fa10e2",
                talk_role="Shortest generic solver",
                approach_summary=(
                    "Uses the intended abstraction from the start: split the sentence into words, reorder them by `order`, and join them back with spaces."
                ),
                why_interesting=(
                    "The clean baseline for this family. It makes the later hard-coded and case-by-case solutions look obviously like different ways of thinking."
                ),
                key_moments=[
                    "Event 1: the first observed checkpoint already passes private `3/3`.",
                    "Event 2: the same code also passes public `3/3`.",
                    "Event 3: submission follows immediately with unchanged code."
                ],
                teaching_implications=[
                    "Use this replay to show what it looks like when a student treats `order` as data instead of as a menu of special cases.",
                    "It is a good opening clip because the intended abstraction is visible in one line."
                ],
                question_design_implications=[
                    "The task has a very readable direct solution, which makes wrong abstractions easy to contrast on stage.",
                    "It is a good talk question because the correct code is short enough to hold in working memory."
                ],
            ),
            CaseConfig(
                student_id="384851c6834647139983873aea99d419",
                talk_role="Public-sample hardcoder",
                approach_summary=(
                    "Writes a branch like `if order==(0, 2, 1): return 'apple orange banana'`, effectively memorizing one public example instead of using the input sentence generically."
                ),
                why_interesting=(
                    "One of the cleanest public-pass/private-fail replays in the repo. The student literally learns a visible example and nothing else."
                ),
                key_moments=[
                    "Event 1: public `1/3` with a single hard-coded example output.",
                    "Event 2: public `2/3`; event 3: public `3/3`, all with the same sample-specific idea.",
                    "Event 4: private immediately drops to `0/3`.",
                    "Event 6: final submission stays at `0`."
                ],
                teaching_implications=[
                    "This is the replay to use when explaining overfitting in the most concrete possible way.",
                    "It helps instructors name the behavior kindly but precisely: the student solved the examples, not the rule."
                ],
                question_design_implications=[
                    "This question demonstrates why public tests need at least one anti-hardcoding sentinel with unseen words.",
                    "If the public set teaches only three visible permutations, some students will infer that memorizing those is the task."
                ],
            ),
            CaseConfig(
                student_id="107337b2583a4bfebe3e917b315d2684",
                talk_role="Finite-state brute forcer",
                approach_summary=(
                    "Enumerates all six possible three-word permutations with explicit `if/elif` branches rather than using the tuple as an indexing plan."
                ),
                why_interesting=(
                    "A subtle but important contrast: the code is correct, yet it avoids the intended abstraction. "
                    "It shows that students can reach correctness by exhaustively covering a tiny state space."
                ),
                key_moments=[
                    "Events 1-4: public remains below full pass while the student hand-builds case branches and still has spacing mistakes.",
                    "Event 6: public reaches `3/3` once the branch outputs are formatted correctly.",
                    "Event 7: private also reaches `100`; event 9: submission."
                ],
                teaching_implications=[
                    "Use this replay to discuss the difference between 'correct for this tiny universe' and 'using a transferable abstraction.'",
                    "It is a strong reminder that some students reason by exhaustive cases before they reason by data structure."
                ],
                question_design_implications=[
                    "If the instructional goal is tuple-driven indexing, a three-word universe is small enough that brute force can also win.",
                    "That is not automatically bad, but it means the item measures correctness more than abstraction choice."
                ],
            ),
        ],
    ),
    QuestionConfig(
        namespace="ns_25t2_py21_2",
        problem_id=18,
        cluster_file="analysis/ERRORS-cluster-c013-pangram-check-f0d5ae7d.md",
        why_use=(
            "A classic 'looks easy, is actually conceptual' problem about coverage, filtering, and control flow. "
            "It reliably reveals early returns, sample overfitting, and confusion between total characters and distinct letters."
        ),
        question_takeaways=[
            "This is one of the clearest repo examples of public-pass illusion followed by private-test correction.",
            "The problem cleanly separates checking for any alphabetic text from checking coverage of all 26 letters.",
            "It is ideal for discussing hidden tests as a prompt to revisit the rule, not to guess more code."
        ],
        cases=[
            CaseConfig(
                student_id="13bc0b2cf15145219dd6719b89dfc3cd",
                talk_role="Shortest clean invariant",
                approach_summary=(
                    "Represents the task directly from the start: build the alphabet as a set and check whether it is a subset of `set(text.lower())`."
                ),
                why_interesting=(
                    "A stronger opening baseline than the previous pick. "
                    "It shows the exact invariant with almost no replay overhead."
                ),
                key_moments=[
                    "Event 1: the first observed checkpoint already passes private `3/3`.",
                    "Event 2: the same code also passes public `3/3`.",
                    "Event 3: submission follows immediately with unchanged code."
                ],
                teaching_implications=[
                    "Use this replay to establish the target representation before showing heuristic shortcuts and false summits.",
                    "It makes later failures easier to interpret because the audience has already seen the right invariant cleanly."
                ],
                question_design_implications=[
                    "This item is strong because the core solution is simple and teachable once students choose the right representation.",
                    "It rewards conceptual clarity more than syntax juggling."
                ],
            ),
            CaseConfig(
                student_id="2ee6740d56614ebbb3e68f6fe2992f28",
                talk_role="Public-pass then private-fix solver",
                approach_summary=(
                    "Starts with an early-return rule that rejects non-letters, then a length/count heuristic, and only late in the session "
                    "adopts the real invariant: unique alphabetic letters."
                ),
                why_interesting=(
                    "A strong replay for the moment when public success creates false confidence, then hidden cases force a deeper repair of the core logic."
                ),
                key_moments=[
                    "`0s`, event 1: public partial; code returns `False` too early on non-letters.",
                    "`46.9s`, event 61: public all-pass with the wrong `count >= 26` heuristic.",
                    "`47.2s`, event 62: private fails immediately; hidden cases punish total-letter counting.",
                    "`70.6s`, event 103: private all-pass after switching to a `set()` of unique letters.",
                    "`71.4s`, event 107: final submission `100`."
                ],
                teaching_implications=[
                    "Show this replay when explaining why students must ask 'what family of inputs is this code really solving?'",
                    "It is especially useful for teaching how to recover after the first private-test failure without panicking."
                ],
                question_design_implications=[
                    "The hidden tests are excellent here because they expose exactly the shortcut strategies we want to discourage.",
                    "This question works well in a talk because the transition from apparent success to real success is easy to narrate."
                ],
            ),
            CaseConfig(
                student_id="ce4de84afb3e4d219f3688124ec46b12",
                talk_role="Short false summit on filtering",
                approach_summary=(
                    "Gets to a plausible `set`-equality solution quickly, but filters out only spaces. "
                    "That is enough for the public tests and still wrong for hidden punctuation cases."
                ),
                why_interesting=(
                    "Cleaner and shorter than the previous long regression pick. "
                    "The audience can see the exact missing subproblem in one glance: filtering non-letters, not just spaces."
                ),
                key_moments=[
                    "Event 1: first public run only reaches `1/3` because case handling is incomplete.",
                    "Event 2: lowercasing repair reaches public `3/3`.",
                    "Event 3: private immediately drops to `33`; punctuation and other non-letters still poison the set.",
                    "Event 5: final submission stays at `33`."
                ],
                teaching_implications=[
                    "This is a good replay for teaching 'filter, then reason' rather than assuming spaces are the only noise.",
                    "It also shows how one successful public rerun can freeze thinking before the invariant is actually complete."
                ],
                question_design_implications=[
                    "Hidden tests should include punctuation and digits, not just mixed case, to expose incomplete filtering rules.",
                    "This question works well because the private failure points to a coherent missing case rather than an arbitrary exception."
                ],
            ),
        ],
    ),
    QuestionConfig(
        namespace="ns_25t3_py13_1",
        problem_id=10,
        cluster_file="analysis/ERRORS-cluster-c022-find-characters-appearing-more-than-once-a831cf60.md",
        why_use=(
            "A very good same-question comparison for order-sensitive reasoning. "
            "Students often find duplicates, but not in the required first-appearance order, or they destroy the order with sets."
        ),
        question_takeaways=[
            "This question exposes a subtle but teachable distinction between solving the data problem and solving the contract.",
            "It is a good talk example of how 'I found the repeated characters' is not the same as 'I met the output spec'.",
            "The contrast cases here are especially strong for discussing representation choices like `set`, `count`, and ordered scans."
        ],
        cases=[
            CaseConfig(
                student_id="24bf4a098ea84ff48f0461396cb53a29",
                talk_role="Shortest clean baseline",
                approach_summary=(
                    "Writes a direct ordered scan from the start: walk through the string, use `s.count(ch) > 1` to detect repetition, "
                    "and append only the first time each repeated character is seen."
                ),
                why_interesting=(
                    "A cleaner opening exemplar for this question. "
                    "The first observed code already satisfies the order contract, so later failures look like true representation mistakes rather than spec ambiguity."
                ),
                key_moments=[
                    "Event 1: the first observed checkpoint already passes private `3/3`.",
                    "Event 2: the same code also passes public `3/3`.",
                    "Event 3: submission follows immediately with unchanged code."
                ],
                teaching_implications=[
                    "Use this replay to establish the contract clearly: repeated characters, first-appearance order, no duplicates in the output list.",
                    "It provides a clean anchor before showing wrong-unit reasoning like `split()` or order-destroying `set` logic."
                ],
                question_design_implications=[
                    "This question is strong because the correct output contract is readable enough to compare directly against wrong abstractions.",
                    "A simple clean solution makes later set-order and representation failures more teachable."
                ],
            ),
            CaseConfig(
                student_id="9059d198c33b4b349eb2af1315239956",
                talk_role="Short order-repair debugger",
                approach_summary=(
                    "Starts by using `set(s)`-style reasoning that destroys order, then briefly sorts the repeated characters, "
                    "and finally switches to an ordered accumulation that preserves first appearance."
                ),
                why_interesting=(
                    "A much shorter version of the same point. "
                    "The order bug is visible immediately, and the repair is easy to narrate in under a minute."
                ),
                key_moments=[
                    "Event 1: public `1/3`; the first attempt relies on `set(s)`, so the repeated characters lose first-appearance order.",
                    "Events 5-6: public `2/3`; switching to `set(filter(...))` and then `sorted(...)` fixes membership but still not the contract.",
                    "Event 7: public `3/3` once the answer is rebuilt in input order.",
                    "Event 8: private `100`; event 10: submission."
                ],
                teaching_implications=[
                    "This is the cleanest short clip for teaching that sets answer the wrong question when order matters.",
                    "It is useful for showing how a student can fix the abstraction without changing the task itself."
                ],
                question_design_implications=[
                    "The item is well-designed because one good hidden case can separate true order handling from fragile `set`-based solutions.",
                    "For teaching, pair the replay with a visual trace of `seen` and `repeated` state."
                ],
            ),
            CaseConfig(
                student_id="ee012cee3fa5491d8db37141d2a954fe",
                talk_role="Early win, then regression",
                approach_summary=(
                    "Spends most of the session trapped in the same bad idea family: list/set conversions and mixed return types that destroy order or the required output structure."
                ),
                why_interesting=(
                    "One of the strongest regression exemplars in the repo: early public success, immediate private failure, then repeated destabilizing edits that leave the student worse off."
                ),
                key_moments=[
                    "Events 1-18: repeated list/set experiments with runtime and wrong-answer feedback.",
                    "Event 25: first public `3/3`; event 26: private `0/3`, revealing an order/type bug the public tests missed.",
                    "Event 34: brief private `100`, but it does not stabilize.",
                    "Events 35-125: long oscillation among private `67`, `33`, and `0` while set-like reasoning keeps returning.",
                    "Event 218: final submission is only `33`."
                ],
                teaching_implications=[
                    "Use this replay to teach regression control: keep a working version, isolate the hidden-case hypothesis, and avoid rewriting away a partial success.",
                    "It is also a strong example of how repeated execution can mask weak reasoning about invariants."
                ],
                question_design_implications=[
                    "This question benefits from hidden tests because order bugs are hard to expose with only simple public examples.",
                    "It is an excellent talk question precisely because the wrong solutions are often locally plausible."
                ],
            ),
        ],
    ),
]

FUNNY_MOMENTS: list[FunnyMoment] = [
    FunnyMoment(
        namespace="ns_25t2_py22_1",
        problem_id=15,
        student_id="60f6e5f27899406ea16a5470210db8d1",
        title="Python With A JavaScript Accent",
        timestamp="Replay `0:00-0:03` (events `1-3`)",
        what_happens=(
            "The student tries `s.startswith('Hello'|| 'Hi')`, then `s.startswith('Hello' or 'Hi')`, "
            "before finally writing the real two-prefix check."
        ),
        why_funny=(
            "It is instantly recognizable to an educator audience as 'Python spoken with JavaScript and English grammar mixed together'. "
            "The intent is correct; the operators are from another universe."
        ),
        reveals=(
            "Students often understand the goal before they understand the language-specific operator semantics. "
            "Surface fluency can outrun actual Python fluency."
        ),
        stage_angle=(
            "Read the line out loud and call it 'Python, but with a JavaScript accent.' Let the audience catch the bug before you explain it."
        ),
    ),
    FunnyMoment(
        namespace="ns_25t2_py22_1",
        problem_id=15,
        student_id="60f6e5f27899406ea16a5470210db8d1",
        title="Negotiating With The Autograder",
        timestamp="Replay `~59.7s` (event `81`)",
        what_happens=(
            "The first all-public-pass version includes a special case like `if s=='Hithere': return False` "
            "before a still-brittle prefix rule."
        ),
        why_funny=(
            "It is the purest 'I am not solving the rule; I am bargaining with one visible test case' moment. "
            "Most educators have seen exactly this instinct."
        ),
        reveals=(
            "When students are close, they often patch visible counterexamples instead of restating the invariant. "
            "Hidden tests matter because they force the conversation back to the rule."
        ),
        stage_angle=(
            "Describe it as the moment the student enters treaty negotiations with the grader."
        ),
    ),
    FunnyMoment(
        namespace="ns_25t2_py22_1",
        problem_id=15,
        student_id="590240758edf48fa81f701ae4295dc82",
        title="The Triple-Quoted Graveyard",
        timestamp="Observed session time `1:36:49` (event `131`)",
        what_happens=(
            "The final weaker solution stays live, while the better boundary-aware logic is buried inside a triple-quoted comment block."
        ),
        why_funny=(
            "The fix is visibly present and also unusable. It feels like the student held a funeral for the correct solution and left the wrong one in charge."
        ),
        reveals=(
            "Students often use comments as ad hoc version control. That preserves emotional safety, but it also makes regression much more likely."
        ),
        stage_angle=(
            "Call it 'code necromancy' or 'the triple-quoted graveyard' and show the live wrong code next to the entombed fix."
        ),
    ),
    FunnyMoment(
        namespace="ns_25t3_py13_1",
        problem_id=7,
        student_id="384851c6834647139983873aea99d419",
        title="The Entire Function Learns One Fruit Sentence",
        timestamp="Observed session time `2:09` (event `4`)",
        what_happens=(
            "After a few public reruns, the function still contains `if order==(0, 2, 1): return 'apple orange banana'` "
            "and nonetheless reaches public `3/3` before failing private `0/3`."
        ),
        why_funny=(
            "It is hard not to laugh when the whole program seems convinced that all sentence-shuffling in Python is secretly about one fruit salad."
        ),
        reveals=(
            "This is sample overfitting in its purest form: the student has learned the visible example, not the transformation rule."
        ),
        stage_angle=(
            "Read the hard-coded return line verbatim and say: 'the function has memorized exactly one sentence.'"
        ),
    ),
    FunnyMoment(
        namespace="ns_25t3_py13_1",
        problem_id=7,
        student_id="107337b2583a4bfebe3e917b315d2684",
        title="Why Use A Tuple When You Can List Every Universe",
        timestamp="Observed session time `8:21` (event `7`)",
        what_happens=(
            "The student eventually passes by writing all six `if/elif` branches for the six possible three-word permutations."
        ),
        why_funny=(
            "It feels like watching someone defeat abstraction by sheer determination. "
            "The program solves the entire permutation universe one branch at a time."
        ),
        reveals=(
            "Students sometimes prefer exhaustive case coverage to a data-driven rule, especially when the state space is visibly tiny."
        ),
        stage_angle=(
            "Introduce it as 'the moment brute force wins a small, perfectly legal victory over elegance.'"
        ),
    ),
    FunnyMoment(
        namespace="ns_25t2_py21_2",
        problem_id=18,
        student_id="a2316b024ae946b59ebe2f04090321d9",
        title="The Pangram Checker That Forgot C",
        timestamp="Observed session time `0:00` (event `1`)",
        what_happens=(
            "The code checks letters against `'absdefghijklmnopqrstuvwxyz'`, an alphabet string that omits `c`."
        ),
        why_funny=(
            "The function whose whole job is to verify all letters starts by forgetting one. "
            "It is funny because the student's internal oracle is itself buggy."
        ),
        reveals=(
            "Under cognitive load, students can make mistakes in the very representation they plan to trust. "
            "Even the checking mechanism may need checking."
        ),
        stage_angle=(
            "Put the alphabet on the slide, pause, and let the audience discover the missing `c` themselves."
        ),
    ),
    FunnyMoment(
        namespace="ns_25t2_py21_2",
        problem_id=18,
        student_id="2ee6740d56614ebbb3e68f6fe2992f28",
        title="A Pangram Is Apparently 'Lots Of Letters'",
        timestamp="Replay `46.9s-47.2s` (events `61-62`)",
        what_happens=(
            "After stripping spaces, the student returns `True` when the alphabetic character `count >= 26`."
        ),
        why_funny=(
            "The function has quietly redefined pangram as 'contains a lot of letters'. "
            "Educators immediately imagine 26 copies of `a` getting certified as a pangram."
        ),
        reveals=(
            "This is a textbook shortcut heuristic: the student found a feature correlated with the answer, not the actual invariant."
        ),
        stage_angle=(
            "Ask the room whether `'aaaaaaaaaaaaaaaaaaaaaaaaaa'` now qualifies as great literature."
        ),
    ),
    FunnyMoment(
        namespace="ns_25t2_py11_1",
        problem_id=6,
        student_id="ad7a05553f034a4a9766e6061a80ed7f",
        title="The Hidden Boss Battle Is `10D`",
        timestamp="Observed session time `0:56-1:02` (events `2-4`)",
        what_happens=(
            "The student settles on `card[1]` and `card[0]`, gets a triumphant public `2/2`, and then immediately drops to private `1/2` "
            "because a two-character rank like `10D` breaks the parser."
        ),
        why_funny=(
            "The solution looks finished until the only two-character card in the deck walks on stage like a hidden boss."
        ),
        reveals=(
            "Students often infer the full input shape from the visible samples. One shape-breaking hidden case can expose that assumption instantly."
        ),
        stage_angle=(
            "Build suspense around the villain card `10D` and present it as the moment the deck fights back."
        ),
    ),
    FunnyMoment(
        namespace="ns_25t2_py11_1",
        problem_id=6,
        student_id="56036b0cfd0a453da93c959861c50f96",
        title="Calling `tuple` Like It Needs Two Arguments",
        timestamp="Observed session time `0:00-0:14` (events `1-2`)",
        what_happens=(
            "The student computes the right two numbers, then returns `tuple(a,b)`, fixes that to `(a,b)`, and only after that notices the tuple order is still backwards."
        ),
        why_funny=(
            "Everything is right except the punctuation, and then everything is right except left and right."
        ),
        reveals=(
            "Novices can understand the computation yet still be fighting Python constructors and exact output shape at the same time."
        ),
        stage_angle=(
            "Pause on `tuple(a,b)` and ask the room whether Python feels like receiving two arguments today."
        ),
    ),
    FunnyMoment(
        namespace="ns_25t3_py13_1",
        problem_id=10,
        student_id="4c7d49f2a52e47aea20bf101cc95693f",
        title="Solving A Character Problem With `split()`",
        timestamp="Observed session time `0:00` (event `1`)",
        what_happens=(
            "The first attempt is `t = s.split(); return t` for a question about repeated characters inside one string."
        ),
        why_funny=(
            "It is funny because the student is solving a perfectly reasonable word problem, just not the problem on the exam."
        ),
        reveals=(
            "A lot of early debugging is really representation repair. Students may need to re-decide what the data unit even is before they can solve the task."
        ),
        stage_angle=(
            "Introduce it as 'the moment the student temporarily changes the syllabus from characters to words.'"
        ),
    ),
    FunnyMoment(
        namespace="ns_25t3_py13_1",
        problem_id=10,
        student_id="ee012cee3fa5491d8db37141d2a954fe",
        title="The Grader Becomes An Accomplice",
        timestamp="Replay `17.9s-18.4s` (events `24-26`)",
        what_happens=(
            "The student builds the answer by iterating over `set(s)`, which destroys first-appearance order, and still gets an immediate public all-pass."
        ),
        why_funny=(
            "The audience can see the abstraction is wrong, but the public tests briefly give it a gold star anyway."
        ),
        reveals=(
            "Public tests can accidentally validate the wrong abstraction. "
            "Order-sensitive questions need an adversarial public example, not just hidden ones."
        ),
        stage_angle=(
            "Tell the audience: 'this is the exact moment the grader becomes an accomplice.'"
        ),
    ),
    FunnyMoment(
        namespace="ns_25t2_py14_1",
        problem_id=10,
        student_id="8441c3b982914b779cf15f66e9857474",
        title="A Whole Vowel-Reversal Screenplay For Two Samples",
        timestamp="Observed session final state `1:12:09` (event `35`, submission)",
        what_happens=(
            "The final code has `if(g==\"Hello\"): print(\"HollE\")` and then a second branch for "
            "the multiline public sample before falling into unfinished loops."
        ),
        why_funny=(
            "The student has not really written a vowel-reversal algorithm. "
            "They have written a tiny stage play starring the visible examples."
        ),
        reveals=(
            "When a transformation feels slippery, some students retreat to memorizing exemplar "
            "inputs and outputs instead of extracting the rule."
        ),
        stage_angle=(
            "Show the two sample branches and say the code has learned the script but not the plot."
        ),
    ),
    FunnyMoment(
        namespace="ns_25t3_py22",
        problem_id=5,
        student_id="0c796407724441a482dd8912fa4831c6",
        title="The Entire Solution Is `dc\\nba`",
        timestamp="Observed session final state `1:14:01` (event `11`, submission)",
        what_happens=(
            "The whole function returns `\"dc\\nba\"`, the public sample output, no matter what input it receives."
        ),
        why_funny=(
            "It is the most brutally honest overfit in the repo: not even a fake algorithm, just the answer sheet."
        ),
        reveals=(
            "Some students temporarily interpret the public example as the task itself when the transformation rule is not yet internalized."
        ),
        stage_angle=(
            "Put the full function on screen. The room gets the joke before you finish reading it."
        ),
    ),
    FunnyMoment(
        namespace="ns_25t3_py22",
        problem_id=5,
        student_id="b327a9e2a2cb49c38e502835f4959f10",
        title="Routing By The First Character",
        timestamp="Observed session final state `2:37` (event `13`, submission)",
        what_happens=(
            "The code branches on `s[0:1]` and chooses between `wz\\nyx`, `43\\n21`, and `dc\\nba`."
        ),
        why_funny=(
            "The function behaves like a tiny oracle for three seen inputs and nothing else."
        ),
        reveals=(
            "Visible examples can turn into a lookup table when students do not trust themselves to generalize the positional rule."
        ),
        stage_angle=(
            "Frame it as a three-entry customer-support menu for the grader."
        ),
    ),
    FunnyMoment(
        namespace="ns_25t3_py11",
        problem_id=10,
        student_id="3d6f6d72d5c546a091659808509c4fce",
        title="The Duplicate Remover Memorizes Six Whole Words",
        timestamp="Observed session final state `1:13:48` (event `55`, submission)",
        what_happens=(
            "The final function has exact branches for `banana`, `hello`, `abc`, `python`, `apple`, and `world`."
        ),
        why_funny=(
            "Instead of removing duplicate characters, the program has built a tiny dictionary of favorite English words."
        ),
        reveals=(
            "Sample memorization is not always laziness. It is often a fallback when the student cannot stabilize a general procedure."
        ),
        stage_angle=(
            "Read the words like flash cards and let the audience notice the algorithm has become a phrasebook."
        ),
    ),
    FunnyMoment(
        namespace="ns_25t3_py22",
        problem_id=6,
        student_id="47a311a308e745228f5d3b9cda3048a9",
        title="The Username Generator Knows Exactly One User",
        timestamp="Observed session final state `1:14:56` (event `28`, submission)",
        what_happens=(
            "The function ignores its parameters and simply returns `s='ali123'`."
        ),
        why_funny=(
            "The task asks for a username generator; the code replies with one already-generated username and calls it a day."
        ),
        reveals=(
            "When students overfit samples, they may freeze the whole function at the example output rather than even approximate the rule."
        ),
        stage_angle=(
            "Say: 'this is less a function than a commemorative plaque for Ali.'"
        ),
    ),
    FunnyMoment(
        namespace="ns_25t2_py21_1",
        problem_id=20,
        student_id="242f6a6bda8d40adb0a6324bf648b44e",
        title="The Pattern Generator Gives Up After Five",
        timestamp="Observed session final state `1:04:10` (event `50`, submission)",
        what_happens=(
            "The program branches on `n == 1` through `n == 5` and prints a handcrafted triangle for each case."
        ),
        why_funny=(
            "It solves pattern generation by refusing to generate patterns once `n` gets ambitious."
        ),
        reveals=(
            "Students will often trade algorithm design for case listing when the visible range of examples feels finite."
        ),
        stage_angle=(
            "Scroll just far enough to make the audience realize there is a new `elif` for every integer."
        ),
    ),
    FunnyMoment(
        namespace="ns_25t2_py21_2",
        problem_id=26,
        student_id="149b3b661c744be48fb090042a0fe3b4",
        title="Answering The Wrong Exam With Confidence",
        timestamp="Observed session final state `1:22:37` (event `71`, submission)",
        what_happens=(
            "The solution opens `filename`, reads lines, and prints a spacing pattern from a different file-I/O zig-zag problem."
        ),
        why_funny=(
            "It is funny because the code is earnest, detailed, and confidently solving a task the grader never asked."
        ),
        reveals=(
            "Question transfer can misfire. Students sometimes recognize a familiar surface form and retrieve the wrong template."
        ),
        stage_angle=(
            "Call it a beautiful answer to a question that exists on some parallel exam."
        ),
    ),
]


FUNNY_QUESTION_ORDER: list[FunnyQuestionPlan] = [
    FunnyQuestionPlan(
        namespace="ns_25t2_py22_1",
        problem_id=15,
        question_summary="Check For Greeting Prefix",
        choices=[
            FunnyQuestionChoice(
                student_id="60f6e5f27899406ea16a5470210db8d1",
                response_to_share="s.startswith('Hello'|| 'Hi')",
                reason="Cross-language syntax confusion lands instantly and opens the theme that intent can outrun Python fluency.",
            ),
            FunnyQuestionChoice(
                student_id="60f6e5f27899406ea16a5470210db8d1",
                response_to_share="if s=='Hithere': return False",
                reason="A perfect visible-test bargaining moment; the audience sees the student patching one sample instead of stating the rule.",
            ),
        ],
    ),
    FunnyQuestionPlan(
        namespace="ns_25t3_py13_1",
        problem_id=7,
        question_summary="Shuffle a Three Word Sentence",
        choices=[
            FunnyQuestionChoice(
                student_id="384851c6834647139983873aea99d419",
                response_to_share="if order==(0, 2, 1): return 'apple orange banana'",
                reason="The purest sample memorization clip in the repo; the whole algorithm learns one fruit sentence.",
            ),
            FunnyQuestionChoice(
                student_id="107337b2583a4bfebe3e917b315d2684",
                response_to_share="six if/elif branches, one for each permutation",
                reason="Brute force beats abstraction in a way that is both funny and immediately understandable.",
            ),
        ],
    ),
    FunnyQuestionPlan(
        namespace="ns_25t2_py14_1",
        problem_id=10,
        question_summary="Reverse Vowel Order in a String",
        choices=[
            FunnyQuestionChoice(
                student_id="8441c3b982914b779cf15f66e9857474",
                response_to_share="if(g==\"Hello\"): print(\"HollE\") ... elif(g=='''Hello, World! ...'''): ...",
                reason="The student writes a tiny screenplay for the samples instead of a vowel-reversal algorithm.",
            ),
        ],
    ),
    FunnyQuestionPlan(
        namespace="ns_25t3_py22",
        problem_id=5,
        question_summary="Swap Diagonal Characters in a 2-Line String",
        choices=[
            FunnyQuestionChoice(
                student_id="0c796407724441a482dd8912fa4831c6",
                response_to_share='return "dc\\nba"',
                reason="The entire function is just the public sample output; the joke is visible in one line.",
            ),
            FunnyQuestionChoice(
                student_id="b327a9e2a2cb49c38e502835f4959f10",
                response_to_share="if s[0:1]=='x': 'wz\\nyx' elif s[0:1]=='1': '43\\n21' else: 'dc\\nba'",
                reason="A hilariously specific sample router that shows how examples can become a lookup table.",
            ),
        ],
    ),
    FunnyQuestionPlan(
        namespace="ns_25t3_py11",
        problem_id=10,
        question_summary="Remove Duplicate Characters from String",
        choices=[
            FunnyQuestionChoice(
                student_id="3d6f6d72d5c546a091659808509c4fce",
                response_to_share='if s == "banana": return "ban" ...',
                reason="The function memorizes example words like flash cards instead of learning character deduplication.",
            ),
            FunnyQuestionChoice(
                student_id="d863584c1d954bc181e654049e154321",
                response_to_share="lis = s.split()",
                reason="The wrong unit of analysis is obvious and funny: the student turns a character problem into a word problem.",
            ),
        ],
    ),
    FunnyQuestionPlan(
        namespace="ns_25t2_py11_1",
        problem_id=6,
        question_summary="Card to Value Tuple",
        choices=[
            FunnyQuestionChoice(
                student_id="56036b0cfd0a453da93c959861c50f96",
                response_to_share="return tuple(a,b)",
                reason="Everything is right except the punctuation, and then everything is right except the tuple order.",
            ),
            FunnyQuestionChoice(
                student_id="ad7a05553f034a4a9766e6061a80ed7f",
                response_to_share="rank = card[0]; suit = card[1]  # defeated by 10D",
                reason="A clean hidden-boss moment: the parser looks finished until one two-character rank walks on stage.",
            ),
        ],
    ),
    FunnyQuestionPlan(
        namespace="ns_25t2_py21_2",
        problem_id=18,
        question_summary="Pangram Check",
        choices=[
            FunnyQuestionChoice(
                student_id="a2316b024ae946b59ebe2f04090321d9",
                response_to_share='letters = "absdefghijklmnopqrstuvwxyz"',
                reason="The pangram checker forgets `c`, which is visually funny before you even explain the bug.",
            ),
            FunnyQuestionChoice(
                student_id="2ee6740d56614ebbb3e68f6fe2992f28",
                response_to_share="return count >= 26",
                reason="It quietly redefines pangram as 'contains lots of letters,' which is a great heuristic-vs-invariant punchline.",
            ),
        ],
    ),
    FunnyQuestionPlan(
        namespace="ns_25t3_py13_1",
        problem_id=10,
        question_summary="Find Characters Appearing More Than Once",
        choices=[
            FunnyQuestionChoice(
                student_id="4c7d49f2a52e47aea20bf101cc95693f",
                response_to_share="t = s.split(); return t",
                reason="Another wrong-unit moment that lands quickly because the student is solving a word problem instead.",
            ),
            FunnyQuestionChoice(
                student_id="ee012cee3fa5491d8db37141d2a954fe",
                response_to_share="for c in set(s): ...",
                reason="The grader briefly blesses the wrong abstraction, which makes the joke useful for question-design discussion too.",
            ),
        ],
    ),
    FunnyQuestionPlan(
        namespace="ns_25t3_py22",
        problem_id=6,
        question_summary="Create Username from First Name and User ID",
        choices=[
            FunnyQuestionChoice(
                student_id="47a311a308e745228f5d3b9cda3048a9",
                response_to_share="s='ali123'; return(s)",
                reason="The function knows exactly one person, which makes sample overfitting instantly legible.",
            ),
        ],
    ),
    FunnyQuestionPlan(
        namespace="ns_25t2_py21_1",
        problem_id=20,
        question_summary="File Content Zig-Zag Shift",
        choices=[
            FunnyQuestionChoice(
                student_id="242f6a6bda8d40adb0a6324bf648b44e",
                response_to_share="elif n == 1 ... elif n == 5 ...",
                reason="Funny as a lookup-table anti-pattern, though it needs a bit more setup than the shorter string examples.",
            ),
            FunnyQuestionChoice(
                student_id="149b3b661c744be48fb090042a0fe3b4",
                response_to_share="with open(filename, 'r') as f:",
                reason="It is a beautiful 'solved the wrong exam' clip when you want a bigger laugh after the audience trusts the pattern.",
            ),
        ],
    ),
]


def all_question_keys() -> list[tuple[str, int]]:
    keys = {(cfg.namespace, cfg.problem_id) for cfg in CURATED}
    keys.update((moment.namespace, moment.problem_id) for moment in FUNNY_MOMENTS)
    keys.update((plan.namespace, plan.problem_id) for plan in FUNNY_QUESTION_ORDER)
    return sorted(keys)


def load_attempt_rows() -> dict[tuple[str, int, str], dict[str, str]]:
    rows: dict[tuple[str, int, str], dict[str, str]] = {}
    with PROCESS_CSV.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            key = (row["namespace"], int(row["problem_id"]), row["student_id"])
            rows[key] = row
    return rows


def load_question_stats() -> dict[tuple[str, int], dict[str, Any]]:
    keys = all_question_keys()
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
            FROM read_csv_auto(?) a
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


def path_for_existing_replay(namespace: str, problem_id: int, student_id: str, suffix: str) -> Path:
    return ANALYSIS_DIR / f"replay-{namespace}-{problem_id}-{student_id}.{suffix}"


def parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


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


def load_events(namespace: str, problem_id: int, student_id: str) -> list[dict[str, Any]]:
    conn = duckdb.connect()
    try:
        rows = conn.execute(
            """
            SELECT
              seconds_since_start,
              timestamp_utc,
              event_type,
              evaluation_type,
              summary,
              reason,
              score,
              num_test_passed,
              test_case_count,
              is_parseable
            FROM read_parquet(?)
            WHERE namespace = ?
              AND problem_id = ?
              AND student_id = ?
            ORDER BY
              timestamp_utc,
              CASE event_type
                WHEN 'saved_code' THEN 1
                WHEN 'test_run' THEN 2
                WHEN 'submission' THEN 3
                ELSE 9
              END,
              evaluation_type
            """,
            [str(TIMELINE_PARQUET), namespace, problem_id, student_id],
        ).fetchall()
    finally:
        conn.close()

    events: list[dict[str, Any]] = []
    for (
        seconds_since_start,
        timestamp_utc,
        event_type,
        evaluation_type,
        summary,
        reason,
        score,
        num_test_passed,
        test_case_count,
        is_parseable,
    ) in rows:
        events.append(
            {
                "seconds_since_start": float(seconds_since_start or 0.0),
                "timestamp_utc": timestamp_utc,
                "event_type": str(event_type or ""),
                "evaluation_type": str(evaluation_type or ""),
                "summary": str(summary or ""),
                "reason": str(reason or ""),
                "score": float(score) if score is not None else None,
                "num_test_passed": int(num_test_passed) if num_test_passed is not None else None,
                "test_case_count": int(test_case_count) if test_case_count is not None else None,
                "is_parseable": bool(is_parseable) if is_parseable is not None else None,
            }
        )
    return events


def replay_json_key_moments(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    moments = []
    for item in payload.get("timeline", [])[:6]:
        stamp = fmt_seconds(item.get("timestamp"))
        kind = str(item.get("kind") or "moment").replace("_", " ")
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        moments.append(f"`{stamp}` {kind}: {text}")
    return moments


def auto_key_moments(events: list[dict[str, Any]]) -> list[str]:
    moments: list[str] = []

    def add_once(label: str, predicate: Any) -> None:
        for event in events:
            if predicate(event):
                desc = describe_event(event)
                moments.append(f"`{fmt_seconds(event['seconds_since_start'])}` {label}: {desc}")
                return

    add_once("first parseable snapshot", lambda e: e.get("is_parseable") is True)
    add_once(
        "first public progress",
        lambda e: e["evaluation_type"] == "public"
        and (e.get("num_test_passed") or 0) > 0,
    )
    add_once(
        "first public all-pass",
        lambda e: e["evaluation_type"] == "public"
        and (e.get("test_case_count") or 0) > 0
        and e.get("num_test_passed") == e.get("test_case_count"),
    )
    add_once(
        "first private progress",
        lambda e: e["evaluation_type"] == "private"
        and (e.get("num_test_passed") or 0) > 0,
    )
    add_once(
        "first private all-pass",
        lambda e: e["evaluation_type"] == "private"
        and (e.get("test_case_count") or 0) > 0
        and e.get("num_test_passed") == e.get("test_case_count"),
    )
    add_once("first submission", lambda e: e["event_type"] == "submission")

    public_runs = [e for e in events if e["evaluation_type"] == "public" and e.get("num_test_passed") is not None]
    for prev, curr in zip(public_runs, public_runs[1:]):
        prev_pass = int(prev.get("num_test_passed") or 0)
        curr_pass = int(curr.get("num_test_passed") or 0)
        if curr_pass < prev_pass:
            moments.append(
                f"`{fmt_seconds(curr['seconds_since_start'])}` public regression: "
                f"{prev_pass}/{prev.get('test_case_count') or '?'} -> {curr_pass}/{curr.get('test_case_count') or '?'}"
            )
            break

    if events:
        last = events[-1]
        moments.append(f"`{fmt_seconds(last['seconds_since_start'])}` final state: {describe_event(last)}")

    deduped: list[str] = []
    seen: set[str] = set()
    for item in moments:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped[:6]


def describe_event(event: dict[str, Any]) -> str:
    score = event.get("score")
    passed = event.get("num_test_passed")
    total = event.get("test_case_count")
    summary = event.get("summary") or event.get("reason") or event.get("event_type") or "event"
    bits = [summary]
    if score is not None:
        bits.append(f"score {fmt_score(score)}")
    if passed is not None and total is not None and total > 0:
        bits.append(f"tests {passed}/{total}")
    return ", ".join(bits)


def rel_report_path(path: str) -> str:
    if path.startswith("analysis/"):
        return "./" + path.removeprefix("analysis/")
    if path.startswith("problems/"):
        return "../" + path
    return path


def question_header(cfg: QuestionConfig, stats: dict[str, Any]) -> list[str]:
    source_artifacts = cfg.source_artifacts or [
        ("problem JSON", f"problems/{cfg.namespace}/{cfg.problem_id}.json"),
        ("question error analysis", cfg.cluster_file),
    ]
    source_links = ", ".join(
        f"[{label}]({rel_report_path(path)})" for label, path in source_artifacts
    )
    lines = [
        f"## {stats['question_title']} (`{cfg.namespace}/{cfg.problem_id}`)",
        "",
        cfg.why_use,
        "",
        f"- Track A submitters: `{stats['attempts']}`",
        f"- Full-pass rate among submitters: `{stats['full_pass_pct']}%`",
        f"- Average public test runs: `{stats['avg_public_runs']}`",
        f"- Dominant archetypes: {', '.join(stats['top_archetypes'])}",
        f"- Source artifacts: {source_links}",
        "",
        "What this question reveals:",
    ]
    for item in cfg.question_takeaways:
        lines.append(f"- {item}")
    return lines


def build_case_section(
    cfg: QuestionConfig,
    case: CaseConfig,
    attempt_row: dict[str, str],
) -> list[str]:
    namespace = cfg.namespace
    problem_id = cfg.problem_id
    student_id = case.student_id
    replay_json = path_for_existing_replay(namespace, problem_id, student_id, "json")
    replay_rec = path_for_existing_replay(namespace, problem_id, student_id, "rec")
    if case.key_moments:
        key_moments = case.key_moments
    elif replay_json.exists():
        key_moments = replay_json_key_moments(replay_json)
    else:
        key_moments = auto_key_moments(load_events(namespace, problem_id, student_id))
    artifact_bits: list[str] = []
    if replay_json.exists():
        artifact_bits.append(f"[narrative JSON](./{replay_json.name})")
    if replay_rec.exists():
        artifact_bits.append(f"[asciinema replay](./{replay_rec.name})")

    lines = [
        f"### {case.talk_role}",
        "",
        f"- Student ID: `{student_id}`",
        f"- Primary archetype: `{attempt_row['primary_archetype']}`",
        f"- Outcome: `{attempt_row['outcome_category']}`",
        f"- Final score: `{fmt_score(attempt_row['latest_submission_score'])}`",
        f"- Event count: `{attempt_row['event_count']}`",
        f"- Public test runs: `{attempt_row['public_test_run_count']}`",
        f"- Active time: `{fmt_seconds(attempt_row['total_active_time_seconds'])}`",
        f"- Replay tuple: `{namespace} / {problem_id} / {student_id}`",
    ]
    if artifact_bits:
        lines.append(f"- Existing replay artifacts: {', '.join(artifact_bits)}")
    lines.extend(
        [
            "",
            "What the student actually does:",
            f"- {case.approach_summary}",
            "",
            "Why it is interesting:",
            f"- {case.why_interesting}",
            "",
            "Key moments in the replay:",
        ]
    )
    for item in key_moments:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "What it illustrates about student learning:",
        ]
    )
    for item in case.teaching_implications:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "How it can inform question design:",
        ]
    )
    for item in case.question_design_implications:
        lines.append(f"- {item}")
    return lines


def build_funny_section(qstats: dict[tuple[str, int], dict[str, Any]]) -> list[str]:
    lines = [
        "## Funny Moments To Use On Stage",
        "",
        "These are kind laughs, not ridicule. The humor comes from recognizable debugging behavior, overfitting, and Python misunderstandings that many instructors have seen before.",
        "",
        "Timestamp note:",
        "- When a prebuilt replay exists, the timestamp below refers to the replay/cast timing.",
        "- Otherwise it refers to observed session time from the canonical timeline plus the event number.",
    ]

    for moment in FUNNY_MOMENTS:
        stats = qstats[(moment.namespace, moment.problem_id)]
        replay_json = path_for_existing_replay(moment.namespace, moment.problem_id, moment.student_id, "json")
        replay_rec = path_for_existing_replay(moment.namespace, moment.problem_id, moment.student_id, "rec")
        artifact_bits: list[str] = []
        if replay_json.exists():
            artifact_bits.append(f"[narrative JSON](./{replay_json.name})")
        if replay_rec.exists():
            artifact_bits.append(f"[asciinema replay](./{replay_rec.name})")

        lines.extend(
            [
                "",
                f"### {moment.title}",
                "",
                f"- Question: `{stats['question_title']}`",
                f"- Namespace / problem: `{moment.namespace} / {moment.problem_id}`",
                f"- Student ID: `{moment.student_id}`",
                f"- Timestamp: {moment.timestamp}",
            ]
        )
        if artifact_bits:
            lines.append(f"- Replay artifacts: {', '.join(artifact_bits)}")
        lines.extend(
            [
                f"- What happens: {moment.what_happens}",
                f"- Why it is funny: {moment.why_funny}",
                f"- What it reveals: {moment.reveals}",
                f"- How to present it hilariously: {moment.stage_angle}",
            ]
        )

    return lines


def build_funny_question_order_section(qstats: dict[tuple[str, int], dict[str, Any]]) -> list[str]:
    lines = [
        "## Funny Questions To Cover In Order",
        "",
        "This is the funny-first stage sequence rather than the full pedagogical set. It prioritizes questions where the joke lands immediately and then turns into a teaching point.",
    ]

    for plan in FUNNY_QUESTION_ORDER:
        stats = qstats[(plan.namespace, plan.problem_id)]
        lines.extend(
            [
                "",
                f"- {plan.question_summary}",
            ]
        )
        for choice in plan.choices:
            lines.append(
                f"  - Student `{choice.student_id}`: `{choice.response_to_share}`: {choice.reason}"
            )

    return lines


def build_markdown() -> str:
    attempts = load_attempt_rows()
    qstats = load_question_stats()
    generated_at = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Replay Exemplars For “How Students Learn Python”",
        "",
        f"_Generated by `analysis/generate_replays_md.py` on {generated_at}._",
        "",
        "This memo is optimized for talk preparation. It prioritizes questions where the same prompt produces visibly different approaches to problem solving, debugging, and failure.",
        "",
        "How to use it:",
        "- Open with the shortest successful replay for a question so the audience sees the clean mental model first.",
        "- Then show one productive-struggle replay and one unstable or incomplete replay on the same question.",
        "- Treat the examples as question-local comparisons. Do not use them for naive cross-term claims; later terms are progression-filtered by course design.",
        "",
        "Selection notes after review:",
        "- `Shuffle a Three Word Sentence` is now in the main set because it is the clearest sample-overfitting/public-pass/private-fail family in the repo.",
        "- Several opener cases were replaced with genuinely shortest correct replays so each question starts with a clean baseline.",
        "- The funny appendix is now broader than the core pedagogical set, because the funniest stage moments are not always the best full teaching questions.",
        "- A separate funny-only question order now appears at the end so the talk can front-load laughs without losing the stronger analytical exemplars.",
        "",
        "Replay generation note:",
        "- For any tuple below, generate a fresh cast with `uv run --script analysis/generate_asciinema.py --namespace ... --problem-id ... --student-id ... --output analysis/replay-...rec`.",
    ]

    for question in CURATED:
        stats = qstats[(question.namespace, question.problem_id)]
        lines.extend(["", *question_header(question, stats), ""])
        for case in question.cases:
            key = (question.namespace, question.problem_id, case.student_id)
            attempt_row = attempts[key]
            lines.extend(build_case_section(question, case, attempt_row))
            lines.append("")

    lines.extend(["", *build_funny_section(qstats)])
    lines.extend(["", *build_funny_question_order_section(qstats)])

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    markdown = build_markdown()
    OUT_PATH.write_text(markdown, encoding="utf-8")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
