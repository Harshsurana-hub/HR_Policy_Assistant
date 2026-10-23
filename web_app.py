"""Local browser interface for the existing, document-grounded CLI pipeline."""
import argparse
import json
import re
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from common import ROOT
from main import ask, load

STATE = {"ready": False, "error": "The assistant is starting."}
ENGINE = None
LOCK = threading.Lock()

class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, content_type="application/json"):
        if content_type == "application/json":
            body = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass  # The browser may close a request while navigating to the PDF.

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/status":
            metadata_path = ROOT / "chroma_db" / "manifest.json"
            metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
            return self.send(200, {**STATE, "pages": metadata.get("pages", 0), "chunks": metadata.get("chunks", 0)})
        routes = {"/": (ROOT / "web/index.html", "text/html; charset=utf-8"),
                  "/style.css": (ROOT / "web/style.css", "text/css; charset=utf-8"),
                  "/app.js": (ROOT / "web/app.js", "application/javascript; charset=utf-8"),
                  "/manual": (ROOT / "hr_manual.pdf", "application/pdf")}
        if path not in routes:
            return self.send(404, {"error": "Not found"})
        file, kind = routes[path]
        if not file.exists():
            return self.send(404, {"error": "File unavailable"})
        return self.send(200, file.read_bytes(), kind)

    def do_POST(self):
        if self.path != "/api/ask":
            return self.send(404, {"error": "Not found"})
        # Reject requests from other sites; the API is bound to loopback only.
        origin = self.headers.get("Origin")
        host = self.headers.get("Host")
        if origin and origin not in {f"http://{host}"}:
            return self.send(403, {"error": "Use the local assistant page to ask questions."})
        if self.headers.get("Content-Type", "").split(';')[0] != "application/json":
            return self.send(415, {"error": "JSON input required."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 16000:
                return self.send(400, {"error": "Question is too long or missing."})
            data = json.loads(self.rfile.read(length))
            question = data.get("question", "")
            if not isinstance(question, str) or not 1 <= len(question.strip()) <= 2000:
                return self.send(400, {"error": "Enter a question of 1–2,000 characters."})
        except (ValueError, AttributeError):
            return self.send(400, {"error": "Invalid question input."})
        if not STATE["ready"]:
            return self.send(503, {"error": STATE["error"]})
        if not LOCK.acquire(blocking=False):
            return self.send(503, {"error": "One question is already being answered. Please wait."})
        try:
            result = ask(question.strip(), *ENGINE)
            answer, _, reference = result.partition("\n\nReference: ")
            pages = [int(n) for n in re.findall(r"\d+", reference)]
            return self.send(200, {"answer": answer.removeprefix("Answer: "), "reference": reference,
                                   "pages": pages, "supported": result != "Not found"})
        except Exception as exc:
            limited = "429" in str(exc) or "RESOURCE_EXHAUSTED" in str(exc)
            return self.send(429 if limited else 502, {"error": "Gemini's request limit was reached. Please try again when quota is available." if limited else "The model request failed. Check your internet connection and local API configuration, then retry."})
        finally:
            LOCK.release()

    def log_message(self, format, *args):
        # Do not log employee questions or credentials.
        pass

def initialize():
    global ENGINE
    try:
        ENGINE = load()
        STATE.update(ready=True, error="")
    except Exception:
        STATE.update(ready=False, error="Setup is incomplete. Check .env and run python ingest.py before starting the UI.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    threading.Thread(target=initialize, daemon=True).start()
    url = f"http://127.0.0.1:{args.port}"
    print(f"HR Policy Assistant is available at {url}\nPress Control-C to stop.", flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
