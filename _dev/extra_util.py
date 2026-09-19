"""Helpers for the EXTRA lesson material: run real code so printed output is always accurate."""
import contextlib
import io
import os
import re
import sqlite3
import subprocess
import tempfile


def _block(lang, src, out):
    return [("code", lang, src), ("output", out.rstrip("\n"))]


def py(src, setup=""):
    """Run `setup` silently first (e.g. to create files), then `src`; only `src` is shown."""
    buf = io.StringIO()
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d:  # examples may write files; keep the repo clean
        os.chdir(d)
        try:
            env = {"__name__": "__lesson__"}
            if setup:
                exec(compile(setup, "<setup>", "exec"), env)
            with contextlib.redirect_stdout(buf):
                exec(compile(src, "<lesson>", "exec"), env)
        finally:
            os.chdir(cwd)
    return _block("python", src, buf.getvalue())


def js(src):
    r = subprocess.run(["node", "-e", src], capture_output=True, text=True, timeout=20)
    if r.returncode:
        raise RuntimeError(r.stderr)
    return _block("javascript", src, r.stdout)


def java(src):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "Main.java")
        open(path, "w").write(src)
        r = subprocess.run(["java", path], capture_output=True, text=True, timeout=60)
    if r.returncode:
        raise RuntimeError(r.stderr)
    return _block("java", src, r.stdout)


def sql(setup, query):
    """Run `setup` (hidden DDL/INSERTs) then `query`; show the query and a text table."""
    con = sqlite3.connect(":memory:")
    con.executescript(setup)
    cur = con.execute(query)
    cols = [c[0] for c in cur.description]
    rows = [[("NULL" if v is None else str(v)) for v in r] for r in cur.fetchall()]
    widths = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]
    line = lambda cells: " | ".join(c.ljust(widths[i]) for i, c in enumerate(cells)).rstrip()
    out = "\n".join([line(cols), "-+-".join("-" * w for w in widths)] + [line(r) for r in rows])
    return _block("sql", query, out)


def sh(cmds, cwd_setup=None):
    """Run shell commands in a throwaway git sandbox; show the commands and their output."""
    with tempfile.TemporaryDirectory() as d:
        env = {**os.environ, "GIT_AUTHOR_NAME": "Ada", "GIT_AUTHOR_EMAIL": "ada@example.com",
               "GIT_COMMITTER_NAME": "Ada", "GIT_COMMITTER_EMAIL": "ada@example.com",
               "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "HOME": d}
        if cwd_setup:
            subprocess.run(cwd_setup, shell=True, cwd=d, env=env, capture_output=True, check=True)
        r = subprocess.run(cmds, shell=True, cwd=d, env=env, capture_output=True, text=True)
        out = (r.stdout + r.stderr)
    out = re.sub(r"\b[0-9a-f]{7}\b", "a1b2c3d", out) if False else out
    return _block("bash", cmds, out)
