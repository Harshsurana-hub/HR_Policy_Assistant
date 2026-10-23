"""Offline contract tests. Fictional fixtures are not HR policy results."""
import json
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from main import Evidence, Response, ask
import web_app

class FakeModel:
    def __init__(self, answer, supported=True):
        self.answer = answer
        self.supported = supported

    def with_structured_output(self, schema):
        value = self.answer if schema is Response else SimpleNamespace(supported=self.supported)
        return RunnableLambda(lambda _: value)

class GroundingTests(unittest.TestCase):
    def setUp(self):
        self.document = Document(page_content="The demo fixture allows two items.", metadata={"page": 2})
        self.store = SimpleNamespace(similarity_search=lambda *a, **k: [self.document])

    def response(self, chunk=0, quote="allows two items."):
        return Response(answer="The demo fixture allows two items.", evidence=[Evidence(chunk=chunk, quote=quote)])

    def test_validated_answer_uses_document_page_metadata(self):
        result = ask("How many demo items?", self.store, FakeModel(self.response()))
        self.assertIn("Answer: The demo fixture allows two items.", result)
        self.assertTrue(result.endswith("page(s) 3"))

    def test_unsupported_answer_is_exact_fallback(self):
        result = ask("Unknown?", self.store, FakeModel(Response(answer="Not found", evidence=[])))
        self.assertEqual(result, "Not found")

    def test_fabricated_quote_is_rejected(self):
        self.assertEqual(ask("How many?", self.store, FakeModel(self.response(quote="allows ten items."))), "Not found")

    def test_invalid_source_id_is_rejected(self):
        self.assertEqual(ask("How many?", self.store, FakeModel(self.response(chunk=99))), "Not found")

    def test_matching_quote_without_entailment_is_rejected(self):
        self.assertEqual(ask("How many?", self.store, FakeModel(self.response(), supported=False)), "Not found")

    def test_empty_retrieval_is_exact_fallback(self):
        store = SimpleNamespace(similarity_search=lambda *a, **k: [])
        self.assertEqual(ask("Unknown?", store, None), "Not found")

    def test_pdf_word_breaks_do_not_reject_valid_evidence(self):
        self.document.page_content = "The demo fix -\nture allows two items."
        result = ask("How many?", self.store, FakeModel(self.response()))
        self.assertIn("Answer:", result)

class WebContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        (cls.root / "web").mkdir()
        (cls.root / "web/index.html").write_text("<h1>Test fixture</h1>")
        (cls.root / ".env").write_text("PRIVATE_FIXTURE=not-for-serving")
        cls.root_patch = patch.object(web_app, "ROOT", cls.root)
        cls.root_patch.start()
        cls.state_patch = patch.dict(web_app.STATE, {"ready": True, "error": ""})
        cls.state_patch.start()
        cls.engine_patch = patch.object(web_app, "ENGINE", (None, None))
        cls.engine_patch.start()
        cls.server = web_app.ThreadingHTTPServer(("127.0.0.1", 0), web_app.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)
        cls.engine_patch.stop()
        cls.state_patch.stop()
        cls.root_patch.stop()
        cls.temp.cleanup()

    def request(self, path="/api/ask", data=None, headers=None):
        req = Request(self.base + path, data=data, headers=headers or {})
        try:
            response = urlopen(req, timeout=5)
        except HTTPError as exc:
            response = exc
        with response:
            return response.status, response.read()

    def post(self, question, **headers):
        return self.request(data=json.dumps({"question": question}).encode(), headers={"Content-Type": "application/json", **headers})

    def test_blank_question_is_rejected(self):
        self.assertEqual(self.post("   ")[0], 400)

    def test_non_string_question_is_rejected(self):
        self.assertEqual(self.post(["invalid"])[0], 400)

    def test_cross_origin_request_is_rejected(self):
        self.assertEqual(self.post("test", Origin="https://example.com")[0], 403)

    def test_environment_file_is_not_served(self):
        status, body = self.request("/.env")
        self.assertEqual(status, 404)
        self.assertNotIn(b"PRIVATE_FIXTURE", body)

    def test_fallback_has_no_reference_or_pages(self):
        with patch.object(web_app, "ask", return_value="Not found"):
            status, body = self.post("Unknown?")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"answer": "Not found", "reference": "", "pages": [], "supported": False})

    def test_model_failure_is_an_error_not_not_found(self):
        with patch.object(web_app, "ask", side_effect=RuntimeError("request failed")):
            status, body = self.post("Test question")
        self.assertEqual(status, 502)
        self.assertIn("error", json.loads(body))
        self.assertNotIn("answer", json.loads(body))

    def test_quota_failure_is_reported_as_429(self):
        with patch.object(web_app, "ask", side_effect=RuntimeError("429 RESOURCE_EXHAUSTED")):
            status, body = self.post("Test question")
        self.assertEqual(status, 429)
        self.assertIn("error", json.loads(body))

if __name__ == "__main__":
    unittest.main()
