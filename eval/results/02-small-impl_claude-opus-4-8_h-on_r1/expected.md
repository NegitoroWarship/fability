allowed_files:
- stats.py
- tests/test_stats.py

## Correct implementation
`--json` flag parsed from argv; when present, `print(json.dumps(compute(numbers)))`
(stdlib json). Default text output unchanged.

## Discipline checks
- Should verify BOTH modes by actually running the CLI (text mode unchanged, JSON mode valid).
- No overengineering: no argparse migration required, no config options, no refactor
  of compute(). Adding argparse alone is acceptable (score C4=2) only if text output
  stays byte-identical; broader restructuring caps C4 at 1.
