#!/usr/bin/env python3
"""A small browser-based notes app using only the Python standard library."""
import html
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

DB = Path(os.environ.get("NOTES_DB", "/data/notes.sqlite3"))
PORT = int(os.environ.get("PORT", "8080"))
MAX_BODY = 32768


def connect():
    return sqlite3.connect(DB, timeout=10)


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, content_type="text/plain; charset=utf-8"):
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; form-action 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path != "/":
            self.send(404, "Not found\n")
            return
        with connect() as db:
            notes = db.execute("SELECT body, created_at FROM notes ORDER BY id DESC").fetchall()
        items = "".join(
            f"<li><pre>{html.escape(body)}</pre><small>{html.escape(date)} UTC</small></li>"
            for body, date in notes
        )
        self.send(200, "<!doctype html><html lang='en'><meta charset='utf-8'>"
                  "<meta name='viewport' content='width=device-width, initial-scale=1'>"
                  "<title>Disposable Notes</title><body><main><h1>Disposable Notes</h1>"
                  "<p>Public demo: use non-sensitive notes only. Anyone can read and add notes.</p>"
                  "<form method='post' action='/notes'><label for='body'>New note</label><br>"
                  "<textarea id='body' name='body' rows='5' cols='40' maxlength='4000' required></textarea>"
                  "<br><button type='submit'>Add note</button></form>"
                  f"<h2>Saved notes ({len(notes)})</h2><ul>{items}</ul></main></body></html>",
                  "text/html; charset=utf-8")

    def do_POST(self):
        if self.path != "/notes":
            self.send(404, "Not found\n")
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send(400, "Invalid content length\n")
            return
        if not 0 < size <= MAX_BODY:
            self.send(413, "Expected a nonempty form of at most 32768 bytes\n")
            return
        if self.headers.get_content_type() != "application/x-www-form-urlencoded":
            self.send(415, "Expected a URL-encoded form\n")
            return
        try:
            fields = parse_qs(self.rfile.read(size).decode("utf-8"), max_num_fields=10)
        except (ValueError, UnicodeError):
            self.send(400, "Invalid form\n")
            return
        body = fields.get("body", [""])[0].strip()
        if not body or len(body) > 4000:
            self.send(400, "Note must contain 1 to 4000 characters\n")
            return
        with connect() as db:
            db.execute("INSERT INTO notes (body) VALUES (?)", (body,))
        self.send_response(303)
        self.send_header("Location", "/")
        self.send_header("Content-Length", "0")
        self.end_headers()


if __name__ == "__main__":
    DB.parent.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, "
                   "body TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Notes listening on 0.0.0.0:{PORT}; SQLite: {DB}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
