#!/bin/zsh
cd -- "${0:A:h}" || exit 1
if [[ ! -x .venv/bin/python ]]; then
  echo 'Please follow the setup instructions in README.md first.'
  read 'reply?Press Return to close.'
  exit 1
fi
.venv/bin/python web_app.py --open
read 'reply?Press Return to close.'
