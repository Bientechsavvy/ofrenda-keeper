"""Local open-weight model through Ollama. Standard library only.
The chat text is sent only to Ollama on this computer (http://localhost:11434)."""
import json, os, urllib.request

URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")
TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "300"))


def complete(system, user):
    body = json.dumps({"model": MODEL, "stream": False, "options": {"temperature": 0.2},
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.load(r)["message"]["content"].strip()
