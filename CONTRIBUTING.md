# Contributing

Keep the project easy to explain and run during a college practical.

1. Set up Python 3.12 and install requirements.txt.
2. Make focused changes without adding unrelated frameworks.
3. Run `python -m unittest -v test_assistant` for offline checks.
4. For changes affecting retrieval, prompts or embeddings, run `python evaluate.py` with your own local key and the actual supplied manual. Inspect every answer and source page.
5. Update README and TEST_RESULTS.md only with checks that were actually executed.

Policy answers must come from retrieved document passages. Do not hardcode the five assignment answers or use general knowledge as company-policy evidence. Unsupported answers must remain exactly `Not found`; API errors must remain errors.

Never commit `.env`, credentials, the private environment or generated vector databases. Do not fabricate screenshots, policy references or test results. Use fictional fixtures only in clearly labelled offline tests.
