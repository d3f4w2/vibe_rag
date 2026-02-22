# V1 Manual Acceptance Checklist (STEP-09)

## Scope
- Confirm V1 baseline acceptance behavior for CLI output, uncertainty handling, and failure-path diagnostics.
- This checklist complements automated tests and is required before closing STEP-09.

## Environment
- Working directory: `C:\Users\ljh\Desktop\rag`
- Conda env: `vibe-rag`
- Command prefix: `conda run -n vibe-rag`

## Manual Scenarios

### M1: Missing required stain input should fail fast
1. Run:
   `conda run -n vibe-rag python -m src.cli.main --top-k 5`
2. Expected:
   - Process exits with code `2`.
   - `stderr` contains `argument error`.
   - Error message references `--stain-text` or `--stain-file`.

### M2: Invalid UTF-8 stain file should be reported as argument error
1. Create a file with invalid UTF-8 bytes (PowerShell):
   `Set-Content -Path .\pytest_tmp_manual\manual_invalid_utf8.txt -Value ([byte[]](0xff,0xfe,0xfd)) -AsByteStream`
2. Run:
   `conda run -n vibe-rag python -m src.cli.main --stain-file .\pytest_tmp_manual\manual_invalid_utf8.txt --top-k 5`
3. Expected:
   - Process exits with code `2`.
   - `stderr` contains `argument error`.
   - Error message includes `UTF-8` and `--stain-file`.

### M3: Successful query should return structured JSON
1. Preconditions:
   - Embedding provider environment variables are configured.
   - Vector index is available for retrieval.
2. Run:
   `conda run -n vibe-rag python -m src.cli.main --stain-text "manual smoke query" --top-k 5`
3. Expected:
   - Process exits with code `0`.
   - `stdout` is valid JSON with keys:
     - `similar_cases`
     - `tendency`
     - `reason`
     - `disclaimer`
     - `meta`
   - `meta.top_k == 5`.

### M4: Runtime failure should return runtime exit code
1. Preconditions:
   - Force API timeout (for example, set a non-routable embedding endpoint).
2. Run:
   `conda run -n vibe-rag python -m src.cli.main --stain-text "timeout smoke query" --top-k 5`
3. Expected:
   - Process exits with code `1`.
   - `stderr` contains `runtime error`.

## Final Pass Criteria
- M1 and M2 must pass on any local machine.
- M3 and M4 pass when corresponding external preconditions are satisfied.
- Results align with automated baseline:
  `conda run -n vibe-rag python -m pytest -q --ignore pytest_tmp_manual --ignore .pytest_tmp --ignore .pytest_tmp_run_20260221`
