# Key-format compatibility test execution

Date: 2026-10-20. This is a record of the terminal execution during live setup;
the provider requests are recorded separately in the JSONL traces.

Before the fix, the new authorization-key regression case failed because the
validator rejected dots. One initial invalid-header case used a NUL character,
which the operating system itself disallows in environment variables; that case
was replaced with another control character that can reach application validation.

After correcting the validator and that test setup, the actual command was:

```powershell
.venv/Scripts/python.exe -m pytest
```

The terminal execution collected **134 items** and reported **134 passed in 0.40s**,
exit code 0. The suite includes seven added key-format/header-character cases.
All real Google transport is blocked by the unit-test fixture unless explicitly
mocked. These tests verify local contracts; the subsequent probe and complete
fixed evaluation establish the saved live behavior.
