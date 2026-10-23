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

The current README uses genuine terminal captures and live UI previews. Earlier saved-results report images are historical assets and are not used as terminal evidence.

## Terminal evidence
The user supplied five genuine terminal screenshots from a subsequent run. All five show the expected policy outcomes; supported answers cite pages 60, 42 and 62. These screenshots are embedded in README and replace the earlier report illustrations.

## Browser UI verification
- Local backend ready: 79 pages, 280 persisted chunks.
- Live browser suggestion: PL answer 12 days, source page 60; citation links to /manual#page=60.
- Live browser input: GST returns exactly Not found; no supporting source card displayed.
- Conversation export: downloaded actual conversation as text.
- Desktop/source-panel layout reviewed at 1440×1000; compact layout reviewed at normal browser size.
- Mobile layout reviewed at 390×844: document width equals viewport width (390 px), no horizontal overflow. Mobile new-conversation reset clears the draft.
- HTTP validation: blank input 400, wrong content type 415, external origin 403, unknown path 404, /.env 404, PDF header and content type passed.
- Python compilation and launcher shell syntax passed.

## Offline regression suite
`python -m unittest -v test_assistant` executed successfully: 14 tests passed. They cover grounded-answer validation and HTTP contracts using fictional fixtures and mocked model responses, without Gemini API calls. They do not establish live retrieval quality or replace the recorded policy evaluation. The GitHub Actions workflow runs this same suite; its result is shown by the live badge rather than assumed.
