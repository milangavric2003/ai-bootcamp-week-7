# Source-by-source review of the measured Gemma answers

Date: 2026-10-20. Reviewer: Codex, inspecting `after-answers.jsonl` against the
actual chunk texts from `src.corpus` / `src.chunking`. This is a semantic review
in addition to the fixed metrics, not the assignment's independent peer review.
No prompt or retrieval tuning followed these results.

| ID | Observed answer and source check | Finding |
| --- | --- | --- |
| E01 | 22 days of annual leave per calendar year; hb-07-chunk-0 states exactly that entitlement | Supported; unrelated remote-work citation removed |
| E02 | Password change every 90 days; hb-05-chunk-0 states that interval | Supported; irrelevant second citation removed |
| E03 | 800 EUR per year for courses, conferences and certifications; hb-08-chunk-0 supports the amount and uses | Supported |
| E04 | Up to 5 business days after manager approval; hb-01-chunk-1 explicitly anchors handover to approval | Supported, with the timing qualification retained |
| E05 | Refuses, with no citations; retrieval only provides onboarding and annual-leave text | Honest about supplied context, but still FAIL: the corpus has an equipment answer that retrieval misses |
| E06 | Up to 3 remote days per week; hb-03-chunk-0 is the current policy | Supported; no superseded policy |
| E07 | 08:00-18:00 Monday-Friday; hb-10-chunk-0 supports hours and weekdays | Supported |
| E08 | Within 30 days of return, through finance app; hb-04-chunk-0 supports both deadline and channel | Supported; irrelevant password citation removed |
| E09 | IT portal under Hardware, plus up to 5 business days after manager approval; hb-01-chunk-2 supports the location and hb-01-chunk-1 the timing | Both requested parts supported by the corresponding citations |
| E10 | Local score-gate refusal, no citations | Correct; no stock-price evidence and no API call |
| E11 | Model refusal despite annual-leave retrieval, no citations | Correct; annual leave does not establish parental-leave policy |
| E12 | Local no-results refusal, no citations | Correct; no evidence and no API call |

The eight generated answers contain no unsupported factual claims or missing
requested parts found in this review. This statement is limited to this saved run
and the supplied source texts; it is not a guarantee about later model responses.
E05 remains unanswered. Valid source IDs alone are not evidence that every future
generated claim is true.

The separate CLI check (`E11-cli.txt`, `E11-cli-answers.jsonl`) again refused E11
while showing the same annual-leave retrieval, without fabricated citations.

Behavior accuracy stays 11/12: E11 changes from a wrong answer to a correct refusal,
while E05 changes from a wrong answer to a refusal on a question that should be
answerable from the corpus. E05 was FAIL both before and after, so there is no
PASS-to-FAIL regression, but the change in behavior must still be reported.
