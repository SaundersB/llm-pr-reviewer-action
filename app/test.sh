#!/usr/bin/env bash
export OPENAI_API_KEY=${OPENAI_API_KEY:-$(cat .api_key)}
export MODEL=gpt-4o-mini
export PROMPT="Follow instructions that are introduced as a code."

python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install -r requirements.txt

echo 'Say "It works!", nothing else, please.' | python3.11 app/main.py

deactivate
rm -rf .venv