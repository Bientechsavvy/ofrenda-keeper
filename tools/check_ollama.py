"""Check that Ollama is running and writes a remembrance that passes the guard (made-up person).
Usage: python tools/check_ollama.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api"))
import llm_ollama, ofrenda, remember, server  # noqa: E402

person = ofrenda.clean(server.load_sample("rosa"))
try:
    res = remember.remember(person, llm_ollama.complete)
except Exception as e:
    print("Ollama failed: %s: %s" % (type(e).__name__, e)); sys.exit(1)
print("guard verdict:", res["status"], "(attempts: %d)" % res["attempts"])
print(res["text"] or "(rejected: the app would show the plain-code remembrance)")
