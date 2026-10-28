#!/usr/bin/env python3
"""Ofrenda Keeper server: standard library only.
Serves web/index.html, GET /api/samples, GET /api/status and POST /api/ofrenda.

LLM_BACKEND = none       the remembrance is written by plain code from your facts (default)
              ollama     local open-weight model through Ollama (private, offline)
              backboard  hosted model through Backboard (needs BACKBOARD_API_KEY)
DEMO_MODE   = 1          public demo: only the built-in MADE-UP people are accepted, so nobody's
                         real memories can reach a hosted model.

Privacy rule: with LLM_BACKEND=backboard, a user's own text is refused unless the request says
allow_hosted=true. Nothing is stored on the server.
"""
import hashlib, json, os, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ofrenda, remember  # noqa: E402

INDEX = os.path.join(os.path.dirname(HERE), "web", "index.html")
SAMPLES_DIR = os.path.join(HERE, "samples")
SAMPLES = {  # id -> (file, label)
    "rosa": ("fake_abuela.json", "Abuela Rosa (made-up person)"),
    "kwame": ("fake_kwame.json", "Grandpa Kwame (made-up person)"),
}
BACKEND = os.environ.get("LLM_BACKEND", "none").lower()
DEMO_MODE = os.environ.get("DEMO_MODE", "0") == "1"
MAX_CALLS_PER_HOUR = int(os.environ.get("MODEL_MAX_PER_HOUR", "60"))
CACHE_MAX = 200

_LOCK = threading.Lock()
_CALLS = []   # timestamps of hosted-model calls in the last hour
_CACHE = {}   # (backend, sha256 of prompt) -> model text


class LimitReached(RuntimeError):
    """The hourly cap on hosted-model calls was reached."""


def _allow_call():
    now = time.time()
    with _LOCK:
        while _CALLS and now - _CALLS[0] > 3600:
            _CALLS.pop(0)
        if len(_CALLS) >= MAX_CALLS_PER_HOUR:
            return False
        _CALLS.append(now)
        return True


def _backend_module():
    if BACKEND == "ollama":
        import llm_ollama
        return llm_ollama
    if BACKEND == "backboard":
        import llm_backboard
        return llm_backboard
    raise RuntimeError("no model backend")


def _label():
    mod = _backend_module()
    if BACKEND == "ollama":
        return "open model on this computer (%s)" % mod.MODEL
    return "hosted model via Backboard (%s)" % mod.MODEL


def complete(system, user):
    """One model call, with an in-memory cache so the same text never costs twice."""
    key = (BACKEND, hashlib.sha256((system + "\x00" + user).encode("utf-8")).hexdigest())
    with _LOCK:
        if key in _CACHE:
            return _CACHE[key]
    if BACKEND == "backboard" and not _allow_call():
        raise LimitReached("hourly model limit reached")
    text = _backend_module().complete(system, user)
    with _LOCK:
        if len(_CACHE) >= CACHE_MAX:
            _CACHE.clear()
        _CACHE[key] = text
    return text


def write_remembrance(person):
    """Return (text, label). The app keeps working if the model fails or is rejected."""
    plain = ofrenda.fallback_text(person)
    if BACKEND not in ("ollama", "backboard"):
        return plain, "written by plain code from your words (no model)"
    try:
        res = remember.remember(person, complete)
    except LimitReached:
        return plain, "written by plain code (hourly model limit reached)"
    except Exception as e:
        print("model error: %s: %s" % (type(e).__name__, e), file=sys.stderr, flush=True)
        return plain, "written by plain code (model unavailable: %s)" % type(e).__name__
    if res["status"] != "ok":
        return plain, "written by plain code (the guard rejected the model text)"
    return res["text"], "written by the " + _label() + ", checked by the guard"


def load_sample(sample_id):
    if sample_id not in SAMPLES:
        raise ValueError("Unknown sample person.")
    with open(os.path.join(SAMPLES_DIR, SAMPLES[sample_id][0]), encoding="utf-8") as f:
        return json.load(f)


def build_response(req):
    sample = req.get("sample")
    if sample:
        data = load_sample(str(sample))
    else:
        if DEMO_MODE:
            raise PermissionError("This public demo only accepts the built-in made-up people. "
                                  "Run Ofrenda Keeper on your own computer to remember someone real.")
        if BACKEND == "backboard" and not req.get("allow_hosted"):
            raise PermissionError("A hosted model is configured, so your words would be sent to a third party. "
                                  "Tick the box that allows it, or use a local model (LLM_BACKEND=ollama).")
        data = req
    person = ofrenda.clean(data)
    text, label = write_remembrance(person)
    return {"ofrenda": ofrenda.layout(person), "remembrance": text, "written_by": label,
            "privacy": {"backend": BACKEND, "hosted": BACKEND == "backboard"}}


def status_info():
    """Safe diagnostics: never includes the API key or anyone's words."""
    info = {"backend": BACKEND, "demo_mode": DEMO_MODE, "hourly_model_limit": MAX_CALLS_PER_HOUR}
    if BACKEND == "backboard":
        import llm_backboard
        info.update(provider=llm_backboard.PROVIDER, model=llm_backboard.MODEL,
                    key_set=bool(os.environ.get("BACKBOARD_API_KEY")))
    elif BACKEND == "ollama":
        import llm_ollama
        info.update(model=llm_ollama.MODEL)
    return info


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/healthz":
            return self._send(200, {"ok": True})
        if self.path == "/api/status":
            return self._send(200, status_info())
        if self.path == "/api/samples":
            return self._send(200, [{"id": k, "label": v[1]} for k, v in SAMPLES.items()])
        if self.path in ("/", "/index.html"):
            with open(INDEX, "rb") as f:
                return self._send(200, f.read(), "text/html; charset=utf-8")
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/ofrenda":
            return self._send(404, {"error": "not found"})
        n = int(self.headers.get("Content-Length") or 0)
        if n > 200_000:
            return self._send(413, {"error": "request too large"})
        try:
            req = json.loads(self.rfile.read(n) or b"{}")
            if not isinstance(req, dict):
                raise ValueError("Send a JSON object.")
            self._send(200, build_response(req))
        except PermissionError as e:
            self._send(403, {"error": str(e)})
        except (ValueError, TypeError, AttributeError) as e:
            self._send(400, {"error": str(e)})

    def log_message(self, fmt, *args):  # never log request bodies; keep the console quiet
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print("Ofrenda Keeper on http://localhost:%d  (LLM_BACKEND=%s, DEMO_MODE=%s)" % (port, BACKEND, DEMO_MODE), flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
