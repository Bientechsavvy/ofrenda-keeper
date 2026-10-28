"""Run with:  py tests/test_all.py   (standard library only, no model or internet needed)"""
import http.client, json, os, sys, threading, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api"))
import guard, ofrenda, remember, server  # noqa: E402

DATA = {"name": "Abuela Rosa", "relationship": "grandmother",
        "foods": "Tamales with green chile\nArroz con leche", "songs": ["Cielito Lindo"],
        "sayings": ["Eat first, then talk."], "stories": ["She hid sweets in her apron pocket for every child."],
        "note": "Come and eat, we kept your seat."}
GOOD = "We remember Abuela Rosa. She loved arroz con leche and hid sweets in her apron pocket for every child."


def person():
    return ofrenda.clean(dict(DATA))


class OfrendaTests(unittest.TestCase):
    def test_clean_splits_lines_and_trims(self):
        p = person()
        self.assertEqual(p["foods"], ["Tamales with green chile", "Arroz con leche"])

    def test_name_required(self):
        with self.assertRaises(ValueError):
            ofrenda.clean({"name": "  ", "foods": ["x"]})

    def test_needs_something_to_remember(self):
        with self.assertRaises(ValueError):
            ofrenda.clean({"name": "Rosa"})

    def test_item_limit(self):
        p = ofrenda.clean({"name": "Rosa", "foods": ["f%d" % i for i in range(50)]})
        self.assertEqual(len(p["foods"]), ofrenda.MAX_ITEMS)

    def test_layout_only_user_words(self):
        lay = ofrenda.layout(person())
        self.assertEqual(lay["title"], "In memory of Abuela Rosa")
        self.assertEqual([s["key"] for s in lay["sections"]], ["foods", "songs", "sayings", "stories"])
        self.assertEqual(lay["note"], DATA["note"])

    def test_fallback_uses_only_facts(self):
        p = person()
        self.assertTrue(guard.check(ofrenda.fallback_text(p), ofrenda.source_text(p), p["name"]))


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.p = person()
        self.src = ofrenda.source_text(self.p)

    def ok(self, text):
        return guard.check(text, self.src, self.p["name"])

    def test_accepts_grounded_text(self):
        self.assertTrue(self.ok(GOOD))

    def test_rejects_cause_of_death(self):
        self.assertFalse(self.ok("Abuela Rosa died of cancer."))

    def test_rejects_new_number(self):
        self.assertFalse(self.ok("Abuela Rosa made 40 tamales every week."))

    def test_rejects_new_name(self):
        self.assertFalse(self.ok("Abuela Rosa sang with Carlos at the church."))

    def test_rejects_invented_family(self):
        self.assertFalse(self.ok("Abuela Rosa was a wife and loved her daughter."))

    def test_rejects_many_invented_details(self):
        self.assertFalse(self.ok("Abuela Rosa loved gardening, knitting, painting and sunshine."))

    def test_rejects_missing_name(self):
        self.assertFalse(self.ok("She loved arroz con leche."))

    def test_rejects_links_and_markdown(self):
        self.assertFalse(self.ok("Abuela Rosa https://x.com"))
        self.assertFalse(self.ok("**Abuela Rosa** loved arroz con leche."))

    def test_allows_cause_if_user_wrote_it(self):
        d = dict(DATA, note="She was sick for a long time but still cooked.")
        p = ofrenda.clean(d)
        self.assertTrue(guard.check("Abuela Rosa was sick for a long time but still cooked.", ofrenda.source_text(p), p["name"]))


class RememberTests(unittest.TestCase):
    def test_accepts_good_reply(self):
        r = remember.remember(person(), lambda s, u: GOOD)
        self.assertEqual(r["status"], "ok")

    def test_retries_with_shorter_prompt(self):
        calls = []

        def fake(system, user):
            calls.append(system)
            return "Abuela Rosa died in 1990." if len(calls) == 1 else GOOD
        r = remember.remember(person(), fake)
        self.assertEqual((r["status"], r["attempts"]), ("ok", 2))
        self.assertNotEqual(calls[0], calls[1])

    def test_rejected_after_two_bad_replies(self):
        r = remember.remember(person(), lambda s, u: "Abuela Rosa died in 1990.")
        self.assertEqual(r["status"], "rejected")

    def test_prompt_contains_only_user_facts(self):
        facts = remember.facts_prompt(person())
        self.assertIn("Arroz con leche", facts)
        self.assertNotIn("1990", facts)


class ServerLogicTests(unittest.TestCase):
    def setUp(self):
        self.saved = (server.BACKEND, server.DEMO_MODE, server.complete)

    def tearDown(self):
        server.BACKEND, server.DEMO_MODE, server.complete = self.saved

    def test_sample_without_model(self):
        server.BACKEND = "none"
        r = server.build_response({"sample": "rosa"})
        self.assertIn("no model", r["written_by"])
        self.assertIn("Abuela Rosa", r["remembrance"])

    def test_demo_refuses_own_text(self):
        server.DEMO_MODE = True
        with self.assertRaises(PermissionError):
            server.build_response(dict(DATA))

    def test_hosted_needs_consent(self):
        server.DEMO_MODE, server.BACKEND = False, "backboard"
        with self.assertRaises(PermissionError):
            server.build_response(dict(DATA))

    def test_model_text_used_when_guard_passes(self):
        server.DEMO_MODE, server.BACKEND = False, "ollama"
        server.complete = lambda s, u: GOOD
        server._label = lambda: "open model on this computer (test)"
        r = server.build_response(dict(DATA))
        self.assertEqual(r["remembrance"], GOOD)
        self.assertIn("checked by the guard", r["written_by"])

    def test_falls_back_when_guard_rejects(self):
        server.DEMO_MODE, server.BACKEND = False, "ollama"
        server.complete = lambda s, u: "Abuela Rosa died in 1990."
        r = server.build_response(dict(DATA))
        self.assertIn("guard rejected", r["written_by"])
        self.assertNotIn("1990", r["remembrance"])

    def test_falls_back_when_model_down(self):
        server.DEMO_MODE, server.BACKEND = False, "ollama"

        def boom(s, u):
            raise ConnectionError("down")
        server.complete = boom
        r = server.build_response(dict(DATA))
        self.assertIn("model unavailable: ConnectionError", r["written_by"])

    def test_unknown_sample(self):
        with self.assertRaises(ValueError):
            server.build_response({"sample": "nope"})

    def test_status_has_no_key(self):
        os.environ["BACKBOARD_API_KEY"] = "secret-test-key"
        server.BACKEND = "backboard"
        try:
            self.assertNotIn("secret-test-key", json.dumps(server.status_info()))
        finally:
            del os.environ["BACKBOARD_API_KEY"]


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.BACKEND, server.DEMO_MODE = "none", True
        cls.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def call(self, method, path, body=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port)
        c.request(method, path, json.dumps(body) if body is not None else None)
        r = c.getresponse()
        return r.status, r.read()

    def test_health_and_page(self):
        self.assertEqual(self.call("GET", "/healthz")[0], 200)
        code, body = self.call("GET", "/")
        self.assertEqual(code, 200)
        self.assertIn(b"Ofrenda Keeper", body)

    def test_samples_and_ofrenda(self):
        self.assertEqual(len(json.loads(self.call("GET", "/api/samples")[1])), 2)
        code, body = self.call("POST", "/api/ofrenda", {"sample": "kwame"})
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["ofrenda"]["title"], "In memory of Grandpa Kwame")

    def test_demo_blocks_own_text_403(self):
        self.assertEqual(self.call("POST", "/api/ofrenda", dict(DATA))[0], 403)

    def test_bad_json_400(self):
        c = http.client.HTTPConnection("127.0.0.1", self.port)
        c.request("POST", "/api/ofrenda", "[1,2]")
        self.assertEqual(c.getresponse().status, 400)


if __name__ == "__main__":
    unittest.main()
