# Plan: Validate and normalize inline citation groups

21 October 2026. Python, existing pytest and fixed runner, repository-root virtualenv.

1. Snapshot the current source/evidence hashes, run unchanged tests and preserve
   the current complete semantic offline baseline and saved E09 model decision.
2. Add focused parser tests before runtime edits: actual grouped E09 replay,
   repeated/multiple groups, all unknown/unselected/member and malformed cases.
3. In `src/generation.py`, validate every balanced bracket group against the
   already checked selected-source set. Split comma groups, strip formatting
   whitespace, reject empty/unknown/unselected members, deduplicate in order, and
   render each ID as its own bracket marker. Check unmatched/nested brackets too.
4. Keep single markers/no-marker answers supported, prose untouched and all
   existing JSON/schema/refusal rules. Do not change the prompt or retrieval.
5. Run tests, replay actual raw response, full semantic live evaluation, lexical
   control, unchanged offline control and E09 CLI. Save fresh traces and compare
   with unchanged tools; no score is inferred from the old interrupted baseline.
6. Inspect actual sources/answers and all remaining quality failures. Update the
   current README/handoff with the new result while retaining earlier experiments
   as historical evidence. Leave everything unstaged/uncommitted.

One generation-format compatibility fix, separately authorized after retrieval.
This does not change required homework boundaries or combine hybrid scoring.
All fixed evaluation/metric files and prior experiment artifacts retain hashes.
Use the existing rate-limited evidence runner with a fresh output destination;
2.1-second spacing covers all hosted attempts, including retries/fallback.

No additional research agents are needed: this is a local parser contract fix.
