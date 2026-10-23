# Executed verification — 23 October 2026

Final model: gemini-3.5-flash-lite. Python 3.12.14; direct dependency versions pinned in requirements.txt.

| Check | Actual result |
|---|---|
| Syntax and imports | Passed |
| Missing PDF, database and API key | Expected understandable errors observed |
| Actual PDF loading | 79 pages, all readable |
| Chunking and metadata | 280 chunks, page metadata retained |
| Gemini embeddings | Completed |
| Persistent ChromaDB | All 280 chunks stored |
| Reopen in separate process | Passed, without re-ingestion |
| Privilege Leave | 12 days, page 60 |
| Probation | 3 months, page 42 |
| Insurance premium | Exact Not found |
| GST rate | Exact Not found |
| Maternity | Source-stated 90 days with conversion inconsistency noted, page 62 |
| Unsupported Mars-travel question | Exact Not found |
| CLI blank question and exit | Blank skipped; Goodbye displayed |

Actual generated responses: data/evaluation.json. All six final results were checked against their expected document outcome. Manual section names and eligibility details were also reviewed directly. Earlier failed runs exposed PDF word-break issues; the final run uses cleaned context and boolean support validation. The initial gemini-2.5-flash quota was exhausted; Google's API recommended the current Flash-Lite generation, which completed the final tests.

Browser screenshots of the saved actual application-output reports are included in screenshots/ and embedded in README. They are explicitly labelled as recorded-result reports, not live terminal captures.
