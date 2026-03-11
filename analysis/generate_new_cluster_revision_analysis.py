#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///
"""Generate the new-cluster testcase revision review markdown."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parent
TARGET_DIR = ROOT / "new-clusters-2026-03-11"
OUTPUT_PATH = TARGET_DIR / "analysis.md"


def tidy(text: str) -> str:
    """Normalize multiline literals used as testcase keys."""

    return "\n".join(line.rstrip() for line in dedent(text).strip().splitlines())


@dataclass(frozen=True)
class ChangeNote:
    label: str
    status: str
    area: str
    explanation: str


@dataclass(frozen=True)
class Opportunity:
    priority: str
    cluster_id: str
    title: str
    impact: str
    ease: str
    why: str
    suggested_tests: str


@dataclass(frozen=True)
class ClusterPlan:
    title: str
    refs: tuple[str, ...]
    takeaway: str
    change_notes: dict[tuple[str, str, str], ChangeNote]
    missed_opportunities: tuple[Opportunity, ...]


ASSESSMENTS: dict[str, ClusterPlan] = {
    "C002": ClusterPlan(
        title="Shuffle a Three Word Sentence",
        refs=(
            "analysis/ERRORS-cluster-c002-shuffle-a-three-word-sentence-6b942fc6.md",
            "analysis/quick-fixes.md",
        ),
        takeaway=(
            "This revision is tightly aligned with the prior C002 analysis: it now exposes all "
            "six permutations publicly, including the cyclic orders that used to stay hidden."
        ),
        change_notes={
            ("public_testcase", "added", tidy("is_equal(shuffle_sentence('red blue green', (1,0,2)))")): ChangeNote(
                label="Add the missing self-inverse permutation `(1,0,2)` on unseen words",
                status="aligned",
                area="P0 anti-hardcoding sentinel public tests",
                explanation=(
                    "Adds a third non-sample order without changing the concept, so students can no "
                    "longer overfit to just the two original public tuples."
                ),
            ),
            ("public_testcase", "added", tidy("is_equal(shuffle_sentence('alpha beta gamma', (2,0,1)))")): ChangeNote(
                label="Add cyclic permutation `(2,0,1)` on unseen words",
                status="aligned",
                area="C002 private-case finding about cyclic permutations",
                explanation=(
                    "Directly targets the inverse-permutation bug the report highlighted: code that "
                    "works on self-inverse public orders fails here."
                ),
            ),
            ("public_testcase", "added", tidy("is_equal(shuffle_sentence('one two three', (1,2,0)))")): ChangeNote(
                label="Add the other cyclic permutation `(1,2,0)`",
                status="aligned",
                area="C002 private-case finding about cyclic permutations",
                explanation=(
                    "Covers the second hidden cyclic order, so both common public-only tuple shortcuts "
                    "now fail before final submission."
                ),
            ),
            ("public_testcase", "added", tidy("is_equal(shuffle_sentence('sun moon star', (0,1,2)))")): ChangeNote(
                label="Add identity order `(0,1,2)` on unseen words",
                status="aligned",
                area="C002 identity-order / ignores-`order` coverage",
                explanation=(
                    "Checks the degenerate case explicitly and catches solutions that always rearrange "
                    "words even when the tuple says to leave them untouched."
                ),
            ),
        },
        missed_opportunities=(),
    ),
    "C078": ClusterPlan(
        title="Check For Greeting Prefix",
        refs=(
            "analysis/ERRORS-cluster-c078-check-for-greeting-prefix-969f783c.md",
            "analysis/quick-fixes.md",
        ),
        takeaway=(
            "The revision moves in the right direction by making the trailing-space contract, case "
            "sensitivity, and leading-space semantics visible. It is still only a partial implementation "
            "of the earlier recommendation because the shortest negative cases remain private."
        ),
        change_notes={
            ("public_testcase", "added", tidy('is_equal(starts_with_greeting("HelloWorld"), False)')): ChangeNote(
                label='Add `HelloWorld -> False`',
                status="aligned",
                area="P1 short/edge public tests for trailing-space semantics",
                explanation=(
                    "Directly addresses the most common failure mode: accepting `Hello` without the "
                    "required trailing space."
                ),
            ),
            ("public_testcase", "added", tidy('is_equal(starts_with_greeting("Hello "), True)')): ChangeNote(
                label='Add bare prefix positive `Hello  -> True`',
                status="aligned",
                area="P1 short/edge public tests for C078",
                explanation=(
                    "Matches the prior recommendation to expose the exact contract that a bare greeting "
                    "followed by a space is valid."
                ),
            ),
            ("public_testcase", "added", tidy('is_equal(starts_with_greeting("Hi "), True)')): ChangeNote(
                label='Add bare prefix positive `Hi  -> True`',
                status="aligned",
                area="P1 short/edge public tests for C078",
                explanation=(
                    "Makes the `Hi ` branch explicit instead of relying only on longer phrases like "
                    "`Hi friend`."
                ),
            ),
            ("public_testcase", "added", tidy('is_equal(starts_with_greeting("hello world"), False)')): ChangeNote(
                label='Add lowercase negative `hello world -> False`',
                status="aligned",
                area="C078 case-sensitivity failures",
                explanation=(
                    "Targets the documented pattern where students lowercase the input or accept "
                    "case-insensitive greetings."
                ),
            ),
            ("public_testcase", "added", tidy('is_equal(starts_with_greeting(" hi there"), False)')): ChangeNote(
                label='Add leading-space negative ` hi there -> False`',
                status="aligned",
                area="C078 `strip()` / `lstrip()` semantic bug",
                explanation=(
                    "Directly catches solutions that trim leading whitespace before checking the prefix."
                ),
            ),
            ("public_testcase", "removed", tidy('is_equal(starts_with_greeting("Hello there"), True)')): ChangeNote(
                label='Remove normal positive phrase `Hello there -> True`',
                status="tradeoff",
                area="Not a previously identified gap",
                explanation=(
                    "This is a coverage trade-off rather than a targeted fix. It frees room for edge "
                    "cases but removes a simple sanity-check positive example."
                ),
            ),
            ("public_testcase", "removed", tidy('is_equal(starts_with_greeting("Hi friend"), True)')): ChangeNote(
                label='Remove normal positive phrase `Hi friend -> True`',
                status="tradeoff",
                area="Not a previously identified gap",
                explanation=(
                    "Same trade-off as above: the suite becomes edge-heavier but loses a normal positive "
                    "example with characters after the prefix."
                ),
            ),
            ("public_testcase", "removed", tidy('is_equal(starts_with_greeting("Hithere"), False)')): ChangeNote(
                label='Remove `Hithere -> False`',
                status="tradeoff",
                area="Weakens one public guard on the no-space `Hi` bug",
                explanation=(
                    "The earlier recommendation explicitly kept a `Hi`-family no-space negative public. "
                    "Replacing it with only `HelloWorld` leaves the `Hi` side less visible."
                ),
            ),
            ("public_testcase", "removed", tidy('is_equal(starts_with_greeting("Welcome"), False)')): ChangeNote(
                label='Remove generic negative `Welcome -> False`',
                status="tradeoff",
                area="Low-value generic negative coverage",
                explanation=(
                    "This removal is mostly harmless, but it does not map to any specific failure family "
                    "we had previously identified."
                ),
            ),
        },
        missed_opportunities=(
            Opportunity(
                priority="P1",
                cluster_id="C078",
                title="Add the truly short negatives publicly: `\"\"`, `\"Hi\"`, and `\"Hello\"`",
                impact="High",
                ease="Trivial",
                why=(
                    "The report linked 79 non-full rows to short/empty-string `IndexError` and 92 rows "
                    "to accepting `Hi`/`Hello` without the trailing space. Those failures are still hidden."
                ),
                suggested_tests='is_equal(starts_with_greeting(""), False); is_equal(starts_with_greeting("Hi"), False); is_equal(starts_with_greeting("Hello"), False)',
            ),
        ),
    ),
    "C085": ClusterPlan(
        title="Expand Sum of Products",
        refs=(
            "analysis/ERRORS-cluster-c085-expand-sum-of-products-727deffc.md",
            "analysis/quick-fixes.md",
        ),
        takeaway=(
            "C085 is the cleanest implementation of the earlier recommendations: the revised suite now "
            "hits both anti-hardcoding and variable-length parser traps in public."
        ),
        change_notes={
            ("public_testcase", "added", tidy("is_equal(expand_sum_of_products('(p+q)(r+s)'), 'p*r + p*s + q*r + q*s')")): ChangeNote(
                label="Add unseen symbolic baseline `(p+q)(r+s)`",
                status="aligned",
                area="P0 anti-hardcoding sentinel public tests",
                explanation=(
                    "Breaks memorization of the original `(a+b)(c+d)` sample while keeping the same "
                    "conceptual difficulty."
                ),
            ),
            ("public_testcase", "added", tidy("is_equal(expand_sum_of_products('(m+n)(u+v)'), 'm*u + m*v + n*u + n*v')")): ChangeNote(
                label="Add a second unseen symbolic baseline `(m+n)(u+v)`",
                status="aligned",
                area="P0 anti-hardcoding sentinel public tests",
                explanation=(
                    "Further reduces the chance that students can pass by memorizing one or two literal "
                    "public expansions."
                ),
            ),
            ("public_testcase", "added", tidy("is_equal(expand_sum_of_products('(x+y)(a+b)'), 'x*a + x*b + y*a + y*b')")): ChangeNote(
                label="Add another reordered symbolic baseline `(x+y)(a+b)`",
                status="aligned",
                area="P0 anti-hardcoding sentinel public tests",
                explanation=(
                    "Keeps the easy symbolic shape public but makes it clear that the exact letters do not matter."
                ),
            ),
            ("public_testcase", "added", tidy("is_equal(expand_sum_of_products('(alpha+beta)(gamma+delta)'), 'alpha*gamma + alpha*delta + beta*gamma + beta*delta')")): ChangeNote(
                label="Add multi-character identifiers",
                status="aligned",
                area="P0 variable-length / parser edge cases",
                explanation=(
                    "Directly targets the largest C085 failure family: fixed-position parsers that only work "
                    "for one-character tokens."
                ),
            ),
            ("public_testcase", "added", tidy("is_equal(expand_sum_of_products('(123+45)(67+890)'), '123*67 + 123*890 + 45*67 + 45*890')")): ChangeNote(
                label="Add multi-digit numeric terms",
                status="aligned",
                area="P0 variable-length / parser edge cases",
                explanation=(
                    "Exposes the fixed-width numeric parsing bug that used to appear only in private cases."
                ),
            ),
            ("public_testcase", "added", tidy("is_equal(expand_sum_of_products('(cat+dog)(sun+moon)'), 'cat*sun + cat*moon + dog*sun + dog*moon')")): ChangeNote(
                label="Add word tokens instead of algebraic-looking symbols",
                status="aligned",
                area="P0 anti-hardcoding sentinel public tests",
                explanation=(
                    "Makes it even harder to fake an algebra-only parser by indexing literal character positions."
                ),
            ),
            ("public_testcase", "removed", tidy("is_equal(expand_sum_of_products('(a+b)(c+d)'), 'a*c + a*d + b*c + b*d')")): ChangeNote(
                label="Remove the canonical `(a+b)(c+d)` public sample",
                status="partial",
                area="Supports the anti-hardcoding shift",
                explanation=(
                    "Removing the most memorizable sample helps, but the real improvement comes from the "
                    "stronger replacements rather than the deletion itself."
                ),
            ),
            ("public_testcase", "removed", tidy("is_equal(expand_sum_of_products('(x+y)(z+w)'), 'x*z + x*w + y*z + y*w')")): ChangeNote(
                label="Remove the second sample-shaped symbolic case",
                status="partial",
                area="Supports the anti-hardcoding shift",
                explanation=(
                    "Same rationale: useful mainly because it avoids a public suite made entirely of sample-adjacent expressions."
                ),
            ),
            ("public_testcase", "removed", tidy("is_equal(expand_sum_of_products('(1+5)(10+12)'), '1*10 + 1*12 + 5*10 + 5*12')")): ChangeNote(
                label="Replace the old numeric sample with a stronger numeric edge case",
                status="partial",
                area="Supports stronger variable-length coverage",
                explanation=(
                    "The new numeric case is better because it is more visibly fixed-width-hostile than the original sample."
                ),
            ),
        },
        missed_opportunities=(),
    ),
    "C092": ClusterPlan(
        title="Describe Number Based on Divisibility",
        refs=(
            "analysis/ERRORS-cluster-c092-describe-number-based-on-divisibility-550c6af3.md",
            "analysis/quick-fixes.md",
        ),
        takeaway=(
            "The revised public tests target the right hidden errors, but this is the only cluster where "
            "the suite also got narrower. It now shows `FizzBuzz` and `Normal` publicly, while `Fizz` and "
            "`Buzz` disappear from public coverage."
        ),
        change_notes={
            ("public_testcase", "added", tidy('is_equal(describe_number(45), "FizzBuzz")')): ChangeNote(
                label='Replace `15` with another `FizzBuzz` multiple (`45`)',
                status="aligned",
                area="C092 `FizzBuzz` branch-order bug",
                explanation=(
                    "Keeps the same intended trap public: solutions that check `% 3` or `% 5` first still fail."
                ),
            ),
            ("public_testcase", "added", tidy('is_equal(describe_number(34), "Normal")')): ChangeNote(
                label='Add `Normal` casing example on a non-sample number',
                status="aligned",
                area="P1 formatting/casing visibility for `Normal`",
                explanation=(
                    "Directly targets the largest C092 family: returning `'normal'` instead of `'Normal'`."
                ),
            ),
            ("public_testcase", "removed", tidy('is_equal(describe_number(9), "Fizz")')): ChangeNote(
                label='Remove the `Fizz` public example',
                status="tradeoff",
                area="Removes branch coverage that was not identified as expendable",
                explanation=(
                    "This does not map to a prior recommendation. It weakens public coverage for one of the "
                    "four required labels."
                ),
            ),
            ("public_testcase", "removed", tidy('is_equal(describe_number(10), "Buzz")')): ChangeNote(
                label='Remove the `Buzz` public example',
                status="tradeoff",
                area="Removes branch coverage that was not identified as expendable",
                explanation=(
                    "Same issue as above: the suite becomes less balanced across the four output branches."
                ),
            ),
            ("public_testcase", "removed", tidy('is_equal(describe_number(15), "FizzBuzz")')): ChangeNote(
                label='Remove the simple `FizzBuzz` sample (`15`)',
                status="partial",
                area="Concept preserved via `45`, but deletion adds no new leverage",
                explanation=(
                    "Net coverage for the `FizzBuzz` branch remains, so this is not a regression, but the "
                    "improvement comes from the replacement rather than the removal."
                ),
            ),
            ("public_testcase", "removed", tidy('is_equal(describe_number(7), "Normal")')): ChangeNote(
                label='Remove the simple `Normal` sample (`7`)',
                status="partial",
                area="Concept preserved via `34`, but deletion adds no new leverage",
                explanation=(
                    "The casing issue is still exposed through `34 -> Normal`, but removing the simpler public "
                    "baseline was not part of the earlier recommendation."
                ),
            ),
        },
        missed_opportunities=(
            Opportunity(
                priority="P1",
                cluster_id="C092",
                title="Restore one public `Fizz` case and one public `Buzz` case",
                impact="Medium",
                ease="Trivial",
                why=(
                    "The revision now covers `FizzBuzz` and `Normal` well, but it unnecessarily dropped public "
                    "coverage for the other two required labels."
                ),
                suggested_tests='is_equal(describe_number(9), "Fizz"); is_equal(describe_number(10), "Buzz")',
            ),
        ),
    ),
    "C095": ClusterPlan(
        title="Convert Excel Column Name to 1-Based Index",
        refs=(
            "analysis/ERRORS-cluster-c095-convert-excel-column-name-to-1-based-index-ec81fd59.md",
            "analysis/quick-fixes.md",
        ),
        takeaway=(
            "C095 is improved, but only partially. The public suite now walks students through a cleaner "
            "1-letter to 2-letter staircase, yet the exact 3+/4-letter edge cases that our quick-fix note "
            "called out are still private-only."
        ),
        change_notes={
            ("public_testcase", "added", tidy('is_equal(excel_index("A"), 1)')): ChangeNote(
                label='Add base case `A -> 1`',
                status="aligned",
                area="Anti-hardcoding + baseline mapping visibility",
                explanation=(
                    "Makes the simplest base-26 mapping public instead of relying only on the prose example."
                ),
            ),
            ("public_testcase", "added", tidy('is_equal(excel_index("Z"), 26)')): ChangeNote(
                label='Add single-letter boundary `Z -> 26`',
                status="aligned",
                area="Single-letter boundary coverage",
                explanation=(
                    "Helps catch off-by-one or incomplete alphabet tables before students reach multi-letter columns."
                ),
            ),
            ("public_testcase", "added", tidy('is_equal(excel_index("AA"), 27)')): ChangeNote(
                label='Add the first two-letter rollover `AA -> 27`',
                status="aligned",
                area="Early-return / positional-weight trap for C095",
                explanation=(
                    "Directly exposes solutions that return after processing only the first letter or that treat "
                    "the label as simple concatenation."
                ),
            ),
            ("public_testcase", "added", tidy('is_equal(excel_index("ZZ"), 702)')): ChangeNote(
                label='Add two-letter upper boundary `ZZ -> 702`',
                status="aligned",
                area="Two-letter positional-weight coverage",
                explanation=(
                    "Strengthens public coverage of base-26 weighting across two positions."
                ),
            ),
        },
        missed_opportunities=(
            Opportunity(
                priority="P0",
                cluster_id="C095",
                title="Move one 3-/4-letter edge case into public (`XFD` and ideally `AAAA`)",
                impact="High",
                ease="Trivial",
                why=(
                    "Our own quick-fix note named exactly this gap. The revised public suite still stops at `BBA`, "
                    "so the 24 longer-label parser failures remain largely hidden."
                ),
                suggested_tests='is_equal(excel_index("XFD"), 16384); is_equal(excel_index("AAAA"), 18279)',
            ),
        ),
    ),
    "C096": ClusterPlan(
        title="Sales Data Analysis",
        refs=(
            "analysis/ERRORS-cluster-c096-sales-data-analysis-14952156.md",
            "analysis/quick-fixes.md",
        ),
        takeaway=(
            "This is a strong revision. The new public tests are smaller, more discriminative, and much more "
            "aligned with the earlier recommendation to expose one branch-specific failure mode per task."
        ),
        change_notes={
            ("public_testcase", "added", tidy(
                """
                sales_data = [
                 {"product_id":"A","units_sold":10,"revenue":100},
                 {"product_id":"B","units_sold":5,"revenue":60},
                 {"product_id":"A","units_sold":5,"revenue":50}
                ]
                is_equal(analyse_sales_data(sales_data,'total_revenue'),210)
                """
            )): ChangeNote(
                label="Replace sample-sized `total_revenue` with a tiny discriminative dataset",
                status="aligned",
                area="P1 dispatch-branch coverage for task-driven functions",
                explanation=(
                    "Now students can isolate the `total_revenue` branch without parsing a large example or "
                    "depending on the sample product IDs."
                ),
            ),
            ("public_testcase", "added", tidy(
                """
                sales_data = [
                 {"product_id":"A","units_sold":10,"revenue":100},
                 {"product_id":"B","units_sold":5,"revenue":60},
                 {"product_id":"A","units_sold":5,"revenue":50}
                ]
                is_equal(analyse_sales_data(sales_data,'product_wise_total_units_and_revenue'),{'A':(15,150),'B':(5,60)})
                """
            )): ChangeNote(
                label="Use a tiny repeated-product dataset for the aggregation branch",
                status="aligned",
                area="P1 dispatch-branch coverage for task-driven functions",
                explanation=(
                    "Publicly exposes the repeated-`product_id` aggregation behavior instead of hiding it inside a larger sample."
                ),
            ),
            ("public_testcase", "added", tidy(
                """
                sales_data = [
                 {"product_id":"A","units_sold":10,"revenue":100},
                 {"product_id":"B","units_sold":10,"revenue":200}
                ]
                is_equal(analyse_sales_data(sales_data,'top_selling_product'),'B')
                """
            )): ChangeNote(
                label="Make the tie-break rule public for `top_selling_product`",
                status="aligned",
                area="C096 hidden tie-break behavior",
                explanation=(
                    "This was explicitly a hidden-case requirement before; the revision now shows the revenue tie-break publicly."
                ),
            ),
            ("public_testcase", "added", tidy(
                """
                sales_data = [
                 {"product_id":"A","units_sold":10,"revenue":100},
                 {"product_id":"A","units_sold":5,"revenue":60}
                ]
                is_equal(analyse_sales_data(sales_data,'average_product_price'),{'A':10.67})
                """
            )): ChangeNote(
                label="Make non-integer average rounding public",
                status="aligned",
                area="P1 rounding visibility for `average_product_price`",
                explanation=(
                    "Directly targets the documented `10.6%` failure family where students compute the right "
                    "average but do not round to two decimals."
                ),
            ),
            ("public_testcase", "removed", tidy(
                """
                sales_data = [
                   {"product_id": "P101", "units_sold": 50, "revenue": 400},
                   {"product_id": "P102", "units_sold": 30, "revenue": 900},
                   {"product_id": "P101", "units_sold": 70, "revenue": 600},
                   {"product_id": "P103", "units_sold": 120, "revenue": 600}
                ]
                is_equal(
                    analyse_sales_data(
                        sales_data,
                        "total_revenue"
                    ),
                    2500
                )
                """
            )): ChangeNote(
                label="Drop the large sample-specific `total_revenue` public test",
                status="partial",
                area="Replaced by smaller branch-isolating coverage",
                explanation=(
                    "Helpful because it removes dependence on the sample product IDs, but the real gain comes "
                    "from the tighter replacement case."
                ),
            ),
            ("public_testcase", "removed", tidy(
                """
                sales_data = [
                   {"product_id": "P101", "units_sold": 50, "revenue": 400},
                   {"product_id": "P102", "units_sold": 30, "revenue": 900},
                   {"product_id": "P101", "units_sold": 70, "revenue": 600},
                   {"product_id": "P103", "units_sold": 120, "revenue": 600}
                ]
                is_equal( 
                    analyse_sales_data(
                        sales_data,
                        "product_wise_total_units_and_revenue"
                    ),
                    {'P101': (120, 1000), 'P102': (30, 900), 'P103': (120, 600)}
                )
                """
            )): ChangeNote(
                label="Drop the large sample-specific aggregation public test",
                status="partial",
                area="Replaced by smaller branch-isolating coverage",
                explanation=(
                    "The new small dataset makes the repeated-ID requirement easier to diagnose and less overfit-prone."
                ),
            ),
            ("public_testcase", "removed", tidy(
                """
                sales_data = [
                   {"product_id": "P101", "units_sold": 50, "revenue": 400},
                   {"product_id": "P102", "units_sold": 30, "revenue": 900},
                   {"product_id": "P101", "units_sold": 70, "revenue": 600},
                   {"product_id": "P103", "units_sold": 120, "revenue": 600}
                ]
                is_equal(
                    analyse_sales_data(
                        sales_data,
                        "top_selling_product"
                    ),
                    "P101"
                )
                """
            )): ChangeNote(
                label="Drop the large sample-specific top-seller test",
                status="partial",
                area="Replaced by a cleaner tie-break-focused public case",
                explanation=(
                    "The replacement is better because it isolates the tie-break rule rather than bundling it into a long sample."
                ),
            ),
            ("public_testcase", "removed", tidy(
                """
                sales_data = [
                   {"product_id": "P101", "units_sold": 50, "revenue": 400},
                   {"product_id": "P102", "units_sold": 30, "revenue": 900},
                   {"product_id": "P101", "units_sold": 70, "revenue": 600},
                   {"product_id": "P103", "units_sold": 120, "revenue": 600}
                ]
                is_equal(
                    analyse_sales_data(
                        sales_data,
                        "average_product_price"
                    ),
                    {'P101': 8.33, 'P102': 30, 'P103': 5}
                )
                """
            )): ChangeNote(
                label="Drop the large sample-specific average-price test",
                status="partial",
                area="Replaced by a stronger rounding-focused public case",
                explanation=(
                    "The new `10.67` case is more discriminative for the exact rounding bug our analysis highlighted."
                ),
            ),
        },
        missed_opportunities=(),
    ),
    "C099": ClusterPlan(
        title="Parse Equation and Solve for x",
        refs=(
            "analysis/ERRORS-cluster-c099-parse-equation-and-solve-for-x-29a54a89.md",
            "analysis/quick-fixes.md",
        ),
        takeaway=(
            "This is another strong revision: it publicizes implied coefficients, subtraction, no-constant cases, "
            "multi-digit coefficients, and negative right-hand sides. Those were exactly the parser traps our "
            "earlier analysis said were hiding behind the private suite."
        ),
        change_notes={
            ("public_testcase", "added", tidy(
                """
                is_equal(
                    solve_for_x("x + 2 = 5"),
                    3.0
                )
                """
            )): ChangeNote(
                label='Add implied-coefficient case `x + 2 = 5`',
                status="aligned",
                area="P0 variable-length / parser edge cases for implied coefficients",
                explanation=(
                    "Directly targets the documented failure where students try to `int('')` instead of treating missing `a` as `1`."
                ),
            ),
            ("public_testcase", "added", tidy(
                """
                is_equal(
                    solve_for_x("10x + 20 = 60"),
                    4.0
                )
                """
            )): ChangeNote(
                label='Add multi-digit coefficient case `10x + 20 = 60`',
                status="aligned",
                area="P0 fixed-width parser traps",
                explanation=(
                    "Exposes parsers that only work when coefficients are one character long."
                ),
            ),
            ("public_testcase", "added", tidy(
                """
                is_equal(
                    solve_for_x("2x=6"),
                    3.0
                )
                """
            )): ChangeNote(
                label='Add no-constant case `2x=6`',
                status="aligned",
                area="P0 fixed-format parser traps",
                explanation=(
                    "Catches solutions that assume every equation must contain an explicit `+ b` or `- b` term."
                ),
            ),
            ("public_testcase", "added", tidy(
                """
                is_equal(
                    solve_for_x("x - 3 = 7"),
                    10.0
                )
                """
            )): ChangeNote(
                label='Add subtraction with implied coefficient `x - 3 = 7`',
                status="aligned",
                area="P0 subtraction/sign parser edge cases",
                explanation=(
                    "Combines two earlier hidden traps at once: implied `a=1` and a negative constant term."
                ),
            ),
            ("public_testcase", "added", tidy(
                """
                is_equal(
                    solve_for_x("3x + 7 = -2"),
                    -3.0
                )
                """
            )): ChangeNote(
                label='Add negative-RHS case `3x + 7 = -2`',
                status="aligned",
                area="P0 sign-handling robustness",
                explanation=(
                    "Targets the sign/spacing family that previously passed public and then failed private."
                ),
            ),
        },
        missed_opportunities=(
            Opportunity(
                priority="P0",
                cluster_id="C099",
                title="Add one whitespace-stressed composite edge case",
                impact="High",
                ease="Trivial",
                why=(
                    "The suite is much better, but the prompt explicitly allows irregular internal and trailing "
                    "spaces. A single public case that combines whitespace normalization with an implied coefficient "
                    "or negative RHS would close the last obvious hidden-parser gap."
                ),
                suggested_tests='is_equal(solve_for_x(" x + 5 = -5 "), -10.0) or is_equal(solve_for_x(" 10x+20=60 "), 4.0)',
            ),
        ),
    ),
}


STATUS_LABELS = {
    "aligned": "Aligned",
    "partial": "Partial",
    "tradeoff": "Trade-off",
}

STATUS_ORDER = {
    "tradeoff": 0,
    "partial": 1,
    "aligned": 2,
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def find_case_path(cluster_dir: Path, suffix: str) -> Path:
    matches = sorted(cluster_dir.glob(f"*_{suffix}.json"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one *_{suffix}.json in {cluster_dir}, found {len(matches)}")
    return matches[0]


def diff_cases(original: list[dict], revised: list[dict]) -> dict[str, list[str]]:
    """Return added/removed testcase inputs, preserving JSON order."""

    original_keys = {(tidy(case.get("input", "")), tidy(case.get("output", ""))) for case in original}
    revised_keys = {(tidy(case.get("input", "")), tidy(case.get("output", ""))) for case in revised}

    added = [
        tidy(case.get("input", ""))
        for case in revised
        if (tidy(case.get("input", "")), tidy(case.get("output", ""))) not in original_keys
    ]
    removed = [
        tidy(case.get("input", ""))
        for case in original
        if (tidy(case.get("input", "")), tidy(case.get("output", ""))) not in revised_keys
    ]
    return {"added": added, "removed": removed}


def summarize_counts(cluster_id: str, notes: list[ChangeNote]) -> str:
    aligned = sum(note.status == "aligned" for note in notes)
    partial = sum(note.status == "partial" for note in notes)
    tradeoff = sum(note.status == "tradeoff" for note in notes)
    return (
        f"`{cluster_id}`: {aligned} aligned, {partial} partial, {tradeoff} trade-off "
        f"testcase changes."
    )


def slug_priority(priority: str) -> tuple[int, str]:
    order = {"P0": 0, "P1": 1, "P2": 2}
    return (order[priority], priority)


def md(text: str) -> str:
    return text.replace("|", "\\|")


def build_report() -> str:
    cluster_dirs = sorted(path for path in TARGET_DIR.iterdir() if path.is_dir())
    if not cluster_dirs:
        raise RuntimeError(f"No cluster directories found under {TARGET_DIR}")

    sections: list[str] = []
    all_notes: list[ChangeNote] = []
    all_opportunities: list[Opportunity] = []
    per_cluster_counts: list[str] = []

    for cluster_dir in cluster_dirs:
        cluster_id = cluster_dir.name
        if cluster_id not in ASSESSMENTS:
            raise RuntimeError(f"Missing assessment metadata for {cluster_id}")

        plan = ASSESSMENTS[cluster_id]
        original = load_json(find_case_path(cluster_dir, "original"))
        revised = load_json(find_case_path(cluster_dir, "revised"))

        public_original = original.get("public_testcase") or []
        public_revised = revised.get("public_testcase") or []
        private_original = original.get("private_testcase") or []
        private_revised = revised.get("private_testcase") or []

        public_diff = diff_cases(public_original, public_revised)
        private_diff = diff_cases(private_original, private_revised)

        actual_keys = {
            ("public_testcase", "added", case) for case in public_diff["added"]
        } | {
            ("public_testcase", "removed", case) for case in public_diff["removed"]
        } | {
            ("private_testcase", "added", case) for case in private_diff["added"]
        } | {
            ("private_testcase", "removed", case) for case in private_diff["removed"]
        }

        expected_keys = set(plan.change_notes)
        if actual_keys != expected_keys:
            missing = sorted(expected_keys - actual_keys)
            extra = sorted(actual_keys - expected_keys)
            raise RuntimeError(
                f"{cluster_id} annotations are out of sync.\nMissing: {missing}\nExtra: {extra}"
            )

        ordered_rows: list[tuple[str, ChangeNote]] = []
        for scope, diff in (("public_testcase", public_diff), ("private_testcase", private_diff)):
            for kind in ("added", "removed"):
                for case in diff[kind]:
                    note = plan.change_notes[(scope, kind, case)]
                    ordered_rows.append((f"{scope.replace('_', ' ').replace('testcase', '').strip()} {kind}", note))
                    all_notes.append(note)

        per_cluster_counts.append(summarize_counts(cluster_id, [note for _, note in ordered_rows]))
        all_opportunities.extend(plan.missed_opportunities)

        table_lines = [
            "| Change | Mapping | Improvement Area | Explanation |",
            "| --- | --- | --- | --- |",
        ]
        for change_kind, note in ordered_rows:
            table_lines.append(
                f"| {md(change_kind.title() + ': ' + note.label)} | {STATUS_LABELS[note.status]} | "
                f"{md(note.area)} | {md(note.explanation)} |"
            )

        missed_lines: list[str] = []
        if plan.missed_opportunities:
            for opportunity in sorted(plan.missed_opportunities, key=lambda item: slug_priority(item.priority)):
                missed_lines.append(
                    f"- `{opportunity.priority}`: {opportunity.title}. Why: {opportunity.why} "
                    f"Suggested tests: `{opportunity.suggested_tests}`."
                )
        else:
            missed_lines.append("- No high-priority missed opportunity stood out here; the revision already matches the earlier diagnosis well.")

        sections.append(
            "\n".join(
                [
                    f"## {cluster_id} - {plan.title}",
                    f"Refs: {', '.join(f'`{ref}`' for ref in plan.refs)}.",
                    (
                        f"Public tests changed from `{len(public_original)}` to `{len(public_revised)}`. "
                        f"Private tests changed from `{len(private_original)}` to `{len(private_revised)}`."
                    ),
                    plan.takeaway,
                    "",
                    "### Change-by-Change Mapping",
                    *table_lines,
                    "",
                    "### Missed Opportunities",
                    *missed_lines,
                ]
            )
        )

    aligned_total = sum(note.status == "aligned" for note in all_notes)
    partial_total = sum(note.status == "partial" for note in all_notes)
    tradeoff_total = sum(note.status == "tradeoff" for note in all_notes)

    opportunities_table = [
        "| Priority | Cluster | Suggested change | Impact | Ease | Why it still matters |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for opportunity in sorted(all_opportunities, key=lambda item: (slug_priority(item.priority), item.cluster_id, item.title)):
        opportunities_table.append(
            f"| {opportunity.priority} | {opportunity.cluster_id} | {md(opportunity.title)} | "
            f"{opportunity.impact} | {opportunity.ease} | {md(opportunity.why)} |"
        )

    executive_lines = [
        "# Test Revision Review - 2026-03-11",
        "",
        "Each cluster folder now uses the consistent pair format `C###_original.json` and `C###_revised.json`.",
        "",
        "## Executive Summary",
        (
            f"There are `{len(all_notes)}` testcase changes across the seven clusters: `{aligned_total}` directly "
            f"aligned with earlier findings, `{partial_total}` partially aligned, and `{tradeoff_total}` coverage "
            f"trade-offs that were not themselves previously identified as priorities."
        ),
        "- Strong, directly aligned revisions: `C002`, `C085`, `C096`, and `C099`.",
        "- Partial revisions: `C078` and `C095` move in the right direction but still leave the most useful hidden traps private.",
        "- Mixed revision: `C092` exposed the right hidden failure modes, but it also removed public `Fizz`/`Buzz` coverage.",
        *[f"- {line}" for line in per_cluster_counts],
        "",
        "## Highest-Priority Missed Opportunities",
        *opportunities_table,
        "",
        "The priorities above are ranked by the combination of likely impact on known student failure modes and how little evaluator work is needed to implement the change.",
    ]

    return "\n".join([*executive_lines, "", *sections, ""])


def main() -> None:
    report = build_report()
    OUTPUT_PATH.write_text(report)
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
