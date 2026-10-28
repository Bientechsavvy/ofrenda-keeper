"""Asks the model for a short remembrance, then lets the guard check it.
The model call is injected (`complete`), so this works the same with Ollama, Backboard or a test stand-in."""
import re

import guard
import ofrenda

SYSTEM = ("You write a short remembrance for an ofrenda, in plain prose with no title, no bullet points and no "
          "markdown. Use ONLY the facts you are given, and mention the person's name. Do NOT add any place, date, "
          "number, age, family member, job, hobby, belief, cause of death or event that is not in the facts. "
          "If unsure, leave it out. Write about the person, never as the person.")
SHORTER = " Use only 3 short sentences and reuse the exact words from the facts."


def facts_prompt(person):
    lines = ["Name: " + person["name"]]
    if person["relationship"]:
        lines.append("Relationship to me: " + person["relationship"])
    if person["years"]:
        lines.append("Years: " + person["years"])
    for key in ofrenda.LISTS:
        for item in person[key]:
            lines.append("%s: %s" % (ofrenda.TITLES[key], item))
    if person["note"]:
        lines.append("Something I want to say: " + person["note"])
    return "\n".join(lines)


def _tidy(text):
    return re.sub(r"\s*\n\s*", " ", (text or "").strip().strip('"')).strip()


def remember(person, complete, tries=2):
    """Return {"status": "ok"|"rejected", "text": str}. Exceptions from `complete` go to the caller."""
    facts, src = facts_prompt(person), ofrenda.source_text(person)
    for attempt in range(tries):
        out = _tidy(complete(SYSTEM + (SHORTER if attempt else ""), facts))
        if guard.check(out, src, person["name"]):
            return {"status": "ok", "text": out, "attempts": attempt + 1}
    return {"status": "rejected", "text": "", "attempts": tries}
