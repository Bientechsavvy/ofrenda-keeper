"""One tiny test call to check your Backboard key and model. Needs BACKBOARD_API_KEY exported.
Usage: python tools/check_backboard.py   (prints the reply or a clear error, never the key)"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api"))
import llm_backboard  # noqa: E402

try:
    print("Reply:", llm_backboard.complete("Reply with one short sentence.", "Say hello."))
except Exception as e:
    print("Failed: %s: %s" % (type(e).__name__, e))
    sys.exit(1)
