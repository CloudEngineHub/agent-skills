# Audited secret replacement

This Python/SQLite project has no dependencies beyond the standard library.

Run the full suite with `python3 -m unittest`.

`replace_secret` must persist a replacement and its matching audit record
together. After a failed operation, reopening the database must show the old
value and no new audit record. A successful operation must persist both.
The `after_write` callback is a fault-injection boundary after the secret write
and before the audit write; keep it there when fixing the implementation.

The existing exception test passes. That is evidence for handled exceptions,
not for abrupt process termination. A subprocess can use `os._exit(23)` at the
callback boundary to terminate without running exception handlers or cleanup.
