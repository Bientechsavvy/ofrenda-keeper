# Ofrenda Keeper

A private, offline place to build an ofrenda page and a short remembrance for someone you miss.

**You give the words. Code lays out the page. An open-weight model may phrase a short remembrance from your words only. A guard throws away anything it invents.**

A tool about someone who has died must never make up memories about them. So the foods, songs, sayings, stories and note on the page are copied from what you typed. The remembrance is the only model-written part, and if the guard rejects it (or there is no model) the app writes a plain-code remembrance from the same facts.

## Features
- Form: name, relationship, years, foods, songs, sayings, stories, and one thing you want to say.
- A printable ofrenda page with candles and a marigold border.
- Copy as text, Print, and **Download as one file**: a single .html file that works with no server and no internet, so the ofrenda outlives this app.
- Two MADE-UP sample people. No real person is included.

## How the guard works (and its limits)
It rejects model text that adds a number, a link, a capitalised name, markdown, the person's name missing, risky inventions (cause of death, religion, spouse, children, birthplace) the user did not write, or more than 3 unknown descriptive words. It is a heuristic, not a proof: it can miss a small plain invented detail. That is why the page shows your own words separately and says who wrote the remembrance.

## Privacy
- Nothing is stored. Everything is processed in memory.
- `LLM_BACKEND=ollama`: your words go only to Ollama on your computer.
- `LLM_BACKEND=backboard`: your words go to a third party, so the app refuses unless you tick the consent box.
- `DEMO_MODE=1` (the public demo): only the made-up people are accepted.

## Run it (Windows Git Bash)
```
py tests/test_all.py
export LLM_BACKEND=none
py api/server.py
```
Open http://localhost:8000. With a local model (install Ollama, then `ollama pull qwen2.5:1.5b`):
```
py tools/check_ollama.py
export LLM_BACKEND=ollama
py api/server.py
```
To try another open model, for example `export OLLAMA_MODEL=gemma3:1b` after `ollama pull gemma3:1b`. Check `/api/status` for the setup (it never shows a key).

## Deploy on Render
New > Web Service > Public Git Repository. Build: `echo no build step`. Start: `python api/server.py`. Environment tab: `DEMO_MODE=1`, `LLM_BACKEND=backboard`, `BACKBOARD_API_KEY` (secret), `BACKBOARD_PROVIDER`, `BACKBOARD_MODEL`, `MODEL_MAX_PER_HOUR=60`. Check `/healthz` and `/api/status`.

## Limits
- Small local models often write stiff or rejected text; the plain-code remembrance is then shown.
- English only for the guard's risky-word list.
- Tested with made-up people only.

MIT license.
