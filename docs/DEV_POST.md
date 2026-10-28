---
title: Ofrenda Keeper: a machine that may only speak with the words you give it
published: false
tags: devchallenge, hf26challenge
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26)*

## What I Built

The scariest thing an AI can do on Día de los Muertos is invent a memory of someone who has died.

Ofrenda Keeper is a private place to build an ofrenda page for someone you miss. You type what you really know: their name, favourite foods, songs, sayings, a story, one thing you want to say. It lays out a page with candles and a marigold border, and writes a short remembrance.

My reading of "Ghost in the Machine": the ghost is the model, and the rule is that it may only speak with the words you gave it.

- **Code builds the page.** Every food, song, saying and story on it is copied from what you typed.
- **A model may phrase one short remembrance** from those facts only.
- **A guard checks it.** If the text adds a number, a link, a name, a cause of death, a spouse, a belief or too many unknown descriptive words, it is thrown away and the app writes a plain-code remembrance from your facts. The app works with no model at all.

## Demo

Live demo (made-up people only): https://[YOUR-RENDER-NAME].onrender.com/

The public demo refuses real memories on purpose, so nobody's words reach a hosted model. It may take about a minute to wake up. Pick **Grandpa Kwame** or **Abuela Rosa** (both invented) and see the ofrenda.

## Code

{% embed https://github.com/[YOUR-GITHUB-NAME]/ofrenda-keeper %}

Python standard library only, MIT license, 31 tests.

## How I Built It

- **Ofrenda builder (no AI):** validates the form, caps list sizes, and lays out the page. A **Download as one file** button saves the ofrenda as a single .html file that needs no server.
- **Remembrance:** a small prompt gives the model only your facts and tells it not to add places, dates, ages, family, hobbies, beliefs or causes of death. If the first answer fails the guard, it tries once more with a shorter prompt.
- **Guard:** compares the model text with everything you typed. It is a heuristic, not a proof, and I say so in the README: it can miss a small plain invented detail. That is why the page shows your own words separately and states who wrote the remembrance.
- **Models:** locally, Ollama with [qwen2.5:1.5b / YOUR MODEL]. The public demo uses a hosted open-model route through Backboard ([moonshotai/kimi-k2.6, CONFIRM IT IS OPEN-WEIGHT BEFORE SAYING SO]).
- **Hosting:** Render, with the key set only in Render's environment settings.

**What happened when I ran the local model:** [PASTE THE OUTPUT OF `py tools/check_ollama.py` AND SAY HONESTLY IF THE GUARD REJECTED IT]

## Why Does Open Innovation Matter?

A remembrance is the most private text I can imagine. With an open-weight model running through Ollama, a family can write about a grandmother on their own laptop with the internet off, and nothing is sent anywhere or stored. A closed API would need those words to leave the house. Open code also means the guard can be read and argued with, and the download button means the ofrenda is not locked inside a service that might disappear.

## My Agent Session

[OPTIONAL: ADD YOUR DEVRELAY LINK, OR DELETE THIS SECTION]

## The Spirit of It

[ONLY IF TRUE: ADD A REAL PERSON'S OWN WORDS, WITH THEIR PERMISSION. OTHERWISE DELETE THIS SECTION. Do not invent anyone.]

## Prize Categories

- Best Use of Render (the demo is deployed there)
- Best Use of Backboard ([ONLY IF A HOSTED REMEMBRANCE REALLY RAN ON THE DEMO])
- Best Use of Gemma ([ONLY IF YOU REALLY RAN A GEMMA MODEL, e.g. OLLAMA_MODEL=gemma3:1b])

<!-- Thanks for participating! -->
