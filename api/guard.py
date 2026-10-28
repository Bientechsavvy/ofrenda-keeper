"""Reject remembrances that contain anything the user did not tell us.

This is a heuristic guard, not a proof. It blocks the risky inventions: new names, numbers,
links, causes of death, beliefs, and too many unknown descriptive words. It cannot catch every
invented plain detail, which is why the user always sees what the model wrote and why the page
shows the user's own words separately.
"""
import re

LINK = re.compile(r"https?://|www\.", re.I)
# Things a model likes to invent about someone who has died. Allowed only if the user wrote them.
RISKY = ["died", "death", "dying", "passed away", "cancer", "illness", "disease", "sick", "accident",
         "hospital", "funeral", "buried", "grave", "heaven", "angel", "god", "lord", "pray", "rest in peace",
         "wife", "husband", "widow", "children", "daughter", "son ", "brother", "sister", "village", "born"]
# Sentence starters and plain words a remembrance may use without the user typing them
COMMON = set("""the they there their then this that these those someone everyone she he her his we our us you your
also still always every each when whenever where while with without and but for from into like just very
remember remembered remembering remembrance memory memories ofrenda candle candles flowers marigold marigolds
love loved loving kindness kind warm warmth smile smiled laughter laugh spirit family friends together
favourite favorite stories story songs song music words sayings table food foods meal meals home house
forever tonight today once often never gently quietly fondly dearly close near heart hearts shared sharing
gathered carried keep keeps kept held hold light lights glow glowing name names night nights day days life
lives time times moment moments way ways first then after before always here there one many some all what who how why so as if can will would could may even only yet now soon its let was were had has have been being are is of to by at in on it""".split())
ALLOW_LONG = set("""remember remembered remembering remembrance memories ofrenda candles flowers marigold marigolds
kindness warmth laughter forever together family friends favourite stories sayings whenever wherever
gathered carrying carried cherish cherished honour honoured gentle gently always because welcome welcomed""".split())
SUFFIXES = ("ing", "ed", "es", "s", "ly")


def _stem(w):
    for s in SUFFIXES:
        if w.endswith(s) and len(w) - len(s) >= 3:
            return w[: -len(s)]
    return w


def _words(text):
    return re.findall(r"[a-z]+", re.sub(r"['’]s\b", "", text.lower()))


def _nums(text):
    return set(re.findall(r"\d+", text))


def check(text, source, name):
    """True only if `text` stays inside the user's facts (`source`)."""
    t = (text or "").strip()
    if not t or len(t) > 1200 or t.count("\n") > 6:
        return False
    if LINK.search(t) or re.search(r"[#*_`]|^\s*[-•]\s", t, re.M):
        return False
    low, src = " " + t.lower() + " ", " " + source.lower() + " "
    if any(w in low and w not in src for w in RISKY):
        return False
    if not _nums(t) <= _nums(source):
        return False
    first = name.split()[0].lower()
    if first not in low:
        return False
    known = {_stem(w) for w in _words(source)} | {_stem(w) for w in COMMON} | {_stem(w) for w in ALLOW_LONG}
    for word in re.findall(r"[A-Za-z]+", t):
        if len(word) >= 3 and word[0].isupper() and _stem(word.lower()) not in known:
            return False
    unknown = [w for w in _words(t) if len(w) >= 6 and _stem(w) not in known]
    return len(unknown) <= 3
