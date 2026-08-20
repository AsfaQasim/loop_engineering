# A4 LESSON: Secrets & Environment Test

## Takeaway
RUN 1 failed because the script only reads `DUMMY_API_TOKEN` from environment variables (via `os.environ`), not from `.env` files. In cloud/CI environments, `.env` files are gitignored and not present, so secrets must be provided as environment variables through configuration panels or pipeline settings. RUN 2 succeeded because the environment variable was explicitly set in the execution environment.

## Mechanical Reason
- `test_env.py` uses `os.environ.get('DUMMY_API_TOKEN')` which queries the process's environment block.
- `.env` files are not automatically loaded by Python; they require explicit parsing (e.g., `python-dotenv`).
- Cloud environments (GitHub Actions, etc.) do not include gitignored files, so `.env` is absent.
- Therefore, RUN 1 fails unless the environment variable is set externally; RUN 2 succeeds because we set it via `DUMMY_API_TOKEN=secret_12345` in the shell.