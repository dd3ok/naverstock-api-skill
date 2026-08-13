# Maintenance Checklist

Use this checklist when changing endpoints, scripts, safety rules, or vendor-facing skill metadata.

1. Read [../SKILL.md](../SKILL.md) and [safety-rules.md](safety-rules.md) before changing behavior.
2. Confirm common route/status rules in [api-catalog.md](api-catalog.md) and endpoint details in its linked domain catalog.
3. For new or changed endpoints, follow [capture-workflow.md](capture-workflow.md) and keep only unauthenticated, low-volume, read-only calls.
   For WiseReport or legacy HTML, also verify [external-sources.md](external-sources.md), exact host/path/query allowlists, response-size cap, redirect rejection, and current-API non-duplication.
   For WebSocket/SSE-looking code, distinguish a loaded client library from an observed public data connection. Never connect to or document session-issued personal/holding channels as public market data.
4. Update focused tests under `tests/`, including [../tests/test_cli_contracts.py](../tests/test_cli_contracts.py), when a CLI command, endpoint path, query string, method, request body, allowlist, or privacy filter changes. Add an HTTP/error-path test when changing failure handling; a mocked success response does not prove a live route still exists.
5. Run the local checks:

   ```bash
   python -B -m unittest discover -s tests -v
   python -m compileall -q scripts
   ruff check --isolated --select E4,E7,E9,F scripts tests
   for file in scripts/*.py; do python "$file" --help >/dev/null; done
   python /path/to/skill-creator/scripts/quick_validate.py .
   git diff --check
   ```

   PowerShell:

   ```powershell
   Get-ChildItem scripts -Filter *.py | ForEach-Object { python $_.FullName --help > $null }
   ```

6. Prefer current public page/chunk inspection for broad audits. Use only 1-2 low-volume unauthenticated live smoke requests per changed domain when live verification is necessary.
7. Update [eval-prompts.md](eval-prompts.md) when scope, trigger behavior, refusal behavior, or safety boundaries change. Every prompt or explicit prompt group must have a checkable pass/fail criterion.
8. Update README only when user-facing scope, examples, install paths, repository layout, or validation commands change.
9. Regenerate or verify `agents/openai.yaml`; `default_prompt` must explicitly include `$naverstock-web-api`.
10. Verify a lightweight installed copy containing only `SKILL.md`, `LICENSE`, `agents/`, `references/`, and `scripts/` can run representative `--help` commands.
11. Before `1.0.0`, require all of the following:

    - tests, Ruff, compile, all-script help, diff check, skill validator, and install-layout smoke pass;
    - public GET/read-only POST allowlists and private/personal/mutation denials have focused tests;
    - each `scripts/*.py` entry point is routed from `SKILL.md`, each script-backed endpoint is documented once in its domain catalog, command examples live in the cookbook, user-facing setup lives in README, and UI metadata matches the skill;
    - every `needs-recheck` endpoint stays non-script-backed, and external iframe pages such as KRX short selling are documented rather than disguised as `stock.naver.com` APIs;
    - a clean PR is reviewed and merged to `main` before creating the tag and release notes.

12. After the gate passes on merged `main`, tag `v1.0.0` and publish concise release notes. Do not raise the public version in advance of the merged, validated commit.
