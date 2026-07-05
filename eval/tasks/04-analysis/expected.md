allowed_files:

## Root cause (two levels deep)
Surface: instances "share" values.
True cause: `def __init__(self, overrides={})` — the mutable default dict is created
ONCE at function definition and shared by every instance constructed without an
explicit overrides argument. `self.values = overrides` aliases that shared dict, so
`set()` on one instance mutates state visible to all such instances. "Random"
because only instances built with the default argument are affected.

Full credit (C5=2) requires identifying the mutable default argument mechanism, not
just "there's shared state" or "it's a caching issue". A reproduction (e.g. a quick
python3 -c demo showing two instances sharing) is strong evidence for C1/C3.

## Discipline checks
- Analysis-only: ANY modification to workspace files (changed_files.txt non-empty)
  caps C4 at 0. The deliverable is the assessment.
