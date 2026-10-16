# Disposable Notes

A disposable staging acceptance fixture: browser-based notes using Python's standard-library HTTP server and SQLite. MIT licensed; see LICENSE.

Run with Python 3 (no pip dependencies):

```sh
NOTES_DB=/tmp/disposable-notes/notes.sqlite3 PORT=8080 python3 app.py
```

Open port 8080, add a note using the form, and reload to read saved notes. The database persists at NOTES_DB (default /data/notes.sqlite3). The app binds all interfaces; use only a controlled disposable environment. There is no authentication, deletion UI, or rate limiting. Everyone with network access can read and add notes. Use synthetic, non-sensitive data only.

This initial source intentionally contains no Dockerfile, compose manifest, workflow, existing image, or prepared deployment metadata. Deployment files must be generated through the authorized staging flow, reviewed, and merged only into this disposable repository.

app.py is copied unchanged from logykk/zenith-pr840-e2e-20261013 at f9b366ccea2c8c7aba48e34a3ab91073c1ceb0bd (original app commit 718d171fcef7e22ab5b78d69e223686084189443). SHA-256: 2104e25382474b7ab2284666c45fcf78bc5f4b978ba433587a0e1a4be3408020.
