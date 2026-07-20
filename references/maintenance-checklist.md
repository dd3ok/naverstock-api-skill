# Maintenance Checklist

Use this checklist when changing endpoints, scripts, safety rules, or vendor-facing skill metadata.

1. Read [../SKILL.md](../SKILL.md) and [safety-rules.md](safety-rules.md) before changing behavior.
2. Confirm endpoint scope and status in [api-catalog.md](api-catalog.md).
3. For new or changed endpoints, follow [capture-workflow.md](capture-workflow.md) and keep only unauthenticated, low-volume, read-only calls.
4. Update focused tests under `tests/`, including [../tests/test_cli_contracts.py](../tests/test_cli_contracts.py), when a CLI command, endpoint path, query string, method, request body, allowlist, or privacy filter changes. Add an HTTP/error-path test when changing failure handling; a mocked success response does not prove a live route still exists.
5. Run the local checks:

   ```bash
   python -B -m unittest discover -s tests -v
   python -m compileall -q scripts
   ruff check scripts tests
   for file in scripts/*.py; do python "$file" --help >/dev/null; done
   python /path/to/skill-creator/scripts/quick_validate.py .
   git diff --check
   ```

   PowerShell:

   ```powershell
   Get-ChildItem scripts -Filter *.py | ForEach-Object { python $_.FullName --help > $null }
   ```

6. Prefer current public page/chunk inspection for broad audits. Use only 1-2 low-volume unauthenticated live smoke requests per changed domain when live verification is necessary.
7. Update [eval-prompts.md](eval-prompts.md) when scope, trigger behavior, refusal behavior, or safety boundaries change.
8. Update README examples and the repository structure table when files, commands, install paths, or validation notes change.
9. Regenerate or verify `agents/openai.yaml`; `default_prompt` must explicitly include `$naverstock-web-api`.
10. Verify a lightweight installed copy containing only `SKILL.md`, `LICENSE`, `agents/`, `references/`, and `scripts/` can run representative `--help` commands.
11. Before `1.0.0`, require all of the following:

    - tests, Ruff, compile, all-script help, diff check, skill validator, and install-layout smoke pass;
    - public GET/read-only POST allowlists and private/personal/mutation denials have focused tests;
    - domestic, foreign, search, home, market-index, crypto, notice, research, and discussion routes are reflected in `SKILL.md`, the catalog, cookbook, README, and metadata;
    - every `needs-recheck` endpoint stays non-script-backed, and external iframe pages such as KRX short selling are documented rather than disguised as `stock.naver.com` APIs;
    - a clean PR is reviewed and merged to `main` before creating the tag and release notes.

12. After the gate passes on merged `main`, tag `v1.0.0` and publish concise release notes. Do not raise the public version in advance of the merged, validated commit.
