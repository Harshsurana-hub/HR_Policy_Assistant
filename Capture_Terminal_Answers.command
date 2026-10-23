#!/bin/zsh
cd -- "${0:A:h}" || exit 1
.venv/bin/python - <<'PY'
from main import load, ask
from evaluate import QUESTIONS

try:
    store, model = load()
    for number, question in enumerate(QUESTIONS[:5], 1):
        print('\033[2J\033[H', end='', flush=True)
        print('=' * 62)
        print('                 HR POLICY ASSISTANT')
        print('=' * 62)
        print(f'\nQuestion {number} of 5: {question}\n', flush=True)
        try:
            print(ask(question, store, model), flush=True)
        except Exception:
            print('API request failed. Check Gemini quota and connection; retry later.')
            break
        # Read directly from the terminal because Python source uses stdin.
        print('\nCapture this Terminal window with Shift-Command-4, then Space.')
        print('Click the Terminal window to save your screenshot to Desktop.')
        print('Press Return here when ready for the next question.', flush=True)
        with open('/dev/tty') as terminal_input:
            terminal_input.readline()
except KeyboardInterrupt:
    print('\nDemo stopped.')
except Exception:
    print('Unable to start. Check your local setup and Gemini connection.')
PY
read 'reply?Finished. Press Return to close.'
