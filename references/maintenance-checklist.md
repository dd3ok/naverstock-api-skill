# Maintenance Checklist

Use this checklist when changing endpoints, scripts, safety rules, or vendor-facing skill metadata.

1. Read [../SKILL.md](../SKILL.md) and [safety-rules.md](safety-rules.md) before changing behavior.
2. Confirm endpoint scope and status in [api-catalog.md](api-catalog.md).
3. For new or changed endpoints, follow [capture-workflow.md](capture-workflow.md) and keep only unauthenticated, low-volume, read-only calls.
4. Update script-backed tests in [../tests/test_cli_contracts.py](../tests/test_cli_contracts.py) when a CLI command, endpoint path, query string, method, or request body changes.
5. Run the local checks:

   ```bash
   python -B -m unittest tests.test_cli_contracts -v
   python -m compileall scripts
   for file in scripts/*.py; do python "$file" --help >/dev/null; done
   git diff --check
   ```

6. Use only 1-2 low-volume unauthenticated live smoke requests when live verification is necessary.
7. Update [eval-prompts.md](eval-prompts.md) when scope, trigger behavior, refusal behavior, or safety boundaries change.
8. Update README examples and the repository structure table when files, commands, install paths, or validation notes change.
9. After merging user-facing script, endpoint, or skill metadata changes to `main`, consider tagging a release and writing concise release notes.
