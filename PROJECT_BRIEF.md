# Week 4 Project Brief: "Ghost in the Machine" (Hacktoberfest 2026)

Status: PLAN, nothing built yet. Any AI agent can continue from this file.

## 1. Challenge facts (from the DEV hub page; Week 4 page itself not readable here)
- Window: Oct 26 to Oct 31, winners the week of Nov 2. Exact deadline time and time zone NOT verified: read the Week 4 page.
- Theme: spooky, or honouring the past (Dia de los Muertos), built with open-weight models or open-source AI at the core.
- Rules on the hub: one submission per challenge, a NEW project started inside the window, no pull requests to existing projects. So this must NOT be a Week 1-3 project renamed.
- Judging (hub): Writing Quality (weighted most), Relevance to Theme, Creativity, Technical Execution, Use of Partner Technology (optional).
- Tags in the template: devchallenge, hf26challenge.
- Template sections: What I Built, Demo, Code, How I Built It, Why Does Open Innovation Matter, My Agent Session (optional), The Spirit of It (optional), Prize Categories.
- Partner prizes (general list, Week 4 may differ): Render, Gemma, Tinker, Backboard. Claim only what is really used. Tinker is not used by us.

## 2. The idea: Ofrenda Keeper
A private, offline tool that helps you build a remembrance (an ofrenda page) for someone you miss. You type or paste what you really know: name, favourite foods, songs, sayings, a few stories. It makes a printable ofrenda card and a short remembrance text.

The honest-by-design rule (same family as Weeks 1-3): **you supply the facts, code lays out the ofrenda, the model only phrases a short remembrance from YOUR facts, a guard rejects any invented memory.** A tool about the dead must never make up things about them. That is the whole point of the post.

Why it fits the theme: honours the past, Dia de los Muertos, family stories kept safe.
Why open matters: runs on a laptop with no internet via Ollama, family stories never leave the machine, nothing stored, works even if a service disappears.

## 3. MVP (build in this order)
1. Form: name, relationship, years (optional), foods, songs, sayings, stories (each a list), optional photo caption.
2. Code builds the ofrenda layout: candles, marigold border, items grouped by type, all text copied from the user's input.
3. Model writes a 4 to 6 sentence remembrance using only the input facts (Ollama qwen2.5:1.5b local; Backboard hosted for the public demo only).
4. Guard: reject text with names, numbers, places, foods, songs or dates not in the input; fall back to a template remembrance written by code. App always works with no model.
5. Print and Copy; "Download as one HTML file" so it outlives the app.
6. Public demo (DEMO_MODE=1): only built-in FAKE people (made-up names). Real memories are never accepted on the hosted site.
7. Tests (unittest), README, DEV post draft, render.yaml, .env.example, zip.

## 4. Architecture
Python standard library only: api/server.py, api/ofrenda.py (layout from facts), api/guard.py, api/remember.py (prompt + chunk), api/llm_ollama.py and llm_backboard.py (reuse patterns), web/index.html, api/samples/*.json (fake), tests/.

## 5. Prize categories (honest)
- Render: yes if deployed there.
- Backboard: only if the hosted remembrance really ran on the demo (check the status line).
- Gemma: only if we actually run a Gemma model; optional swap test with `ollama pull gemma3:1b` if the user wants it.
- Tinker: no.

## 6. First user / Spirit of It
Writing quality is weighted most, so the post matters as much as the code. A real person making an ofrenda for someone they miss would be the best "Spirit of It" section. Needs the user's own permission and words; never invent a story or a person. If none, drop that section.

## 7. Rules (standing)
No invented claims or feedback. Keys only in Render env or shell `export`, never in chat or files. `.env` is not read by the app. Fake data only in the public demo.

## 8. Day plan (deadline Oct 31, verify)
Oct 26-27 build core and tests. Oct 28 UI, Ollama and Backboard checks, deploy. Oct 29 first user, screenshots. Oct 30 post, final test. Oct 31 buffer, submit early.

## 9. Open questions for the user
- Is the ofrenda idea OK, or do they want a spooky one (haunted terminal)?
- Do they have someone to remember or a first user willing to try it?
