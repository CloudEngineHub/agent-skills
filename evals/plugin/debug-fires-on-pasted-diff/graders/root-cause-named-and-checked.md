---
type: llm
---

PASS if all three hold. (1) The reply names the cause precisely: the slice end index `start + size - 1` stops one row short, so every page returns size minus one rows. (2) The fix is minimal: the end index becomes `start + size`, and nothing else in the diff is changed as part of the fix (a suggestion to page in SQL is fine only if it is marked as a separate improvement, not the fix). (3) The reply says how to confirm the cause before or after the change: re-run the failing test, or add a test that asserts a full page of rows and the last page's boundary.

FAIL if the reply guesses at other causes (the ORDER BY, the query, page numbering) without settling on the slice bound, or rewrites the function beyond the one-token fix and presents that as the fix, or gives a fix with no way to confirm it.
