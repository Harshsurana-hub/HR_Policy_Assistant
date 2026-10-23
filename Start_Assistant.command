#!/bin/zsh
cd -- "${0:A:h}" || exit 1
if [[ ! -x .venv/bin/python ]]; then
  echo 'Please follow the setup instructions in README.md first.'
  read 'reply?Press Return to close.'
  exit 1
fi
if [[ ! -f chroma_db/manifest.json ]]; then
  echo 'Building the HR manual database. This can take several minutes.'
  .venv/bin/python ingest.py || { read 'reply?Press Return to close.'; exit 1; }
fi
.venv/bin/python main.py
read 'reply?Press Return to close.'
