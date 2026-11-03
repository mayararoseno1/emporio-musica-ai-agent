# Validation and delivery report

## Actual local verification

Performed on 2026-11-02 (America/Fortaleza), using Python 3.12 in the project `.venv`.

| Check | Observed result |
| --- | --- |
| `python -m pytest -q` | **30 passed in 17.33s** |
| `python -m pip check` | No broken requirements found |
| `python -m compileall -q src scripts main.py` | Success |
| `python main.py --check-data` | All CSVs and policy PDF loaded and validated |
| `python -m scripts.examples` | Five illustrative conversations saved with executed tool evidence |
| `python main.py` without key | Exit 2 with clear configuration instructions; no simulated LLM answer |
| SDK contract | Installed OpenAI SDK exercised over in-memory HTTP transport, including tool output serialization |
| Secret-pattern scan | 22 source/document/config files scanned, 0 matching API-key/private-key patterns; excludes original data, virtualenv and Git internals |
| `git diff --check` | No whitespace errors |

The secret scan is a limited pattern check, not a guarantee against every kind of sensitive information. Original datasets and internal PDF are excluded from Git. Neither `.env` nor credentials are committed.

## Test coverage and interpretation

Tests cover existing/missing products, price filtering and ordering, all products' availability, authorized/unauthorized/missing orders, missing tracking, policy retrieval with exceptions, active promotion/PIX calculations, invalid and injected tool arguments, unknown tools, isolated tool failures, provider failures, bounded loops, empty input and follow-up history. Corruption cases cover negative prices, orphan keys, missing columns, invalid JSON specs shape, absent PDF and invalid order status.

Off-topic, fabricated-price requests and user-claimed customer identities are used in mocked orchestration boundary tests. These show that system instructions stay separate and the model cannot supply a trusted identity. They do **not** prove that a real LLM will always decline off-topic requests, resist every injection or correctly select a tool. Those semantic behaviors are specified in the prompt but require live evaluation.

## Deliverable checklist

| Requirement | Status |
| --- | --- |
| Python implementation and working local CLI | Implemented; data path tested; model path SDK-tested with mock HTTP |
| Read original brief and all supplied data | Completed before feature implementation |
| Catalog, stock, prices and promotions | Implemented and tested against supplied records |
| Policy/store information retrieval | Implemented and tested against original eight-page PDF |
| Order information with data minimization | Implemented and tested, trusted operator demo context only |
| Conversational history | Implemented and mock-tested with follow-up |
| Scope/persona/error/injection instructions | Implemented; deterministic boundaries tested; live semantics unverified |
| Automated tests | 30 passing |
| README in English and Portuguese customer service | Included |
| Between 3 and 5 conversations | Five clearly labeled illustrative conversations plus real tool evidence; real LLM transcripts pending |
| Real incremental Git history | Local analysis, implementation and validation/documentation milestones |
| Public GitHub repository | **Pending explicit publication authorization** |
| Recruiting submission/email | **Not performed**; deadline has not been obtained |
| Live LLM end-to-end run | **Pending API key and provider model access** |
| Human review | Not claimed; recommended before submission |

## Run locally now

```powershell
.\.venv\Scripts\python.exe main.py --check-data
.\.venv\Scripts\python.exe -m pytest -q
```

For actual conversations, copy `.env.example` to `.env`, configure `OPENAI_API_KEY` and run `main.py`. Then run `python -m scripts.examples --live` to obtain five real transcripts. Do not publish API keys, customer data or the internal manual. Follow README steps to recreate the environment on another machine, including obtaining the original challenge data.

## Outstanding work

The local implementation and available offline checks are complete. A fully verified recruitment delivery is **not** claimed: real model behavior, actual LLM transcripts, human review, public hosting and the recruiter submission remain outstanding. No live API costs were incurred. No repository was published, no email was sent and no store state was changed.
