"""Builds the ofrenda page from what the user typed. No model is involved here.

Every word on the ofrenda (foods, songs, sayings, stories, note) is copied from the user's
own input. The fallback remembrance is also written by plain code from the same facts, so
the app works with no model at all.
"""
import re

MAX_ITEMS = 12
MAX_ITEM_CHARS = 240
MAX_STORY_CHARS = 700
LISTS = ("foods", "songs", "sayings", "stories")
TITLES = {
    "foods": "Their favourite foods",
    "songs": "Their songs and music",
    "sayings": "Words they used to say",
    "stories": "Stories we keep",
}


def _one_line(text, limit):
    return " ".join(str(text).split())[:limit]


def _items(value, limit):
    if isinstance(value, str):
        value = value.splitlines()
    if not isinstance(value, list):
        return []
    out = []
    for v in value:
        v = _one_line(v, limit).strip(" -•*")
        if v:
            out.append(v)
    return out[:MAX_ITEMS]


def clean(data):
    """Validate and tidy the form data. Raises ValueError with a message the user can read."""
    if not isinstance(data, dict):
        raise ValueError("Send the details as a JSON object.")
    name = _one_line(data.get("name") or "", 80)
    if not name:
        raise ValueError("Please type the name of the person you are remembering.")
    person = {
        "name": name,
        "relationship": _one_line(data.get("relationship") or "", 60),
        "years": _one_line(data.get("years") or "", 40),
        "note": _one_line(data.get("note") or "", 240),
    }
    for key in LISTS:
        person[key] = _items(data.get(key), MAX_STORY_CHARS if key == "stories" else MAX_ITEM_CHARS)
    if not any(person[k] for k in LISTS) and not person["note"]:
        raise ValueError("Add at least one food, song, saying, story or a note, so there is something to remember.")
    return person


def source_text(person):
    """Everything the user typed, as one string. The guard checks the model text against this."""
    parts = [person["name"], person["relationship"], person["years"], person["note"]]
    for key in LISTS:
        parts.extend(person[key])
    return "\n".join(p for p in parts if p)


def layout(person):
    """The ofrenda page as data: all text comes from the user's input."""
    sub = ", ".join(p for p in (person["relationship"], person["years"]) if p)
    sections = [{"key": k, "title": TITLES[k], "items": person[k]} for k in LISTS if person[k]]
    return {"title": "In memory of " + person["name"], "subtitle": sub, "sections": sections, "note": person["note"]}


def _join(items):
    items = [i.rstrip(".") for i in items]
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def fallback_text(person):
    """A remembrance written by plain code from the user's facts only."""
    name = person["name"]
    first = name.split()[0]
    lines = []
    if person["relationship"]:
        lines.append("We remember %s, our %s." % (name, re.sub(r"^(my|our)\s+", "", person["relationship"], flags=re.I).lower()))
    else:
        lines.append("We remember %s." % name)
    if person["sayings"]:
        lines.append("%s used to say: \"%s\"" % (first, person["sayings"][0].rstrip(".") + "."))
    if person["stories"]:
        lines.append("A story we keep: %s" % person["stories"][0].rstrip(".") + ".")
    elif person["foods"]:
        lines.append("We remember the %s." % person["foods"][0].lower().rstrip("."))
    if person["note"]:
        lines.append(person["note"].rstrip(".") + ".")
    return " ".join(lines)
