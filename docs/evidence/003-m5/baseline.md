# M5 baseline — before pipeline changes

Recorded 19 October 2026, from `main` at commit `ab83d92`.
Specification and plan were committed before implementation. The user explicitly
requested M5 implementation on main now. Minimum submission remains unconfirmed;
the assignment places advanced work after submitting the minimum.

Python 3.13.7, pytest 8.3.3. The initial sandbox test attempt had 34 passes and
one tmp_path setup permission error; its log is preserved as
[pytest-before-sandbox.txt](pytest-before-sandbox.txt). The same commands outside
the sandbox passed all 35 tests. No environment or pipeline setting was changed.

Fresh full evaluation: 10/12, exactly matching M3's after measurement apart from
the timestamp; [comparison](compare-m3.txt), [JSON](before.json),
[tests](pytest-before.txt), [hash manifest](before-manifest.json).
Eval SHA-256: `afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.

| ID | Expected | Actual before M5 | Failure type |
| --- | --- | --- | --- |
| E06 | Answer with current hb-03 rule, 3 days per week, without the superseded rule | Cites hb-03-chunk-0 (0.583333, 3 days) and hb-02-chunk-0 (0.454545, superseded, 2 days); eval PASS with precision 0.50 | Conflicting outdated evidence; official metric blind spot |
| E05 | Answer from hb-01 containing 5 business days | Cites onboarding hb-06-chunk-0 (0.250000) and annual leave hb-07-chunk-1 (0.111111); no correct document or fact; FAIL | Paraphrase retrieval failure |
| E11 | Refuse unsupported parental-leave question | Answers with annual leave hb-07-chunk-1 (0.222222) and hb-07-chunk-0 (0.160000); FAIL | Unsupported answer / failure to refuse |

CLI evidence: [E06](E06-before.txt), [E05](E05-before.txt), [E11](E11-before.txt).

Hypothesis: excluding superseded chunks before ranking removes E06's stale
rule without losing any of the ten passing questions. E05/E11 remain limitations.
Regression risk: historical questions lose access to superseded policies.
Only CURRENT_ONLY eligibility changes; scores, top-k, thresholds, corpus,
questions and metrics remain fixed. Verify the complete suite/eval and inspect
E06 plus E04/E05/E09/E10/E11 controls. Preserve M1/M3 measurements unchanged.
