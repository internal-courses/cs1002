# Thrashers and Question-Language Load

## Direct Answer

No statistically significant evidence that prompt language load alone explains thrashing.

You asked specifically about native Hindi speakers. This dataset does **not** include each student's native language, so we cannot directly test that claim.
What we can test is an indirect signal: do linguistically heavier English prompts coincide with more thrasher behavior?

## Data Used

- Attempt rows analyzed: `151,760`
- Thrasher rows: `2,758` (`1.82%`)
- Python question instances: `245`
- Thrashers source: `analysis/process_analysis/attempt_archetypes.csv` (`thrasher_flag`)
- Prompt source: `problems/*/*.json` question text + testcase counts + template structure

## Main Statistical Evidence

- Weighted correlation (language-load index vs question thrasher rate): `-0.050`, permutation `p=0.4459`.
- Spearman correlation (unweighted): `0.006`, `p=0.9266`.
- Adjusted model (controls: technical difficulty index + log attempts): beta(load) `0.059`, permutation `p=0.6831`.
- High-language-load questions (top quartile) vs low-language-load (bottom quartile): `1.64%` vs `1.78%`, diff `-0.14 pp`, `p=0.1444`.
- Robustness (collapse near-duplicate variants into semantic signatures): weighted corr `-0.050`, `p=0.5589`; Spearman `0.036`, `p=0.6563`.
- Mean language-load index among top 15 thrasher-rate questions vs the rest: `-0.09` vs `0.01`.

## What This Means (Plain Language)

- If p-values are small (<0.05), language-heavy prompts are likely adding extra confusion load.
- If p-values are not small, the data does not support language-load as a major standalone explanation.
- Either way, this is an indirect signal. It does **not** prove which students are native Hindi speakers or why any one student thrashed.

## Where Language Load Looks High

- `ns_25t1_py23_1/12` `Polygon Analysis`: language-load index `1.45`, thrasher rate `0.00%` over `463` attempts.
- `ns_25t1_py23_2/12` `Polygon Analysis`: language-load index `1.45`, thrasher rate `0.00%` over `727` attempts.
- `ns_25t3_py23/10` `Identify Eligible Voters`: language-load index `1.30`, thrasher rate `2.96%` over `844` attempts.
- `ns_25t3_py24_1/13` `Rotate a Stacked‑Item Matrix 90° Clockwise`: language-load index `1.23`, thrasher rate `2.29%` over `699` attempts.
- `ns_25t3_py13_2/12` `Count Word Types by Length and Palindrome Property`: language-load index `1.07`, thrasher rate `2.46%` over `609` attempts.
- `ns_25t3_py13_1/11` `Count Word Types by Length and Palindrome Property`: language-load index `1.07`, thrasher rate `1.83%` over `600` attempts.
- `ns_25t2_py11_1/5` `Describe Number Based on Divisibility`: language-load index `1.07`, thrasher rate `2.61%` over `689` attempts.
- `ns_25t1_py14_2/10` `Key Stroke Analysis`: language-load index `1.04`, thrasher rate `0.28%` over `353` attempts.

## Highest Thrasher-Rate Questions

- `ns_25t1_py12_2/10` `Pattern printing - Centered Triangle Of Zeroes`: thrasher rate `12.59%`, language-load index `-0.27`, attempts `413`.
- `ns_25t1_py12_1/10` `Pattern printing - Centered Triangle Of Zeroes`: thrasher rate `10.11%`, language-load index `-0.27`, attempts `524`.
- `ns_25t2_py22_1/17` `Reversed Squares of List Elements`: thrasher rate `7.08%`, language-load index `-0.03`, attempts `1003`.
- `ns_25t2_py21_2/18` `Pangram Check`: thrasher rate `6.96%`, language-load index `-0.33`, attempts `733`.
- `ns_25t2_py21_2/26` `File Content Zig-Zag Shift`: thrasher rate `6.91%`, language-load index `0.14`, attempts `333`.
- `ns_25t3_py22/10` `Bank Account Number Generator`: thrasher rate `6.75%`, language-load index `0.24`, attempts `415`.
- `ns_25t1_py_15_exe/13` `Pattern Printing - W Pattern`: thrasher rate `6.33%`, language-load index `-0.23`, attempts `79`.
- `ns_25t3_py13_1/13` `Step Triangle Pattern`: thrasher rate `5.81%`, language-load index `-0.16`, attempts `396`.
- `ns_25t3_py23/13` `Fill Blanks with Words from a List`: thrasher rate `5.71%`, language-load index `0.00`, attempts `525`.
- `ns_25t2_py22_1/19` `Sales Data Analysis`: thrasher rate `5.18%`, language-load index `0.44`, attempts `714`.

## Matched-Pair Evidence (Similar technical difficulty, different language load)

- `ns_25t1_py13_1/4` (Markdown Image to HTML Image) vs `ns_25t2_py21_2/26` (File Content Zig-Zag Shift): tech gap `0.09`, language-load gap `1.03`, thrasher-rate gap `-6.91 pp`.
- `ns_25t1_py13_1/4` (Markdown Image to HTML Image) vs `ns_25t3_py22/10` (Bank Account Number Generator): tech gap `0.10`, language-load gap `1.14`, thrasher-rate gap `-6.75 pp`.
- `ns_25t1_py13_2/4` (Markdown Image to HTML Image) vs `ns_25t2_py21_2/26` (File Content Zig-Zag Shift): tech gap `0.09`, language-load gap `1.03`, thrasher-rate gap `-6.71 pp`.
- `ns_25t1_py13_2/4` (Markdown Image to HTML Image) vs `ns_25t3_py22/10` (Bank Account Number Generator): tech gap `0.10`, language-load gap `1.14`, thrasher-rate gap `-6.55 pp`.
- `ns_25t1_py11_1/6` (Counts unique even and odd numbers) vs `ns_25t2_py21_2/26` (File Content Zig-Zag Shift): tech gap `0.03`, language-load gap `1.03`, thrasher-rate gap `-5.76 pp`.

## Caveats (Important)

- No native-language labels are available. We cannot identify Hindi speakers from this data.
- Readability formulas are rough for programming prompts; they are proxies, not ground truth.
- Correlation is not causation. Some high-load prompts may also hide concept ambiguity.
- Thrashing itself is a process label, not a fixed student identity.

## Files Produced

- `analysis/thrashers_language.csv` (question-level feature table)
- `analysis/thrashers_language_clusters.csv` (collapsed semantic-signature table)
- `analysis/thrashers_language_tests.csv` (all statistical test outputs)
- `analysis/thrashers_language_pairs.csv` (matched-pair evidence)
- `analysis/thrashers_language.md` (this report)
