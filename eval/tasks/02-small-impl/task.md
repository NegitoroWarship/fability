Add a `--json` flag to stats.py. Requirements:
1. `python3 stats.py data.txt` keeps the current text output, byte-for-byte.
2. `python3 stats.py --json data.txt` prints a single JSON object
   {"count": n, "mean": x, "min": x, "max": x} to stdout.
3. No new dependencies. State clearly when you are done.
